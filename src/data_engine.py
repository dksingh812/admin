import datetime
import time
import threading
import random
from src.logger import logger
from src.fii_dii_scraper import fetch_fii_dii_data

class DataEngine:
    def __init__(self, broker, strategies=None):
        self.broker = broker
        self.strategies = strategies if strategies else []
        self.subscribed_symbols = []
        self.latest_data = {} # {symbol: {ltp: x, change: y, pct: z}}
        self.fii_dii_data = {} # Store FII/DII data
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        self.poll_interval = 1.0 # Default 1s
        self.fii_dii_last_update = 0

    def set_interval(self, interval):
        self.poll_interval = interval

    def register_strategy(self, strategy):
        if strategy not in self.strategies:
            self.strategies.append(strategy)

    def subscribe(self, symbols):
        with self.lock:
            self.subscribed_symbols = list(set(self.subscribed_symbols + symbols))
            for s in symbols:
                if s not in self.latest_data:
                    self.latest_data[s] = {"ltp": 0.0, "change": 0.0, "pct_change": 0.0, "symbol": s}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("Data Engine: Started")

    def _poll_loop(self):
        # Initial Fetch
        self._update_real_fii_dii()

        while self.running:
            start_time = time.time()

            # 1. Update FII/DII Real every 5 minutes (300s)
            if time.time() - self.fii_dii_last_update > 300:
                # Run in separate thread to avoid blocking main loop
                threading.Thread(target=self._update_real_fii_dii, daemon=True).start()
                self.fii_dii_last_update = time.time()

            # 2. Poll Market Data
            current_symbols = []
            with self.lock:
                current_symbols = self.subscribed_symbols[:]

            for symbol in current_symbols:
                # Returns dict {ltp, change, pct_change}
                quote = self.broker.get_ltp(symbol)

                # Check for float fallback
                if isinstance(quote, float):
                    quote = {"ltp": quote, "change": 0.0, "pct_change": 0.0}

                tick_data = {
                    "symbol": symbol,
                    "ltp": quote.get("ltp", 0.0),
                    "change": quote.get("change", 0.0),
                    "pct_change": quote.get("pct_change", 0.0)
                }

                with self.lock:
                    self.latest_data[symbol] = tick_data

                # Notify Strategies
                for strategy in self.strategies:
                    if strategy.active:
                        try:
                            strategy.on_tick(tick_data)
                        except Exception as e:
                            logger.error(f"Error in strategy {strategy.name}: {e}")

            elapsed = time.time() - start_time
            sleep_time = max(0.0, self.poll_interval - elapsed)
            time.sleep(sleep_time)

    def _update_real_fii_dii(self):
        try:
            # { "fii": {buy, sell, net}, "dii": {...}, "date": ... }
            raw_data = fetch_fii_dii_data()

            # Format for UI compatibility
            # Old UI expects: fii_net_crores, dii_net_crores

            formatted = {
                "fii": f"₹{raw_data['fii'].get('net', 0)} Cr",
                "dii": f"₹{raw_data['dii'].get('net', 0)} Cr",
                "details": raw_data, # Store full details for tooltip/future use
                "last_updated": datetime.datetime.now().strftime("%H:%M")
            }

            with self.lock:
                self.fii_dii_data = formatted
                # Sanitize for logging (Windows CP1252 doesn't like ₹)
                log_fii = formatted['fii'].replace('₹', 'Rs. ')
                log_dii = formatted['dii'].replace('₹', 'Rs. ')
                logger.info(f"FII/DII Updated: FII {log_fii}, DII {log_dii}")

        except Exception as e:
            logger.error(f"Failed to update FII/DII: {e}")

    def get_fii_dii(self):
        with self.lock:
            if not self.fii_dii_data:
                 return {"fii": "Loading...", "dii": "Loading...", "details": {}}
            return self.fii_dii_data

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Data Engine: Stopped")

    def get_latest_tick(self, symbol):
        with self.lock:
            return self.latest_data.get(symbol, {})
