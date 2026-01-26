import requests
from datetime import datetime
import os

base = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"

date = datetime.utcnow().strftime("%Y%m%d")
hour = datetime.utcnow().strftime("%H")

url = f"{base}/hrrr.{date}/conus/hrrr.t{hour}z.wrfsfcf01.grib2"

os.makedirs("data", exist_ok=True)

print("Downloading:", url)
r = requests.get(url)
r.raise_for_status()

open("data/hrrr.grib2","wb").write(r.content)
