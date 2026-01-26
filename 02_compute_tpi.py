import xarray as xr
import numpy as np

ds = xr.open_dataset(
    "data/hrrr.grib2",
    engine="cfgrib",
    backend_kwargs={"filter_by_keys": {"stepType": "instant"}},
)

def pick(name):
    for k in ds.variables:
        if k.lower() == name.lower():
            return ds[k]
    raise KeyError(f"{name} not found. Have: {sorted(ds.variables)}")

# Variables HRRR actually provides (from your log)
cape = pick("cape")
cin  = pick("cin")
blh  = pick("blh")      # boundary layer height (m)
t    = pick("t")        # 2m temperature (K)
pr   = pick("prate") if "prate" in ds.variables else pick("tp")  # precip proxy

# Normalize
cape_n = (cape / 3000).clip(0, 1)
cin_n  = (1 + cin / 150).clip(0, 1)
blh_n  = (blh / 2000).clip(0, 1)
pr_n   = (pr / pr.max()).clip(0, 1)

# Tornado Potential Index (boundary-sensitive)
tpi = cape_n * cin_n * blh_n * pr_n
tpi = tpi.clip(0, 1)
tpi.name = "tpi"

xr.Dataset({"tpi": tpi}).to_netcdf("data/tpi.nc")
print("Wrote data/tpi.nc")
