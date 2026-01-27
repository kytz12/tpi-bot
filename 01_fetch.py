import os
import requests
from datetime import datetime

os.makedirs("data", exist_ok=True)

BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"

def try_download(url: str, out_path: str) -> bool:
    r = requests.get(url, stream=True, timeout=60)
    if r.status_code != 200:
        print("Not available:", r.status_code, url)
        return False
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    print("Downloaded OK:", url)
    return True

# Use UTC date/hour by default (override with env vars if you want)
# Example override: DATE=20260126 HOUR=21 FHR=00
date = os.environ.get("DATE", datetime.utcnow().strftime("%Y%m%d"))
hour = int(os.environ.get("HOUR", datetime.utcnow().strftime("%H")))
fhr = int(os.environ.get("FHR", "0"))

# HRRR cycles are 00-23; round hour down to nearest cycle hour
cycle = f"{hour:02d}"
fhr_str = f"{fhr:02d}"

# Prefer CONUS, surface fields file: wrfsfcf
# Example:
# .../hrrr.20260126/conus/hrrr.t21z.wrfsfcf01.grib2
fn = f"hrrr.t{cycle}z.wrfsfcf{fhr_str}.grib2"
url = f"{BASE}/hrrr.{date}/conus/{fn}"

out_path = "data/grib.grib2"
ok = try_download(url, out_path)

if not ok:
    # fallback: try fhr=01 if 00 missing (sometimes timing)
    fn2 = f"hrrr.t{cycle}z.wrfsfcf01.grib2"
    url2 = f"{BASE}/hrrr.{date}/conus/{fn2}"
    ok2 = try_download(url2, out_path)
    if not ok2:
        raise SystemExit("Could not download HRRR GRIB2. Try different DATE/HOUR/FHR.")
