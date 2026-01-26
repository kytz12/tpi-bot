#!/usr/bin/env python3
import subprocess
import sys
import yaml
import os

def load_config(path="config.yml"):
    if not os.path.exists(path):
        print("No config.yml found — using defaults.")
        return {}
    with open(path, "r") as fh:
        return yaml.safe_load(fh) or {}

def run_step(cmd):
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Step failed: {e}", file=sys.stderr)
        return e.returncode

def main():
    cfg = load_config()
    steps = [
        ["python", "01_fetch.py"],
        ["python", "02_compute_tpi.py"],
        ["python", "03_plot_post.py"],
    ]

    for cmd in steps:
        rc = run_step(cmd)
        if rc != 0:
            print("Pipeline stopped due to failure.", file=sys.stderr)
            return rc

    post_cfg = cfg.get("post", {}) or {}
    if post_cfg.get("discord", False):
        # call the poster script which will check for configured webhook
        return run_step(["python", "post_discord.py"])

    print("Pipeline completed successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())