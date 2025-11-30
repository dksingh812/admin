import time
import threading
from src.logger import logger

class DataEngine:
    def __init__(self, broker, strategies=None):
        self.broker = broker
        self.strategies = strategies if strategies else []
        self.subscribed_symbols = []
        self.latest_data = {} # {symbol: {ltp: x, change: y}}
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Performance Tuning
        self.poll_interval = 0.5 # Default to 0.5s to be safe with rate limits

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
                    self.latest_data[s] = {"ltp": 0.0, "change": 0.0, "symbol": s}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("Data Engine: Started")

    def _poll_loop(self):
        while self.running:
            start_time = time.time()

            # 1. Fetch Data
            # Optimization: Broker should support fetching multiple LTPs in one call if possible
            # For now we loop (MockBroker is fast, UpstoxBroker needs bulk fetch impl)

            current_symbols = []
            with self.lock:
                current_symbols = self.subscribed_symbols[:]

            # We assume broker has a bulk fetch or we loop
            # If broker supports websocket, this loop might just read from a queue
            # But here we implement Polling as the robust baseline

            for symbol in current_symbols:
                ltp = self.broker.get_ltp(symbol)

                tick_data = {
                    "symbol": symbol,
                    "ltp": ltp,
                    "change": 0.0
                }

                with self.lock:
                    self.latest_data[symbol] = tick_data

                # Notify Strategies
                for strategy in self.strategies:
                    if strategy.active:
                        try:
                            # Run strategy on_tick in a separate thread or non-blocking?
                            # For now, blocking is safer to ensure order
                            strategy.on_tick(tick_data)
                        except Exception as e:
                            logger.error(f"Error in strategy {strategy.name}: {e}")

            # Sleep remainder of interval
            elapsed = time.time() - start_time
            sleep_time = max(0.0, self.poll_interval - elapsed)
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Data Engine: Stopped")

    def get_latest_tick(self, symbol):
        with self.lock:
            return self.latest_data.get(symbol, {})
