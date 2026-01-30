import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

# ---------------- config editing ----------------
def set_config_date(path: str, date_str: str) -> None:
    """
    Updates (or inserts) a line `date: YYYY-MM-DD` in config.yml.
    Keeps the rest of the file intact.
    """
    lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    out_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("date:"):
            out_lines.append(f'date: "{date_str}"\n')
            found = True
        else:
            out_lines.append(line)

    if not found:
        # Put date at top if missing
        out_lines.insert(0, f'date: "{date_str}"\n')

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

# ---------------- runner ----------------
def run_cmd(cmd, *, cwd=None) -> int:
    print(f"$ {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=cwd)
    return p.returncode

def ensure_dirs():
    os.makedirs("data/daily", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def append_csv(src_path: str, dest_path: str) -> None:
    """
    Append CSV file to dest. If dest doesn't exist, create it (with header).
    If dest exists, append without repeating header.
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)

    # quick header handling
    with open(src_path, "r", encoding="utf-8") as fsrc:
        content = fsrc.read()

    if not os.path.exists(dest_path):
        with open(dest_path, "w", encoding="utf-8") as fdst:
            fdst.write(content)
    else:
        # strip header (first line) when appending
        lines = content.splitlines(True)
        if len(lines) > 1:
            with open(dest_path, "a", encoding="utf-8") as fdst:
                fdst.writelines(lines[1:])

def main():
    """
    Builds a multi-day training dataset by looping dates and running:
      01_fetch.py -> 02_compute_tpi.py -> 04_make_grid_and_labels.py -> 05_make_features_v0.py

    Output:
      data/train_master_v0.csv  (appended across days)
      data/daily/YYYYMMDD_train_v0.csv (per-day snapshot)
      logs/build_dataset.log
    """
    ensure_dirs()

    # --------- set your range here ----------
    START = os.environ.get("START_DATE", "2015-01-01")
    END   = os.environ.get("END_DATE",   "2015-12-31")
    SLEEP_SEC = float(os.environ.get("SLEEP_SEC", "0.5"))  # be polite to SPC servers

    start_dt = datetime.strptime(START, "%Y-%m-%d")
    end_dt = datetime.strptime(END, "%Y-%m-%d")

    master_out = "data/train_master_v0.csv"
    log_path = "logs/build_dataset.log"

    # If you want to resume safely, keep a checkpoint file
    checkpoint_path = "data/.checkpoint_last_date.txt"
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            last = f.read().strip()
        if last:
            try:
                last_dt = datetime.strptime(last, "%Y-%m-%d")
                if last_dt >= start_dt and last_dt < end_dt:
                    start_dt = last_dt + timedelta(days=1)
                    print(f"Resuming after checkpoint date {last}")
            except Exception:
                pass

    dt = start_dt
    n_ok = 0
    n_skip = 0
    n_fail = 0

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n=== build run {datetime.utcnow().isoformat()}Z | {START} -> {END} ===\n")

    while dt <= end_dt:
        date_str = dt.strftime("%Y-%m-%d")
        stamp = dt.strftime("%Y%m%d")
        print("\n" + "=" * 80)
        print(f"DATE: {date_str}")
        print("=" * 80)

        # Update config.yml date (your scripts read it)
        set_config_date("config.yml", date_str)

        # Run pipeline
        # Note: 01_fetch.py exits nonzero if no tornado CSV exists for that day
        # We'll treat that as a SKIP (not a failure).
        rc1 = run_cmd([sys.executable, "01_fetch.py"])
        if rc1 != 0:
            print(f"SKIP (no tornado CSV / fetch failed) for {date_str}")
            n_skip += 1
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"{date_str} SKIP fetch\n")
            # checkpoint
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                f.write(date_str)
            dt += timedelta(days=1)
            time.sleep(SLEEP_SEC)
            continue

        rc2 = run_cmd([sys.executable, "02_compute_tpi.py"])
        rc4 = run_cmd([sys.executable, "04_make_grid_and_labels.py"])
        rc5 = run_cmd([sys.executable, "05_make_features_v0.py"])

        if rc2 == 0 and rc4 == 0 and rc5 == 0 and os.path.exists("data/train_v0.csv"):
            # Snapshot per day
            daily_out = f"data/daily/{stamp}_train_v0.csv"
            # Copy train_v0.csv -> daily snapshot
            with open("data/train_v0.csv", "r", encoding="utf-8") as src, open(daily_out, "w", encoding="utf-8") as dst:
                dst.write(src.read())

            # Append into master
            append_csv("data/train_v0.csv", master_out)

            n_ok += 1
            print(f"OK: appended -> {master_out}")
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"{date_str} OK\n")
        else:
            n_fail += 1
            print(f"FAIL: pipeline error on {date_str}")
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"{date_str} FAIL rc2={rc2} rc4={rc4} rc5={rc5}\n")

        # checkpoint
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            f.write(date_str)

        dt += timedelta(days=1)
        time.sleep(SLEEP_SEC)

    print("\nDONE")
    print(f"OK={n_ok}  SKIP={n_skip}  FAIL={n_fail}")
    print(f"Master dataset: {master_out}")
    print(f"Log: {log_path}")

if __name__ == "__main__":
    main()
