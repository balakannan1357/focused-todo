import csv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "tn_elections.csv")

BASE_URL = "https://results.eci.gov.in/"  # ECI results portal

# Mapping of year to path segment used by the results site
YEAR_PATH = {
    2006: "AcwiseU05.htm",
    2011: "AcwiseU05.htm",
    2016: "AcwiseU05.htm",
    2021: "AcwiseU05.htm",
}

STATE_CODE = "S22"  # Tamil Nadu


def fetch_constituency_data(year: int) -> pd.DataFrame:
    """Fetch candidate level data for all constituencies for a given year."""
    path = YEAR_PATH.get(year)
    if not path:
        raise ValueError(f"No path mapping for {year}")
    url = f"{BASE_URL}ResultAcmah{year}/{path}?st_code={STATE_CODE}"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = []
    for table in soup.select("table"):
        headers = [h.get_text(strip=True) for h in table.select("th")]
        for tr in table.select("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.select("td")]
            if len(cells) == len(headers):
                row = dict(zip(headers, cells))
                row["Year"] = year
                rows.append(row)
    return pd.DataFrame(rows)


def build_dataset(years=None):
    years = years or YEAR_PATH.keys()
    all_rows = []
    for year in years:
        df = fetch_constituency_data(year)
        all_rows.append(df)
    combined = pd.concat(all_rows, ignore_index=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved data to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_dataset()
