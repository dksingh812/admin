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

        # Need Volume for the requested strategy
        volume = tick_data.get("volume", 0) # DataEngine might not pass volume yet?
        # Mocking volume if missing for stability, but ideally DataEngine passes it.
        # Check DataEngine updates later.

        if symbol not in self.histories: self.histories[symbol] = {"close": [], "volume": []}

        h = self.histories[symbol]
        h["close"].append(price)
        h["volume"].append(volume)

        if len(h["close"]) > 500:
            h["close"].pop(0)
            h["volume"].pop(0)

        # 2. Manage Risk (Existing Logic)
        self.manage_risk(tick_data)

        # 3. Check Entry Conditions
        if len(h["close"]) < self.min_history: return

        # Convert to DataFrame
        df = pd.DataFrame({
            "close": h["close"],
            "volume": h["volume"]
        })

        if self.check_entry(df):
            self.execute_legs("BUY", price)

    def check_entry(self, df):
        # Evaluate all conditions (AND logic)
        for cond in self.entry_conditions:
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
        # Parse Constant Value
        try:
            return float(name)
        except ValueError:
            pass

        series = df['close']
        period = int(params.get("period", 14))

        if name == "LTP": return series.iloc[-1]
        if name == "SMA": return Indicators.sma(series, period).iloc[-1]
        if name == "EMA": return Indicators.ema(series, period).iloc[-1]
        if name == "RSI": return Indicators.rsi(series, period).iloc[-1]

        # New: Volume Support
        if name == "Volume": return df['volume'].iloc[-1]
        if name == "VolMA": return Indicators.sma(df['volume'], period).iloc[-1]

        # Advanced Indicators Warning
        if name in ["VWAP", "SuperTrend", "Bollinger H", "Bollinger L"]:
            logger.warning(f"Indicator '{name}' requires OHLCV data which is not fully supported. Returning 0.0.")
            return 0.0

        return 0.0
