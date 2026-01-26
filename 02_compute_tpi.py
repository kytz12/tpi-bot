def open_surface(grib_path: str) -> xr.Dataset:
    ds = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface", "stepType": "instant"}},
    )
    ds_hag = xr.open_dataset(
        grib_path,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround", "stepType": "instant"}},
    )
    return xr.merge([ds, ds_hag], compat="override")
