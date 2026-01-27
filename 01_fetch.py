import os
import sys
import requests
from datetime import datetime

def yymmdd_from_iso(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%y%m%d")  # YYMMDD

def download(url: str, out_path: str, timeout: int = 60) -> bool:
    r = requests.get(url, timeout=timeout)
    if r.status_code == 200 and r.content:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(r.content)
        return True
    return False

def main():
    # Read config date from config.yml (simple parse; avoids extra deps)
    date = None
    with open("config.yml", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("date:"):
                date = line.split(":", 1)[1].strip().strip('"').strip("'")
                break

    if not date:
        print("Could not find `date:` in config.yml", file=sys.stderr)
        sys.exit(1)

    yymmdd = yymmdd_from_iso(date)

    # SPC archived daily tornado CSV format (YYMMDD_rpts_torn.csv)
    # SPC also documents report URLs with YYMMDD_rpts.gif and YYMMDD_prt_rpts.html :contentReference[oaicite:1]{index=1}
    csv_url = f"https://www.spc.noaa.gov/climo/reports/{yymmdd}_rpts_torn.csv"
    gif_url = f"https://www.spc.noaa.gov/climo/reports/{yymmdd}_rpts.gif"
    html_url = f"https://www.spc.noaa.gov/climo/reports/{yymmdd}_prt_rpts.html"

    ok_csv = download(csv_url, "data/torn.csv")
    ok_gif = download(gif_url, "data/spc_rpts.gif")
    ok_html = download(html_url, "data/spc_prt_rpts.html")

    if not ok_csv:
        print(f"Could not download tornado CSV (maybe no tornado file for that day): {csv_url}", file=sys.stderr)
        sys.exit(1)

    print(f"Downloaded: {csv_url} -> data/torn.csv")
    if ok_gif:
        print(f"Downloaded: {gif_url} -> data/spc_rpts.gif")
    if ok_html:
        print(f"Downloaded: {html_url} -> data/spc_prt_rpts.html")

if __name__ == "__main__":
    main()
