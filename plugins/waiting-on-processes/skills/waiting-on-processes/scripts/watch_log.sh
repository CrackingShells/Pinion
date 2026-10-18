#!/usr/bin/env bash
# watch_log.sh — Monitor-friendly event stream for a log. Emits each line appended after arming that matches
# --events or --fail, then exits at the first terminal state with a RESULT=... line. It always ends by itself.
#
# usage: watch_log.sh --log FILE --ok REGEX --fail REGEX [--events REGEX] [--pid PID] [--from-start] [--new-only] [--timeout S] [--interval S]
#   --events REGEX  progress lines worth a notification. Keep it selective: every line is a chat message, and
#                   Monitor stops watches that flood.
#   --ok / --fail   terminal markers (POSIX ERE, see wait_for.sh). Failure lines are always emitted.
#                   Markers are checked against the whole file, so a job that already finished is still reported;
#   --new-only      ...unless the log is appended across runs: then only lines added after arming count as markers
#   --pid PID       end with RESULT=EXITED_WITHOUT_MARKER if the process dies silently
#   --from-start    also replay matching lines already in the log (default: only lines appended after arming)
#   --timeout S     whole seconds; default 1740 = 29 min, just under Monitor's 30-min cap, so the script ends and
#                   labels the outcome before the tool kills it
# exit: 0 OK · 1 FAILED · 2 EXITED_WITHOUT_MARKER · 3 TIMEOUT · 64 usage error
set -u
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
die() { echo "watch_log.sh: $*" >&2; exit 64; }

log="" events="" ok="" fail="" pid="" from_start=0 new_only=0 timeout=1740 interval=1
while (($#)); do
  case $1 in
    -h|--help) usage; exit 0 ;;
    --from-start) from_start=1; shift; continue ;;
    --new-only) new_only=1; shift; continue ;;
  esac
  (($# >= 2)) || die "$1 needs a value"
  case $1 in
    --log) log=$2 ;; --events) events=$2 ;; --ok) ok=$2 ;; --fail) fail=$2 ;; --pid) pid=$2 ;;
    --timeout) timeout=$2 ;; --interval) interval=$2 ;;
    *) die "unknown argument $1" ;;
  esac
  shift 2
done
[[ -n $log && -n $ok && -n $fail ]] || die "--log, --ok and --fail are required"
[[ $timeout =~ ^[0-9]+$ ]] || die "--timeout must be whole seconds, got '$timeout'"
[[ $interval =~ ^[0-9]+([.][0-9]+)?$ && ! $interval =~ ^0+([.]0*)?$ ]] || die "--interval must be a positive number of seconds, got '$interval'"
[[ -z $pid || $pid =~ ^[0-9]+$ ]] || die "--pid must be numeric, got '$pid'"

filter=$fail; [[ -n $events ]] && filter="$events|$fail"
file_inode() { ls -i "$log" 2>/dev/null | awk '{print $1}'; }   # portable (BSD and GNU stat differ)
line_count() { local n; n=$(wc -l < "$log"); echo "${n//[[:space:]]/}"; }
seen=0 inode="" base=0   # base: first line that counts for markers (--new-only)
if [[ -f $log ]]; then
  inode=$(file_inode)
  ((from_start)) || seen=$(line_count)
  ((new_only)) && base=$(line_count)
fi

emit_new() {
  [[ -f $log ]] || return 0
  local n ino; n=$(line_count); ino=$(file_inode)
  if [[ $ino != "$inode" ]] || ((n < seen)) || ((n < base)); then seen=0; base=0; inode=$ino; fi   # rotated or truncated: start over
  if ((n > seen)); then sed -n "$((seen + 1)),${n}p" "$log" | grep -E -- "$filter"; seen=$n; fi
  return 0
}
check_markers() {
  [[ -f $log ]] || return 0
  local body; body=$(tail -n "+$((base + 1))" "$log")
  printf '%s\n' "$body" | grep -qE -- "$fail" && { echo "RESULT=FAILED"; exit 1; }
  printf '%s\n' "$body" | grep -qE -- "$ok" && { echo "RESULT=OK"; exit 0; }
  return 0
}

deadline=$((SECONDS + timeout))
while :; do
  emit_new
  check_markers
  if [[ -n $pid ]] && ! kill -0 "$pid" 2>/dev/null; then
    emit_new; check_markers                     # the marker may have landed just before exit
    echo "RESULT=EXITED_WITHOUT_MARKER"; tail -n 3 "$log" 2>/dev/null; exit 2
  fi
  ((SECONDS >= deadline)) && { echo "RESULT=TIMEOUT (the job may still be running)"; exit 3; }
  sleep "$interval"
done
