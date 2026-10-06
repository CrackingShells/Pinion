# Evidence

Reproductions behind the claims in SKILL.md and anti-patterns.md, which cite the scenario IDs below.

Contents: Shell-level patterns (T, B) · Process-identity patterns (H3) · Claude Code harness behaviour (H, R1) ·
Monitor tool (M) · Compound traps (T6–T7, R2–R3, H3f) · TaskStop scope (TS) · Bundled scripts (S) · Scheduled wake-ups and the sweep (W) · Hooks and task edges (E)


Environment: Claude Code 2.1.281 (desktop app); macOS (Darwin 25.6, zsh, BSD userland + Homebrew
coreutils); a Linux host (Linux 6.8, GNU coreutils and grep 3.11, procps-ng 4.0.4, bash 5).
Dummy job: `scripts/lab/job.py {success|crash|hang|chatty|noisy_ok|rotate}`; harness `scripts/lab/cap.py N 'cmd'`
runs a command in its own process group and kills it at N s, reporting HUNG vs exited and leftovers.

Legend: ✅ works · ❌ anti-pattern (verified failure) · ⚠️ platform-dependent

## Shell-level patterns

| ID | Pattern | Scenario | Observed | Why |
|---|---|---|---|---|
| T1 | `tail -f log \| grep -m1 READY` | log goes quiet after match | ❌ HUNG (12 s cap), tail+job left over | grep exits, but tail only gets SIGPIPE on its *next* write; quiet log ⇒ never |
| T2 | same | log keeps being written | ✅ by luck, 1.6 s | next line triggers SIGPIPE — passes a quick test, fails once the log goes quiet |
| T3 | `tail -f \| grep --line-buffered X \| head -1` | chatty log, X printed once | ❌ HUNG, match *was printed* | head exits, but grep only dies when it writes another *match* |
| T4 | `tail -f \| grep X \| head -1` | chatty log | ❌ HUNG, *nothing printed* | grep block-buffers into a pipe; the match sits in its buffer |
| T5 | `until grep -q X log; do sleep 0.5; done` | quiet log | ✅ 1.2 s | re-reads the file; no pipeline to tear down |
| B1 | `python job.py > log` (no `-u`) | 6 s job, checked at 3 s | ❌ 0 lines at 3 s (4 at exit); with `-u`: 2 lines | stdout to a file/pipe is block-buffered (Python, C stdio, many CLIs) |
| B2 | `until grep -q DONE log` | job crashes | ❌ HUNG forever | only the happy path can end the loop |
| B3 | `job > log 2>/dev/null` + `grep -E 'DONE\|Traceback'` | job crashes | ❌ HUNG | the Traceback went to stderr, never reached the log |
| B4 | `wait_for.sh` (fail-regex → ok-regex → `kill -0 $PID` → deadline, labelled result) | success / crash / hang | ✅ OK 1.3 s / FAILED 1.3 s (shows Traceback lines) / TIMEOUT 6.1 s | every terminal state has an exit branch and a distinct label |
| B4b | same | job `kill -9`'d, no marker ever | ✅ `EXITED_WITHOUT_MARKER` 1.4 s | liveness check catches silent death (OOM killer, SIGKILL) |
| B5 | fail regex `[Ee]rror` | healthy job prints `Errors: 0` | ❌ false FAILED at 0.1 s | over-broad regex; anchor it (`^Traceback`, `^[A-Za-z]*Error:`) |
| B6 | `until grep -q DONE log \|\| (( SECONDS > 2 )); done; echo finished` | slow job | ❌ printed "job finished!" at 3.4 s | the deadline branch is indistinguishable from success unless labelled |
| — | watcher timeout | B4 hang case | job still alive after watcher exited | ending a watch ≠ stopping the job; decide explicitly |

## Process-identity patterns

| ID | Pattern | Observed | Why |
|---|---|---|---|
| H3 | `until ! pgrep -f "job.py hang"` (no such process) | ⚠️ macOS: exits 0.1 s · **Linux: HUNG (rc 124 at 6 s cap)** | Linux procps pgrep only excludes itself; the loop's own `bash -c '…job.py hang…'` matches. BSD pgrep excludes ancestors (`-a` re-includes them → HUNG on macOS too) |
| H3d | `pgrep -f "[j]ob.py hang"` | ✅ both | bracket regex doesn't match its own literal text |
| H3e | `while ps aux \| grep -q "job.py hang"` | ❌ HUNG (macOS) | grep matches its own command line — everywhere |
| — | Claude Code wraps each Bash call as `zsh -c "… eval '<the whole call text>'"` | a forked subshell `( … ) &` keeps that argv ⇒ later `pgrep -f` for any text in that call matches the orphan | prefer PIDs (`kill -0 $PID`) over name matching |

## Claude Code harness behaviour (2.1.281)

| ID | Test | Observed |
|---|---|---|
| H1 | `sleep 45 &` inside a Bash call | call returns immediately; child reparented to PID 1 (untracked orphan, invisible to /tasks & TaskStop), survives the call |
| H1c | `(sleep 20; echo late) &` | call returns immediately; orphan subshell's late output is lost |
| H4 | `wait <PID from previous call>` | fails **instantly**, rc 127, "not a child of this shell" — a `wait $PID; echo done` "completes" at once |
| H5 | shell vars across calls | not persisted (each call is a fresh `zsh -c`); `cd` persists only via the harness |
| H7 | `sleep 3; echo` | allowed |
| H7b | `sleep 30; echo` | **blocked** by the harness, with a message pointing to Monitor with an until-loop or `run_in_background`, and against chaining shorter sleeps |
| H6 | foreground `until [ -f flag ]` with `timeout: 4000` | auto-moved to background (tracked ID, output file); completion notification arrived when flag appeared |
| R1 | the job itself with `run_in_background: true` (crash mode) | ✅ notification: "failed with exit code 1" — no grep needed at all |
| — | stock macOS has no `timeout(1)` (the test Mac had it from Homebrew coreutils) | use bash `$SECONDS` deadlines for portability |
| — | zsh `rm -f *.log` with no match | error "no matches found" (zsh NOMATCH) — globs in agent commands can abort a chain |

## Monitor tool (2.1.281)

| ID | Monitor command | Observed |
|---|---|---|
| M1 | `tail -f log \| grep --line-buffered READY` (one-shot need) | ❌ 1 event, then **stayed armed until expiry** (25 s in the test; up to 30 min in real use). Expiry did clean up `tail`. |
| M2 | `python3 emit.py` (prints every 2 s, no `-u`) | ❌ all 4 events delivered **in one batch at exit** (~8 s late); an endless script would never deliver |
| M2b | `python3 -u emit.py` | ✅ one live event every 2 s |
| M2' | inline `python3 -c '…\"%T\"…'` | ❌ quoting broke → SyntaxError on stderr, only visible in the output file; notification said just "script failed (exit 1)". Put scripts in files. |
| M3 | `bash watch_job.sh LOG PID` (emit new progress/terminal lines, exit on OK/FAILED/EXITED) on crash job | ✅ streamed steps + Traceback + `WATCH_END=FAILED`, then ended by itself |
| M4 | `tail -n +1 -f log \| grep --line-buffered '^DONE$'` on crash job | ❌ **silent for the full 30 s** — crash at ~4 s went unreported ("expired with no events") |
| M5 | `until grep -qs '^READY$' log \|\| ! kill -0 PID; do sleep 0.5; done; echo …` | ✅ exactly one event, stream ended |

## Compound traps

| ID | Pattern | Observed | Why |
|---|---|---|---|
| T6 | `tail -f log \| grep -m1 READY` when READY is older than the last 10 lines | ❌ HUNG, never matched | tail -f starts at the last 10 lines — arming late misses the event |
| T6b | fix only the arming: `tail -n +1 -f … \| grep -m1` | ❌ matched **and still HUNG** | the T1 SIGPIPE trap is still there |
| T7 | `tail -f` across log rotation (file deleted + recreated) | ❌ HUNG | `-f` follows the old inode |
| T7b | fix only rotation: `tail -F … \| grep -m1` | ❌ matched **and still HUNG** | T1 again |
| T7c | `until grep -qs READY log` across rotation | ✅ 2.1 s | re-opens by name every iteration |
| R2 | `grep -E '\d+'` / `grep -E '(?i)fatal'` | ⚠️ macOS BSD grep & the harness's ugrep: match · **Linux GNU grep 3.11: silent no-match** (`\d`: no warning at all; `(?i)`: warning on stderr only) | PCRE syntax isn't ERE; use `[0-9]`, `grep -i` |
| R3 | `grep` in the Bash tool vs in a script | Bash tool: `grep` is a **shell function → ugrep** (harness snapshot) · inside `bash -c`/Monitor/script files: `/usr/bin/grep` | a regex tested at the prompt can behave differently in the watcher |
| H3f | `ps … \| grep -E "[j]ob.py"` in a call whose text also contains `job.py hang` elsewhere | ❌ matched **its own wrapper** | the harness wrapper carries the whole call text; bracket trick only hides the pattern itself |

## TaskStop scope (2.1.281, macOS)

Each `run_in_background` call gets its own process group (pgid = wrapper zsh).

| ID | Inside the tracked task | Survived TaskStop? |
|---|---|---|
| TS1 | job run directly | no ✅ |
| TS2 | `job &` then a wait loop | no ✅ (same process group) |
| TS3 | `nohup job &` then a wait loop | no ✅ |
| TS4 | child with `start_new_session=True` (≈ `setsid`, self-daemonizing servers, `tmux new -d`, `docker run -d`) | **yes ❌ — stray, reparented to PID 1** |
| — | `( job & )` from a *foreground* call (never tracked) | **yes ❌** — orphan until killed by PID |

## Bundled scripts (`wait_for.sh`, `watch_log.sh`)

Run on macOS (bash 3.2) and on Linux (bash 5, GNU coreutils/grep); `cap.py` or `timeout` caps every run.

| ID | Scenario | wait_for.sh | watch_log.sh |
|---|---|---|---|
| S1 | success / crash (Traceback on stderr) / healthy job printing `Errors: 0` | OK · FAILED (+Traceback lines) · OK — both OSes | OK · FAILED, streaming steps + Traceback — both OSes |
| S2 | job SIGKILLed, no marker | EXITED_WITHOUT_MARKER — both OSes | EXITED_WITHOUT_MARKER |
| S3 | silent hang | TIMEOUT at deadline | TIMEOUT at deadline |
| S4 | log deleted and recreated / log created after arming | OK / OK | OK (inode change detected) |
| S5 | `DONE` from a previous run already in the log | OK after 0 s ❌ by default; `--new-only` → FAILED from the new run ✅ | n/a (fresh log per run) |
| S6 | Traceback written just before the process exits (seen only on the post-death re-check) | FAILED ✅ (without the re-check this would read EXITED_WITHOUT_MARKER) | FAILED ✅ |
| S7 | status command hangs: `--cmd 'sleep 10…' --timeout 2` / `--cmd 'trap "" TERM; sleep 8' --cmd-timeout 1` | TIMEOUT at 2 s (check capped by the deadline) / TIMEOUT at 3 s after TERM→KILL escalation; no orphaned `sleep` — both OSes | n/a |
| S8 | `--cmd` status PENDING → FAILED | FAILED | n/a |
| S9 | bad arguments (`--timeout 30m`, `abc`, `--interval x`, `--pid abc`, missing value) | rc 64 with a message | same validation |
| S11 | wait_for.sh itself stopped mid-check: SIGTERM/SIGKILL to its process group (what TaskStop does), SIGTERM/SIGINT to its PID only | n/a | — |
| — | ↳ result | all four: script gone in ≤1.1 s, **no leftover status command** — macOS; group and PID SIGTERM — Linux. Designs that fail this: putting the status command in its own process group (`set -m`) orphans it on a group kill; running the check inside `$(…)` delays the TERM trap by up to `--cmd-timeout`. | |
| S12 | `--new-only`, rerun truncates the log with `>` (same inode) / old DONE then new Traceback appended | OK from the new run / FAILED — both OSes | `--new-only`: old Traceback ignored, new DONE → OK — both OSes |
| S10 | 200 lines already in the log, 1 new line appended | n/a | only the new line emitted; `--from-start` replays all |
| — | zsh: `a="--timeout 30m"; cmd $a` passes ONE argument in zsh (no word splitting), two in bash | | |

## Scheduled wake-ups and `sweep.sh` (W)

| ID | Test | Observed |
|---|---|---|
| W1 | one-shot `CronCreate(cron="<min> <hour> <day> <month> *", recurring=false, prompt="sweep.sh --kill, then confirm")` with two planted escapees (an `&` orphan and a `start_new_session` child, both parent PID 1) | fired at the first idle moment after the scheduled minute; `--kill` → `STOPPED 2/2`; re-run → `SWEEP_RESULT=CLEAN`; `ps -p` confirms both gone. No watcher was involved: the harness owns the timer |
| W2 | `ScheduleWakeup(delaySeconds=60, prompt="sweep.sh, report only")` called **outside `/loop`** | accepted, rounded to the minute (fired about 2.5 min after the request); listed in `CronList` as a one-shot cron job → same mechanism as CronCreate; sweep reported `ESCAPED 2` |
| W3 | `sleep 901 &` as the first command of a Bash call | blocked by the sleep guard, which reads the text (the sleep was backgrounded) |
| W4 | `sweep.sh` classification on macOS | current session: exactly the 2 planted escapees, 30 processes TRACKED. MCP servers carry the session ID but not `CLAUDE_PID`, so the Claude PID is learned per session from Bash-tool processes. `--all-sessions`: 9 escapees of *other* sessions, including a local model server started with a `--run-as-service`-style daemon flag (18 h, parent PID 1), a service detached on purpose → report-only across sessions |
| W5 | `sweep.sh` on Linux: stand-in "Claude" with a tracked child and a double-forked escapee | escapee → ESCAPED (parent 1), children → TRACKED; after killing the stand-in, all 3 → ESCAPED; `--kill` → `STOPPED 3/3`; then CLEAN; no session ID in env → rc 64 |
| W6 | failure honesty | when an inspection step fails silently (e.g. BSD awk rejecting a multi-line `-v` value), a sweep that ignores the error prints `CLEAN` having seen nothing. `sweep.sh` passes inputs through files and prints `SWEEP_RESULT=ERROR` (rc 2) on any inspection failure. Unreadable `/proc/<pid>/environ` (non-dumpable own processes) is counted and reported, not hidden |
| W7 | runtime | 0.62 s on macOS (≈300 processes), 0.28 s on Linux |
| W8 | a shell-plugin daemon started by a shell init file inside a headless session launched with `env -i`, orphaned when that session ended | had `CLAUDECODE=1` and `CLAUDE_CODE_ENTRYPOINT` but no `CLAUDE_CODE_SESSION_ID`, so session-scoped sweeps missed it; `--all-sessions` now reports it as UNATTRIBUTED and never kills it |
| W9 | `--kill` combined with `--all-sessions` or another session's id | refused with rc 64: other sessions' escapees may be services detached on purpose, and only a human can tell |
| W10 | a one-shot CronCreate wake-up after it fired | `CronList` empty and `CronDelete` reported no such job, but the desktop app's schedule panel still listed it as pending, with a countdown matching the same cron fields read in another timezone; the entry disappeared after the cron store was touched |

## Hooks and task edges (E)

Hook runs used headless `claude -p` 2.1.273 on macOS, with hooks passed via `--settings`.

| ID | Test | Observed |
|---|---|---|
| E1 | SessionEnd hook (settings) in a `-p` run | fires (reason `other`), even on an early error exit; the hook env has the ending session's `CLAUDE_CODE_SESSION_ID` and `CLAUDE_PID` (= the hook's parent); stdin `session_id` matches. With `sweep.sh --kill` and `timeout: 10`, a `nohup … &` orphan (parent PID 1) was stopped in 0.80–0.87 s; with nothing to kill the sweep took 0.57–0.62 s |
| E2 | a `run_in_background` task still running when a `-p` run ends | killed by the harness (`[killed]` in its output file); only escapees survive the session |
| E3 | PostToolUse payloads | Bash `run_in_background`: `tool_response.backgroundTaskId`, no PID/PGID/output path; Monitor: `taskId`, `timeoutMs`, `persistent` |
| E4 | background-task completion and Monitor events | no dedicated hook event; UserPromptSubmit fires on each task notification (completion with status and exit code, each Monitor event, stream end). Undocumented |
| E5 | Stop hook payload | includes `background_tasks[]` (id, type, status, command) and `session_crons[]` |
| E6 | hooks declared in skill frontmatter | PreToolUse and Stop register when the skill is invoked and fire; `${CLAUDE_SKILL_DIR}` is not substituted in hook commands; a SessionEnd hook in frontmatter never fired (2 runs) |
| E7 | `nohup python3 -c '…sleep(903)' > /dev/null 2>&1 &` as a `run_in_background` task (desktop 2.1.281, reproduced independently of the `-p` run) | notification "completed (exit code 0)" at once; the python process was reparented to PID 1 and found by `sweep.sh` as ESCAPED |
