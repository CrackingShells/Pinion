# Monitor-friendly watcher: emits one line per NEW progress/terminal line, exits on any terminal state.
# usage: bash watch_job.sh LOG PID
log=$1 pid=$2 seen=0
while :; do
  n=$(wc -l < "$log" 2>/dev/null || echo 0)
  if (( n > seen )); then
    sed -n "$((seen+1)),${n}p" "$log" | grep -E '^step |^DONE$|^Traceback|^[A-Za-z]*Error:|Killed'
    seen=$n
  fi
  grep -qE '^DONE$' "$log" && { echo "WATCH_END=OK"; exit 0; }
  grep -qE '^Traceback|^[A-Za-z]*Error:' "$log" && { echo "WATCH_END=FAILED"; exit 1; }
  kill -0 "$pid" 2>/dev/null || { echo "WATCH_END=EXITED_WITHOUT_MARKER"; exit 2; }
  sleep 1
done
