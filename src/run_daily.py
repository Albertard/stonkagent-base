#!/usr/bin/env python3
"""StonkAgent daily runner: tokens -> prices -> signals -> briefing.

Run once a day (cron). Each step is idempotent and writes its JSON to
data/. Exit code 0 only if all three steps succeed.
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")


def run(script, required=True):
    r = subprocess.run([sys.executable, os.path.join(SRC, script)], cwd=ROOT)
    if r.returncode != 0:
        print(f"FAILED: {script} (exit {r.returncode})", file=sys.stderr)
        if required:
            sys.exit(r.returncode)


if __name__ == "__main__":
    run("fetch_tokens.py")
    run("fetch_prices.py")
    run("signals.py")
    # Journal is best-effort: it skips cleanly until the contract is deployed.
    run("log_decision.py", required=False)
    print("daily run complete")
