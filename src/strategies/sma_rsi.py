from abc import ABC, abstractmethod
import pandas as pd
from src.logger import logger

class Strategy(ABC):
    def __init__(self, name, broker, config):
        self.name = name
        self.broker = broker
        self.config = config
        self.active = False
        self.target_symbol = None # Symbol to trade

    def set_symbol(self, symbol):
        self.target_symbol = symbol

    @abstractmethod
    def on_tick(self, tick_data):
        """Called whenever new market data arrives."""
        pass

    def start(self):
        if not self.target_symbol:
            logger.error(f"Cannot start {self.name}: No symbol selected.")
            return False
        self.active = True
        logger.info(f"Strategy {self.name} Started on {self.target_symbol}")
        return True

    def stop(self):
        self.active = False
        logger.info(f"Strategy {self.name} Stopped")

class SMARSIStrategy(Strategy):
    def __init__(self, broker, config):
        super().__init__("SMA_RSI", broker, config)
        # Dictionary to hold history per symbol: { 'RELIANCE': [p1, p2...], 'NIFTY': [...] }
        self.histories = {}
        self.sma_period = config.get("sma_period", 14)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_overbought = config.get("rsi_overbought", 70)
        self.rsi_oversold = config.get("rsi_oversold", 30)

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0

        series = pd.Series(prices)
        delta = series.diff().dropna()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Handle division by zero
        rs = gain / loss.replace(0, 0.000001)
        return 100 - (100 / (1 + rs)).iloc[-1]

    def on_tick(self, tick_data):
        if not self.active:
            return

        symbol = tick_data.get("symbol")

        # Only process if this is the target symbol (Single Symbol Strategy for now)
        if self.target_symbol and symbol != self.target_symbol:
            return

        price = tick_data.get("ltp")

        if symbol not in self.histories:
            self.histories[symbol] = []

        history = self.histories[symbol]
        history.append(price)

        # Keep history manageable
        if len(history) > 200:
            history.pop(0)

        if len(history) < max(self.sma_period, self.rsi_period) + 2:
            return

        # Technical Analysis
        sma = sum(history[-self.sma_period:]) / self.sma_period
        rsi = self.calculate_rsi(history, self.rsi_period)

        logger.info(f"{symbol} - Price: {price}, SMA: {sma:.2f}, RSI: {rsi:.2f}")

        # Signal Logic
        if price > sma and rsi < self.rsi_oversold:
            logger.info(f"SIGNAL: BUY {symbol} @ {price}")
            self.broker.place_order(symbol, 1, "BUY")

        elif price < sma and rsi > self.rsi_overbought:
            logger.info(f"SIGNAL: SELL {symbol} @ {price}")
            self.broker.place_order(symbol, 1, "SELL")
