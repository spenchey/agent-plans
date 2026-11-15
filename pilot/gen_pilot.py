#!/usr/bin/env python3
"""One-shot generator for the Motor Inn pilot roster and the two October plans.

Runs on Mini 2 inside the agent-plans venv. It writes pilot/roster.yaml and the
two plan.yaml files, then it is done. After that the Planner edits plan.yaml
through the CLI. This script is not part of the pilot.
"""
import sys
from pathlib import Path

import yaml

PILOT = Path(sys.argv[1])
ORIGIN = "2026-10-09T13:30:00-05:00"


class _Indented(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, Dumper=_Indented, sort_keys=False, width=100, allow_unicode=True), encoding="utf-8")


# ---------------------------------------------------------------- roster
def bot(name, desc, caps, cap=1, kind=None):
    row = {"name": name, "description": desc, "capabilities": caps, "capacity": cap}
    if kind:
        row["kind"] = kind
    return row


roster = {
    "schema_version": 1,
    "default_max_parallel": 4,
    "bots": [
        bot("coordinator", "Orchestrator. The main Claude session. First contact, shapes asks, dispatches briefs, owns every plan. Does not write plan.yaml.", ["intake", "coordination", "dispatch"], 2),
        bot("planner", "Single writer of plan.yaml. One designated writer. Decomposes, estimates, assigns, replans, records status and actuals.", ["planning", "estimation", "scheduling"], 1),
        bot("emily", "Hermes profile emily on Mini 2 (local models). Stills, video direction, VO takes, email design and copy drafts.", ["creative_production", "still_compose", "email_design", "voice_direction", "copy_drafting"], 1),
        bot("rory", "Hermes profile rory on Mini 2 (local GLM). Offer facts, audience segments, Mailchimp and DealerVault reads (Mini 1), reporting. Aggregates only.", ["offer_facts", "audience_segments", "mailchimp_read", "reporting"], 1),
        bot("rory-copy-seo", "Hermes profile rory-copy-seo. Copy compliance passes and SEO copy.", ["copy_compliance", "seo_copy"], 1),
        bot("dev", "Hermes profile dev. Code, send automation, scheduled jobs, PRs.", ["coding", "send_automation", "email_send_ops"], 1),
        bot("emily-qa", "Hermes profile emily-qa. Runs machine gates and prepares QC evidence. It prepares; Accuracy decides.", ["gate_runs", "qc_prep"], 1),
        bot("toyota-producer", "Claude production agent for the Toyota October spots. Assembly, edit briefs, native scheduling.", ["video_assembly", "production_coordination", "native_publish"], 1),
        bot("november-producer", "Claude production agent for the November films. Listed for lane awareness (Mac Studio Ref2VA is busy with its finals).", ["video_assembly", "production_coordination"], 1),
        bot("chevy-coordinator", "Claude production agent for the Chevy October campaign. Assembly, native scheduling, attribution reports.", ["video_assembly", "production_coordination", "native_publish", "reporting_ops"], 1),
        bot("accuracy", "Verifier. Our machine gates plus the coordinator full-size QC. The only path to done: only Accuracy attests, then the Planner records done.", ["verification", "fact_check", "frame_qc", "full_size_qc", "listen_qc"], 2),
        bot("gpu-cb87", "GPU lane, not a person. spark-cb87 media lease, one unit at a time (never :8189, release by 21:50 CT). Capacity 1.", ["gpu_cb87", "gpu_render"], 1),
        bot("gpu-studio", "GPU lane, not a person. Mac Studio, 24/7 render node, one GPU job at a time. Capacity 1.", ["gpu_studio", "gpu_render"], 1),
        bot("spencer", "Human gate. Spencer's approvals only. Silence, a reaction, or a relayed approval from an agent does not count.", ["human_approval"], 1, kind="human"),
    ],
}
dump(PILOT / "roster.yaml", roster)

CAPS = {b["name"]: set(b["capabilities"]) for b in roster["bots"]}


# ---------------------------------------------------------------- tasks
def est(o, l, p):
    return {"optimistic": o, "likely": l, "pessimistic": p}


def T(id, title, section, ttype, objective, assignee, caps, e, crit, deps=(), status="planned",
      risk="low", rev=True, human=False, out=None, out_type="markdown", retries=2, start=None, attempts=None):
    assert set(caps) <= CAPS[assignee], (id, assignee, caps)
    hrs = e[2]
    return {
        "id": id, "title": title, "section": section, "task_type": ttype, "objective": objective,
        "_deps": list(deps), "_out": out or f"{id}-result.md", "_out_type": out_type,
        "estimate_hours": est(*e), "required_capabilities": list(caps), "assignee": assignee,
        "acceptance_criteria": crit, "risk": risk, "reversible": rev, "needs_human": human,
        "budget": {"tokens": 0, "hours": round(hrs * 1.5, 2), "usd": 0},
        "max_retries": retries, "status": status,
        "actuals": {"start": start, "end": None, "hours": None, "attempts": attempts if attempts is not None else (1 if start else 0)},
    }


def finish(tasks):
    by = {t["id"]: t for t in tasks}
    consumed = set()
    for t in tasks:
        t["inputs"] = []
        t["depends_on"] = list(t["_deps"])
        for d in t["_deps"]:
            assert d in by, (t["id"], d)
            t["inputs"].append({"artifact": by[d]["_out"], "from_task": d})
            consumed.add(d)
        t["outputs"] = [{"artifact": t["_out"], "type": t["_out_type"]}]
    deliverables = [t["_out"] for t in tasks if t["id"] not in consumed]
    order = ["id", "title", "section", "task_type", "objective", "inputs", "outputs", "depends_on", "estimate_hours",
             "required_capabilities", "assignee", "acceptance_criteria", "risk", "reversible", "needs_human",
             "budget", "max_retries", "status", "actuals"]
    clean = [{k: t[k] for k in order} for t in tasks]
    return clean, deliverables


G = "gate"  # human gate shorthand for task_type

# ------------------------------------------------------------ TOYOTA
toyota = [
    T("TY01", "[MOT-3356] Spencer approves the three Toyota scripts (Not a Drop, Group Chat, Feet Off)", "Approvals", "approval_gate",
      "Record Spencer's script approval of 2026-10-08 (scripts v2 for Not a Drop and Group Chat; Concept A Feet Off). Evidence: Linear MOT-3356 milestone comment 'production started on the approved scripts' and reports/TOYOTA_VIDEO_SCRIPTS_v2.md.",
      "spencer", ["human_approval"], (0.1, 0.25, 0.5),
      ["The approval record names Spencer, the date, and the exact script versions approved.",
       "The record cites the Linear MOT-3356 comment that states the approval."],
      human=True, out="TY01-script-approval-record.md"),
    T("TY02", "[MOT-3356] Spencer approves the Emily voice-over scripts", "Approvals", "approval_gate",
      "Record Spencer's VO approval of 2026-10-09 about 09:40 CT (verbatim 'approve the vo scripts', relayed by the coordinator first-hand). Evidence: reports/TOYOTA_VO_SCRIPTS.md status block.",
      "spencer", ["human_approval"], (0.1, 0.25, 0.5),
      ["The approval record quotes Spencer's words and the time.",
       "The record names the VO script file and states that Feet Off carries the new lines."],
      human=True, out="TY02-vo-approval-record.md"),
    T("TY03", "[MOT-3356] Start-frame stills v4 selected for all three spots", "Stills", "still_compose",
      "One Qwen-2.1 multi-ref compose per still on corrected plates (nightly method), native 9:16. Selects live in toyota-oct/stills/selects_v4. Needs coordinator full-size QC before it is called done.",
      "emily", ["creative_production", "still_compose"], (1, 2, 4),
      ["Every still is one multi-ref compose, with no pasted cut-outs.",
       "Truck scale, hands, head ratio and sign text pass full-size QC.",
       "Selects and sha256 sums are recorded."],
      deps=["TY01"], status="in_review", out="TY03-stills-v4-selects.json", out_type="json", start="2026-10-09T04:07:00-05:00", attempts=4),
    T("TY04", "[MOT-3356] Render the approved Emily VO takes (tuned locked-voice route)", "Audio", "voice_render",
      "ChatterboxTTS tuned route, 3 seeds per line, picked by pitch movement and pacing, checked by two ASR models and voice match. Output in toyota-oct/audio/vo_v4. End tag runs about 1 s longer.",
      "emily", ["voice_direction"], (1, 1.5, 3),
      ["Every approved line has a picked take with ASR and voice-match results.",
       "The end tag read fits at a natural pace.",
       "No AI-disclosure line, no aging or popularity language, phone 712-792-5000 only."],
      deps=["TY02"], status="in_review", out="TY04-vo-v4-picks.json", out_type="json", start="2026-10-09T09:48:00-05:00", attempts=2),
    T("TY05", "[MOT-3356] A person listens to every VO take before it goes in a cut", "Audio", "listen_qc",
      "Coordinator listens to each picked take: pronunciation (TUN-druh, CARE-ul, four-runner, letter-by-letter A-P-R and U-S-B-C), pacing, no robotic artifacts.",
      "accuracy", ["listen_qc"], (0.5, 1, 2),
      ["Every picked VO take was listened to by a person and passes pronunciation and pacing.",
       "Failing lines are re-rolled before assembly."],
      deps=["TY04"], out="TY05-vo-listen-notes.md"),
    T("TY06", "[MOT-3356] H3 finals on cb87: Not a Drop", "Motion", "gpu_render",
      "Full-quality H3 fl2va finals (bf16, 30 steps, 736x1312) for the Not a Drop shots that need generative motion; lock-plate shots built in the edit. cb87 lease rules: one unit, never :8189, release by 21:50 CT, alternate with Chevy.",
      "gpu-cb87", ["gpu_cb87"], (1, 1.5, 3),
      ["Every Not a Drop shot has a final-tier take that passes video_qc.",
       "The lease is released and no process is left on cb87."],
      deps=["TY03"], status="in_progress", out="TY06-nd-finals-manifest.json", out_type="json", start="2026-10-09T12:26:00-05:00", attempts=1),
    T("TY07", "[MOT-3356] H3 finals on cb87: The Group Chat", "Motion", "gpu_render",
      "Full-quality H3 finals for the Group Chat shots. Queued behind Not a Drop and Feet Off in the Chevy/Toyota alternation. Group Chat video-model audio stays muted except Emily's one on-camera line.",
      "gpu-cb87", ["gpu_cb87"], (1, 1.5, 3),
      ["Every Group Chat shot has a final-tier take that passes video_qc.",
       "Model audio is muted on every shot except Emily's scripted on-camera line.",
       "The lease is released and no process is left on cb87."],
      deps=["TY03"], out="TY07-gc-finals-manifest.json", out_type="json"),
    T("TY08", "[MOT-3356] H3 finals on cb87: Feet Off", "Motion", "gpu_render",
      "Full-quality H3 finals for the Feet Off shots (Crawl Control story).",
      "gpu-cb87", ["gpu_cb87"], (1, 1.5, 3),
      ["Every Feet Off shot has a final-tier take that passes video_qc.",
       "The lease is released and no process is left on cb87."],
      deps=["TY03"], status="in_progress", out="TY08-fo-finals-manifest.json", out_type="json", start="2026-10-09T12:46:00-05:00", attempts=1),
    T("TY09", "[MOT-3356] Studio Ref2VA close-face finals", "Motion", "gpu_render",
      "Mac Studio Ref2VA final-tier close and medium face shots (identity video). One GPU job at a time; the Studio is also a 24/7 render node (November finals).",
      "gpu-studio", ["gpu_studio"], (1, 2, 4),
      ["Studio final-tier face shots are delivered with sha256 sums.",
       "Identity matches the locked Emily reference."],
      deps=["TY03"], status="in_review", out="TY09-studio-ref2va-manifest.json", out_type="json", start="2026-10-09T04:30:00-05:00", attempts=1),
    T("TY10", "[MOT-3356] Assemble Not a Drop with the approved VO", "Assembly", "video_assembly",
      "Rebuilt cut: native 9:16, approved VO on the beats in TOYOTA_VO_SCRIPTS.md, ambience bed, J/L cuts, end tag about 4 s, rate-only offer end tag with Nov 2, 2026 and 712-792-5000. Must pass edit_brief_check.py.",
      "toyota-producer", ["video_assembly"], (1, 2, 3.5),
      ["The cut uses the approved VO lines and the final-tier takes.",
       "edit_brief_check.py reports 0 errors.",
       "End tag shows the offer exactly as OFFER-FACTS, legible at 390 px."],
      deps=["TY05", "TY06", "TY09"], out="TY10-NotADrop-VO-master.mp4", out_type="video"),
    T("TY11", "[MOT-3356] Assemble The Group Chat with the approved VO", "Assembly", "video_assembly",
      "Rebuilt cut with approved VO unchanged and model audio muted except Emily's on-camera line.",
      "toyota-producer", ["video_assembly"], (1, 2, 3.5),
      ["The cut uses the approved VO lines and the final-tier takes.",
       "edit_brief_check.py reports 0 errors.",
       "End tag shows the offer and price exactly as ruled by Spencer, legible at 390 px."],
      deps=["TY05", "TY07", "TY09", "TY16"], out="TY11-GroupChat-VO-master.mp4", out_type="video"),
    T("TY12", "[MOT-3356] Assemble Feet Off with the new approved VO", "Assembly", "video_assembly",
      "Rebuilt cut with the new Crawl Control VO, so the story reads without sound-on guessing.",
      "toyota-producer", ["video_assembly"], (1, 2, 3.5),
      ["The cut uses the approved Feet Off VO lines and the final-tier takes.",
       "edit_brief_check.py reports 0 errors.",
       "End tag shows the offer and price exactly as ruled by Spencer, legible at 390 px."],
      deps=["TY05", "TY08", "TY09", "TY16"], out="TY12-FeetOff-VO-master.mp4", out_type="video"),
    T("TY13", "[MOT-3356] Frame-by-frame QC: Not a Drop", "QC", "frame_qc",
      "Every shot at full size: anatomy, self-intersection, hands, head ratio, truck scale, tailgate state, sign text, eyelines, walk pace about 1.3 m/s, parked cars static; lip sync on every word; jump cuts; line sensitivity (no aging/popularity, no AI line); loudness -14 LUFS.",
      "accuracy", ["frame_qc"], (1, 1.5, 3),
      ["Every shot was checked frame by frame at full size and logged.",
       "Lip sync, walk pace and parked-car stillness pass.",
       "Offer, price and fine print match OFFER-FACTS."],
      deps=["TY10"], out="TY13-NotADrop-frame-qc.md"),
    T("TY14", "[MOT-3356] Frame-by-frame QC: The Group Chat", "QC", "frame_qc",
      "Same bar: USB-C port locations true to the pressroom photos, non-speaking friends, Emily's one on-camera line in sync.",
      "accuracy", ["frame_qc"], (1, 1.5, 3),
      ["Every shot was checked frame by frame at full size and logged.",
       "Port locations, lip sync and muted model audio pass.",
       "Offer, price and fine print match OFFER-FACTS."],
      deps=["TY11"], out="TY14-GroupChat-frame-qc.md"),
    T("TY15", "[MOT-3356] Frame-by-frame QC: Feet Off", "QC", "frame_qc",
      "Same bar: Crawl Control push pad on the lower-console dial, 4L, no claim the truck steers itself, no speed or grade numbers.",
      "accuracy", ["frame_qc"], (1, 1.5, 3),
      ["Every shot was checked frame by frame at full size and logged.",
       "Crawl Control claim says only what the owner's manual supports.",
       "Offer, price and fine print match OFFER-FACTS."],
      deps=["TY12"], out="TY15-FeetOff-frame-qc.md"),
    T("TY16", "Decide: may the Group Chat and Feet Off end tags show the price beside the APR?", "Approvals", "approval_gate",
      "OFFER-FACTS rule 1 and Spencer's 10/7 ruling disagree (open on MOT-3356, 10/8 22:31 comment). Group Chat shows $48,991 and Feet Off $59,448 next to 4.99% APR. Spencer rules; the end tags follow.",
      "spencer", ["human_approval"], (0.1, 2, 12),
      ["Spencer's explicit ruling and timestamp are recorded.",
       "The ruling names which end tags may show a price beside an APR."],
      human=True, out="TY16-price-beside-apr-ruling.md"),
    T("TY17", "[MOT-3356] Coordinator full-size QC of all three rebuilt cuts", "QC", "full_size_qc",
      "Coordinator watches each cut at full size as a viewer, with sound: story reads, voice locks, feet, eyelines, jump cuts, end tag at phone size. Nothing reaches Spencer before this passes.",
      "accuracy", ["full_size_qc"], (0.5, 1, 2),
      ["All three cuts passed a full-size viewing with sound by the coordinator.",
       "Every defect found is fixed or listed for Spencer."],
      deps=["TY13", "TY14", "TY15"], out="TY17-coordinator-full-size-qc.md"),
    T("TY18", "[MOT-3356] Spencer final approval of the three Toyota videos", "Approvals", "approval_gate",
      "Spencer watches the three rebuilt cuts and approves, or names changes. Open choices to carry: the Tundra TRD bed decal is not rendered; the 4Runner dial labels are soft (real-pixel patch available).",
      "spencer", ["human_approval"], (0.25, 4, 24),
      ["Spencer's explicit approval of each cut and the timestamp are recorded.",
       "The approved file names and sha256 sums are recorded."],
      deps=["TY17"], human=True, out="TY18-final-video-approval.md"),
    T("TY19", "[MOT-3356] Schedule the Toyota posts natively (FB scheduled reel, YT private plus publishAt, IG one-shot)", "Publish", "native_publish",
      "native-publish recipe after Spencer's approval: captions and tracked links, landing-page 200 check, register in posts_registry.json, sync Google Calendar. No Slack approval card.",
      "toyota-producer", ["native_publish"], (0.5, 1, 2),
      ["Each approved cut is scheduled natively on the approved platforms and dates.",
       "Tracked links return 200 and are registered for the weekly report.",
       "Google Calendar shows every scheduled post."],
      deps=["TY18"], risk="high", out="TY19-schedule-receipt.md"),
    T("TY20", "[MOT-3449] Toyota model-targeted subsets, holdouts, and calendar", "Email", "audience_segments",
      "Rory v3: tundra-trucks 961 (holdout 96), gh-family 1,049 (105), 4runner-suv 1,281 (128), aggregates only; calendar caps (550 a day Chevy plus Toyota, 2 per person per 7 days); Toyota runs 10/13 to 10/29.",
      "rory", ["audience_segments"], (2, 4, 8),
      ["Segment sizes and holdouts are recorded as aggregates only, with no contact data.",
       "The calendar keeps Chevy plus Toyota at or under 550 a day and Toyota inside 10/13 to 10/29."],
      out="TY20-segments-v3.json", out_type="json"),
    T("TY21", "[MOT-3450] Toyota emails fixed to the house standard (v4 packet)", "Email", "email_design",
      "Emily task t_620b39c4 on spark-fa5a. Fix: footer address 1526 Le Clark Rd, FNAME and TOYVEH merge fields with fallbacks, owner variants, remove tracking-reveal and 'no asterisks' copy, no tier names in fine print. Sender noreply@motorinnmail.com, UTMs on every link, top subject plus 2 alternates, 10 percent holdout (none under 100), follow-ups fu-nonopen/fu-open/fu-hot/fu-click.",
      "emily", ["email_design", "copy_drafting"], (2, 4, 8),
      ["Every footer shows 1526 Le Clark Rd and every email has working FNAME and TOYVEH merge fields with fallbacks.",
       "The full follow-up set and owner variants exist, with UTMs on every link.",
       "No copy reveals tracking, and no tier names appear in fine print."],
      deps=["TY20"], status="in_progress", out="TY21-toyota-email-packet-v4.md", start="2026-10-08T22:51:00-05:00", attempts=2),
    T("TY22", "[MOT-3266] Toyota email compliance QA against the QRG and OFFER-FACTS", "Email", "copy_compliance",
      "Line-by-line: APR, term, trim eligibility, exclusions, either/or cash rule, doc fee, 11/2/2026 end date, live VDP price and stock still active.",
      "rory-copy-seo", ["copy_compliance"], (1, 2, 4),
      ["Every APR, term, price and end date matches the QRG and the live VDP.",
       "Cash and APR are never presented as combinable.",
       "No unsupported history, popularity or aging language appears."],
      deps=["TY21"], out="TY22-toyota-email-compliance-qa.md"),
    T("TY23", "[MOT-3450] Coordinator full-size QC of the Toyota email packet", "Email", "full_size_qc",
      "Open every send file and every follow-up at phone width: address, merge fields, UTMs, fine print, links, holdout and suppression, subject picks.",
      "accuracy", ["full_size_qc", "fact_check"], (0.5, 1, 2),
      ["Every send file and follow-up was opened at phone width and passes.",
       "Links resolve with the correct UTMs and the sender is noreply@motorinnmail.com."],
      deps=["TY21", "TY22"], out="TY23-toyota-email-coordinator-qc.md"),
    T("TY24", "Spencer picks the Toyota (and Chevy) email subject lines", "Approvals", "approval_gate",
      "reports/SUBJECT_PICKS_for_Spencer.md. Spencer replies 'approve all' or names the ones to change.",
      "spencer", ["human_approval"], (0.1, 2, 12),
      ["Spencer's explicit pick for each subject line and the timestamp are recorded."],
      human=True, out="TY24-subject-picks-approval.md"),
    T("TY25", "[MOT-3451] Send, poll, follow-up and report automation cloned for Toyota (build only)", "Email", "send_automation",
      "Dev task t_362e81fc: clone the tire system (send, engagement poll, follow-up send, campaign report) for Chevy and Toyota. Presend live-VDP price check PR #777 and data-driven runtime PR #778 passed Eve and are held unmerged until Spencer's packet OK. Build only; arms nothing.",
      "dev", ["send_automation", "coding"], (3, 6, 12),
      ["Send, poll, follow-up and report jobs exist for Toyota and arm nothing.",
       "The presend live-VDP price check blocks a stale price."],
      status="in_review", out="TY25-send-automation-pr.md", start="2026-10-08T17:00:00-05:00", attempts=1),
    T("TY26", "Spencer approves the final Toyota email packet", "Approvals", "approval_gate",
      "One final packet states exactly what Spencer is approving: subjects, send files, follow-up set, segments and holdouts, send dates. Nothing is sent without this approval.",
      "spencer", ["human_approval"], (0.25, 4, 24),
      ["Spencer's explicit approval of the final Toyota email packet and the timestamp are recorded.",
       "The approved packet version and sha256 are recorded."],
      deps=["TY20", "TY23", "TY24"], human=True, out="TY26-toyota-email-packet-approval.md"),
    T("TY27", "Arm the Toyota sends: first send 10/13 at 13:00 CT", "Email", "email_send_ops",
      "Merge PR #777/#778 after the packet OK, then schedule the Mailchimp sends and arm the poll, follow-up and report launchd jobs for the first send 2026-10-13 13:00 CT, at most 250 a day per the calendar.",
      "dev", ["email_send_ops"], (1, 2, 4),
      ["The first Toyota send is scheduled for 2026-10-13 13:00 CT.",
       "The 10 percent holdout, suppression and UTMs are in place on the scheduled send.",
       "The poll, follow-up and report jobs are armed."],
      deps=["TY26", "TY25"], risk="high", out="TY27-toyota-arm-receipt.md"),
    T("TY28", "Verify the Toyota sends are armed", "Email", "verification",
      "Read back the Mailchimp schedule and the launchd jobs; compare to the approved packet.",
      "accuracy", ["verification"], (0.25, 0.5, 1),
      ["The scheduled send time, audience, holdout and subject match the approved packet.",
       "The follow-up and report jobs are loaded."],
      deps=["TY27"], out="TY28-toyota-arm-verification.md"),
    T("TY29", "[MOT-3451] Toyota attribution report job (opens, clicks, VDP by UTM, holdout vs mailed)", "Reporting", "reporting_ops",
      "Weekly Monday report to Spencer: opens, clicks, VDP visits by UTM, holdout versus mailed, follow-up performance. Aggregates only; separates exposure lift from sale contribution.",
      "dev", ["send_automation", "coding"], (2, 3, 6),
      ["The report job runs on the schedule and posts aggregates only.",
       "The report separates exposure lift from sale contribution."],
      deps=["TY27"], out="TY29-toyota-report-job.md"),
    T("TY30", "Milestone: Toyota emails armed before the first send", "Milestones", "milestone",
      "Marker. Toyota emails are verified armed ahead of 2026-10-13 13:00 CT.",
      "coordinator", ["coordination"], (0, 0, 0),
      ["Toyota emails are verified armed ahead of the first send."],
      deps=["TY28"], out="TY30-milestone.md"),
]

# ------------------------------------------------------------ CHEVY
chevy = [
    T("CH01", "[MOT-3448] Story B stills v3 (six stills, native 16:9 and 9:16) through coordinator full-size QC", "Stills", "still_compose",
      "Qwen-Image-2.1 multi-ref compose on cb87 (VDP photo, father and son refs, Blender layout). Notes in STILLS-QC.md. Rejected on the way: S1 v1 to v3, S4 v1 to v2.",
      "emily", ["creative_production", "still_compose"], (4, 7, 10),
      ["All six stills pass coordinator full-size QC.",
       "STILLS-QC.md records the rejects and the fixes."],
      out="CH01-STILLS-QC.md", start="2026-10-08T19:59:00-05:00", attempts=3),
    T("CH02", "[MOT-3448] Story B H3 motion takes and full-quality re-renders (UNLOCKED)", "Motion", "gpu_render",
      "H3 drafts, then full-quality re-renders pre-rendered UNLOCKED via tier_overrides. All takes pass geometry (motorinn-studio #121) and video_qc.",
      "gpu-cb87", ["gpu_cb87"], (4, 6, 9),
      ["All takes pass geometry and video_qc.",
       "The lease is released and no process is left on cb87."],
      deps=["CH01"], status="in_review", out="CH02-motion-takes-manifest.json", out_type="json", start="2026-10-09T03:15:00-05:00", attempts=2),
    T("CH03", "[MOT-3448] H1 16:9 retake on a new seed (the full re-render dropped the broom)", "Motion", "gpu_render",
      "Retake queued on a new seed to replace the draft-tier Super Scale H1 16:9. Strict Chevy/Toyota alternation on cb87.",
      "gpu-cb87", ["gpu_cb87"], (0.5, 0.75, 1.5),
      ["The H1 16:9 take keeps every prop and passes geometry and video_qc.",
       "The lease is released and no process is left on cb87."],
      deps=["CH02"], out="CH03-h1-retake.json", out_type="json"),
    T("CH04", "[MOT-3448] Final candidates assembled (16:9 and 9:16, 20.2 s, UNLOCKED, not approved)", "Assembly", "video_assembly",
      "rebuild-v3/cut/final: candidate cuts, DELIVERY-NOTES.md, edit_brief JSONs, SHA256SUMS. End card on the #120 hierarchy ($62,855 above 'or 0% APR for 60 months*' above badge, phone, GM legal), legible at 390 px; audio about -14.6 LUFS, no music, no Emily VO.",
      "chevy-coordinator", ["video_assembly"], (2, 3, 5),
      ["edit_brief_check reports 0 errors in both aspects.",
       "The candidate cuts and SHA256SUMS are delivered and the sums match the files."],
      deps=["CH02"], out="CH04-DELIVERY-NOTES.md", start="2026-10-09T05:15:00-05:00", attempts=2),
    T("CH05", "[MOT-3448] Coordinator full-size QC of the final candidates after the H1 retake", "QC", "full_size_qc",
      "Watch both aspects at full size with sound; confirm the H1 retake keeps every prop; father and son H3 voices flagged for Spencer's ear (A1).",
      "accuracy", ["full_size_qc"], (0.5, 1, 2),
      ["Both aspects passed a full-size viewing with sound by the coordinator.",
       "The H1 retake replaces the draft-tier H1."],
      deps=["CH03", "CH04"], out="CH05-final-candidate-qc.md"),
    T("CH06", "Spencer reviews the Story B final candidate and listens to the father and son voices", "Approvals", "approval_gate",
      "Candidates are UNLOCKED, not approved, not for ship. Spencer approves, or names changes. Includes the father and son raw H3 voices that need his ear (A1) and the end card hierarchy.",
      "spencer", ["human_approval"], (0.25, 4, 24),
      ["Spencer's explicit approval of the Story B cut and the timestamp are recorded.",
       "The approved file names and sha256 sums are recorded."],
      deps=["CH04"], human=True, out="CH06-story-b-approval.md"),
    T("CH07", "Story B posts scheduled natively for 10/14 and 10/29", "Publish", "native_publish",
      "Reported done by the coordinator. The pilot found no scheduler receipt, registry entry, or calendar event and the cut is not approved, so this stays in review until a receipt is attached and Accuracy attests.",
      "chevy-coordinator", ["native_publish"], (0.5, 1, 2),
      ["Story B is scheduled natively for 2026-10-14 and 2026-10-29 on the approved platforms.",
       "The scheduled file is the Spencer-approved cut.",
       "Google Calendar shows both scheduled posts."],
      deps=["CH04"], status="in_review", risk="high", out="CH07-schedule-receipt.md", start="2026-10-09T08:00:00-05:00", attempts=1),
    T("CH08", "[MOT-3449] Chevy segments, holdouts and calendar v3 (Rory)", "Email", "audience_segments",
      "Cleaned/unsubscribed join, import of 274 tagged, arm-level segments with holdouts: silverado-broad 1,579 (158), silverado-owner 116 (12), silverado-service 65, equinox-owner 73, equinox-service 91, colorado-owner 26, colorado-service 28, trax 12; calendar v3/v4. Aggregates only.",
      "rory", ["audience_segments"], (3, 6, 10),
      ["Segment sizes and holdouts are recorded as aggregates only, with no contact data.",
       "Segments under 100 have no holdout."],
      out="CH08-segments-v3.json", out_type="json", start="2026-10-08T14:59:00-05:00", attempts=3),
    T("CH09", "[MOT-3398] Targeted Chevy email drafts per segment with follow-ups (Emily plus Jeeves)", "Email", "email_design",
      "Per segment: subject (top pick plus 2 alternates), audience, verified offer wording, CTA, full disclosures; follow-ups fu-nonopen/open/hot/click plus owner variants. Proof packet v2 and subject rewrites of 10/9 09:15 exist.",
      "emily", ["email_design", "copy_drafting"], (3, 5, 9),
      ["Every segment has a draft, a top subject and 2 alternates, verified offer wording and full disclosures.",
       "UTMs are on every link and the sender is noreply@motorinnmail.com."],
      deps=["CH08"], status="in_review", out="CH09-chevy-email-packet.md", start="2026-10-08T14:55:00-05:00", attempts=2),
    T("CH10", "[MOT-3392] Final compliance pass on the Chevy emails (GM Financial terms, disclosures, VINs)", "Email", "copy_compliance",
      "Verify GM terms, disclosure wording, payment example math, qualifying VINs, stacking rules; confirm each stock is still active on its live VDP.",
      "rory-copy-seo", ["copy_compliance"], (1, 2, 4),
      ["Every APR, term, price and end date matches the GM terms and the live VDP.",
       "Cash and APR are never presented as combinable.",
       "No unsupported history, popularity or aging language appears."],
      deps=["CH09"], out="CH10-chevy-email-compliance-qa.md"),
    T("CH11", "[MOT-3451] Send, poll, follow-up and report automation for Chevy (build only)", "Email", "send_automation",
      "Same build as Toyota (PR #777 presend live-VDP price check, #778 data-driven runtime), Eve passed, held unmerged until Spencer's packet OK.",
      "dev", ["send_automation", "coding"], (3, 6, 12),
      ["Send, poll, follow-up and report jobs exist for Chevy and arm nothing.",
       "The presend live-VDP price check blocks a stale price."],
      status="in_review", out="CH11-send-automation-pr.md", start="2026-10-08T17:00:00-05:00", attempts=1),
    T("CH12", "[MOT-3398] Coordinator full-size QC of the Chevy email packet", "Email", "full_size_qc",
      "Open every send file and follow-up at phone width: address, merge fields, UTMs, fine print, links, holdout and suppression.",
      "accuracy", ["full_size_qc", "fact_check"], (0.5, 1, 2),
      ["Every send file and follow-up was opened at phone width and passes.",
       "Links resolve with the correct UTMs and the sender is noreply@motorinnmail.com."],
      deps=["CH09", "CH10"], out="CH12-chevy-email-coordinator-qc.md"),
    T("CH13", "Spencer picks the Chevy (and Toyota) email subject lines", "Approvals", "approval_gate",
      "reports/SUBJECT_PICKS_for_Spencer.md. Spencer replies 'approve all' or names the ones to change.",
      "spencer", ["human_approval"], (0.1, 2, 12),
      ["Spencer's explicit pick for each subject line and the timestamp are recorded."],
      human=True, out="CH13-subject-picks-approval.md"),
    T("CH14", "Spencer approves the final Chevy email packet", "Approvals", "approval_gate",
      "One final packet states exactly what Spencer is approving: subjects, send files, follow-up set, segments and holdouts, send dates. Nothing is sent without this approval.",
      "spencer", ["human_approval"], (0.25, 4, 24),
      ["Spencer's explicit approval of the final Chevy email packet and the timestamp are recorded.",
       "The approved packet version and sha256 are recorded."],
      deps=["CH08", "CH12", "CH13"], human=True, out="CH14-chevy-email-packet-approval.md"),
    T("CH15", "Arm the Chevy sends: first send 10/13 at 10:00 CT", "Email", "email_send_ops",
      "Merge PR #777/#778 after the packet OK, then schedule the Mailchimp sends and arm the poll, follow-up and report launchd jobs for the first send 2026-10-13 10:00 CT, Chevy inside the 550 a day shared cap.",
      "dev", ["email_send_ops"], (1, 2, 4),
      ["The first Chevy send is scheduled for 2026-10-13 10:00 CT.",
       "The 10 percent holdout, suppression and UTMs are in place on the scheduled send.",
       "The poll, follow-up and report jobs are armed."],
      deps=["CH14", "CH11"], risk="high", out="CH15-chevy-arm-receipt.md"),
    T("CH16", "Verify the Chevy sends are armed", "Email", "verification",
      "Read back the Mailchimp schedule and the launchd jobs; compare to the approved packet.",
      "accuracy", ["verification"], (0.25, 0.5, 1),
      ["The scheduled send time, audience, holdout and subject match the approved packet.",
       "The follow-up and report jobs are loaded."],
      deps=["CH15"], out="CH16-chevy-arm-verification.md"),
    T("CH17", "[MOT-3451] Attribution report job for Chevy and Toyota", "Reporting", "reporting_ops",
      "Opens, clicks, VDP visits by UTM, holdout versus mailed, follow-up performance; aggregates only; weekly Monday; separates exposure lift from sale contribution.",
      "dev", ["send_automation", "coding"], (2, 3, 6),
      ["The report job runs on the schedule and posts aggregates only.",
       "The report separates exposure lift from sale contribution."],
      deps=["CH15"], out="CH17-report-job.md"),
    T("CH18", "First Monday attribution report posted (2026-10-19)", "Reporting", "reporting_ops",
      "Run the report job, check the numbers against GA4 and Mailchimp, post to Spencer. Plain statement when a post drove views on a unit that did not sell.",
      "chevy-coordinator", ["reporting_ops"], (0.5, 1, 2),
      ["The report posted with aggregates only and the lift versus sale split.",
       "Numbers were checked against the source systems."],
      deps=["CH17"], out="CH18-first-attribution-report.md"),
    T("CH19", "Milestone: Chevy emails armed before the first send", "Milestones", "milestone",
      "Marker. Chevy emails are verified armed ahead of 2026-10-13 10:00 CT.",
      "coordinator", ["coordination"], (0, 0, 0),
      ["Chevy emails are verified armed ahead of the first send."],
      deps=["CH16"], out="CH19-milestone.md"),
]


def write_plan(slug, plan_id, title, goal, dod, deadline, priority, tasks, hours_budget):
    clean, deliverables = finish(tasks)
    doc = {
        "schema_version": 1, "plan_id": plan_id, "version": 1, "title": title, "priority": priority,
        "goal": goal, "owner": "coordinator", "definition_of_done": dod,
        "budget": {"tokens": 0, "hours": hours_budget, "usd": 0},
        "human_approval_policy": (
            "Spencer approves, first-hand in chat or on the Linear card, every script, final video, subject line, "
            "email packet, and any rule change before it is used. Silence, a reaction, or a relayed approval from an agent does not count. "
            "While a gate is open, hold the work it blocks; work it does not block continues. Linear stays the system of record: "
            "task titles carry the MOT card id, and this plan never creates or edits Linear cards. Local models first; no cloud credits without a per-generation OK."),
        "constraints": {"deadline": deadline, "max_parallel": 4, "schedule_origin": ORIGIN},
        "provided_inputs": [], "deliverables": deliverables, "tasks": clean,
    }
    d = PILOT / "plans" / slug
    dump(d / "plan.yaml", doc)
    (d / "log.md").write_text(
        "# Decision log\n\nAppend-only. Add new entries at the bottom. Do not edit earlier entries.\n\n"
        "## 2026-10-09 v1\n\n"
        f"- Reason: Pilot plan for {title}, built from the Linear cards and the artifacts on disk at 13:30 CT.\n"
        "- Change: Initial tasks, dependencies, PERT estimates, roster assignments and acceptance criteria.\n"
        "- Frozen: none at creation.\n", encoding="utf-8")
    print("wrote", d, len(clean), "tasks")


write_plan("2026-10-09-toyota-october", "toyota-october-2026", "Toyota October 2026",
           "Rebuild the three Toyota October videos (Not a Drop, Group Chat, Feet Off) with the approved Emily VO, get Spencer's final approval, schedule the posts natively, and arm the Toyota emails for the first send on 2026-10-13 at 13:00 CT.",
           "Three approved videos are scheduled natively, the Toyota emails are verified armed before 2026-10-13 13:00 CT, and reporting is armed. Linear cards MOT-3356, MOT-3449, MOT-3450 and MOT-3451 stay the system of record.",
           "2026-10-13T13:00:00-05:00", 2, toyota, 80)
write_plan("2026-10-09-chevy-october", "chevy-october-2026", "Chevy October 2026",
           "Finish Story B (approved cut, posts scheduled 10/14 and 10/29), arm the Chevy emails for the first send on 2026-10-13 at 10:00 CT, and report attribution weekly.",
           "Story B is approved and its schedule is attested, the Chevy emails are verified armed before 2026-10-13 10:00 CT, and the first Monday attribution report is posted. Linear cards MOT-3448, MOT-3449, MOT-3398, MOT-3392 and MOT-3451 stay the system of record.",
           "2026-10-13T10:00:00-05:00", 1, chevy, 70)
