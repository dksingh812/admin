import os
import pandas as pd
import yfinance as yf
from src.config import DATA_DIR
from src.logger import logger

HISTORICAL_DIR = os.path.join(DATA_DIR, "historical")
os.makedirs(HISTORICAL_DIR, exist_ok=True)

class DataDownloader:
    def __init__(self, broker=None):
        self.broker = broker

    def fetch_and_store(self, symbol, period="1y", interval="1d", source="yfinance"):
        """
        Fetches data and stores it as CSV in Data/historical/{symbol}.csv
        """
        logger.info(f"Fetching data for {symbol} ({period}, {interval}) via {source}...")

        df = None
        if source == "yfinance":
            df = self._fetch_yf(symbol, period, interval)
        elif source == "upstox" and self.broker:
            # Not fully implemented for V1 as Upstox History API is complex
            logger.warning("Upstox History API not linked yet, falling back to yfinance.")
            df = self._fetch_yf(symbol, period, interval)

        if df is not None and not df.empty:
            path = self._get_path(symbol)
            df.to_csv(path)
            logger.info(f"Saved {len(df)} rows to {path}")
            return True, f"Success: {len(df)} rows"
        else:
            return False, "No data found"

    def _fetch_yf(self, symbol, period, interval):
        try:
            # Handle NSE symbols for Yahoo
            yf_symbol = symbol
            if not (symbol.endswith(".NS") or symbol.endswith(".BO") or symbol.startswith("^")):
                # Guess it's NSE equity
                yf_symbol = f"{symbol}.NS"

            # Map interval for yfinance
            # YF supports: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            df = yf.download(yf_symbol, period=period, interval=interval, progress=False)

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            # Standardize Columns
            df.reset_index(inplace=True)
            df.rename(columns={
                "Date": "timestamp", "Datetime": "timestamp",
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            }, inplace=True)

            # Filter valid
            required = ["timestamp", "open", "high", "low", "close"]
            if not all(col in df.columns for col in required):
                # Try lower case
                df.columns = [c.lower() for c in df.columns]

            return df
        except Exception as e:
            logger.error(f"YFinance download error: {e}")
            return None

    def load_data(self, symbol):
        path = self._get_path(symbol)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                return df
            except Exception as e:
                logger.error(f"Failed to load CSV: {e}")
        return None

    def _get_path(self, symbol):
        safe_sym = symbol.replace("^", "").replace(".NS", "")
        return os.path.join(HISTORICAL_DIR, f"{safe_sym}.csv")
