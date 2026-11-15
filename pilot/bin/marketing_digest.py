#!/usr/bin/env python3
"""Daily agent-plans digest for Slack #marketing-team.

Refreshes the dashboard and the planner digest, then builds a plain-English
message that leads with "Waiting on Spencer" and posts it with the existing
Jeeves bot (the same bot that posts the campaign reports). The bot token is read
from ~/.hermes/profiles/jeeves/.env at run time and is never printed or stored
here. Dry run unless --post is passed.

Usage:
  marketing_digest.py            # print the message, send nothing
  marketing_digest.py --post     # post to #marketing-team
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
REPO = PILOT.parent
sys.path.insert(0, str(REPO))

from planner.model import load_plan, load_roster  # noqa: E402
from planner.reports import is_awaiting_human, is_dispatchable  # noqa: E402
from planner.util import parse_datetime, plan_dirs  # noqa: E402

CHANNEL = "C0BPXH8AQDS"  # #marketing-team (Jeeves bot is a member)
TOKEN_FILE = Path.home() / ".hermes" / "profiles" / "jeeves" / ".env"
CT = ZoneInfo("America/Chicago")
MOT = re.compile(r"\[(MOT-\d+)\]\s*")


def run_planner(*args: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "planner", "--root", str(PILOT), *args],
        cwd=REPO, check=True, stdout=subprocess.DEVNULL,
    )


def clean(title: str) -> str:
    return MOT.sub("", title).strip()


def card_ids(tasks) -> str:
    ids = sorted({m for t in tasks for m in MOT.findall(t.title)})
    return f" ({', '.join(ids)})" if ids else ""


def short(text: str, n: int = 90) -> str:
    text = clean(text)
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"



ENV_FILE = Path.home() / "clawd" / ".env"


def read_env(name: str, path: Path = ENV_FILE) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(rf"\s*(?:export\s+)?{name}=(.*)", line)
        if m:
            return m.group(1).strip().strip("\"'")
    raise RuntimeError(f"no {name} in {path}")


def linear_cards(ids: list[str]) -> dict:
    """Read-only: state, updatedAt and the newest comment for each MOT card. Never prints the key."""
    key = read_env("LINEAR_API_KEY")
    out = {}
    for ident in ids:
        query = ("query($id:String!){issue(id:$id){identifier title updatedAt state{name} "
                 "comments(first:10){nodes{createdAt body}}}}")
        body = json.dumps({"query": query, "variables": {"id": ident}}).encode()
        data = None
        for auth in (key, "Bearer " + key):
            req = urllib.request.Request("https://api.linear.app/graphql", data=body, method="POST",
                                         headers={"Authorization": auth, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as exc:
                if exc.code not in (400, 401, 403):
                    raise RuntimeError(f"linear http {exc.code}") from None
        issue = ((data or {}).get("data") or {}).get("issue")
        if not issue:
            continue
        comments = sorted(issue["comments"]["nodes"], key=lambda c: c["createdAt"])
        last = comments[-1] if comments else None
        out[ident] = {
            "state": issue["state"]["name"], "updated": parse_datetime(issue["updatedAt"], "updatedAt"),
            "last_comment": (last["body"].strip().splitlines()[0][:140] if last else ""),
            "last_comment_at": parse_datetime(last["createdAt"], "createdAt") if last else None,
        }
    return out


def plan_updated(plans) -> datetime:
    stamp = max(Path(p.path).stat().st_mtime for p in plans if p.path)
    return datetime.fromtimestamp(stamp, CT)


def load_all():
    roster = load_roster(PILOT / "roster.yaml")
    plans = [load_plan(d / "plan.yaml") for d in plan_dirs(PILOT, include_templates=False)]
    return roster, plans


def section_text(path: Path, heading: str) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    return [ln for ln in m.group(1).splitlines() if ln.strip() and ln.strip() != "- (none)"]


def build(now: datetime, tag: str = "", title: str = "Marketing plans digest") -> str:
    roster, plans = load_all()
    human = {b.name for b in roster.bots if b.kind == "human"}
    title_of = {}
    waiting_now: dict[str, list] = {}
    coming: dict[str, list] = {}
    in_review, in_motion, done_24h, blocked = [], [], [], []
    ready = []
    reported = []
    for plan in plans:
        known = {t.id: t for t in plan.tasks}
        dependents = {t.id: [] for t in plan.tasks}
        for t in plan.tasks:
            for d in t.depends_on:
                dependents[d.task].append(t)
            title_of[t.id] = t
        for t in plan.tasks:
            label = plan.title or plan.plan_id
            if t.assignee in human and t.status == "in_review":
                reported.append((label, t))
            elif t.assignee in human and t.status not in {"done", "cancelled"}:
                key = t.objective
                if is_awaiting_human(t, known):
                    holding = [clean(x.title) for x in dependents[t.id] if x.status != "done"][:3]
                    waiting_now.setdefault(key, []).append((plan, t, holding))
                else:
                    open_deps = [clean(known[d.task].title) for d in t.depends_on if known[d.task].status != "done"]
                    coming.setdefault(key, []).append((plan, t, open_deps))
            elif t.status == "in_review":
                in_review.append((label, t))
            elif t.status == "in_progress":
                in_motion.append((label, t))
            elif t.status in {"blocked", "failed"}:
                blocked.append((label, t))
            if t.status == "done" and t.actuals.end:
                try:
                    if now - parse_datetime(t.actuals.end, "end") <= timedelta(hours=24):
                        done_24h.append((label, t))
                except Exception:
                    pass
            if is_dispatchable(t, known):
                ready.append((label, t))

    lines = []
    stamp = now.astimezone(CT).strftime("%a %b %-d, %-I:%M %p CT")
    lines.append(f"*{title}, {stamp}*" + (f" ({tag})" if tag else ""))
    lines.append("_FYI only. No action needed from the agents. Linear stays the system of record; this is the planner's read of it._")
    lines.append("")
    lines.append("*Waiting on Spencer*")
    if waiting_now:
        for items in waiting_now.values():
            plan, t, holding = items[0]
            tasks = [x[1] for x in items]
            where = " and ".join(sorted({(x[0].title or x[0].plan_id) for x in items}))
            line = f"• *{clean(t.title)}*{card_ids(tasks)} ({where})"
            if holding:
                line += ". Holding up: " + "; ".join(short(h, 70) for h in holding)
            lines.append(line)
    else:
        lines.append("• Nothing right now.")
    if coming:
        lines.append("")
        lines.append("_Coming to Spencer once the work before it finishes:_")
        for items in coming.values():
            plan, t, open_deps = items[0]
            tasks = [x[1] for x in items]
            after = "; ".join(short(d, 75) for d in open_deps[:2]) or "earlier work"
            more = f" +{len(open_deps) - 2} more" if len(open_deps) > 2 else ""
            lines.append(f"• {clean(t.title)}{card_ids(tasks)}. After: {after}{more}.")
    if reported:
        lines.append("")
        lines.append("_Spencer already approved (per the coordinator); the approval record is still being filed:_")
        for label, t in reported:
            lines.append(f"• {label}: {short(t.title, 90)}")
    lines.append("")
    lines.append("*Done and checked in the last 24 hours*")
    if done_24h:
        for label, t in done_24h:
            lines.append(f"• {label}: {short(t.title)}")
    else:
        lines.append("• Nothing new.")
    lines.append("")
    lines.append("*Finished, waiting for the accuracy check*")
    if in_review:
        for label, t in in_review:
            lines.append(f"• {label}: {short(t.title)} ({t.assignee})")
    else:
        lines.append("• None.")
    lines.append("")
    lines.append("*Being worked now*")
    if in_motion:
        for label, t in in_motion:
            lines.append(f"• {label}: {short(t.title)} ({t.assignee})")
    else:
        lines.append("• None.")
    if blocked:
        lines.append("")
        lines.append("*Blocked or failed*")
        for label, t in blocked:
            lines.append(f"• {label}: {short(t.title)} ({t.status})")
    lines.append("")
    lines.append("*Ready to hand out*")
    if ready:
        for label, t in ready:
            lines.append(f"• {label}: {short(t.title)} ({t.assignee})")
    else:
        lines.append("• Nothing is unblocked and unassigned.")
    flagged = [(label, t) for label, t in in_review if t.risk == "high"]
    if flagged:
        lines.append("")
        lines.append("*Heads-up: reported done but not yet proven*")
        for label, t in flagged:
            lines.append(f"• {label}: {short(t.title, 80)}. {t.objective.split('. ', 1)[-1] if '. ' in t.objective else t.objective}")
    risks = section_text(PILOT / "dashboard" / "digest.md", "Risks")
    if risks:
        lines.append("")
        lines.append("*Risks*")
        lines.extend(risks)
    lines.append("")
    lines.append("*Emails armed?*")
    for plan in plans:
        known = {t.id: t for t in plan.tasks}
        for t in plan.tasks:
            if t.task_type == "email_send_ops" and t.title.startswith("Arm"):
                if t.status == "done":
                    lines.append(f"• {plan.title or plan.plan_id}: armed.")
                else:
                    open_deps = [clean(known[d.task].title) for d in t.depends_on if known[d.task].status not in {"done", "cancelled"}]
                    why = "; ".join(short(d, 70) for d in open_deps[:3]) or "ready to arm"
                    lines.append(f"• {plan.title or plan.plan_id}: NOT armed yet. Waiting on: {why}.")
    lines.append("")
    lines.append("*Linear check*")
    try:
        ids = sorted({m for p in plans for t in p.tasks for m in MOT.findall(t.title)})
        cards = linear_cards(ids)
        updated = plan_updated(plans)
        drift = [(i, c) for i, c in cards.items() if c["updated"] > updated + timedelta(minutes=2)]
        lines.append(f"• Plan last updated {updated.strftime('%a %-I:%M %p CT')}; checked {len(cards)} of {len(ids)} Linear cards at {now.astimezone(CT).strftime('%-I:%M %p CT')}.")
        if drift:
            lines.append("• *The plan may be behind.* These cards changed after the last plan update:")
            for i, c in sorted(drift):
                note = f' Latest comment: "{c["last_comment"]}"' if c["last_comment"] else ""
                lines.append(f"  - {i} ({c['state']}), updated {c['updated'].astimezone(CT).strftime('%a %-I:%M %p CT')}.{note}")
        else:
            lines.append("• No card has changed since the plan was last updated.")
        if now - updated > timedelta(hours=36):
            lines.append("• *The plan itself has not been updated for over 36 hours.*")
    except Exception as exc:
        lines.append(f"• Linear could not be read ({exc}); this digest reflects the plan only.")
    lines.append("")
    lines.append("*Key dates*")
    for plan in plans:
        if plan.deadline:
            d = parse_datetime(plan.deadline, "deadline").astimezone(CT)
            lines.append(f"• {plan.title or plan.plan_id}: first email send {d.strftime('%a %b %-d, %-I:%M %p CT')}")
    done = sum(1 for p in plans for t in p.tasks if t.status == "done")
    total = sum(len(p.tasks) for p in plans)
    lines.append("")
    lines.append(f"_{done} of {total} tasks done across {len(plans)} plans; each done task has an Accuracy pass and matching file hashes (checked just now). Only the accuracy check can mark a task done._")
    return "\n".join(lines)


def read_token() -> str:
    for line in TOKEN_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(?:export\s+)?SLACK_BOT_TOKEN=(.*)", line)
        if m:
            return m.group(1).strip().strip("\"'")
    raise RuntimeError(f"no SLACK_BOT_TOKEN in {TOKEN_FILE}")


def post(text: str) -> str:
    body = json.dumps({"channel": CHANNEL, "text": text, "unfurl_links": False, "unfurl_media": False}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage", data=body, method="POST",
        headers={"Authorization": "Bearer " + read_token(), "Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"slack request failed: {exc.reason}") from None
    if not data.get("ok"):
        raise RuntimeError(f"slack error: {data.get('error')}")
    return str(data.get("ts"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", action="store_true", help="post to #marketing-team (dry run otherwise)")
    ap.add_argument("--title", default="Marketing plans digest", help="message title")
    ap.add_argument("--label", default="", help="short tag shown in the header, e.g. test run")
    ap.add_argument("--at", help="ISO-8601 clock for the planner views (default now)")
    args = ap.parse_args()
    now = parse_datetime(args.at, "at") if args.at else datetime.now(CT)
    at = now.isoformat()
    run_planner("validate")  # raises if any done task lacks a passing attestation or the plans are invalid
    run_planner("dashboard", "--at", at)
    run_planner("digest", "--at", at)
    text = build(now, args.label, args.title)
    (PILOT / "dashboard" / "marketing-digest.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    if not args.post:
        print("\n[dry run: nothing posted]")
        return 0
    ts = post(text)
    print(f"\n[posted to #marketing-team, ts={ts}]")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # never leak anything but the message
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
