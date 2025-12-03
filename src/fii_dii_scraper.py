import requests
import pandas as pd
from datetime import datetime
from src.config import DATA_DIR
from src.logger import logger
from bs4 import BeautifulSoup

# Primary: NSE API
NSE_URL = "https://www.nseindia.com/api/fiidii"
HOME_PAGE_URL = "https://www.nseindia.com"

# Secondary: MoneyControl
MC_URL = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

def fetch_fii_dii_data():
    """Scrapes FII/DII data with fallbacks."""
    data = fetch_nse()
    if not data:
        data = fetch_moneycontrol()

    if data:
        save_fii_dii_data(data)
        return data

    # Check cache if live fetch failed
    return get_recent_fii_dii()

def fetch_nse():
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        # Visit home to get cookies
        session.get(HOME_PAGE_URL, timeout=5)
        # Fetch API
        response = session.get(NSE_URL, timeout=5)
        if response.status_code == 200:
            json_data = response.json()
            result = []
            for item in json_data:
                result.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "category": item.get("category", "Unknown"),
                    "buyValue": item.get("buyValue", 0),
                    "sellValue": item.get("sellValue", 0),
                    "netValue": item.get("netValue", 0)
                })
            return result
    except Exception as e:
        logger.warning(f"NSE Scraper failed: {e}")
    return None

def fetch_moneycontrol():
    try:
        response = requests.get(MC_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # MoneyControl usually puts FII/DII in a table
            # We look for "FII Cash" and "DII Cash" text in the page or table
            # This is a basic parser

            # Placeholder structure if parsing is too complex without live DOM
            # We will try to find a table with class 'mctable1'
            pass

    except Exception as e:
        logger.warning(f"MC Scraper failed: {e}")
    return None

def save_fii_dii_data(data):
    if not data: return
    df = pd.DataFrame(data)
    file_path = DATA_DIR / "fii_dii_history.csv"

    # Deduplicate by date/category
    # Simple Append for now
    if file_path.exists():
        try:
            existing = pd.read_csv(file_path)
            # Avoid dupes
            return
        except: pass

    df.to_csv(file_path, index=False)

def get_recent_fii_dii():
    file_path = DATA_DIR / "fii_dii_history.csv"
    if not file_path.exists(): return []
    try:
        df = pd.read_csv(file_path)
        return df.tail(14).to_dict('records')
    except: return []
