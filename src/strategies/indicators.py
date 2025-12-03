import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def sma(series: pd.Series, length: int):
        return series.rolling(window=length).mean()

    @staticmethod
    def ema(series: pd.Series, length: int):
        return series.ewm(span=length, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, length: int):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()

        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        rs = rs.fillna(0) # Should be refined, but sufficient for simple RSI

        # Standard RMA (Wilder's Smoothing) approach is better for RSI, but standard rolling mean is often used in simplified versions.
        # Let's implement Wilder's Smoothing for better accuracy if possible, otherwise stick to simple rolling.
        # For compatibility and simplicity, using simple rolling mean first.
        # A more accurate Wilder's implementation:

        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)

        ma_up = up.ewm(com=length - 1, adjust=True, min_periods=length).mean()
        ma_down = down.ewm(com=length - 1, adjust=True, min_periods=length).mean()

        rs = ma_up / ma_down
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        fast_ema = series.ewm(span=fast, adjust=False).mean()
        slow_ema = series.ewm(span=slow, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        hist = macd_line - signal_line

        # Return DataFrame to match pandas_ta style slightly, or just the main line?
        # The Strategy Builder expects a Series (mostly).
        # But MACD returns 3 things.
        # Let's return the MACD line primarily, but if the caller needs Signal/Hist, we might need a different approach.
        # For the Strategy Builder generic condition checker (e.g. MACD > 0), returning the MACD line is standard.
        # If user wants "MACD Signal", they might need to select that.
        # For now, return a DataFrame so the builder can pick columns if we enhance it later,
        # but the BuilderStrategy currently expects a single float/series value from calculate_indicator.
        # Let's return the MACD line for now to keep it compatible with "val1 > val2".
        return macd_line

    @staticmethod
    def bollinger_bands(series: pd.Series, length: int = 20, std: float = 2.0):
        sma = series.rolling(window=length).mean()
        rstd = series.rolling(window=length).std()
        upper = sma + (std * rstd)
        lower = sma - (std * rstd)
        # Return dataframe with columns usually
        return pd.DataFrame({"BBL": lower, "BBM": sma, "BBU": upper})

    @staticmethod
    def vwap(df: pd.DataFrame):
        # VWAP requires High, Low, Close, Volume
        if not {'high', 'low', 'close', 'volume'}.issubset(df.columns):
            return None

        v = df['volume']
        tp = (df['high'] + df['low'] + df['close']) / 3
        return (tp * v).cumsum() / v.cumsum()

    @staticmethod
    def supertrend(df: pd.DataFrame, length: int = 7, multiplier: float = 3.0):
        if not {'high', 'low', 'close'}.issubset(df.columns):
            return None

        high = df['high']
        low = df['low']
        close = df['close']

        # ATR Calculation
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/length, adjust=False).mean()

        # Basic Upper/Lower Bands
        hl2 = (high + low) / 2
        basic_upper = hl2 + (multiplier * atr)
        basic_lower = hl2 - (multiplier * atr)

        # Final Bands
        final_upper = basic_upper.copy()
        final_lower = basic_lower.copy()

        # We need to iterate to handle the "previous close" logic for SuperTrend
        # This makes it slow in Python but necessary without Numba/Vectorization tricks.
        # Vectorized implementation is possible but complex.
        # For simplicity in V1 without Numba:

        trend = np.zeros(len(df))
        st = np.zeros(len(df))

        # Arrays for speed
        c = close.values
        fu = final_upper.values
        fl = final_lower.values

        # Initialize
        trend[0] = 1
        st[0] = fl[0]

        for i in range(1, len(df)):
            # Upper Band Logic
            if (fu[i] < fu[i-1]) or (c[i-1] > fu[i-1]):
                fu[i] = fu[i]
            else:
                fu[i] = fu[i-1]

            # Lower Band Logic
            if (fl[i] > fl[i-1]) or (c[i-1] < fl[i-1]):
                fl[i] = fl[i]
            else:
                fl[i] = fl[i-1]

            # Trend Logic
            prev_trend = trend[i-1]
            if prev_trend == 1: # Uptrend
                if c[i] < fl[i-1]:
                    trend[i] = -1
                    st[i] = fu[i]
                else:
                    trend[i] = 1
                    st[i] = fl[i] # Should use current fl? Actually usually max(fl, prev_fl) logic is handled above
                    # Correct SuperTrend uses the finalized bands
            else: # Downtrend
                if c[i] > fu[i-1]:
                    trend[i] = 1
                    st[i] = fl[i]
                else:
                    trend[i] = -1
                    st[i] = fu[i]

        return pd.DataFrame({"SUPERT": st, "SUPERTd": trend}, index=df.index)
