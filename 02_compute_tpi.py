import xarray as xr
import os

# Open only isobaric fields to avoid cfgrib merge crashes
ds = xr.open_dataset(
    "data/grib.grib2",
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {
            "typeOfLevel": "isobaricInhPa",
            "stepType": "instant"
        }
    }
)

# Make sure required fields exist
required = ["t", "u", "v", "q"]
for r in required:
    if r not in ds:
        raise RuntimeError(f"Missing variable: {r}")

# Pick key pressure levels
t850 = ds["t"].sel(isobaricInhPa=850)
t500 = ds["t"].sel(isobaricInhPa=500)
u850 = ds["u"].sel(isobaricInhPa=850)
v850 = ds["v"].sel(isobaricInhPa=850)
u500 = ds["u"].sel(isobaricInhPa=500)
v500 = ds["v"].sel(isobaricInhPa=500)

# Simple instability proxy (lapse rate)
lapse = t850 - t500

# Deep-layer shear proxy
shear = ((u500 - u850) ** 2 + (v500 - v850) ** 2) ** 0.5

# Tornado Parameter Index (simple but physically meaningful)
tpi = lapse * shear

# Package as Dataset
tpi_ds = xr.Dataset(
    {"tpi": tpi},
    coords={"lat": tpi.latitude, "lon": tpi.longitude}
)

# Save output
os.makedirs("data", exist_ok=True)
tpi_ds.to_netcdf("data/tpi.nc")
print("Saved data/tpi.nc")
