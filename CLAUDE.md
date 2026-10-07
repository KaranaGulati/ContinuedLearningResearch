# CLAUDE.md

Read `what we are trying to do now.md` first. It says where the work stands and what to do next. `README.md` is the original study brief, and `PREREGISTRATION.md` is the current analysis plan, which supersedes the brief where they differ (the design is now matched pairs, not within-player).

- Commit and push directly to `main`.
- Use the venv: `.venv/bin/python`. Setup commands are in the handoff file.
- The 200-per-group pilot is exploratory and may be scored and analysed with `analyze.py --exploratory`. The confirmatory sample must not be scored until `PREREGISTRATION.md` has a dated prediction and N committed, and it must exclude the pilot's players.
- Run long jobs with the Bash tool's background mode, not `&` or `nohup`; those get killed when the command returns.
- Keep `what we are trying to do now.md` current: update it at the end of each session.
