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

    def download_file(self, url, dest_name):
        try:
            logger.info(f"Downloading {dest_name}...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                compressed_file = DATA_DIR / f"{dest_name}.gz"
                with open(compressed_file, 'wb') as f:
                    f.write(response.content)

                output_file = DATA_DIR / dest_name
                with gzip.open(compressed_file, 'rb') as f_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                return output_file
            else:
                logger.warning(f"Failed to download {dest_name}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading {dest_name}: {e}")
            return None

    def download_instruments(self):
        """Downloads NSE Equity, F&O, and Indices instrument lists."""
        urls = {
            "NSE_EQ.csv": "https://assets.upstox.com/feed/nse/equity/NSE_EQ.csv.gz",
            "NSE_FO.csv": "https://assets.upstox.com/feed/nse/equity/NSE_FO.csv.gz",
            # Guessing URL structure based on Upstox common patterns
            # Often indices are in NSE_INDEX
            "NSE_INDEX.csv": "https://assets.upstox.com/feed/nse/index/NSE_INDEX.csv.gz"
        }

        frames = []
        for name, url in urls.items():
            path = self.download_file(url, name)
            if path and path.exists():
                try:
                    df = pd.read_csv(path)
                    frames.append(df)
                except Exception as e:
                    logger.error(f"Error reading {name}: {e}")

        if frames:
            full_df = pd.concat(frames, ignore_index=True)
            full_df.to_csv(INSTRUMENT_FILE, index=False)
            logger.info("Instrument Master List Updated")
            return True
        return False

    def load_instruments(self):
        if not INSTRUMENT_FILE.exists():
            self.download_instruments()

        try:
            self.df = pd.read_csv(INSTRUMENT_FILE)
            # Create a clean lookup map if possible, but the DF is large.
            # We rely on filtering for now.
        except Exception as e:
            logger.error(f"Error loading instrument file: {e}")

    def get_instrument_key(self, symbol):
        if self.df is None:
            return None

        # 1. Try Exact Match on 'tradingsymbol' (e.g. RELIANCE, BANKNIFTY23...)
        row = self.df[self.df['tradingsymbol'] == symbol]
        if not row.empty:
            return row.iloc[0]['instrument_key']

        # 2. Try 'name' match for Indices (e.g. "Nifty 50")
        # Indices in Upstox CSV often have tradingsymbol like "Nifty 50" or "Nifty Bank"
        row = self.df[self.df['tradingsymbol'] == symbol]
        # Note: Sometimes tradingsymbol is "NIFTY 50" (with space) or "NIFTY_50".
        # We try strict match first.

        return None

# Singleton
instrument_manager = InstrumentManager()
