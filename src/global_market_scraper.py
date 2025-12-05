import yfinance as yf
import requests
from bs4 import BeautifulSoup
import threading
import time
from src.logger import logger

# Symbol Mapping (Yahoo Finance)
YF_MAPPING = {
    "US": {
        "Dow Jones": "^DJI",
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC"
    },
    "EUROPE": {
        "FTSE": "^FTSE",
        "CAC": "^FCHI",
        "DAX": "^GDAXI"
    },
    "ASIA": {
        "GIFT NIFTY": "^NSEI", # Proxy
        "Nikkei 225": "^N225",
        "Straits Times": "^STI",
        "Hang Seng": "^HSI",
        "KOSPI": "^KS11"
    },
    "COMMODITIES": {
        "Brent Crude": "BZ=F",
        "Gold": "GC=F",
        "Crude Oil": "CL=F",
        "Silver": "SI=F",
        "Natural Gas": "NG=F"
    }
}

class GlobalMarketScraper:
    def __init__(self):
        self.data = {} # { "Region": { "Name": { "price": x, "change": y, "pct": z } } }
        self.lock = threading.Lock()
        self.running = False

    def start(self, interval=60):
        if self.running: return
        self.running = True
        threading.Thread(target=self._loop, args=(interval,), daemon=True).start()

    def _loop(self, interval):
        logger.info("Global Market Scraper Started")
        while self.running:
            self.fetch_all()
            time.sleep(interval)

    def fetch_all(self):
        # We process each region
        for region, symbols in YF_MAPPING.items():
            self._fetch_yfinance(region, symbols)

    def _fetch_yfinance(self, region, symbols_map):
        for name, ticker_sym in symbols_map.items():
            try:
                t = yf.Ticker(ticker_sym)
                info = t.fast_info

                # Check for None
                price = info.last_price
                prev = info.previous_close

                if price is not None and prev is not None:
                    change = price - prev
                    pct = (change / prev) * 100 if prev != 0 else 0.0

                    self._update_cache(region, name, price, change, pct)
                else:
                    logger.warning(f"YF No Data for {name}")

            except Exception as e:
                logger.warning(f"YFinance Failed for {name}: {e}")

    def _update_cache(self, region, name, price, change, pct):
        with self.lock:
            if region not in self.data: self.data[region] = {}
            self.data[region][name] = {
                "price": price,
                "change": change,
                "pct": pct
            }

    def get_data(self):
        with self.lock:
            return self.data

global_market_scraper = GlobalMarketScraper()
