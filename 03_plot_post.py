import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

ds = xr.open_dataset("data/tpi.nc")
tpi = ds["tpi"]

plt.figure(figsize=(10,6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.set_extent([-125, -66, 24, 50])

tpi.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="hot")

os.makedirs("out", exist_ok=True)
plt.savefig("out/tpi.png")
plt.close()
