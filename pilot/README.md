# Motor Inn agent-plans pilot

Pilot of https://github.com/r0b0tlab/agent-plans (Apache-2.0) for the marketing agents. Started 2026-10-09 after Spencer said "run along linear, marketing team channel". Linear stays the system of record. Plans mirror the Linear cards (ids are in the task titles) and never create or edit cards.

Everything pilot-specific lives in this folder. The upstream checkout one level up is untouched, so `python3 -m planner check` there still passes. Every command below runs from `~/Projects/agent-plans` with the `--root pilot` flag:

    cd ~/Projects/agent-plans
    p() { .venv/bin/python -m planner --root pilot "$@"; }

Files: `roster.yaml` (who can do what), `plans/2026-10-09-toyota-october`, `plans/2026-10-09-chevy-october`, `evidence/` (approval records), `dashboard/` (generated), `bin/marketing_digest.py` (Slack digest), `gen_pilot.py` (one-shot generator, not part of the loop).

## How an agent reads the ready queue

1. `p ready` prints, per plan, `dispatch` (unblocked work an agent may take) and `awaiting_human` (Spencer's gates; agents never touch these).
2. Take only tasks whose assignee is you. `p brief pilot/plans/<slug> <task_id>` writes `briefs/<task_id>.md`: objective, inputs with sha256, expected output path, acceptance criteria, estimate, budget, retries left.
3. Do the work. Do not widen scope. GPU work follows the lane rules: gpu-cb87 and gpu-studio take one job at a time.
4. Record each output: `p record-artifact pilot/plans/<slug> <task_id> --file <path> --name <output name from the task>`.
5. Report to the planner (task id, status, hours, where the files are) and stop at `in_review`. Workers never write `plan.yaml` and never set `done`.
6. The planner is the only writer of `plan.yaml`: `p set-status pilot/plans/<slug> <task_id> in_progress|in_review|blocked|failed --start <ISO> --hours <n>`.

A task that waits on Spencer is a human gate. It appears in `awaiting_human` only after its dependencies are done. Hold it; agents do not nudge Spencer.

## How the coordinator attests (the only path to done)

Accuracy is the verifier: our machine gates plus the coordinator's full-size QC. A task is done only after all four steps, in order:

1. Check the work first-hand against every acceptance criterion in `plan.yaml`: open the file at full size, run the gate, read the receipt. For a Spencer gate, the evidence must be his own words from chat or the Linear card, with the time. An agent relaying "he approved" is not evidence unless the coordinator saw it first-hand.
2. Make sure the output is recorded: `p record-artifact ... --file ... --name ...` (this hashes it into `artifacts/<task>/manifest.yaml`).
3. Attest. Pass only if every criterion is met: `p attest-done pilot/plans/<slug> <task_id> --verdict pass --at <ISO>`. Otherwise `--verdict fail --notes "what failed"`; a fail goes back to rework (`set-status ... failed` or `in_review`).
4. The planner records it: `p complete pilot/plans/<slug> <task_id> --hours <n> --attempts <n> --start <ISO> --end <ISO>`. It refuses without a passing attestation from accuracy and matching hashes.

Then run `p validate`, `p schedule <plan>`, `p gantt <plan>`, `p portfolio`, `p portfolio schedule` and `p dashboard` to refresh the views. If actuals slip, `p replan <plan> --now --reason "..."`.

Never type `done` into `plan.yaml`. Never attest your own work as the producer. The done-lock is enforced inside this tool chain; it is not a cryptographic signature.

## Slack digest

`bin/marketing_digest.py` refreshes the dashboard and the planner digest, then builds a plain-English message that leads with "Waiting on Spencer". `--post` sends it to #marketing-team through the existing Jeeves bot (token read at run time from `~/.hermes/profiles/jeeves/.env`, never printed). Without `--post` it is a dry run. Rory and Emily only answer bot messages that @mention them, and the digest mentions nobody.

Schedule: launchd agent `com.motorinn.agent-plans-digest` (in `~/Library/LaunchAgents`), daily 08:00 America/Chicago. Logs are in `logs/`. Stop it with `launchctl bootout gui/$(id -u)/com.motorinn.agent-plans-digest`. Dashboard: `dashboard/index.html`. Latest message text: `dashboard/marketing-digest.md`.

## Keeping the plan current (added after the 2026-10-09 correction)

The first digest went stale because approvals reached the coordinator, not the plan. The daily digest now guards against that: it runs `validate` first (a done task without an Accuracy pass blocks the post), then reads the Linear cards named in the task titles (read-only, key from `~/clawd/.env`, never printed) and prints a "Linear check" section. If a card changed after `plan.yaml` was last updated, or the plan is over 36 hours old, the digest says "The plan may be behind". When the coordinator learns of an approval or a schedule, the planner updates the plan the same hour: record the evidence file under `evidence/`, then `record-artifact`, `attest-done`, `complete`.

A Spencer approval that has been reported but whose record (timestamp, packet version, file hash) is not filed yet sits in `in_review` on the gate task. The digest shows it as "already approved, record being filed", not as something Spencer is asked for.

## Known gaps (2026-10-09, after the second correction)

- Story B is approved, scheduled and in the social calendar (CH06, CH07, CH25 attested). The social-calendar log shows created=2 after each YouTube schedule, but created=0 on both Facebook runs; look once at the social calendar for the two Facebook reels.
- Packet approvals are attested from the coordinator's first-hand quotes (CH14 Chevy offer-emails-v7, TY26 Toyota emily-v3), with the packet file hashes recorded.
- Emails are not armed. The 10/13 dry run failed (segment tags, holdouts, send caps); CH20 to CH22 (Chevy) and TY31 (Toyota) track the fix, and both arm tasks depend on them.
- TY16 is attested: the governing reading bans OEM customer cash netted into a price beside a special APR (OFFER-FACTS rule 1 agrees). Live VDPs checked: GH and 4Runner carry only a dealer discount, so price plus APR passes; the Tundra nets $1,000 Toyota Customer Cash, so it stays rate-only.
- CH02, CH09, CH11, TY03, TY04, TY09 and TY25 are finished work still waiting for the Accuracy check.
- The Rory v3 segments file backs both CH08 and TY20 (one job, two plans); TY20 actual hours are an estimated share.
- The portfolio schedule shows `accuracy` over-allocated across the two plans: the verifier is the bottleneck.
