import os
import time
import requests
from datetime import datetime, timedelta, timezone

BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"
MIN_BYTES = 1_000_000
RETRIES = 3
RETRY_DELAY = 5  # seconds

def try_download(dt_utc: datetime, fhr: int = 1) -> bool:
    date = dt_utc.strftime("%Y%m%d")
    hour = dt_utc.strftime("%H")
    url = f"{BASE}/hrrr.{date}/conus/hrrr.t{hour}z.wrfsfcf{fhr:02d}.grib2"
    print("Trying:", url)

    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > MIN_BYTES:
                os.makedirs("data", exist_ok=True)
                with open("data/hrrr.grib2", "wb") as f:
                    f.write(r.content)
                print("Downloaded OK:", url)
                return True
            else:
                print(f"Not available (status={{r.status_code}}, size={{len(r.content)}})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request error (attempt {{attempt}}/{{RETRIES}}): {{e}}")
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print("Giving up on this URL for now.")
                return False

def main() -> int:
    now = datetime.now(timezone.utc)
    for back in range(0, 7):  # last 0..6 hours
        if try_download(now - timedelta(hours=back), fhr=1):
            return 0
    print("Could not find an available HRRR file in the last 6 hours on NOMADS.")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
