import pandas as pd
import pandas_ta as ta

class Indicators:
    @staticmethod
    def sma(series: pd.Series, length: int):
        return ta.sma(series, length=length)

    @staticmethod
    def ema(series: pd.Series, length: int):
        return ta.ema(series, length=length)

    @staticmethod
    def rsi(series: pd.Series, length: int):
        return ta.rsi(series, length=length)

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        return ta.macd(series, fast=fast, slow=slow, signal=signal)

    @staticmethod
    def bollinger_bands(series: pd.Series, length: int = 20, std: float = 2.0):
        return ta.bbands(series, length=length, std=std)

    @staticmethod
    def vwap(df: pd.DataFrame):
        # VWAP requires High, Low, Close, Volume
        if not {'high', 'low', 'close', 'volume'}.issubset(df.columns):
            return None
        return ta.vwap(df['high'], df['low'], df['close'], df['volume'])

    @staticmethod
    def supertrend(df: pd.DataFrame, length: int = 7, multiplier: float = 3.0):
        if not {'high', 'low', 'close'}.issubset(df.columns):
            return None
        return ta.supertrend(df['high'], df['low'], df['close'], length=length, multiplier=multiplier)
