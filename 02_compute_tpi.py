import xarray as xr
import numpy as np

ds = xr.open_dataset(
    "data/hrrr.grib2",
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {
            "typeOfLevel": "surface",
            "stepType": "instant"
        }
    }
)
