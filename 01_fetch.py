import requests
from datetime import datetime, timedelta, timezone
import os

BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"

def try_download(date_yyyymmdd: str, hour_hh: str, fhr: int = 1) -> bool:
    url = f"{BASE}/hrrr.{date_yyyymmdd}/conus/hrrr.t{hour_hh}z.wrfsfcf{fhr:02d}.gr
