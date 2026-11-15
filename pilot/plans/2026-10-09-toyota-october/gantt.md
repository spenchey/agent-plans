# Gantt

Generated from `plan.yaml` by `python -m planner gantt`. Do not edit by hand.

- Plan: toyota-october-2026 v10
- Origin: 2026-10-09T13:30:00-05:00
- CPM duration: 24.125h (std dev 4.0528h along the critical path)
- Resource-constrained makespan: 28.2083h
- Critical path: TY23, TY26, TY27, TY29
- `crit` means unconstrained CPM slack is zero. Bar times are the resource-constrained schedule.

| ID | Start | Finish | Slack | Assignee | Critical |
| --- | --- | --- | --- | --- | --- |
| TY01 | 0 | 0.2667 | 6.9 | spencer | no |
| TY16 | 0 | 0.5417 | 10.9583 | accuracy | no |
| TY20 | 0 | 4.3333 | 0 | rory | no |
| TY25 | 0 | 6.5 | 12.125 | dev | no |
| TY03 | 0.2667 | 2.4333 | 6.9 | emily | no |
| TY02 | 0.5417 | 0.8083 | 8.4833 | spencer | no |
| TY24 | 0.8083 | 4.1583 | 8.5667 | spencer | no |
| TY09 | 2.4333 | 4.6 | 6.9 | gpu-studio | no |
| TY06 | 4.1583 | 5.825 | 7.4 | gpu-cb87 | no |
| TY21 | 4.3333 | 8.6667 | 0 | emily | no |
| TY32 | 4.6 | 5.45 | 23.275 | spencer | no |
| TY33 | 5.45 | 6.3 | 23.275 | spencer | no |
| TY07 | 5.825 | 7.4917 | 7.4 | gpu-cb87 | no |
| TY31 | 6.5 | 11.8333 | 13.2917 | dev | no |
| TY08 | 7.4917 | 9.1583 | 7.4 | gpu-cb87 | no |
| TY04 | 8.6667 | 10.3333 | 8.4833 | emily | no |
| TY22 | 8.6667 | 10.8333 | 0 | rory-copy-seo | no |
| TY05 | 10.3333 | 11.4167 | 8.4833 | accuracy | no |
| TY23 | 10.8333 | 11.9167 | 0 | accuracy | yes |
| TY10 | 11.4167 | 13.5 | 6.9 | toyota-producer | no |
| TY26 | 11.9167 | 18.625 | 0 | spencer | yes |
| TY11 | 13.5 | 15.5833 | 6.9 | toyota-producer | no |
| TY13 | 13.5 | 15.1667 | 6.9 | accuracy | no |
| TY12 | 15.5833 | 17.6667 | 6.9 | toyota-producer | no |
| TY14 | 15.5833 | 17.25 | 6.9 | accuracy | no |
| TY15 | 17.6667 | 19.3333 | 6.9 | accuracy | no |
| TY27 | 18.625 | 20.7917 | 0 | dev | yes |
| TY17 | 19.3333 | 20.4167 | 6.9 | accuracy | no |
| TY18 | 20.4167 | 27.125 | 6.9 | spencer | no |
| TY28 | 20.7917 | 21.3333 | 2.7917 | accuracy | no |
| TY29 | 20.7917 | 24.125 | 0 | dev | yes |
| TY30 | 21.3333 | 21.3333 | 2.7917 | coordinator | no |
| TY19 | 27.125 | 28.2083 | 6.9 | toyota-producer | no |

```mermaid
gantt
    title Toyota October 2026 v10
    dateFormat YYYY-MM-DD HH:mm
    axisFormat %m-%d %H:%M
    section Approvals
    TY01 [MOT-3356] Spencer approves the three Toyota scripts (Not a Drop, Group Chat, Feet Off) - spencer :done, ty01, 2026-10-09 13:30, 16m
    TY02 [MOT-3356] Spencer approves the Emily voice-over scripts - spencer :done, ty02, 2026-10-09 14:02, 16m
    TY24 Spencer picks the Chevy and Toyota email subject lines - spencer :done, ty24, 2026-10-09 14:18, 201m
    TY26 Spencer approves the final Toyota email packet - spencer :crit, done, ty26, 2026-10-10 01:25, 403m
    TY18 [MOT-3356] Spencer final approval of the three Toyota videos - spencer :ty18, 2026-10-10 09:55, 403m
    section Stills
    TY03 [MOT-3356] Start-frame stills v4 selected for all three spots - emily :active, ty03, 2026-10-09 13:46, 130m
    section Audio
    TY04 [MOT-3356] Render the approved Emily VO takes (tuned locked-voice route) - emily :active, ty04, 2026-10-09 22:10, 100m
    TY05 [MOT-3356] A person listens to every VO take before it goes in a cut - accuracy :ty05, 2026-10-09 23:50, 65m
    section Motion
    TY09 [MOT-3356] Studio Ref2VA close-face finals - gpu-studio :active, ty09, 2026-10-09 15:56, 130m
    TY06 [MOT-3356] H3 finals on cb87 Not a Drop - gpu-cb87 :active, ty06, 2026-10-09 17:39, 100m
    TY07 [MOT-3356] H3 finals on cb87 The Group Chat - gpu-cb87 :ty07, 2026-10-09 19:19, 100m
    TY08 [MOT-3356] H3 finals on cb87 Feet Off - gpu-cb87 :active, ty08, 2026-10-09 20:59, 100m
    section Assembly
    TY10 [MOT-3356] Assemble Not a Drop with the approved VO - toyota-producer :ty10, 2026-10-10 00:55, 125m
    TY11 [MOT-3356] Assemble The Group Chat with the approved VO - toyota-producer :ty11, 2026-10-10 03:00, 125m
    TY12 [MOT-3356] Assemble Feet Off with the new approved VO - toyota-producer :ty12, 2026-10-10 05:05, 125m
    section QC
    TY16 Confirm the Group Chat and Feet Off end tags follow Spencer's standing price rule - accuracy :done, ty16, 2026-10-09 13:30, 33m
    TY13 [MOT-3356] Frame-by-frame QC Not a Drop - accuracy :ty13, 2026-10-10 03:00, 100m
    TY14 [MOT-3356] Frame-by-frame QC The Group Chat - accuracy :ty14, 2026-10-10 05:05, 100m
    TY15 [MOT-3356] Frame-by-frame QC Feet Off - accuracy :ty15, 2026-10-10 07:10, 100m
    TY17 [MOT-3356] Coordinator full-size QC of all three rebuilt cuts - accuracy :ty17, 2026-10-10 08:50, 65m
    section Publish
    TY19 [MOT-3356] Schedule the Toyota posts natively (FB scheduled reel, YT private plus publishAt, IG one-shot) - toyota-producer :ty19, 2026-10-10 16:37, 65m
    section Email
    TY20 [MOT-3449] Toyota model-targeted subsets, holdouts, and calendar - rory :done, ty20, 2026-10-09 13:30, 260m
    TY25 [MOT-3451] Send, poll, follow-up and report automation cloned for Toyota (build only) - dev :active, ty25, 2026-10-09 13:30, 390m
    TY21 [MOT-3450] Toyota emails fixed to the house standard (v4 packet) - emily :active, ty21, 2026-10-09 17:50, 260m
    TY31 Fix the 10/13 dry-run failures (segment tags, holdouts, send caps) for the Toyota sends - dev :active, ty31, 2026-10-09 20:00, 320m
    TY22 [MOT-3266] Toyota email compliance QA against the QRG and OFFER-FACTS - rory-copy-seo :ty22, 2026-10-09 22:10, 130m
    TY23 [MOT-3450] Coordinator full-size QC of the Toyota email packet - accuracy :crit, ty23, 2026-10-10 00:20, 65m
    TY27 Arm the Toyota sends first send 10/13 at 13 00 CT - dev :crit, ty27, 2026-10-10 08:07, 130m
    TY28 Verify the Toyota sends are armed - accuracy :ty28, 2026-10-10 10:17, 33m
    section Reporting
    TY29 [MOT-3451] Toyota attribution report job (opens, clicks, VDP by UTM, holdout vs mailed) - dev :crit, ty29, 2026-10-10 10:17, 200m
    section Milestones
    TY30 Milestone Toyota emails armed before the first send - coordinator :milestone, ty30, 2026-10-10 10:50, 0m
    section Spencer actions
    TY32 Run the one-line SSH config command on Mac mini 2 - spencer :ty32, 2026-10-09 18:06, 51m
    TY33 Delete the leftover customer-data files in Rory's cache on Mac mini 2 - spencer :ty33, 2026-10-09 18:57, 51m
```
