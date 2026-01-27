import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

def read_config_date_and_outname():
    date = None
    outpng = "tornado_reports_map.png"
    with open("config.yml", "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("date:"):
                date = s.split(":", 1)[1].strip().strip('"').strip("'")
            if s.startswith("output_png:"):
                outpng = s.split(":", 1)[1].strip().strip('"').strip("'")
    return date, outpng

def main():
    date, outpng = read_config_date_and_outname()
    pts_path = "data/torn_points.csv"
    if not os.path.exists(pts_path):
        print("Missing data/torn_points.csv. Run 02_compute_tpi.py first.", file=sys.stderr)
        sys.exit(1)

    pts = pd.read_csv(pts_path)

    os.makedirs("out", exist_ok=True)
    out_path = os.path.join("out", outpng)

    # Map
    proj = ccrs.LambertConformal(central_longitude=-96, central_latitude=39)
    fig = plt.figure(figsize=(12, 7))
    ax = plt.axes(projection=proj)

    # CONUS-ish extent
    ax.set_extent([-125, -66, 24, 50], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, linewidth=0)
    ax.add_feature(cfeature.OCEAN, linewidth=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3)

    ax.scatter(
        pts["lon"], pts["lat"],
        s=8,
        transform=ccrs.PlateCarree(),
        alpha=0.7
    )

    title = f"SPC Tornado Reports (points) — {date}" if date else "SPC Tornado Reports (points)"
    ax.set_title(title)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    print(f"Saved map -> {out_path}")

if __name__ == "__main__":
    main()
