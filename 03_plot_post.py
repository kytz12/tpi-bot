import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

ds = xr.open_dataset("data/tpi.nc")
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

# If lat/lon exist, use them; otherwise just plot array (still produces png)
plt.figure(figsize=(11, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.set_extent([-125, -66, 24, 50])

if lat_name and lon_name:
    tpi.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="hot")
else:
    # Fallback
    plt.title("TPI (coords not labeled lat/lon)")
    plt.imshow(tpi.values)
    plt.colorbar()

os.makedirs("out", exist_ok=True)
plt.savefig("out/tpi.png", dpi=160, bbox_inches="tight")
plt.close()

print("Saved out/tpi.png")
