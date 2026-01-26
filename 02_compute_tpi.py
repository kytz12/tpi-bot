import xarray as xr
import numpy as np
import cfgrib

GRIB = "data/hrrr.grib2"

def open_surface(grib_path: str) -> xr.Dataset:
    # Only open the surface-ish group so we avoid coord alignment junk
    ds = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface"}},
    )
    # Some fields are "heightAboveGround" (2m/10m), so open that too and merge
    ds_hag = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround"}},
    )
    return xr.merge([ds, ds_hag], compat="override")

ds = open_surface(GRIB)

def pick(name):
    for k in ds.variables:
        if k.lower() == name.lower():
            return ds[k]
    raise KeyError(f"{name} not found. Have: {sorted(ds.variables)}")

cape = pick("cape")
cin  = pick("cin")
t2m  = pick("t2m")   # K
d2m  = pick("d2m")   # K
u10  = pick("u10")
v10  = pick("v10")

# K -> C
T  = t2m - 273.15
Td = d2m - 273.15

# Simple LCL (m)
lcl = 125.0 * (T - Td)

# 10m wind speed (proxy)
shear = np.sqrt(u10**2 + v10**2)

# Normalize to 0..1
cape_n  = xr.apply_ufunc(lambda x: np.clip(x/3000.0, 0, 1), cape)
lcl_n   = xr.apply_ufunc(lambda x: np.clip(1 - (x/2000.0), 0, 1), lcl)
cin_n   = xr.apply_ufunc(lambda x: np.clip(1 + (x/150.0), 0, 1), cin)
shear_n = xr.apply_ufunc(lambda x: np.clip(x/20.0, 0, 1), shear)

tpi = (cape_n * lcl_n * cin_n * shear_n).clip(0, 1)
tpi.name = "tpi"

# Write clean netcdf
out = xr.Dataset({"tpi": tpi})
out.to_netcdf("data/tpi.nc")
print("Wrote data/tpi.nc")
