import xarray as xr

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
