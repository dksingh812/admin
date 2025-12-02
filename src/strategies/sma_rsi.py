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
        self.legs = [] # List of (Type, Strike, Action, Qty)

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
        # leg_config: (Type, StrikeOffset, Action, Qty)
        # Type: CE/PE/FUT
        # Strike: ATM, ATM+100...

        l_type, l_strike, l_action, l_qty = leg_config

        if l_type == "FUT":
            # Simple fuzzy search for Future
            return f"{underlying} FUT" # Placeholder, ideally find near month

        # Option Logic
        # 1. Calculate Strike
        base = 100
        if "NIFTY" in underlying: base = 50
        if "BANKNIFTY" in underlying: base = 100

        # Round LTP to nearest base
        atm = round(ltp / base) * base

        # Parse Offset
        offset = 0
        if "+" in l_strike: offset = int(l_strike.split("+")[1])
        if "-" in l_strike: offset = -int(l_strike.split("-")[1])

        target_strike = atm + offset

        # 2. Find Symbol in Instrument Manager
        # We need a method in Instrument Manager to find option by (Name, Strike, Type, Expiry)
        # For now, we construct a likely symbol name or search
        # Upstox Format: NIFTY23DEC21000CE
        # We'll try to find it in the loaded DF if possible

        found = instrument_manager.find_option(underlying, target_strike, l_type)
        return found if found else f"{underlying} {target_strike} {l_type}"

    def execute_legs(self, signal, ltp):
        if not self.legs:
            # Trade Underlying directly (Cash)
            self.broker.place_order(self.target_symbol, 1, signal)
            return

        logger.info(f"Executing {len(self.legs)} legs for signal {signal} at LTP {ltp}")

        for leg in self.legs:
            # leg: (Type, Strike, Action, Qty)
            l_type, l_strike, l_action, l_qty = leg

            # Resolve Symbol
            symbol = self.resolve_leg_symbol(self.target_symbol, ltp, leg)
            if not symbol:
                logger.error("Could not resolve option symbol")
                continue

            # Determine Buy/Sell based on Signal AND Leg Action
            # If Signal is BUY (Entry), we follow Leg Action.
            # If Signal is SELL (Exit), we invert Leg Action?
            # Or is Signal purely Directional?
            # Assuming Signal BUY = Bullish Entry.
            # If Leg is "BUY CE", we Buy. If Leg is "SELL PE", we Sell.

            # Simplified: Strategy triggers ENTRY. We execute leg actions.
            # If Strategy triggers EXIT, we inverse.

            final_side = l_action # Default to config
            if signal == "SELL": # Exit signal
                final_side = "SELL" if l_action == "BUY" else "BUY"

            qty = int(l_qty)
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
            logger.info("Signal: BEARISH ENTRY") # Or Exit?
            # For simplicity, if we are Long, we Exit. If we are flat, we Short?
            # Here we just execute the "Sell" logic of legs
            self.execute_legs("SELL", price)
