import xarray as xr
import numpy as np
import cfgrib

GRIB_PATH = "data/hrrr.grib2"

def pick_var(ds, names):
    """Pick the first variable that exists (case-insensitive)."""
    lower = {k.lower(): k for k in ds.variables.keys()}
    for n in names:
        if n.lower() in lower:
            return ds[lower[n.lower()]]
    return None

# 1) Open ALL GRIB “groups” and merge them (fixes DatasetBuildError)
datasets = cfgrib.open_datasets(GRIB_PATH)
ds = xr.merge(datasets, compat="override")

# 2) Grab fields (names vary slightly; we search robustly)
cape = pick_var(ds, ["cape"])
cin  = pick_var(ds, ["cin"])
lcl  = pick_var(ds, ["lcl"])

# If any are missing, print what we *do* have so we can adjust
missing = [n for n,v in [("cape",cape),("cin",cin),("lcl",lcl)] if v is None]
if missing:
    print("Missing vars:", missing)
    print("Available vars:", sorted(list(ds.variables.keys()))[:200])
    raise SystemExit("Required variables not found in GRIB. See log for available vars.")

# 3) Compute a simple MVP TPI
CAPE = cape.values
CIN  = cin.values
LCL  = lcl.values

cape_n = np.clip(CAPE / 2000.0, 0, 1)
lcl_n  = np.clip(1.0 - (LCL / 2000.0), 0, 1)
cin_n  = np.clip(1.0 + (CIN / 100.0), 0, 1)

tpi = cape_n * lcl_n * cin_n
tpi = np.clip(tpi, 0, 1)

out = xr.Dataset({"tpi": (cape.dims, tpi)}, coords={k: ds.coords[k] for k in ds.coords})
out.to_netcdf("data/tpi.nc")
print("Wrote data/tpi.nc")
