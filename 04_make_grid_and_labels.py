import os
import sys
import math
import pandas as pd

# ---------- config helpers (simple parse, no yaml deps) ----------
def read_config():
    cfg = {
        "date": None,
        "grid_res_deg": 0.25,          # ~25 km lat spacing
        "radius_miles": 25.0,          # SPC-style neighborhood
        "extent": [-125.0, -66.0, 24.0, 50.0],  # lon_min, lon_max, lat_min, lat_max (CONUS-ish)
        "out_csv": "data/grid_labels.csv",
    }
    if not os.path.exists("config.yml"):
        return cfg

    with open("config.yml", "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("date:"):
                cfg["date"] = line.split(":", 1)[1].strip().strip('"').strip("'")

            elif line.startswith("grid_res_deg:"):
                cfg["grid_res_deg"] = float(line.split(":", 1)[1].strip())

            elif line.startswith("radius_miles:"):
                cfg["radius_miles"] = float(line.split(":", 1)[1].strip())

            elif line.startswith("extent:"):
                # supports: extent: [-125, -66, 24, 50]
                rhs = line.split(":", 1)[1].strip()
                rhs = rhs.strip().lstrip("[").rstrip("]")
                parts = [p.strip() for p in rhs.split(",") if p.strip()]
                if len(parts) == 4:
                    cfg["extent"] = [float(x) for x in parts]

            elif line.startswith("labels_csv:") or line.startswith("out_labels_csv:"):
                cfg["out_csv"] = line.split(":", 1)[1].strip().strip('"').strip("'")

    return cfg

# ---------- geo helpers ----------
def haversine_miles(lat1, lon1, lat2, lon2):
    # Great-circle distance
    R_km = 6371.0088
    to_rad = math.radians
    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * (math.sin(dlon / 2) ** 2))
    c = 2 * math.asin(math.sqrt(a))
    km = R_km * c
    return km * 0.621371

def make_grid(extent, res_deg):
    lon_min, lon_max, lat_min, lat_max = extent
    # inclusive ranges
    lats = []
    v = lat_min
    while v <= lat_max + 1e-9:
        lats.append(round(v, 6))
        v += res_deg

    lons = []
    v = lon_min
    while v <= lon_max + 1e-9:
        lons.append(round(v, 6))
        v += res_deg

    rows = []
    gid = 0
    for lat in lats:
        for lon in lons:
            rows.append((gid, lat, lon))
            gid += 1

    return pd.DataFrame(rows, columns=["grid_id", "lat", "lon"])

def main():
    cfg = read_config()

    pts_path = "data/torn_points.csv"
    if not os.path.exists(pts_path):
        print("Missing data/torn_points.csv. Run 02_compute_tpi.py first.", file=sys.stderr)
        sys.exit(1)

    pts = pd.read_csv(pts_path)
    if not {"lat", "lon"}.issubset(set(pts.columns)):
        print("torn_points.csv must have columns: lat, lon", file=sys.stderr)
        sys.exit(1)

    # Basic clean
    pts = pts.dropna(subset=["lat", "lon"]).copy()
    pts["lat"] = pd.to_numeric(pts["lat"], errors="coerce")
    pts["lon"] = pd.to_numeric(pts["lon"], errors="coerce")
    pts = pts.dropna(subset=["lat", "lon"])
    pts = pts[(pts["lat"].between(-90, 90)) & (pts["lon"].between(-180, 180))]

    # Build grid
    grid = make_grid(cfg["extent"], cfg["grid_res_deg"])

    # Labeling
    radius = float(cfg["radius_miles"])
    labels = []
    # Small speedup: if no points, everything is 0
    if len(pts) == 0:
        labels = [0] * len(grid)
    else:
        # Brute force for v0 (fine at 0.25° CONUS); optimize later with KD-tree if needed
        pts_list = list(zip(pts["lat"].to_list(), pts["lon"].to_list()))
        for _, r in grid.iterrows():
            glat = float(r["lat"])
            glon = float(r["lon"])
            hit = 0
            for plat, plon in pts_list:
                if haversine_miles(glat, glon, plat, plon) <= radius:
                    hit = 1
                    break
            labels.append(hit)

    out = grid.copy()
    out["date"] = cfg["date"]
    out["label"] = labels

    out_csv = cfg["out_csv"]
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    out.to_csv(out_csv, index=False)

    n_hits = int(out["label"].sum())
    print(f"Saved grid labels -> {out_csv}")
    print(f"Grid points: {len(out)} | Positive-labeled points (within {radius} mi of report): {n_hits}")
    if cfg["date"]:
        print(f"Date: {cfg['date']}")

if __name__ == "__main__":
    main()
