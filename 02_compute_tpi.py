import os
import sys
import pandas as pd

def main():
    in_csv = "data/torn.csv"
    if not os.path.exists(in_csv):
        print("Missing data/torn.csv. Run 01_fetch.py first.", file=sys.stderr)
        sys.exit(1)

    # SPC CSVs occasionally have malformed rows (extra commas).
    # Use python engine + skip bad lines so the run never dies.
    df = pd.read_csv(
        in_csv,
        engine="python",
        on_bad_lines="skip",   # or "warn" if you want to see which lines are skipped
    )

    # Try common column names
    lat_candidates = ["LAT", "Lat", "lat", "slat"]
    lon_candidates = ["LON", "Lon", "lon", "slon"]

    lat_col = next((c for c in lat_candidates if c in df.columns), None)
    lon_col = next((c for c in lon_candidates if c in df.columns), None)

    if lat_col is None or lon_col is None:
        print("Could not find LAT/LON columns. Columns are:", list(df.columns), file=sys.stderr)
        sys.exit(1)

    pts = df[[lat_col, lon_col]].copy()
    pts.columns = ["lat", "lon"]

    # Clean
    pts = pts.dropna()
    pts["lat"] = pd.to_numeric(pts["lat"], errors="coerce")
    pts["lon"] = pd.to_numeric(pts["lon"], errors="coerce")
    pts = pts.dropna()
    pts = pts[(pts["lat"].between(10, 80)) & (pts["lon"].between(-180, -30))]

    os.makedirs("data", exist_ok=True)
    pts.to_csv("data/torn_points.csv", index=False)
    print(f"Saved {len(pts)} points -> data/torn_points.csv")

if __name__ == "__main__":
    main()
