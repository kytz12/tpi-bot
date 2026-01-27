import os
import xarray as xr
import matplotlib.pyplot as plt

os.makedirs("out", exist_ok=True)

nc_path = "data/tpi.nc"
if not os.path.exists(nc_path):
    print("No data/tpi.nc found; skipping plot.")
    raise SystemExit(0)

ds = xr.open_dataset(nc_path)
if "tpi" not in ds:
    raise RuntimeError(f"'tpi' not found in {nc_path}. Keys: {list(ds.data_vars)}")

tpi = ds["tpi"]

plt.figure(figsize=(12, 7))
tpi.plot()  # xarray chooses lat/lon if present, otherwise array index
plt.title("TPI (Instability × Shear proxy)")
plt.tight_layout()
plt.savefig("out/tpi.png", dpi=150)
print("Wrote out/tpi.png")
