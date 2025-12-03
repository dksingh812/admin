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
        self.legs = []
        self.active_positions = []

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
        self.active_positions = []
        logger.info(f"Strategy {self.name} Started on {self.target_symbol}")
        return True

    def stop(self):
        self.active = False
        logger.info(f"Strategy {self.name} Stopped")

    def resolve_leg_symbol(self, underlying, ltp, l_type, l_strike):
        if l_type == "FUT":
            return f"{underlying} FUT"

        base = 100
        if "NIFTY" in underlying: base = 50
        if "BANKNIFTY" in underlying: base = 100

        atm = round(ltp / base) * base

        offset = 0
        # Parse ATM+50 / ATM-50 format
        if "+" in l_strike:
            try: offset = int(l_strike.split("+")[1])
            except: pass
        if "-" in l_strike:
            try: offset = -int(l_strike.split("-")[1])
            except: pass

        target_strike = atm + offset

        # In a real scenario, we need to find the specific Option Symbol (e.g., BANKNIFTY24DEC48000CE)
        # instrument_manager.find_option should do this lookup.
        found = instrument_manager.find_option(underlying, target_strike, l_type)
        return found if found else f"{underlying} {target_strike} {l_type}"

    def execute_legs(self, signal, ltp):
        if not self.legs:
            return

        logger.info(f"Executing {len(self.legs)} legs for signal {signal} at LTP {ltp}")

        for leg in self.legs:
            # New Format: 12 items
            # type, strike, action, qty, tgt, tgt_u, sl, sl_u, trail, trail_u, buf, buf_u
            try:
                l_type, l_strike, l_action, l_qty, l_tgt, u_tgt, l_sl, u_sl, l_trail, u_trail, l_buf, u_buf = leg
                l_qty = int(l_qty)
                l_tgt = float(l_tgt)
                l_sl = float(l_sl)
                l_trail = float(l_trail)
            except ValueError:
                # Handle old format if present
                continue

            symbol = self.resolve_leg_symbol(self.target_symbol, ltp, l_type, l_strike)
            if not symbol: continue

            final_side = l_action
            if signal == "SELL":
                final_side = "SELL" if l_action == "BUY" else "BUY"

            # Place Entry
            order_id = self.broker.place_order(symbol, l_qty, final_side)

            if order_id:
                # Assuming Fill Price = LTP for calculation
                entry_price = ltp # Ideally fetch from order book

                # Calculate SL/Target Logic
                sl_price = 0.0
                tgt_price = 0.0

                # Helper for Points vs %
                def calc_level(price, val, unit, is_stop, is_buy):
                    if val == 0: return 0.0
                    delta = val if unit == "Pts" else (price * val / 100)

                    if is_buy:
                        return price - delta if is_stop else price + delta
                    else:
                        return price + delta if is_stop else price - delta

                sl_price = calc_level(entry_price, l_sl, u_sl, True, final_side == "BUY")
                tgt_price = calc_level(entry_price, l_tgt, u_tgt, False, final_side == "BUY")

                position = {
                    "symbol": symbol,
                    "side": final_side,
                    "qty": l_qty,
                    "entry": entry_price,
                    "sl": sl_price,
                    "tgt": tgt_price,
                    "trail_val": l_trail,
                    "trail_unit": u_trail,
                    "highest_ltp": entry_price,
                    "lowest_ltp": entry_price,
                    "status": "OPEN"
                }

                self.active_positions.append(position)
                logger.info(f"Position: {symbol} | SL: {sl_price:.2f} ({l_sl}{u_sl}) | Tgt: {tgt_price:.2f} ({l_tgt}{u_tgt})")

    def manage_risk(self, tick_data):
        symbol = tick_data.get("symbol")
        ltp = tick_data.get("ltp")

        for pos in self.active_positions:
            if pos["status"] != "OPEN": continue
            if pos["symbol"] != symbol: continue

            side = pos["side"]
            sl = pos["sl"]
            tgt = pos["tgt"]
            trail_val = pos["trail_val"]
            trail_u = pos["trail_unit"]

            # Update High/Low
            if ltp > pos["highest_ltp"]: pos["highest_ltp"] = ltp
            if ltp < pos["lowest_ltp"]: pos["lowest_ltp"] = ltp

            # Trailing Logic
            if trail_val > 0:
                delta = trail_val if trail_u == "Pts" else (pos["entry"] * trail_val / 100)

                if side == "BUY":
                    # SL moves up as High moves up. Distance = High - Delta?
                    # Or Distance = Current SL + Move?
                    # Standard Trailing: Keep SL at (High - Delta)
                    potential_sl = pos["highest_ltp"] - delta
                    if potential_sl > sl:
                        pos["sl"] = potential_sl
                        logger.info(f"Trailing SL Updated for {symbol}: {potential_sl:.2f}")
                else: # SELL
                    potential_sl = pos["lowest_ltp"] + delta
                    if potential_sl < sl:
                        pos["sl"] = potential_sl
                        logger.info(f"Trailing SL Updated for {symbol}: {potential_sl:.2f}")

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

    def on_tick(self, tick_data):
        if not self.active: return
        self.manage_risk(tick_data)

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

        if price > sma and rsi < self.rsi_oversold:
            self.execute_legs("BUY", price)
        elif price < sma and rsi > self.rsi_overbought:
            self.execute_legs("SELL", price)
