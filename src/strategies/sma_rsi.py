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
        self.active_positions = [] # Track open legs: {symbol, side, qty, entry, sl, tgt, trail, high}

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
        self.active_positions = [] # Clear on start
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
        try:
            l_type = leg_config[0]
            l_strike = leg_config[1]
        except: return None

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
            # Simple cash trade logic
            return

        logger.info(f"Executing {len(self.legs)} legs for signal {signal} at LTP {ltp}")

        for leg in self.legs:
            # (Type, Strike, Action, Qty, Tgt, SL, Trail, Buf)
            try:
                l_type, l_strike, l_action, l_qty, l_tgt, l_sl, l_trail, l_buf = leg
                l_qty = int(l_qty)
                l_tgt = float(l_tgt)
                l_sl = float(l_sl)
                l_trail = float(l_trail)
                l_buf = float(l_buf)
            except ValueError:
                continue

            symbol = self.resolve_leg_symbol(self.target_symbol, ltp, leg)
            if not symbol: continue

            final_side = l_action
            if signal == "SELL":
                final_side = "SELL" if l_action == "BUY" else "BUY"

            # Place Entry
            order_id = self.broker.place_order(symbol, l_qty, final_side)

            if order_id:
                # Track Position for Risk Management
                # We assume fill price ~ current LTP for simplicity (Real app needs Order Update WebSocket)
                entry_price = self.get_latest_price(symbol, ltp)

                # Calculate Absolute Levels
                sl_price = 0.0
                tgt_price = 0.0

                if final_side == "BUY":
                    sl_price = entry_price * (1 - (l_sl / 100))
                    tgt_price = entry_price * (1 + (l_tgt / 100))
                else: # SELL
                    sl_price = entry_price * (1 + (l_sl / 100))
                    tgt_price = entry_price * (1 - (l_tgt / 100))

                position = {
                    "symbol": symbol,
                    "side": final_side,
                    "qty": l_qty,
                    "entry": entry_price,
                    "sl": sl_price,
                    "tgt": tgt_price,
                    "trail_pct": l_trail,
                    "highest_ltp": entry_price, # For trailing
                    "lowest_ltp": entry_price,
                    "status": "OPEN"
                }

                self.active_positions.append(position)
                logger.info(f"Tracking Position: {symbol} Entry:{entry_price} SL:{sl_price:.2f} Tgt:{tgt_price:.2f}")

    def get_latest_price(self, symbol, default_price):
        # Helper to get price from broker/history if available
        # In this context, we might not have it in history yet for the Option symbol
        return default_price

    def manage_risk(self, tick_data):
        # Iterate all active positions and check SL/Target
        symbol = tick_data.get("symbol")
        ltp = tick_data.get("ltp")

        for pos in self.active_positions:
            if pos["status"] != "OPEN": continue
            if pos["symbol"] != symbol: continue

            side = pos["side"]
            sl = pos["sl"]
            tgt = pos["tgt"]
            trail_pct = pos["trail_pct"]

            # Update High/Low for Trailing
            if ltp > pos["highest_ltp"]: pos["highest_ltp"] = ltp
            if ltp < pos["lowest_ltp"]: pos["lowest_ltp"] = ltp

            # Trailing Logic
            if trail_pct > 0:
                if side == "BUY":
                    # If price moved up, move SL up
                    # Simple trail: Keep SL at X% distance from High
                    new_sl = pos["highest_ltp"] * (1 - (trail_pct/100))
                    if new_sl > sl:
                        pos["sl"] = new_sl
                        logger.info(f"Trailing SL Updated for {symbol}: {new_sl:.2f}")
                else: # SELL
                    new_sl = pos["lowest_ltp"] * (1 + (trail_pct/100))
                    if new_sl < sl:
                        pos["sl"] = new_sl
                        logger.info(f"Trailing SL Updated for {symbol}: {new_sl:.2f}")

            # Check Exit
            exit_triggered = False
            reason = ""

            if side == "BUY":
                if ltp <= pos["sl"]:
                    exit_triggered = True; reason = "STOP LOSS"
                elif ltp >= tgt and tgt > 0:
                    exit_triggered = True; reason = "TARGET"
            else: # SELL
                if ltp >= pos["sl"]:
                    exit_triggered = True; reason = "STOP LOSS"
                elif ltp <= tgt and tgt > 0:
                    exit_triggered = True; reason = "TARGET"

            if exit_triggered:
                logger.info(f"Exiting {symbol}: {reason} at {ltp}")
                self.broker.place_order(symbol, pos["qty"], "SELL" if side == "BUY" else "BUY")
                pos["status"] = "CLOSED"

    def on_tick(self, tick_data):
        if not self.active: return

        # 1. Manage Existing Risk
        self.manage_risk(tick_data)

        # 2. Check Entry Signal (Only for Underlying)
        symbol = tick_data.get("symbol")
        if self.target_symbol and symbol != self.target_symbol: return

        price = tick_data.get("ltp")
        if symbol not in self.histories: self.histories[symbol] = []

        history = self.histories[symbol]
        history.append(price)
        if len(history) > 200: history.pop(0)
        if len(history) < max(self.sma_period, self.rsi_period) + 2: return

        # Throttle Entry: Don't enter if we already have open positions?
        # For this logic, we allow multiple entries or limit via Max Trades in RiskEngine
        # But to avoid spamming, we should check active_positions count?
        # User wants "Signal based", so we respect signal.

        sma = sum(history[-self.sma_period:]) / self.sma_period
        rsi = self.calculate_rsi(history, self.rsi_period)

        # logger.info(f"{symbol}: {price}, SMA: {sma:.1f}, RSI: {rsi:.1f}")

        # Signal Logic
        # Simple debounce: Don't trade every tick.
        # We need a state "in_trade" or checking last signal time.
        # For V1 we just place order. RiskEngine max_trades handles the limit.

        if price > sma and rsi < self.rsi_oversold:
            # logger.info("Signal: BULLISH ENTRY")
            self.execute_legs("BUY", price)

        elif price < sma and rsi > self.rsi_overbought:
            # logger.info("Signal: BEARISH ENTRY")
            self.execute_legs("SELL", price)
