from abc import ABC, abstractmethod
import pandas as pd
from src.logger import logger
from src.instrument_manager import instrument_manager
import datetime

class Strategy(ABC):
    def __init__(self, name, broker, config):
        self.name = name
        self.broker = broker
        self.config = config
        self.active = False
        self.target_symbol = None
        self.legs = [] # List of (Type, Strike, Action, Qty, Tgt, SL, Trail, Buf)

    def set_symbol(self, symbol):
        self.target_symbol = symbol

    @abstractmethod
    def on_tick(self, tick_data):
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
        rs = gain / loss.replace(0, 0.000001)
        return 100 - (100 / (1 + rs)).iloc[-1]

    def resolve_leg_symbol(self, underlying, ltp, leg_config):
        # leg_config is tuple of 8 items
        l_type = leg_config[0]
        l_strike = leg_config[1]

        if l_type == "FUT":
            return f"{underlying} FUT"

        base = 100
        if "NIFTY" in underlying: base = 50
        if "BANKNIFTY" in underlying: base = 100

        atm = round(ltp / base) * base

        offset = 0
        if "+" in l_strike: offset = int(l_strike.split("+")[1])
        if "-" in l_strike: offset = -int(l_strike.split("-")[1])

        target_strike = atm + offset

        found = instrument_manager.find_option(underlying, target_strike, l_type)
        return found if found else f"{underlying} {target_strike} {l_type}"

    def execute_legs(self, signal, ltp):
        if not self.legs:
            self.broker.place_order(self.target_symbol, 1, signal)
            return

        logger.info(f"Executing {len(self.legs)} legs for signal {signal} at LTP {ltp}")

        for leg in self.legs:
            # Unpack all 8 params
            # (Type, Strike, Action, Qty, Tgt, SL, Trail, Buf)
            try:
                l_type, l_strike, l_action, l_qty, l_tgt, l_sl, l_trail, l_buf = leg
            except ValueError:
                # Fallback for old config if tuple size mismatch
                l_type, l_strike, l_action, l_qty = leg[:4]
                l_tgt, l_sl, l_trail, l_buf = 0, 0, 0, 0

            symbol = self.resolve_leg_symbol(self.target_symbol, ltp, leg)
            if not symbol:
                logger.error("Could not resolve option symbol")
                continue

            final_side = l_action
            if signal == "SELL":
                final_side = "SELL" if l_action == "BUY" else "BUY"

            qty = int(l_qty)

            # Place Order with Metadata
            # Note: broker.place_order currently only takes basics.
            # We log the Risk parameters for now.
            logger.info(f"Leg Order: {final_side} {qty} {symbol} | Tgt: {l_tgt}%, SL: {l_sl}%")
            self.broker.place_order(symbol, qty, final_side)

    def on_tick(self, tick_data):
        if not self.active: return
        symbol = tick_data.get("symbol")
        if self.target_symbol and symbol != self.target_symbol: return

        price = tick_data.get("ltp")
        if symbol not in self.histories: self.histories[symbol] = []

        history = self.histories[symbol]
        history.append(price)
        if len(history) > 200: history.pop(0)
        if len(history) < max(self.sma_period, self.rsi_period) + 2: return

        sma = sum(history[-self.sma_period:]) / self.sma_period
        rsi = self.calculate_rsi(history, self.rsi_period)

        logger.info(f"{symbol}: {price}, SMA: {sma:.1f}, RSI: {rsi:.1f}")

        if price > sma and rsi < self.rsi_oversold:
            logger.info("Signal: BULLISH ENTRY")
            self.execute_legs("BUY", price)

        elif price < sma and rsi > self.rsi_overbought:
            logger.info("Signal: BEARISH ENTRY")
            self.execute_legs("SELL", price)
