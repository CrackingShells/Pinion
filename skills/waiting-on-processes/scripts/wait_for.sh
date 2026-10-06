#!/usr/bin/env bash
# wait_for.sh — block until a log or status command reaches ANY terminal state, then exit with a labelled result.
# Run it with Bash run_in_background: true (one completion notification), or as a Monitor command
# (the RESULT line becomes the single event).
#
# usage: wait_for.sh --log FILE --ok REGEX [--fail REGEX] [--pid PID] [--new-only] [--timeout S] [--interval S]
#        wait_for.sh --cmd 'STATUS_COMMAND' --ok REGEX [--fail REGEX] [--cmd-timeout S] [--timeout S] [--interval S]
#
#   --log FILE       re-read on every check (immune to quiet logs, late arming and rotation)
#   --new-only       ignore lines already in FILE when the wait starts (use when the log is appended across runs);
#                    a truncated or recreated file is read from the start again
#   --cmd CMD        instead of a file: run CMD every interval and match its output (squeue, gh, curl, ...)
#   --cmd-timeout S  kill a status command that runs longer than this (default 60: well above a healthy squeue/gh/curl
#                    call, short enough that one hung check does not stall the wait). Also capped by --timeout.
#   --ok REGEX       POSIX ERE for success, checked after --fail. Write [0-9], not \d; [Ee]rror, not (?i).
#   --fail REGEX     POSIX ERE for failure. Anchor it (^Traceback|^[A-Za-z]*Error:) so "Errors: 0" does not match.
#   --pid PID        a process whose death without a marker ends the wait (EXITED_WITHOUT_MARKER)
#   --timeout S      whole seconds (default 1800 = 30 min; raise it for training or cluster jobs). Reported as TIMEOUT.
#   --interval S     seconds between checks (default 1; use 30+ for remote APIs to respect rate limits)
#
# prints: RESULT=OK|FAILED|EXITED_WITHOUT_MARKER|TIMEOUT, plus matching or last lines
# exit:   0 OK · 1 FAILED · 2 EXITED_WITHOUT_MARKER · 3 TIMEOUT · 64 usage error
# Ending the wait never stops the watched process; decide that separately.
set -u
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
die() { echo "wait_for.sh: $*" >&2; exit 64; }

log="" cmd="" ok="" fail="" pid="" new_only=0 timeout=1800 interval=1 cmd_timeout=60
while (($#)); do
  case $1 in
    -h|--help) usage; exit 0 ;;
    --new-only) new_only=1; shift; continue ;;
  esac
  (($# >= 2)) || die "$1 needs a value"
  case $1 in
    --log) log=$2 ;; --cmd) cmd=$2 ;; --ok) ok=$2 ;; --fail) fail=$2 ;; --pid) pid=$2 ;;
    --timeout) timeout=$2 ;; --interval) interval=$2 ;; --cmd-timeout) cmd_timeout=$2 ;;
    *) die "unknown argument $1" ;;
  esac
  shift 2
done
[[ -n $ok ]] || die "--ok is required"
[[ -n $log || -n $cmd ]] || die "one of --log or --cmd is required"
[[ $timeout =~ ^[0-9]+$ ]] || die "--timeout must be whole seconds, got '$timeout'"
[[ $cmd_timeout =~ ^[0-9]+$ ]] || die "--cmd-timeout must be whole seconds, got '$cmd_timeout'"
[[ $interval =~ ^[0-9]+([.][0-9]+)?$ && ! $interval =~ ^0+([.]0*)?$ ]] || die "--interval must be a positive number of seconds, got '$interval'"
[[ -z $pid || $pid =~ ^[0-9]+$ ]] || die "--pid must be numeric, got '$pid'"

# --new-only: remember where the log ended (and which file it was) when the wait started
skip=0 inode=""
file_inode() { ls -i "$log" 2>/dev/null | awk '{print $1}'; }
if ((new_only)) && [[ -f $log ]]; then skip=$(wc -l < "$log"); skip=${skip//[[:space:]]/}; inode=$(file_inode); fi

# The status command stays in this script's process group on purpose: TaskStop (or any kill of the group)
# then stops it together with the script. On a per-check timeout, the command's process tree is stopped
# explicitly: TERM, then KILL for anything that ignores TERM.
tree() { local c; echo "$1"; for c in $(pgrep -P "$1" 2>/dev/null); do tree "$c"; done; }
stop_tree() {
  local pids t; pids=$(tree "$1")
  kill -TERM $pids 2>/dev/null
  t=$((SECONDS + 2)); while kill -0 "$1" 2>/dev/null && ((SECONDS < t)); do sleep 0.1; done
  kill -KILL $pids 2>/dev/null
  wait "$1" 2>/dev/null
}
cur="" tmp=""
cleanup() { [[ -n $cur ]] && stop_tree "$cur"; [[ -n $tmp ]] && rm -f "$tmp"; }
trap cleanup EXIT
trap 'exit 143' TERM INT HUP
run_cmd() {   # one status check, capped at min(--cmd-timeout, time left before the deadline); sets $out
  # Runs in this shell, not in $(...): a TERM trap must be able to reach the status command immediately.
  local t cap left
  tmp=$(mktemp)
  left=$((deadline - SECONDS)); cap=$cmd_timeout; ((left < cap)) && cap=$left; ((cap < 1)) && cap=1
  bash -c "$cmd" > "$tmp" 2>&1 & cur=$!
  t=$((SECONDS + cap))
  while kill -0 "$cur" 2>/dev/null && ((SECONDS < t)); do sleep 0.2; done
  if kill -0 "$cur" 2>/dev/null; then stop_tree "$cur"; cur=""; out="$(cat "$tmp")"$'\n'"[status command killed after ${cap}s]"
  else wait "$cur" 2>/dev/null; cur=""; out=$(cat "$tmp"); fi
  rm -f "$tmp"; tmp=""
}
snapshot() {   # sets $out
  if [[ -n $cmd ]]; then run_cmd; return; fi
  out=""; [[ -f $log ]] || return 0
  local n; n=$(wc -l < "$log"); n=${n//[[:space:]]/}
  if ((skip)) && { [[ $(file_inode) != "$inode" ]] || ((n < skip)); }; then skip=0; fi   # recreated, or truncated by '>'
  if ((skip)); then out=$(tail -n "+$((skip + 1))" "$log"); else out=$(cat "$log"); fi
}
report() { echo "RESULT=$1 after ${SECONDS}s"; [[ -n ${2:-} ]] && printf '%s\n' "$2" | tail -n 5; exit "$3"; }
classify() {  # $1 = snapshot text; exits via report() on a marker, returns otherwise
  local hits
  if [[ -n $fail ]] && hits=$(printf '%s\n' "$1" | grep -E -- "$fail"); then report FAILED "$hits" 1; fi
  if printf '%s\n' "$1" | grep -qE -- "$ok"; then report OK "" 0; fi
}

deadline=$((SECONDS + timeout))
while :; do
  snapshot
  classify "$out"
  if [[ -n $pid ]] && ! kill -0 "$pid" 2>/dev/null; then
    snapshot; classify "$out"               # the marker may have landed just before exit
    report EXITED_WITHOUT_MARKER "$out" 2
  fi
  ((SECONDS >= deadline)) && report TIMEOUT "$out" 3
  sleep "$interval"
done
