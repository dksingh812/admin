import requests
import json
import gzip
import shutil
import pandas as pd
from src.config import DATA_DIR
from src.logger import logger

INSTRUMENT_FILE = DATA_DIR / "complete_instrument_list.csv"

class InstrumentManager:
    def __init__(self):
        self.df = None
        self.load_instruments()

    def download_instruments(self):
        """Downloads the daily instrument master list from Upstox."""
        url = "https://assets.upstox.com/feed/nse/equity/NSE_EQ.csv.gz" # Simplified, usually we need F&O too
        # For a full engine, we'd need multiple segments (NSE_FO, BSE_EQ, etc.)
        # Here we just fetch NSE Equity as a proof of concept.

        try:
            logger.info("Downloading Instrument Master List...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                compressed_file = DATA_DIR / "instruments.csv.gz"
                with open(compressed_file, 'wb') as f:
                    f.write(response.content)

                with gzip.open(compressed_file, 'rb') as f_in:
                    with open(INSTRUMENT_FILE, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                logger.info("Instrument Master List Updated")
                return True
        except Exception as e:
            logger.error(f"Error downloading instruments: {e}")
            return False

    def load_instruments(self):
        if not INSTRUMENT_FILE.exists():
            self.download_instruments()

        try:
            # We assume CSV has standard columns. Upstox format varies, but usually:
            # instrument_key, exchange_token, tradingsymbol, name, last_price, etc.
            # We will use 'tradingsymbol' and 'instrument_key'
            self.df = pd.read_csv(INSTRUMENT_FILE)
            # Create a lookup dictionary for speed
            # Key: Trading Symbol (e.g. RELIANCE), Value: Instrument Key (e.g. NSE_EQ|INE002A01018)
            # NOTE: Upstox CSV headers might be different, so we need to be careful.
            # Inspecting common format: 'instrument_key', 'tradingsymbol'
        except Exception as e:
            logger.error(f"Error loading instrument file: {e}")

    def get_instrument_key(self, symbol):
        if self.df is None:
            return None

        # Exact match
        row = self.df[self.df['tradingsymbol'] == symbol]
        if not row.empty:
            return row.iloc[0]['instrument_key']
        return None

# Singleton
instrument_manager = InstrumentManager()
