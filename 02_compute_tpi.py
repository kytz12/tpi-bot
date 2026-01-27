import os
import xarray as xr
import numpy as np

os.makedirs("data", exist_ok=True)

grib_path = "data/grib.grib2"
if not os.path.exists(grib_path):
    raise FileNotFoundError(f"Missing {grib_path}. Did 01_fetch.py download it?")

print("Opening:", grib_path)

# Open ONLY isobaric instant fields to avoid cfgrib merge conflicts
ds = xr.open_dataset(
    grib_path,
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {
            "typeOfLevel": "isobaricInhPa",
            "stepType": "instant",
        }
    },
)

# Check we have what we need
need = ["t", "u", "v"]
missing = [x for x in need if x not in ds.variables]
if missing:
    raise RuntimeError(f"Missing vars in GRIB: {missing}. Available: {sorted(ds.variables)}")

levels = set(ds["isobaricInhPa"].values.tolist())
for lvl in (850, 500):
    if lvl not in levels:
        raise RuntimeError(f"Missing {lvl} hPa in file. Levels found: {sorted(levels)}")

# Instability proxy: lapse-ish (T850 - T500) in K
t850 = ds["t"].sel(isobaricInhPa=850)
t500 = ds["t"].sel(isobaricInhPa=500)
instab = (t850 - t500)

# Deep layer shear proxy: wind magnitude difference 850->500 (m/s)
u850 = ds["u"].sel(isobaricInhPa=850)
v850 = ds["v"].sel(isobaricInhPa=850)
u500 = ds["u"].sel(isobaricInhPa=500)
v500 = ds["v"].sel(isobaricInhPa=500)
shear = np.sqrt((u500 - u850) ** 2 + (v500 - v850) ** 2)

# Normalize lightly so output is 0..1-ish (optional but helps plotting)
instab_n = ((instab - 10) / 25).clip(0, 1)   # tweakable
shear_n  = (shear / 35).clip(0, 1)

tpi = (instab_n * shear_n).clip(0, 1)
tpi.name = "tpi"

tpi_ds = xr.Dataset({"tpi": tpi})

out_nc = "data/tpi.nc"
tpi_ds.to_netcdf(out_nc)
print("Saved", out_nc)
