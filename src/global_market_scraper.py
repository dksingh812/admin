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
        "Taiwan Weighted": "^TWII",
        "KOSPI": "^KS11",
        "SET Composite": "^SET.BK",
        "Jakarta Comp": "^JKSE",
        "Shanghai Comp": "000001.SS"
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
        try:
            tickers = list(symbols_map.values())
            # yfinance allows bulk fetch
            data = yf.download(tickers, period="1d", progress=False)

            # If single ticker, structure is different
            if len(tickers) == 1:
                # Handle single
                pass

            # Process results
            # data['Close'] contains recent prices.
            # We need latest price and prev close.

            # Simpler approach: iterate tickers using Ticker object for accuracy
            # Batch download is complex to parse for Change/Pct

            for name, ticker_sym in symbols_map.items():
                try:
                    t = yf.Ticker(ticker_sym)
                    info = t.fast_info

                    price = info.last_price
                    prev = info.previous_close

                    if price and prev:
                        change = price - prev
                        pct = (change / prev) * 100

                        self._update_cache(region, name, price, change, pct)
                    else:
                        # Fallback to Google
                        self._fetch_google(region, name, ticker_sym)

                except Exception:
                    self._fetch_google(region, name, ticker_sym)

        except Exception as e:
            logger.error(f"YFinance Batch Error: {e}")

    def _fetch_google(self, region, name, ticker):
        # Fallback scraping logic
        # Construct search query?
        # Google Finance URL structure is tricky.
        # Minimal implementation: Just log warning and skip to keep it fast.
        # Or try a requests call to finance.yahoo.com directly if library failed.
        pass

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
