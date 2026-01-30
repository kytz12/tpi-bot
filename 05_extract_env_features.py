import os
import sys
import math
import pandas as pd
from datetime import datetime

def read_config_date():
    date = None
    with open("config.yml", "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("date:"):
                date = s.split(":", 1)[1].strip().strip('"').strip("'")
                break
    return date

def main():
    labels_csv = "data/grid_labels.csv"
    if not os.path.exists(labels_csv):
        print("Missing data/grid_labels.csv. Run 04_make_grid_and_labels.py first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(labels_csv)
    if not {"lat","lon","label"}.issubset(df.columns):
        print("grid_labels.csv must contain lat, lon, label", file=sys.stderr)
        sys.exit(1)

    date = df["date"].iloc[0] if "date" in df.columns and pd.notna(df["date"].iloc[0]) else read_config_date()
    if not date:
        print("Missing date (config.yml date: or date column).", file=sys.stderr)
        sys.exit(1)

    dt = datetime.strptime(date, "%Y-%m-%d")
    doy = dt.timetuple().tm_yday
    # cyclic season encoding
    angle = 2 * math.pi * (doy / 365.25)

    out = df.copy()
    out["doy"] = doy
    out["doy_sin"] = math.sin(angle)
    out["doy_cos"] = math.cos(angle)

    # Features we’ll train on (v0)
    out_path = "data/train_v0.csv"
    os.makedirs("data", exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Saved training table -> {out_path} (rows={len(out)})")

if __name__ == "__main__":
    main()
