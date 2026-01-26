import xarray as xr
import numpy as np

ds = xr.open_dataset("data/hrrr.grib2", engine="cfgrib")

cape = ds["cape"]
lcl = ds["lcl"]
cin = ds["cin"]

cape_n = np.clip(cape / 2000, 0, 1)
lcl_n  = np.clip(1 - (lcl / 2000), 0, 1)
cin_n  = np.clip(1 + (cin / 100), 0, 1)

tpi = cape_n * lcl_n * cin_n

out = xr.Dataset({"tpi": tpi})
out.to_netcdf("data/tpi.nc")
