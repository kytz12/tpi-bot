import xarray as xr
import numpy as np

GRIB = "data/hrrr.grib2"

def open_needed(grib_path: str) -> xr.Dataset:
    # surface (CAPE/CIN often here) — force instant fields only
    ds_surface = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface", "stepType": "instant"}},
    )

    # 2m/10m vars live in heightAboveGround — force instant fields only
    ds_hag = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround", "stepType": "instant"}},
    )

    return xr.merge([ds_surface, ds_hag], compat="override")

ds = open_needed(GRIB)

def pick_ci(name: str) -> xr.DataArray:
    for k in ds.variables:
        if k.lower() == name.lower():
            return ds[k]
    raise KeyError(f"{name} not found. Available: {sorted(ds.variables)}")

# Required fields (per your log these exist)
cape = pick_ci("cape")  # J/kg
cin  = pick_ci("cin")   # J/kg (usually negative)
t2m  = pick_ci("t2m")   # K
d2m  = pick_ci("d2m")   # K
u10  = pick_ci("u10")   # m/s
v10  = pick_ci("v10")   # m/s

# Convert K -> C for LCL approximation
T  = t2m - 273.15
Td = d2m - 273.15

# Simple LCL estimate (meters). Works well as a gating term.
lcl = 125.0 * (T - Td)

# 10m wind speed proxy (we’ll upgrade to true shear later)
wind10 = np.sqrt(u10**2 + v10**2)

# Normalize to 0..1
cape_n  = (cape / 3000.0).clip(0, 1)
lcl_n   = (1.0 - (lcl / 2000.0)).clip(0, 1)
cin_n   = (1.0 + (cin / 150.0)).clip(0, 1)   # CIN negative -> helps
wind_n  = (wind10 / 20.0).clip(0, 1)

tpi = (cape_n * lcl_n * cin_n * wind_n).clip(0, 1)
tpi.name = "tpi"

xr.Dataset({"tpi": tpi}).to_netcdf("data/tpi.nc")
print("Wrote data/tpi.nc")
