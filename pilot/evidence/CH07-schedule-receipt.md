# Story B native schedule receipt (Chevy October)

Source: Mac mini 1, ~/ugc-batches/2026-chevy-story-b-wk42, -wk42-yt169 and -wk44 (native_facebook.json, native_youtube.json), and october-2026-films/tire-special/posts_registry.json. Checked read-only by the pilot on 2026-10-09 after the coordinator ran the scheduling.

| Platform | Id | Publish time | State |
|---|---|---|---|
| Facebook reel (wk42) | 4569692059963610 | 2026-10-15T01:15Z = 2026-10-14 20:15 CT | scheduled |
| Facebook reel (wk44) | 1115103610883580 | 2026-10-30T01:15Z = 2026-10-29 20:15 CT | scheduled |
| YouTube Short (wk42) | KwcO9vT-5wM | 2026-10-14T16:30Z = 2026-10-14 11:30 CT, private plus publishAt, containsSyntheticMedia true | scheduled |
| YouTube Short (wk44) | 8-jBKqrRlnk | 2026-10-29T16:30Z = 2026-10-29 11:30 CT | scheduled |
| Instagram | one-shot launchd jobs com.motorinn.ugc-native-ig-chevy-story-b-wk42 and -wk44, with guard jobs com.motorinn.ugc-guard-chevy-story-b-wk42 and -wk44 | 10/14 and 10/29 | all four jobs are loaded (not running) |

- All four platform ids appear in posts_registry.json.
- Scheduled files: 9x16 sha256 bfa911ea5b8427329ec8aa00be50c81c6bad6a98eaa3f637012b17adc86e56f5 (Facebook and Instagram); 16x9 sha256 93226c65293fc9264019ae2b3d56c9139b54bfe6c5236f07bc12e68dda611e2c (YouTube wk42). These are the files Spencer approved (task CH06).
- Not verified here: Google Calendar sync. No Story B events were visible in Spencer's two calendars. Tracked separately as CH25.
