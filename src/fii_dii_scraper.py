import requests
import pandas as pd
from datetime import datetime
from src.config import DATA_DIR
from src.logger import logger

# NSE often blocks requests without specific cookies.
# We try to mimic a browser visit.
FII_DII_URL = "https://www.nseindia.com/api/fiidii"
HOME_PAGE_URL = "https://www.nseindia.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/reports/fii-dii",
    "Connection": "keep-alive"
}

def fetch_fii_dii_data():
    """Scrapes FII/DII data from NSE."""
    try:
        session = requests.Session()
        # 1. Visit Homepage to get cookies
        session.get(HOME_PAGE_URL, headers=HEADERS, timeout=10)

        # 2. Request Data
        response = session.get(FII_DII_URL, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            fii_dii_list = []

            # The API returns a list of categories
            for item in data:
                fii_dii_list.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "category": item.get("category", "Unknown"),
                    "buyValue": item.get("buyValue", 0),
                    "sellValue": item.get("sellValue", 0),
                    "netValue": item.get("netValue", 0)
                })

            save_fii_dii_data(fii_dii_list)
            logger.info("FII/DII Data Fetched and Saved")
            return fii_dii_list
        else:
            logger.warning(f"Failed to fetch FII/DII data: Status {response.status_code}")
            return []

    except Exception as e:
        logger.error(f"Exception in FII/DII fetch: {e}")
        return []

def save_fii_dii_data(data):
    if not data:
        return

    df = pd.DataFrame(data)
    file_path = DATA_DIR / "fii_dii_history.csv"

    # Check if we already have today's data to avoid duplicates
    if file_path.exists():
        existing_df = pd.read_csv(file_path)
        today = datetime.now().strftime("%Y-%m-%d")
        if today in existing_df['date'].values:
             # Already have data for today
             return

        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

def get_recent_fii_dii():
    """Reads local CSV and returns last 7 entries."""
    file_path = DATA_DIR / "fii_dii_history.csv"
    if not file_path.exists():
        return []

    try:
        df = pd.read_csv(file_path)
        return df.tail(14).to_dict('records')
    except Exception as e:
        logger.error(f"Error reading FII/DII history: {e}")
        return []
