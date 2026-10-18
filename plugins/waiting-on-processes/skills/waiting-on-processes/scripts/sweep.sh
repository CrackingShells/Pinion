#!/usr/bin/env bash
# sweep.sh — find (and optionally stop) processes started from Claude Code that escaped tracking.
# Every process launched from a Claude Code Bash call inherits CLAUDE_CODE_SESSION_ID and CLAUDE_PID in its
# environment, even after it is orphaned (`cmd &` in a foreground call) or starts a new session (setsid,
# daemonizing servers). A process is ESCAPED when its session's Claude process (CLAUDE_PID) is no longer
# among its ancestors: /tasks and TaskStop cannot see or stop it. Names are never used, so the sweep cannot
# match itself.
#
# usage: sweep.sh [--all-sessions | --session ID] [--include-tracked] [--kill]
#   (default)          escaped processes from this session ($CLAUDE_CODE_SESSION_ID)
#   --session ID       escaped processes from another session
#   --all-sessions     escaped processes from any Claude Code session, including ended ones, plus UNATTRIBUTED:
#                      orphans (parent PID 1) marked CLAUDECODE=1 but without a session id (e.g. daemons started
#                      from a stripped environment or shell init files); reported, never killed
#   --include-tracked  also list this session's still-tracked descendants (what /tasks would show and more)
#   --kill             send TERM to each escaped process of THIS session, KILL after 2 s if still alive; refused with
#                      --all-sessions or another --session (never to tracked or UNATTRIBUTED processes)
# prints: one line per process, then SWEEP_RESULT=CLEAN or SWEEP_RESULT=ESCAPED n (after --kill: STOPPED n)
# exit:   0 clean or all stopped · 1 escaped processes remain · 2 ERROR (could not inspect) · 64 usage error
set -u
usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
die() { echo "sweep.sh: $*" >&2; exit 64; }

scope=session session=${CLAUDE_CODE_SESSION_ID:-} tracked=0 kill=0
while (($#)); do
  case $1 in
    -h|--help) usage; exit 0 ;;
    --all-sessions) scope=all ;;
    --session) (($# >= 2)) || die "--session needs a value"; session=$2; shift ;;
    --include-tracked) tracked=1 ;;
    --kill) kill=1 ;;
    *) die "unknown argument $1" ;;
  esac
  shift
done
[[ $scope == all || -n $session ]] || die "no CLAUDE_CODE_SESSION_ID in the environment; pass --session ID or --all-sessions"
# --kill is only ever allowed on the caller's own session: other sessions' escapees may be services the user
# detached on purpose, and only a human can tell.
if ((kill)) && { [[ $scope == all ]] || [[ $session != "${CLAUDE_CODE_SESSION_ID:-}" ]]; }; then
  die "--kill only applies to this session's own escapees; report other sessions' and let the user decide"
fi

# 1. "pid sid claude_pid" for every process of this user that carries a Claude Code session id.
#    Any failure below ends in SWEEP_RESULT=ERROR: a sweep that cannot look must never report CLEAN.
work=$(mktemp -d) || { echo "SWEEP_RESULT=ERROR (mktemp)"; exit 2; }
trap 'rm -rf "$work"' EXIT
fail() { echo "SWEEP_RESULT=ERROR ($1)"; exit 2; }
me=$(id -u)
if [[ -r /proc/self/environ ]]; then   # Linux
  for d in /proc/[0-9]*; do
    [[ -O $d ]] || continue
    env=$( { tr '\0' '\n' < "$d/environ"; } 2>/dev/null ) || { echo x >> "$work/unreadable"; continue; }
    sid=$(printf '%s\n' "$env" | sed -n 's/^CLAUDE_CODE_SESSION_ID=//p' | head -n 1)
    if [[ -z $sid ]]; then printf '%s\n' "$env" | grep -qx 'CLAUDECODE=1' && sid=-; fi
    [[ -n $sid ]] || continue
    cp=$(printf '%s\n' "$env" | sed -n 's/^CLAUDE_PID=//p' | head -n 1)
    echo "${d#/proc/} $sid ${cp:-0}"
  done > "$work/tagged" || fail "reading /proc"
else                                   # macOS/BSD: ps -E appends the environment to the command line
  ps -E -U "$me" -o pid=,command= > "$work/psE" 2>/dev/null || fail "ps -E"
  awk '{ sid = ""; cp = 0; cc = 0
         for (i = 2; i <= NF; i++) {
           if ($i ~ /^CLAUDE_CODE_SESSION_ID=/) { sid = substr($i, 24) }
           if ($i ~ /^CLAUDE_PID=[0-9]+$/)      { cp = substr($i, 12) }
           if ($i == "CLAUDECODE=1")            { cc = 1 }
         }
         if (sid == "" && cc) sid = "-"
         if (sid != "") print $1, sid, cp }' "$work/psE" > "$work/tagged" || fail "parsing ps -E"
fi
ps -A -o pid=,ppid= > "$work/tree" || fail "ps -A"
[[ -s $work/tree ]] || fail "empty process table"

# 2. classify with one ancestry walk per process (awk: portable, no bash 4 associative arrays needed)
self_chain=$$
p=$PPID; while [[ -n $p && $p != 0 && $p != 1 ]]; do self_chain="$self_chain $p"; p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); done
rows=$(awk -v scope="$scope" -v want="$session" -v tracked="$tracked" -v self="$self_chain" '
  FNR == NR { parent[$1] = $2; next }            # first file: the process tree
  { n_t++; tp[n_t] = $1; ts[n_t] = $2; tc[n_t] = $3; tag[$1] = $2
    if ($3 > 0 && $2 != "-") root[$2] = $3 }                  # learn each session'"'"'s Claude PID (only Bash-tool shells carry it)
  END {
    n = split(self, s, " "); for (i = 1; i <= n; i++) skip[s[i]] = 1
    for (i = 1; i <= n_t; i++) {
      pid = tp[i]; sid = ts[i]
      if (pid in skip) continue
      if (sid == "-") {                           # CLAUDECODE=1 but no session id: only orphans, only in --all-sessions
        if (scope == "all" && parent[pid] == 1) print "UNATTRIBUTED", pid, "-"
        continue
      }
      if (scope != "all" && sid != want) continue
      cp = (tc[i] > 0) ? tc[i] : root[sid]; under = 0
      if (cp > 0) {                               # tracked iff the session'"'"'s Claude process is an ancestor
        x = parent[pid]; while (x != "" && x > 1) { if (x == cp) { under = 1; break }; x = parent[x] }
      } else {                                    # no Claude PID known: first ancestor outside the session must not be init
        x = parent[pid]; while (x != "" && x > 1 && tag[x] == sid) x = parent[x]
        under = (x != "" && x > 1)
      }
      if (!under) print "ESCAPED", pid, sid
      else if (tracked && sid == want) print "TRACKED", pid, sid
    }
  }' "$work/tree" "$work/tagged") || fail "classifying"

escaped=0 stopped=0 unattributed=0
while read -r kind pid sid; do
  [[ -n ${kind:-} ]] || continue
  info=$(ps -o ppid=,etime=,command= -p "$pid" 2>/dev/null | sed 's/^ *//') || continue
  [[ -n $info ]] || continue
  echo "$kind pid=$pid session=${sid:0:8} ppid/elapsed/cmd: ${info:0:160}"
  [[ $kind == UNATTRIBUTED ]] && { unattributed=$((unattributed + 1)); continue; }   # never killed: owner unknown
  [[ $kind == ESCAPED ]] || continue
  escaped=$((escaped + 1))
  if ((kill)); then
    kill -TERM "$pid" 2>/dev/null
    t=$((SECONDS + 2)); while kill -0 "$pid" 2>/dev/null && ((SECONDS < t)); do sleep 0.1; done
    kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null && sleep 0.2
    if kill -0 "$pid" 2>/dev/null; then echo "  still alive: $pid"; else echo "  stopped: $pid"; stopped=$((stopped + 1)); fi
  fi
done <<< "$rows"

if [[ -s $work/unreadable ]]; then   # own but non-dumpable processes (setuid, ssh-agent...): say so, don't hide it
  echo "note: $(wc -l < "$work/unreadable" | tr -d ' ') of your processes have an unreadable environment and were not classified"
fi
((unattributed)) && echo "note: $unattributed UNATTRIBUTED orphan(s) carry CLAUDECODE=1 but no session id; review them, they are never killed"
if ((escaped == 0)); then echo "SWEEP_RESULT=CLEAN"; exit 0; fi
if ((kill)); then echo "SWEEP_RESULT=STOPPED $stopped/$escaped"; ((stopped == escaped)) && exit 0; exit 1; fi
echo "SWEEP_RESULT=ESCAPED $escaped"; exit 1
