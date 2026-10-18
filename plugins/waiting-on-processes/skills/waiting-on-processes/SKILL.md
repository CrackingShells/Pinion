---
name: waiting-on-processes
description: Chooses and writes waits and watches in Claude Code that end by themselves and catch failures — waiting for a server, build, test run, training job, cluster job, CI check or log line, or streaming events from a long-running process — using Bash run_in_background, the Monitor tool, ScheduleWakeup/CronCreate and TaskStop, with a scheduled sweep as the safety net that finds and stops processes that escaped every watcher. Avoids the reproduced traps that leave stray processes or miss crashes (tail -f | grep -m1 hanging, block-buffered output, happy-path-only filters, pgrep -f matching itself, orphaned & or setsid children). Use whenever about to write an until/while/sleep loop, tail -f, pgrep or ps polling, or a Monitor command, or to start, background, watch or stop a long-running process — including requests like "tell me when it's ready", "wait until the job finishes", "keep an eye on the logs", "let me know if it crashes" or "run it in the background", even when no tool is named.
---

# Waiting on processes

A wait is correct only if it **ends by itself in every outcome** and **says which outcome it saw**.
Most broken waits fail one of those two tests: they hang after the event (stray process), or they
end silently so that a crash looks the same as "still running". Every trap named below was
reproduced on macOS and on a Linux host; the evidence is in
[references/evidence.md](references/evidence.md). Paths like `scripts/wait_for.sh` are relative to this
skill's base directory, shown when the skill loads; use the absolute path in commands.

Two words used throughout:
- a **wait** delivers one notification (the thing happened, or it can't happen any more);
- a **watch** delivers one notification per event, until a known end or an expiry.

## 1. Pick the mechanism

| Situation | Mechanism | Ends when |
|---|---|---|
| You are starting the command and want to know when it finishes | Run **the command itself** with Bash `run_in_background: true` | It exits — the notification carries the exit code (R1) |
| Something is already running; you need one notification when a condition holds | `scripts/wait_for.sh` under Bash `run_in_background: true` (or as a Monitor command) | OK / FAILED / process died / deadline — always labelled |
| You want progress, or each occurrence of something | **Monitor** running `scripts/watch_log.sh` (bounded) | A terminal state, or its own deadline |
| Genuinely open-ended watch ("every ERROR line from now on") | Monitor with an unbounded filter, `timeout_ms: 1800000`, re-arm on expiry | Monitor expiry (max 30 min) |
| Minutes-to-hours, or remote state (cluster job, CI, deploy) | The scheduler's or CI's own status tool (e.g. an MCP job-status tool if one is installed, `gh pr checks`, `sacct`/`scontrol`) checked on a schedule: a wake-up (§6), or `wait_for.sh --cmd … --interval 30` | Terminal job state, or deadline |
| **Anything left running past this turn** (in addition to the rows above) | A scheduled **sweep** wake-up (§6) | You re-check, clean up, and re-arm or cancel it |

Rule of thumb: prefer the row nearest the top. Running the job as the task needs no pattern
matching at all, so there is nothing to get wrong; each row below adds a filter that can miss.

## 2. The four exits every wait needs

| Exit | Why it is needed | Evidence |
|---|---|---|
| **OK** — success marker seen | the happy path | — |
| **FAILED** — failure marker seen | a success-only filter loops forever on a crash, and a Monitor with one stays silent until it expires | B2, M4 |
| **EXITED_WITHOUT_MARKER** — the process is gone | SIGKILL, the OOM killer and segfaults print no Traceback; only a liveness check (`kill -0 $PID`) sees them | B4b |
| **TIMEOUT** — deadline passed | anything unforeseen; must be reported as TIMEOUT, never as done | B6 |

Before arming anything, ask: *if the job crashed right now, what would my wait print?* If the
answer is "nothing", widen it. Then ask: *if the job hung silently, when would my wait end?*
If the answer is "never", add a deadline. Then **test it once**: point the watcher at
`scripts/lab/job.py crash` (and `hang`) under `scripts/lab/cap.py` and check that it ends with the
right label. A watcher that has never seen a failure has not been tested.

## 3. Recipes

### 3a. Run the job as the task (preferred)

```
Bash(command="python -u train.py > train.log 2>&1", run_in_background=true)
```

The completion notification says `completed (exit code 0)` or `failed with exit code N`. Read
the log for details. Because the task owns the process group, `TaskStop` also stops everything
it started with `&` or `nohup`, but not `setsid` children (see §5).

### 3b. One notification for a condition: `wait_for.sh`

```bash
# local job you did not start as a task: log + PID
bash <skill-dir>/scripts/wait_for.sh --log train.log --pid "$(cat train.pid)" \
  --ok '^Training complete' --fail '^Traceback|^[A-Za-z]*Error:|[Oo]ut of memory' \
  --timeout 3600

# scheduler state: poll a status command instead of a file (every terminal state listed)
# scontrol forgets finished jobs after MinJobAge (300 s by default): keep --interval well below that,
# or use `sacct -j 12345 -X -n -o State` where accounting is enabled
bash <skill-dir>/scripts/wait_for.sh --cmd 'scontrol show job 12345 -o | grep -o "JobState=[A-Z_]*"' \
  --ok 'JobState=COMPLETED' \
  --fail 'JobState=(FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)' \
  --interval 30 --timeout 14400
```

Run it with `run_in_background: true`. It prints one `RESULT=OK|FAILED|EXITED_WITHOUT_MARKER|TIMEOUT`
line (plus the matching or last log lines) and exits 0/1/2/3 (64 on a bad argument). It re-reads the
whole file on every check, which is what makes it immune to quiet logs, late arming and log rotation
(T1, T6, T7). The flip side is that a marker left by a *previous* run matches at once: give each run a
fresh log (`>`, not `>>`), or pass `--new-only`. Each status check is capped at the smaller of
`--cmd-timeout` (60 s) and the time left, and a hung check's process tree is killed (TERM, then KILL),
so `--cmd` waits end on time and leave nothing behind, even when the wait itself is stopped with
`TaskStop` (S7, S11). It never kills the job; decide that afterwards.

Writing an inline loop instead? Keep the same four exits and the label:

```bash
deadline=$((SECONDS+1800))
until grep -qsE '^DONE$|^Traceback|^[A-Za-z]*Error:' app.log || ! kill -0 "$PID" 2>/dev/null || (( SECONDS > deadline )); do sleep 1; done
if grep -qsE '^Traceback|^[A-Za-z]*Error:' app.log; then echo FAILED; elif grep -qs '^DONE$' app.log; then echo OK
elif ! kill -0 "$PID" 2>/dev/null; then echo EXITED_WITHOUT_MARKER; else echo TIMEOUT; fi
```

### 3c. Progress events: Monitor + `watch_log.sh`

```
Monitor(
  command="bash <skill-dir>/scripts/watch_log.sh --log train.log --pid 4242 --events '^epoch [0-9]+ ' --ok '^Training complete' --fail '^Traceback|^[A-Za-z]*Error:'",
  description="train.log: epochs + terminal state",
  timeout_ms=1800000)
```

It emits each line appended after arming that matches `--events` or `--fail` (`--from-start`
replays older ones, which can flood a long log), then one `RESULT=…` line, and exits. Terminal
markers are checked against the whole file, so a job that finished before you armed is still
reported; add `--new-only` if the log is appended across runs, so an old Traceback cannot end the watch.
Its own deadline (29 min by default) sits just under Monitor's 30-minute cap, so the script
ends and labels the outcome before the tool kills it. Re-arm if `RESULT=TIMEOUT` and the job is still running.

### 3d. Open-ended watch (only when there is no end state)

```
Monitor(command="tail -n 0 -F app.log | grep -E --line-buffered '^ERROR|^Traceback|FATAL'",
        description="new errors in app.log", timeout_ms=1800000)
```

Only for "tell me every time X happens": for "tell me when X happens" it stays armed after the
event until expiry (M1). For a single event, run an until-loop that exits as the Monitor command
instead (M5), or use `wait_for.sh`.

## 4. Make the output visible before you filter it

- **Block buffering.** Python, C programs and many CLIs buffer stdout in 4–8 KB blocks when it goes to a
  file or pipe. A watcher then sees nothing for minutes, or until exit (B1, M2). Use `python -u` or
  `PYTHONUNBUFFERED=1`; `stdbuf -oL cmd` for C stdio programs (Linux, or Homebrew coreutils on macOS);
  `grep --line-buffered`, `awk '{…; fflush()}'` in pipelines. Never end a Monitor pipeline in `| head -N`.
- **Stderr.** Tracebacks and most errors go to stderr. Launch jobs with `> log 2>&1`; for a Monitor
  command you run directly, merge with `2>&1` so failures reach the filter (B3).
- **Regex dialect.** Write POSIX ERE: `[0-9]` not `\d`, `[Ee]rror` or `grep -i` not `(?i)`. GNU grep on
  Linux silently never matches `\d` (R2). Anchor failure patterns (`^Traceback`, `^[A-Za-z]*Error:`) so
  that `Errors: 0` does not look like a failure (B5).

## 5. Starting and stopping long-lived processes

- **Start anything long-lived as a `run_in_background` task, without `&`.** A trailing `&` in a
  foreground Bash call returns at once and leaves an orphan (parent PID 1) that `/tasks` and `TaskStop`
  cannot see (H1). Inside a `run_in_background` task it is worse: `nohup cmd &` makes the task end at
  once and report `completed (exit code 0)`, a false success, while the real work escapes (E7). The
  task's command must be the job itself, or a shell that stays alive until the job ends.
- **Know what escapes `TaskStop`.** It stops the task's whole process group, including children started
  with `&` or `nohup` (TS1–TS3, verified on macOS). A child that starts a new session escapes and keeps running (TS4): `setsid`,
  Python `start_new_session=True`, self-daemonizing servers, `tmux new -d`, `screen -dm`, `docker run -d`,
  `ssh -f`. For those, write the PID (or container name) to a file at launch and stop it explicitly.
- **Capture PIDs in the same call that launches.** Shell variables do not survive between Bash calls, and
  `wait $PID` on a PID from an earlier call fails *instantly* with rc 127, which looks exactly like
  completion (H4). Use `cmd > log 2>&1 & echo $! > job.pid`, then `kill -0 "$(cat job.pid)"` later.
- **Ending a wait does not stop the job.** A watcher that times out leaves the job running. Decide
  whether to stop it, and say so.
- **Before you finish:** list what you started (`/tasks`, your pidfiles), stop what is no longer
  needed, and confirm by PID: `ps -p "$(cat job.pid)" || echo stopped`. Then run `scripts/sweep.sh`
  once: it finds what escaped anyway (§6).

## 6. Safety net: a scheduled sweep

Every watcher can fail, including carefully written ones like those in this skill: a subtle bug is
enough to leave a stray process behind. A scheduled wake-up is owned by the harness, not by any process you started, so it still fires
when the watcher hung, died or escaped. You then re-check with fresh eyes and clean up (W1, W2).

**Find escapees without trusting names: `scripts/sweep.sh`.** Every process started from a Claude
Code Bash call inherits `CLAUDE_CODE_SESSION_ID` and `CLAUDE_PID` in its environment, and keeps them
after it is orphaned (`&`) or starts a new session (`setsid`, daemons). The sweep reads process
environments (`ps -E` on macOS, `/proc/<pid>/environ` on Linux) and reports every process of this
session whose Claude process is no longer an ancestor. That is exactly what `/tasks` and `TaskStop`
cannot see. It never matches by name, so it cannot find itself, and it runs in under a second.

```
bash <skill-dir>/scripts/sweep.sh                    # this session: SWEEP_RESULT=CLEAN | ESCAPED n
bash <skill-dir>/scripts/sweep.sh --kill             # stop this session's escapees (TERM, then KILL)
bash <skill-dir>/scripts/sweep.sh --include-tracked  # also list what is still attached
bash <skill-dir>/scripts/sweep.sh --all-sessions     # escapees of any session + UNATTRIBUTED orphans: report only (--kill refused)
```

**Arm the wake-up whenever something outlives the turn** (a job, a server, a watcher):

```
ScheduleWakeup(delaySeconds=1800, reason="safety-net sweep for train job + its watcher",
  prompt="Safety-net check. Started: train job (pidfile /abs/path/train.pid, log /abs/path/train.log), watcher task <watcher-task-id>. Done = 'Training complete' in the log. Run bash <skill-dir>/scripts/sweep.sh; check the pidfile and the log; stop anything no longer needed (sweep.sh --kill for escapees, TaskStop for tasks); re-arm if the job is still running, otherwise report the outcome.")
```

- **Make the prompt self-contained.** It arrives as a new turn, possibly after context compaction:
  name the absolute paths, PIDs or pidfiles, task and job IDs, what "done" means, and the commands to run.
- **Pick a long delay, 20–30 min.** It is a backstop, not the notification; the mechanisms in §1 still
  deliver the result. For multi-day campaigns, use a recurring `CronCreate` at an off-minute
  (e.g. `"17 * * * *"`); it auto-expires after 7 days.
- **When it fires:** run the sweep, check each item named in the prompt, stop what is finished or
  orphaned, then re-arm or cancel (`CronList`, `CronDelete`). Report what you found, even if the
  sweep is clean.
- **Limits, verified:**
  - It fires only when the session is idle, rounded to the minute, so a long turn delays it.
  - It is session-only: nothing fires after the session ends. Cover that gap with
    `sweep.sh --all-sessions` at the start of the next session, or with the SessionEnd hook below.
  - Cross-session escapees can be deliberate, like a service someone detached on purpose (W4):
    report them and let the user decide. Only `--kill` this session's own escapees.
  - Remote work (cluster jobs, CI) is not a local process: check its state with the status tool instead.
  - Blind spot: a process launched with a stripped environment (`env -i`), or a daemon started by a
    shell init file, may carry `CLAUDECODE=1` but no session id. `--all-sessions` lists such orphans as
    UNATTRIBUTED; check them by hand, since their owner cannot be determined (W8).

**SessionEnd backstop (offer it; don't install it unasked).** A `SessionEnd` hook runs when the
session ends, and its environment carries that session's `CLAUDE_CODE_SESSION_ID` and `CLAUDE_PID`, so
`sweep.sh --kill` stops exactly that session's escapees (E1: an orphan stopped in about 0.85 s). Tracked
background tasks are already stopped at session end, so only real escapees are left for it (E2). It
must live in user or project **settings**: the same hook declared in skill frontmatter never fired
(E6). The `timeout` raises the 1.5 s budget that all SessionEnd hooks share:

```json
{"hooks": {"SessionEnd": [{"hooks": [
  {"type": "command", "command": "bash /abs/path/to/waiting-on-processes/scripts/sweep.sh --kill", "timeout": 10}
]}]}}
```

It also stops servers or daemons the user detached on purpose from that session. Say so when you
suggest it, and let the user choose.

## 7. Identify processes by PID, not by name

Name matching finds the watcher as well as the job:

- `until ! pgrep -f "train.py"` never ends on Linux, because procps `pgrep` excludes only itself and
  the loop's own `bash -c '…train.py…'` matches. macOS `pgrep` excludes its ancestors, so the same
  loop *works* on macOS and hangs on Linux (H3).
- `ps aux | grep train.py` always matches its own grep (H3e).
- Claude Code runs each call as `zsh -c "… eval '<the whole call text>'"`. Any process forked from
  that call (a subshell, `( … ) &`) carries the full text, so even the `[t]rain.py` bracket trick
  matches it when the literal appears elsewhere in the call (H3f).

Use the PID captured at launch, or the scheduler's job ID. Fall back to `pgrep -x <name>` (exact
process name, no `-f`) only when neither exists.

## 8. Harness behaviour that shapes these choices

Verified on Claude Code 2.1.281, macOS (BSD userland) and Linux (GNU coreutils, procps-ng 4.0.4,
bash 5); re-check with `scripts/lab/` if behaviour seems different.

- A foreground command that outlives its `timeout` is **moved to the background** as a tracked task
  with an ID and output file, and a notification arrives when it ends (H6). A "blocking" wait loop
  therefore becomes a background task. Know its ID so you can stop it.
- A leading long `sleep` (e.g. `sleep 30; …`) is blocked; short ones are allowed. The guard reads the
  command text, so it also blocks `sleep 900 &`, which would not actually block anything. Do not chain
  short sleeps to get around it; use one of the mechanisms in §1 (H7, W3).
- Monitor: when a command fails to start (e.g. a quoting error in an inline `python -c`), the
  notification just says "exit 1" and the error is only in the output file. Put non-trivial watcher
  code in a script file (M2'). Its expiry (default 5 min, max 30) sends one notice and needs a re-arm.
- The Bash tool runs your login shell, zsh on macOS. Unquoted `$var` is not word-split and a glob that
  matches nothing aborts the command. The bundled scripts run under `bash` explicitly for this reason.
- In the Bash tool, `grep` is a shell function that calls ugrep. Inside `bash -c`, script files and
  Monitor commands it is the system grep (BSD on macOS, GNU on Linux). Test a regex where it will
  actually run (R3).
- `timeout(1)` is not on stock macOS. Use bash `$SECONDS` deadlines, as the bundled scripts do.
- `ScheduleWakeup` is implemented as a one-shot cron job: it appears in `CronList` and `CronDelete`
  cancels it. Its description scopes it to `/loop`, but it worked outside `/loop` (W2); a one-shot
  `CronCreate` is the general equivalent (W1). Harness-tracked work already notifies on completion,
  so never schedule short wake-ups to poll it; wake-ups are for the backstop (§6).
- `CronList` is the source of truth for wake-ups. A UI panel may keep showing a one-shot wake-up
  after it has fired, and may show its countdown in a different timezone. After a one-shot fires,
  confirm with `CronList`, not the panel (W10).

## 9. Anti-pattern index

| Anti-pattern | What goes wrong | ID |
|---|---|---|
| `tail -f log \| grep -m1 X` | hangs forever once the log goes quiet after the match | T1 |
| `… \| grep X \| head -1` | hangs; without `--line-buffered` the match is never even printed | T3, T4 |
| `tail -f` armed after the event / across rotation | misses the event; fixing only this still hangs (T1) | T6, T7 |
| success-only `until grep DONE` | loops forever on a crash | B2 |
| success-only Monitor filter | silent until expiry; a crash looks like progress | M4 |
| unbounded Monitor for a one-shot need | stays armed after the event, up to 30 min | M1 |
| deadline branch printed as "done" | a timeout reported as success | B6 |
| over-broad `[Ee]rror` | false failure on `Errors: 0` | B5 |
| job stdout buffered / stderr dropped | the watcher never sees the marker | B1, B3, M2 |
| `\d`, `(?i)` in `grep -E` | silent no-match on Linux | R2 |
| `pgrep -f name` / `ps \| grep name` loops | match themselves, never end (Linux) | H3, H3e, H3f |
| `cmd &` in a foreground call | untracked orphan | H1 |
| `wait $PID` across calls | instant rc 127, looks like completion | H4 |
| `setsid` / daemonizing child | survives `TaskStop` | TS4 |
| `nohup cmd &` inside a `run_in_background` task | task reports success at once; the job escapes | E7 |
| no backstop for escapees | strays live until someone notices | W1, W2 |
| marker from a previous run in an appended log | instant false OK | S5 |

Full reproductions, the observed output and the reason each one fails:
[references/anti-patterns.md](references/anti-patterns.md).
