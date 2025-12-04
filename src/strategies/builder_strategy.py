from src.strategies.sma_rsi import Strategy
from src.strategies.indicators import Indicators
from src.logger import logger
import pandas as pd

class BuilderStrategy(Strategy):
    def __init__(self, broker, config):
        super().__init__(config.get("name", "CustomStrategy"), broker, config)
        self.entry_conditions = config.get("entry_conditions", [])
        self.exit_conditions = config.get("exit_conditions", [])
        self.legs = config.get("legs", [])
        self.histories = {}
        self.min_history = 200 # Safe default

    def on_tick(self, tick_data):
        if not self.active: return

        symbol = tick_data.get("symbol")
        if self.target_symbol and symbol != self.target_symbol: return

        # 1. Update History
        price = tick_data.get("ltp")
        if symbol not in self.histories: self.histories[symbol] = []
        history = self.histories[symbol]
        history.append(price)
        if len(history) > 500: history.pop(0) # Keep manageable buffer

        # 2. Manage Risk (Existing Logic)
        self.manage_risk(tick_data)

        # 3. Check Entry Conditions
        if len(history) < self.min_history: return

        # Convert to Series for TA
        df = pd.DataFrame({"close": history, "high": history, "low": history}) # Simplified for now, need OHLC for real
        # Note: True OHLC requires a real candle feed. The current tick-based history is an approximation
        # where Close=High=Low=LTP. This works for SMA/RSI but fails for ATR/SuperTrend.
        # Future improvement: Feed actual 1-min candles.

        if self.check_entry(df):
            self.execute_legs("BUY", price)

    def check_entry(self, df):
        # Evaluate all conditions (AND logic)
        for cond in self.entry_conditions:
            # Format: {"ind1": "RSI", "op": ">", "ind2": "60", "params": {...}}
            try:
                val1 = self.calculate_indicator(df, cond["ind1"], cond.get("p1", {}))
                val2 = self.calculate_indicator(df, cond["ind2"], cond.get("p2", {}))

                op = cond["op"]
                if op == ">" and not (val1 > val2): return False
                if op == "<" and not (val1 < val2): return False
                if op == ">=" and not (val1 >= val2): return False
                if op == "<=" and not (val1 <= val2): return False
                if op == "==" and not (val1 == val2): return False
            except Exception as e:
                logger.error(f"Condition Check Error: {e}")
                return False

        return True

    def calculate_indicator(self, df, name, params):
        # Parse Value
        try:
            return float(name)
        except ValueError:
            pass

        series = df['close']

        if name == "LTP": return series.iloc[-1]
        if name == "SMA": return Indicators.sma(series, int(params.get("period", 14))).iloc[-1]
        if name == "EMA": return Indicators.ema(series, int(params.get("period", 14))).iloc[-1]
        if name == "RSI": return Indicators.rsi(series, int(params.get("period", 14))).iloc[-1]

        # Advanced Indicators Warning
        if name in ["VWAP", "SuperTrend", "Bollinger H", "Bollinger L"]:
            logger.warning(f"Indicator '{name}' requires OHLCV data which is not fully supported in this version. Returning 0.0.")
            return 0.0

        return 0.0
