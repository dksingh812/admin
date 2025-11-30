from abc import ABC, abstractmethod
import pandas as pd
from src.logger import logger

class Strategy(ABC):
    def __init__(self, name, broker, config):
        self.name = name
        self.broker = broker
        self.config = config
        self.active = False

    @abstractmethod
    def on_tick(self, tick_data):
        """Called whenever new market data arrives."""
        pass

    def start(self):
        self.active = True
        logger.info(f"Strategy {self.name} Started")

    def stop(self):
        self.active = False
        logger.info(f"Strategy {self.name} Stopped")

class SMARSIStrategy(Strategy):
    def __init__(self, broker, config):
        super().__init__("SMA_RSI", broker, config)
        self.history = [] # List of prices
        self.sma_period = config.get("sma_period", 14)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_overbought = config.get("rsi_overbought", 70)
        self.rsi_oversold = config.get("rsi_oversold", 30)

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0 # Default neutral

        series = pd.Series(prices)
        delta = series.diff().dropna()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]

    def on_tick(self, tick_data):
        if not self.active:
            return

        price = tick_data.get("ltp")
        symbol = tick_data.get("symbol")

        self.history.append(price)
        if len(self.history) > 100:
            self.history.pop(0)

        if len(self.history) < max(self.sma_period, self.rsi_period) + 2:
            return

        # Technical Analysis
        sma = sum(self.history[-self.sma_period:]) / self.sma_period
        rsi = self.calculate_rsi(self.history, self.rsi_period)

        logger.info(f"{symbol} - Price: {price}, SMA: {sma:.2f}, RSI: {rsi:.2f}")

        # Signal Logic (Simple Example)
        # Buy if Price > SMA and RSI < 30 (Oversold but trending up?) - Just an example logic
        if price > sma and rsi < self.rsi_oversold:
            logger.info(f"SIGNAL: BUY {symbol} @ {price}")
            self.broker.place_order(symbol, 1, "BUY")

        elif price < sma and rsi > self.rsi_overbought:
            logger.info(f"SIGNAL: SELL {symbol} @ {price}")
            self.broker.place_order(symbol, 1, "SELL")
