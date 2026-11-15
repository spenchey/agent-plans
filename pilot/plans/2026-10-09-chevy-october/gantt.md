# Gantt

Generated from `plan.yaml` by `python -m planner gantt`. Do not edit by hand.

- Plan: chevy-october-2026 v16
- Origin: 2026-10-09T13:30:00-05:00
- CPM duration: 28.0417h (std dev 4.3702h along the critical path)
- Resource-constrained makespan: 29h
- Critical path: CH08, CH09, CH10, CH12, CH14, CH15, CH17, CH18
- `crit` means unconstrained CPM slack is zero. Bar times are the resource-constrained schedule.

| ID | Start | Finish | Slack | Assignee | Critical |
| --- | --- | --- | --- | --- | --- |
| CH01 | 0 | 7 | 5 | emily | no |
| CH08 | 0 | 6.1667 | 0 | rory | yes |
| CH11 | 0 | 6.5 | 14.9583 | dev | no |
| CH13 | 0 | 3.35 | 11.4 | spencer | no |
| CH20 | 6.1667 | 10.5 | 9.7083 | chevy-coordinator | no |
| CH21 | 6.5 | 10.8333 | 15.875 | dev | no |
| CH02 | 7 | 13.1667 | 5 | gpu-cb87 | no |
| CH09 | 7 | 12.3333 | 0 | emily | yes |
| CH22 | 10.8333 | 12.0833 | 9.7083 | dev | no |
| CH10 | 12.3333 | 14.5 | 0 | rory-copy-seo | yes |
| CH04 | 13.1667 | 16.3333 | 5 | chevy-coordinator | no |
| CH12 | 14.5 | 15.5833 | 0 | accuracy | yes |
| CH14 | 15.5833 | 22.2917 | 0 | spencer | yes |
| CH07 | 16.3333 | 17.4167 | 10.3583 | chevy-coordinator | no |
| CH25 | 17.4167 | 17.6833 | 10.3583 | chevy-coordinator | no |
| CH06 | 22.2917 | 29 | 5 | spencer | no |
| CH15 | 22.2917 | 24.4583 | 0 | dev | yes |
| CH16 | 24.4583 | 25 | 3.875 | accuracy | no |
| CH17 | 24.4583 | 27.7917 | 0 | dev | yes |
| CH19 | 25 | 25 | 3.875 | coordinator | no |
| CH18 | 27.7917 | 28.875 | 0 | chevy-coordinator | yes |

```mermaid
gantt
    title Chevy October 2026 v16
    dateFormat YYYY-MM-DD HH:mm
    axisFormat %m-%d %H:%M
    section Stills
    CH01 [MOT-3448] Story B stills v3 (six stills, native 16 9 and 9 16) through coordinator full-size QC - emily :done, ch01, 2026-10-09 13:30, 7h
    section Motion
    CH02 [MOT-3448] Story B H3 motion takes and full-quality re-renders (UNLOCKED) - gpu-cb87 :active, ch02, 2026-10-09 20:30, 370m
    section Assembly
    CH04 [MOT-3448] Final cuts assembled (16 9 and 9 16, 20.2 s) - chevy-coordinator :done, ch04, 2026-10-10 02:40, 190m
    section Approvals
    CH13 Spencer picks the Chevy and Toyota email subject lines - spencer :done, ch13, 2026-10-09 13:30, 201m
    CH14 Spencer approves the final Chevy email packet - spencer :crit, done, ch14, 2026-10-10 05:05, 403m
    CH06 Spencer approves the Story B final cut and the father and son voices - spencer :done, ch06, 2026-10-10 11:47, 403m
    section Publish
    CH07 Story B posts scheduled natively for 10/14 and 10/29 - chevy-coordinator :done, ch07, 2026-10-10 05:50, 65m
    CH25 Story B posts show in the social calendar (social-calendar sync) - chevy-coordinator :done, ch25, 2026-10-10 06:55, 16m
    section Email
    CH08 [MOT-3449] Chevy segments, holdouts and calendar v3 (Rory) - rory :crit, done, ch08, 2026-10-09 13:30, 370m
    CH11 [MOT-3451] Send, poll, follow-up and report automation for Chevy (build only) - dev :active, ch11, 2026-10-09 13:30, 390m
    CH20 Rebuild the Mailchimp segment tags and holdouts after the failed 10/13 dry run - chevy-coordinator :active, ch20, 2026-10-09 19:40, 260m
    CH21 Code PR that enforces the daily and per-person send caps - dev :active, ch21, 2026-10-09 20:00, 260m
    CH09 [MOT-3398] Targeted Chevy email drafts per segment with follow-ups (Emily plus Jeeves) - emily :crit, active, ch09, 2026-10-09 20:30, 320m
    CH22 Re-run the 10/13 dry run until it passes - dev :ch22, 2026-10-10 00:20, 75m
    CH10 [MOT-3392] Final compliance pass on the Chevy emails (GM Financial terms, disclosures, VINs) - rory-copy-seo :crit, ch10, 2026-10-10 01:50, 130m
    CH12 [MOT-3398] Coordinator full-size QC of the Chevy email packet - accuracy :crit, ch12, 2026-10-10 04:00, 65m
    CH15 Arm the Chevy sends first send 10/13 at 10 00 CT - dev :crit, ch15, 2026-10-10 11:47, 130m
    CH16 Verify the Chevy sends are armed - accuracy :ch16, 2026-10-10 13:57, 33m
    section Reporting
    CH17 [MOT-3451] Attribution report job for Chevy and Toyota - dev :crit, ch17, 2026-10-10 13:57, 200m
    CH18 First Monday attribution report posted (2026-10-19) - chevy-coordinator :crit, ch18, 2026-10-10 17:17, 65m
    section Milestones
    CH19 Milestone Chevy emails armed before the first send - coordinator :milestone, ch19, 2026-10-10 14:30, 0m
```
