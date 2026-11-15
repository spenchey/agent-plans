# Story B social-calendar sync receipt

Source: Mac mini 1, ~/clawd/data/logs/no-model/social-calendar-sync-20261009.log, sha256 627dc60d55e11dc470f4d2519210f3de12e948d787ded71e8d42f3eeb673e932, read by the pilot on 2026-10-09 (13:07 CT last write).

- The sync is the social-calendar sync, not Spencer's Google Calendar (coordinator, 2026-10-09). The earlier pilot search of Spencer's two Google calendars found nothing because of that.
- native_schedule:youtube runs, after each of the two YouTube schedules: "created=2 ... errors=0" (twice).
- launchagents-changed run after the Instagram one-shots and guards were loaded: "created=2 ... errors=0".
- native_schedule:facebook runs: "created=0 ... errors=0" both times. The pilot could not tell from the log whether the two Facebook reels already have calendar entries; worth one look when someone opens the social calendar.
- Every sync line in the log shows errors=0 and warnings=0.
