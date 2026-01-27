import xarray as xr
import matplotlib.pyplot as plt
import os
import sys

# Try to import cartopy, allow fallback if it's not installed
try:
    import cartopy.crs as ccrs
    _HAS_CARTOPY = True
except Exception:
    _HAS_CARTOPY = False
    print("Cartopy not available — falling back to simple plotting.", file=sys.stderr)

def make_plot(in_nc="data/tpi.nc", out_png="out/tpi.png"):
    if not os.path.exists(in_nc):
        raise FileNotFoundError(f"{in_nc} not found — run the compute step first.")

    ds = xr.open_dataset(in_nc)
    if "tpi" not in ds:
        raise KeyError("tpi variable not found in dataset.")
    tpi = ds["tpi"]

    # Try to find lat/lon coordinate names (HRRR via cfgrib can be weird)
    lat_name = None
    lon_name = None
    for c in tpi.coords:
        cl = c.lower()
        if cl in ("latitude", "lat"):
            lat_name = c
        if cl in ("longitude", "lon"):
            lon_name = c

    os.makedirs("out", exist_ok=True)

    if _HAS_CARTOPY and lat_name and lon_name:
        plt.figure(figsize=(11, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.set_extent([-125, -66, 24, 50])
        tpi.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="hot")
        plt.colorbar()
        plt.savefig(out_png, dpi=160, bbox_inches="tight")
        plt.close()
    else:
        # simpler fallback plotting
        plt.figure(figsize=(11, 6))
        plt.title("TPI (simple fallback plot)")
        plt.imshow(tpi.values, origin="lower", cmap="hot")
        plt.colorbar()
        plt.savefig(out_png, dpi=160, bbox_inches="tight")
        plt.close()

    print(f"Saved {out_png}")

if __name__ == "__main__":
    try:
        make_plot()
    except Exception as e:
        print("Error while plotting:", e, file=sys.stderr)
        raise
