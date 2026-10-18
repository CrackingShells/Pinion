#!/usr/bin/env python3
"""Dummy long-running job. Modes:
  success  : progress lines, then 'DONE', exit 0
  crash    : progress lines, then an uncaught exception (Traceback on stderr), exit 1
  hang     : prints 'READY', then goes silent forever
  chatty   : prints 'READY', then keeps printing a line every 0.5s forever
  noisy_ok : success, but prints 'Errors: 0' lines along the way
  rotate   : writes to $LOG itself, then deletes and recreates it (log rotation/restart), writes READY to the new file
Env: DELAY (seconds before terminal event, default 3)
"""
import os, sys, time
mode = sys.argv[1]
delay = float(os.environ.get("DELAY", "3"))
steps = 3
def progress():
    for i in range(steps):
        print(f"step {i+1}/{steps}")
        time.sleep(delay / steps)
if mode == "success":
    progress(); print("DONE"); sys.exit(0)
if mode == "noisy_ok":
    for i in range(steps):
        print(f"step {i+1}/{steps} Errors: 0"); time.sleep(delay / steps)
    print("DONE"); sys.exit(0)
if mode == "crash":
    progress(); raise RuntimeError("CUDA out of memory (simulated)")
if mode == "hang":
    progress(); print("READY"); sys.stdout.flush()
    while True: time.sleep(3600)
if mode == "chatty":
    progress(); print("READY")
    while True:
        print("heartbeat"); sys.stdout.flush(); time.sleep(0.5)
if mode == "rotate":
    log = os.environ["LOG"]
    with open(log, "a") as f: f.write("booting\n")
    time.sleep(delay)
    os.remove(log)
    with open(log, "w") as f: f.write("READY\n")
    time.sleep(3600)
