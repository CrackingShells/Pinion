# Anti-patterns: reproductions and reasons

Each entry: the pattern, why it *looks* right, what the reproduction showed, the mechanism, the fix.
IDs match [evidence.md](evidence.md). The reproduction harness is in `scripts/lab/`.

## Contents
1. Pipelines that never end — T1, T3, T4, T6, T7
2. Filters that miss the outcome — B2, B3, M4, B5, R2, R3
3. Waits that lie about the outcome — B6, H4, S5
4. Output that never arrives — B1, M2, M2'
5. Watches that outlive their purpose — M1
6. Name matching that finds itself — H3, H3e, H3f
7. Processes that escape tracking — H1, TS4, E7, W1

---

## 1. Pipelines that never end

### T1 — `tail -f log | grep -m1 READY`
- **Looks right:** `-m1` makes grep stop after the first match.
- **Observed:** match printed, then HUNG until killed; `tail` and the job were left behind. With a
  log that kept being written (T2), it exited in 1.6 s, so it passes a quick test and fails later.
- **Why:** grep exits, but `tail` learns that only when its *next write* to the closed pipe gets
  SIGPIPE. If the log goes quiet after the match, that write never happens.
- **Fix:** re-read the file: `until grep -qs READY log; …` or `scripts/wait_for.sh`.

### T3 / T4 — `tail -f log | grep [--line-buffered] X | head -1`
- **Looks right:** `head -1` takes the first line and ends the pipeline.
- **Observed:** with `--line-buffered`, the match is printed and then the pipeline HANGS. Without it,
  nothing is printed at all and it HANGS.
- **Why:** `head` exits, but grep dies only when it writes another *match*. Without
  `--line-buffered`, grep's first match is still sitting in its 4 KB output buffer.
- **Fix:** as T1. Never put `head` at the end of a streaming pipeline.

### T6 / T7 — late arming and log rotation
- **Looks right:** `tail -f` shows what is in the log.
- **Observed:** READY written before arming, followed by 20 more lines: never matched (T6). Log deleted
  and recreated by the job: never matched (T7). Fixing only the arming (`tail -n +1 -f`) or only the
  rotation (`tail -F`) gave a match **and still hung**, because the T1 trap remains.
- **Why:** `tail -f` starts from the last 10 lines and follows the original inode.
- **Fix:** `until grep -qs …` re-opens the file by name and reads all of it on every check (T7c ✅).

## 2. Filters that miss the outcome

### B2 — `until grep -q DONE log; do sleep 1; done`
- **Observed:** job crashed at about 1 s; the loop was still running when killed at 10 s.
- **Why:** only the success path can end the loop.
- **Fix:** four exits (OK, FAILED, EXITED_WITHOUT_MARKER, TIMEOUT).

### B3 — failure regex applied to a log that doesn't contain stderr
- **Observed:** `job > log 2>/dev/null` plus `grep -E 'DONE|Traceback'`: HUNG. The Traceback never
  reached the file.
- **Fix:** launch with `> log 2>&1`, and keep a liveness check as the backstop.

### M4 — Monitor with a success-only filter
- **Observed:** `tail -n +1 -f log | grep --line-buffered '^DONE$'` on a job that crashed at about
  4 s: "expired after 30s with no events delivered".
- **Why:** silence from a watch cannot be told apart from progress.
- **Fix:** include failure signatures in the filter, or use `watch_log.sh` with `--pid`.

### B5 — over-broad failure regex
- **Observed:** `[Ee]rror` fired at 0.1 s on a healthy job printing `step 1/3 Errors: 0`.
- **Fix:** anchor: `^Traceback|^[A-Za-z]*Error:|Killed|[Oo]ut of memory`.

### R2 — PCRE syntax in `grep -E`
- **Observed:** on Linux (GNU grep 3.11), `grep -E '\d+'` and `grep -E '(?i)fatal'` returned no match.
  `\d` printed no warning; `(?i)` printed a warning on stderr only. On macOS (BSD grep, ugrep) both matched.
- **Why:** these are PCRE features, not POSIX ERE. GNU grep reads `\d` as a literal `d`.
- **Fix:** `[0-9]`, `[[:space:]]`, `[Ff]atal` or `grep -i`.

### R3 — the regex was tested in a different grep
- **Observed:** in the Bash tool, `grep` is a shell function (from the harness shell snapshot) that
  calls ugrep. Inside `bash -c`, script files and Monitor commands, it is `/usr/bin/grep`.
- **Fix:** test the watcher script itself (`bash script.sh`), not the pattern at the prompt.

## 3. Waits that lie about the outcome

### B6 — deadline branch reported as success
- **Observed:** `until grep -q DONE log || (( SECONDS > 2 )); done; echo "job finished!"` printed
  "job finished!" at 3.4 s for a job that had 27 s left.
- **Fix:** print which condition ended the loop (`RESULT=TIMEOUT`).

### H4 — `wait $PID` on a PID from an earlier Bash call
- **Observed:** `wait <pid>` → "pid <pid> is not a child of this shell", rc 127, instantly.
  `wait $PID; echo done` therefore "completes" at once.
- **Why:** each Bash call is a fresh `zsh -c`; the job's parent was a shell that has already exited.
- **Fix:** `kill -0 "$(cat job.pid)"` in a loop, or run the job itself as the task.

### S5 — a marker left by a previous run
- **Observed:** `DONE` already in an appended log: `wait_for.sh --log stale.log --ok '^DONE$'` →
  `RESULT=OK after 0s` while the new run was still going. With `--new-only`, the same wait ignored the
  old line and reported the new run's Traceback (`RESULT=FAILED after 3s`).
- **Fix:** a fresh log per run (`>` not `>>`), a run-unique marker, or `--new-only` (both scripts).

## 4. Output that never arrives

### B1 — block-buffered stdout
- **Observed:** `python job.py > log`: 0 lines after 3 s of a 6 s job, all 4 at exit. With `-u`: 2 lines at 3 s.
- **Fix:** `python -u`, `PYTHONUNBUFFERED=1`, `stdbuf -oL`.

### M2 — a Monitor script that buffers
- **Observed:** a script printing every 2 s without `-u`: all 4 events delivered in one batch at exit,
  8 s late. With `-u`: live. A script that never exits would never deliver anything.

### M2' — inline scripts in Monitor
- **Observed:** a quoting error in `python3 -c '…\"%T\"…'` produced a SyntaxError on stderr, visible
  only in the output file; the notification said "script failed (exit 1)".
- **Fix:** put watcher code in a file and run the file.

## 5. Watches that outlive their purpose

### M1 — an unbounded Monitor for a one-shot need
- **Observed:** `tail -f log | grep --line-buffered READY` delivered the event, then stayed armed
  until expiry (25 s in the test; up to 30 min in practice). Expiry did clean up `tail`.
- **Fix:** for "tell me when", use a command that exits: `wait_for.sh`, or an until-loop in Monitor (M5 ✅).

## 6. Name matching that finds itself

### H3 — `until ! pgrep -f "job.py hang"` with no such process
- **Observed:** macOS: exited in 0.1 s. **Linux (procps-ng 4.0.4): HUNG** (rc 124 at a 6 s cap).
  On macOS, `pgrep -a` (include ancestors) reproduces the Linux hang.
- **Why:** procps `pgrep` excludes only itself; the loop's own `bash -c` command line contains the
  pattern. BSD `pgrep` excludes itself and its ancestors by default.
- **Fix:** watch the PID. `[j]ob.py` helps (H3d ✅) but see H3f.

### H3e — `while ps aux | grep -q "job.py hang"`
- **Observed:** HUNG. grep matches its own command line on every platform.

### H3f — the bracket trick defeated by the harness wrapper
- **Observed:** `ps … | grep -E "[j]ob.py"` matched its own wrapper process, because the same Bash
  call also contained the literal `job.py hang`.
- **Why:** Claude Code runs each call as `zsh -c "… eval '<the whole call text>'"`, so every process
  of that call (and every forked subshell) carries the entire call text in its argv.
- **Fix:** PIDs or job IDs; `pgrep -x name` as a last resort.

## 7. Processes that escape tracking

### H1 — `cmd &` in a foreground Bash call
- **Observed:** the call returned immediately; the child was reparented to PID 1 and kept running,
  absent from `/tasks`. A `(sleep 20; echo late) &` subshell survived, and its output was lost.
- **Fix:** launch long-lived processes with `run_in_background: true`. If you must detach, write a
  pidfile in the same call and stop it explicitly later.

### TS4 — new-session children survive `TaskStop`
- **Observed:** `TaskStop` killed the task's process group. A direct child, an `&` child and a `nohup`
  child all died (TS1–TS3). A child started with `start_new_session=True` survived with parent PID 1.
- **Covers:** `setsid`, daemonizing servers, `tmux new -d`, `screen -dm`, `docker run -d`, `ssh -f`.
- **Fix:** pidfile or container name at launch; stop it explicitly and confirm with `ps -p`.

### E7 — `nohup cmd &` inside a `run_in_background` task
- **Looks right:** the task is tracked, and `nohup`/`&` feel like extra safety.
- **Observed:** the task ended at once with "completed (exit code 0)"; the real process was reparented
  to PID 1, invisible to `/tasks`, and survived until a sweep stopped it.
- **Why:** the tracked shell backgrounds its only child and exits; the harness then tracks nothing.
- **Fix:** make the task's command the job itself (`python -u train.py > train.log 2>&1`), without `&`.

### W1 — no backstop for what escapes
- **Looks right:** the watcher was written carefully, so nothing should be left over.
- **Observed:** an `&` orphan and a new-session child, both reparented to PID 1, were invisible to
  `/tasks` and `TaskStop`; only a scheduled sweep found and stopped them (W1). A cross-session sweep also
  found a service that another session had detached 18 hours earlier (W4). Careful watchers still
  contain bugs; a harness-owned backstop does not depend on them.
- **Fix:** whenever something outlives the turn, arm a long wake-up (ScheduleWakeup, or a one-shot or
  recurring CronCreate) whose self-contained prompt runs `scripts/sweep.sh` and checks each named
  item (W1, W2).
