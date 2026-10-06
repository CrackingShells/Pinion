# Re-verification harness

Use this when harness behaviour seems to differ from SKILL.md §8 (new Claude Code version, new OS).

- `job.py MODE` — dummy job. Modes: `success`, `crash` (Traceback on stderr), `hang` (prints READY, then silent),
  `chatty` (READY, then a heartbeat every 0.5 s), `noisy_ok` (prints `Errors: 0`), `rotate` (deletes and
  recreates `$LOG`). `DELAY` sets the seconds before the terminal event.
- `cap.py SECONDS 'cmd'` — runs `cmd` in its own process group, kills the group at the cap, and prints
  `RESULT: HUNG` or `RESULT: exited rc=N`, plus any processes left over. Always wrap anti-pattern
  reproductions in it so a trap cannot hang your session.
- `emit.py` — prints 4 events 2 s apart (for Monitor buffering tests).
- `watch_job.sh LOG PID` — the minimal Monitor watcher used in scenario M3.

Example: `./cap.py 10 'DELAY=1 python3 -u job.py hang > t.log 2>&1 & tail -f t.log | grep -m1 READY'`
should report `HUNG`. Check `pgrep`/`grep` behaviour on Linux too; several traps are platform-dependent.
Harness-level checks (auto-backgrounding, sleep blocking, TaskStop scope) need real Bash/Monitor/TaskStop
tool calls; see evidence.md for the exact commands.
