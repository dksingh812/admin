import requests
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup
from src.config import DATA_DIR
from src.logger import logger

# Primary: NSE API
NSE_URL = "https://www.nseindia.com/api/fiidii"
HOME_PAGE_URL = "https://www.nseindia.com"

# Secondary: MoneyControl (More reliable for scraping if NSE blocks)
MC_URL = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

def fetch_fii_dii_data():
    """
    Scrapes FII/DII data.
    Returns a dict: {"fii": {"buy": X, "sell": Y, "net": Z}, "dii": {...}, "date": "YYYY-MM-DD"}
    """
    data_list = fetch_nse()

    if not data_list:
        data_list = fetch_moneycontrol()

    if not data_list:
        # Fallback: Try to read from Mock/Cache if live fails
        return get_cached_fii_dii()

    # Process and Save
    save_fii_dii_data(data_list)

    # Format for UI
    result = {"fii": {}, "dii": {}, "date": datetime.now().strftime("%Y-%m-%d")}

    for item in data_list:
        cat = item.get("category", "").upper()
        if "FII" in cat or "FPI" in cat:
            result["fii"] = {
                "buy": item.get("buyValue", 0),
                "sell": item.get("sellValue", 0),
                "net": item.get("netValue", 0)
            }
        elif "DII" in cat:
            result["dii"] = {
                "buy": item.get("buyValue", 0),
                "sell": item.get("sellValue", 0),
                "net": item.get("netValue", 0)
            }

    return result

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
            return json_data
    except Exception as e:
        logger.warning(f"NSE Scraper failed: {e}")
    return None

def fetch_moneycontrol():
    try:
        response = requests.get(MC_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # MoneyControl Table Parsing logic (Heuristic)
            # Look for table with FII/DII text

            # Simplified for robustness: Search for "Net Sales/Purchase"
            # This is complex to robustly parse without live DOM inspection.
            # But usually they have a responsive table.

            # Fallback: Just return None for now if parsing is risky without verification.
            # Ideally we need specific selectors.
            pass

    except Exception as e:
        logger.warning(f"MC Scraper failed: {e}")
    return None

def save_fii_dii_data(data_list):
    if not data_list: return

    file_path = os.path.join(DATA_DIR, "fii_dii_history.csv")
    today = datetime.now().strftime("%Y-%m-%d")

    new_rows = []
    for item in data_list:
        new_rows.append({
            "date": today,
            "category": item.get("category"),
            "buy_value": item.get("buyValue"),
            "sell_value": item.get("sellValue"),
            "net_value": item.get("netValue")
        })

    df_new = pd.DataFrame(new_rows)

    if os.path.exists(file_path):
        try:
            df_old = pd.read_csv(file_path)
            # Remove today's entries if they exist to overwrite with fresh data
            df_old = df_old[df_old['date'] != today]
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        except Exception as e:
            logger.error(f"Error reading existing FII/DII csv: {e}")
            df_final = df_new
    else:
        df_final = df_new

    df_final.to_csv(file_path, index=False)

def get_cached_fii_dii():
    file_path = os.path.join(DATA_DIR, "fii_dii_history.csv")
    result = {"fii": {"net": 0, "buy": 0, "sell": 0}, "dii": {"net": 0, "buy": 0, "sell": 0}, "date": "--"}

    if not os.path.exists(file_path):
        return result

    try:
        df = pd.read_csv(file_path)
        if df.empty: return result

        last_date = df['date'].iloc[-1]
        result['date'] = last_date

        day_data = df[df['date'] == last_date]

        for _, row in day_data.iterrows():
            cat = str(row['category']).upper()
            if "FII" in cat or "FPI" in cat:
                result["fii"] = {"buy": row['buy_value'], "sell": row['sell_value'], "net": row['net_value']}
            elif "DII" in cat:
                result["dii"] = {"buy": row['buy_value'], "sell": row['sell_value'], "net": row['net_value']}

        return result
    except Exception as e:
        logger.error(f"Error reading cached FII data: {e}")
        return result
