import os
import sys
import pandas as pd

def main():
    in_csv = "data/torn.csv"
    if not os.path.exists(in_csv):
        print("Missing data/torn.csv. Run 01_fetch.py first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(in_csv)

    # SPC tornado report CSVs typically include LAT/LON columns (names can vary a bit)
    # We'll try common options.
    possible_lat = ["LAT", "Lat", "lat", "slat"]
    possible_lon = ["LON", "Lon", "lon", "slon"]

    lat_col = next((c for c in possible_lat if c in df.columns), None)
    lon_col = next((c for c in possible_lon if c in df.columns), None)

    if lat_col is None or lon_col is None:
        print("Could not find LAT/LON columns in CSV. Columns are:", list(df.columns), file=sys.stderr)
        sys.exit(1)

    out = df[[lat_col, lon_col]].copy()
    out.columns = ["lat", "lon"]

    # Clean
    out = out.dropna()
    out = out[(out["lat"].between(10, 80)) & (out["lon"].between(-180, -30))]

    os.makedirs("data", exist_ok=True)
    out.to_csv("data/torn_points.csv", index=False)
    print(f"Saved {len(out)} points -> data/torn_points.csv")

if __name__ == "__main__":
    main()
