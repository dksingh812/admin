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

    def register_strategy(self, strategy):
        if strategy not in self.strategies:
            self.strategies.append(strategy)

    def subscribe(self, symbols):
        self.subscribed_symbols = symbols
        # Initialize cache
        for s in symbols:
            self.latest_data[s] = {"ltp": 0.0, "change": 0.0, "symbol": s}

    def start_polling(self, interval=1.0):
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self.thread.start()

    def _poll_loop(self, interval):
        logger.info("Data Engine: Started Polling")
        while self.running:
            for symbol in self.subscribed_symbols:
                ltp = self.broker.get_ltp(symbol)

                # Update Cache
                tick_data = {
                    "symbol": symbol,
                    "ltp": ltp,
                    "change": 0.0 # Placeholder
                }
                self.latest_data[symbol] = tick_data

                # Notify Strategies
                for strategy in self.strategies:
                    # Basic logic: If strategy cares about this symbol (or all), notify it
                    # Here we send all ticks to all strategies for simplicity
                    if strategy.active:
                        try:
                            strategy.on_tick(tick_data)
                        except Exception as e:
                            logger.error(f"Error in strategy {strategy.name}: {e}")

            time.sleep(interval)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Data Engine: Stopped")

    def get_latest_tick(self, symbol):
        return self.latest_data.get(symbol, {})
