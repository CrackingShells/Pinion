#!/usr/bin/env python3
"""cap.py SECONDS 'shell command' -> runs cmd in its own process group; kills the group at the cap.
Reports RESULT: exited rc=N / HUNG, plus elapsed. Also reports leftover processes from the group."""
import os, signal, subprocess, sys, time
cap, cmd = float(sys.argv[1]), sys.argv[2]
t0 = time.time()
p = subprocess.Popen(["bash", "-c", cmd], start_new_session=True)
try:
    rc = p.wait(timeout=cap); status = f"exited rc={rc}"
except subprocess.TimeoutExpired:
    status = f"HUNG (killed at {cap:g}s cap)"
el = time.time() - t0
# anything left in the group (e.g. a tail -f orphaned after its pipeline 'finished')?
time.sleep(0.3)
left = subprocess.run(["pgrep", "-g", str(p.pid), "-l"], capture_output=True, text=True).stdout.strip()
try: os.killpg(p.pid, signal.SIGKILL)
except ProcessLookupError: pass
print(f"RESULT: {status} elapsed={el:.1f}s" + (f" | LEFTOVER in group: {left!r}" if left else ""))
