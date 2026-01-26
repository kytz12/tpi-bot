import os
import requests
from datetime import datetime, timedelta, timezone

BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"

def try_download(dt_utc: datetime, fhr: int = 1) -> bool:
    date = dt_utc.strftime("%Y%m%d")
    hour = dt_utc.strftime("%H")
    url = f"{BASE}/hrrr.{date}/conus/hrrr.t{hour}z.wrfsfcf{fhr:02d}.grib2"
    print("Trying:", url)

    r = requests.get(url, timeout=120)
    if r.status_code == 200 and len(r.content) > 1_000_000:
        os.makedirs("data", exist_ok=True)
        with open("data/hrrr.grib2", "wb") as f:
            f.write(r.content)
        print("Downloaded OK:", url)
        return True

    print("Not available:", r.status_code)
    return False

def main():
    now = datetime.now(timezone.utc)
    for back in range(0, 7):  # last 6 hours
        if try_download(now - timedelta(hours=back), fhr=1):
            return
    raise SystemExit("Could not find an available HRRR file in the last 6 hours on NOMADS.")

if __name__ == "__main__":
    main()
