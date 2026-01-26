import xarray as xr
import numpy as np
import cfgrib

GRIB = "data/hrrr.grib2"

# Open all GRIB groups and merge
datasets = cfgrib.open_datasets(GRIB)
ds = xr.merge(datasets, compat="override")

def pick(name):
    for k in ds.variables:
        if k.lower() == name.lower():
            return ds[k]
    raise KeyError(f"{name} not found")

cape = pick("cape")
cin  = pick("cin")
t2m  = pick("t2m")    # 2m temperature (K)
d2m  = pick("d2m")    # 2m dewpoint (K)
u10  = pick("u10")    # 10m u wind
v10  = pick("v10")    # 10m v wind

# Convert K → C
T = t2m - 273.15
Td = d2m - 273.15

# Bolton LCL (meters)
lcl = 125.0 * (T - Td)

# 10m wind speed proxy for low-level shear
shear = np.sqrt(u10**2 + v10**2)

# Normalize fields
cape_n  = np.clip(cape / 3000.0, 0, 1)
lcl_n   = np.clip(1 - (lcl / 2000.0), 0, 1)
cin_n   = np.clip(1 + (cin / 150.0), 0, 1)
shear_n = np.clip(shear / 20.0, 0, 1)

# Tornado Potential Index
tpi = cape_n * lcl_n * cin_n * shear_n
tpi = np.clip(tpi, 0, 1)

out = xr.Dataset({"tpi": (cape.dims, tpi)}, coords={k: ds.coords[k] for k in ds.coords})
out.to_netcdf("data/tpi.nc")

print("TPI written to data/tpi.nc")
