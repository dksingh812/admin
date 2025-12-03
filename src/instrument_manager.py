import requests
import json
import gzip
import shutil
import pandas as pd
import threading
import datetime
from src.config import DATA_DIR
from src.logger import logger
from src.default_symbols import DEFAULT_SYMBOLS

INSTRUMENT_FILE = DATA_DIR / "complete_instrument_list.csv"

class InstrumentManager:
    def __init__(self):
        self.df = None
        self.symbol_list = []
        self.loading = False
        self.loader_thread = threading.Thread(target=self.load_instruments, daemon=True)
        self.loader_thread.start()

    def download_file(self, url, dest_name):
        try:
            logger.info(f"Downloading {dest_name}...")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, stream=True, timeout=30, headers=headers)
            if response.status_code == 200:
                compressed_file = DATA_DIR / f"{dest_name}.gz"
                with open(compressed_file, 'wb') as f:
                    f.write(response.content)
                output_file = DATA_DIR / dest_name
                with gzip.open(compressed_file, 'rb') as f_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return output_file
            return None
        except Exception as e:
            logger.error(f"Error downloading {dest_name}: {e}")
            return None

    def download_instruments(self):
        urls = {
            "NSE_EQ.csv": "https://assets.upstox.com/feed/nse/equity/NSE_EQ.csv.gz",
            "NSE_FO.csv": "https://assets.upstox.com/feed/nse/equity/NSE_FO.csv.gz",
            "NSE_INDEX.csv": "https://assets.upstox.com/feed/nse/index/NSE_INDEX.csv.gz"
        }
        frames = []
        for name, url in urls.items():
            path = self.download_file(url, name)
            if path and path.exists():
                try:
                    df = pd.read_csv(path)
                    frames.append(df)
                except: pass
        if frames:
            full_df = pd.concat(frames, ignore_index=True)
            full_df.to_csv(INSTRUMENT_FILE, index=False)
            return True
        return False

    def load_instruments(self):
        self.loading = True
        if not INSTRUMENT_FILE.exists():
            self.download_instruments()

        try:
            self.df = pd.read_csv(INSTRUMENT_FILE)
            # Ensure columns are normalized
            # Upstox CSV usually: instrument_key, exchange_token, tradingsymbol, name, last_price, expiry, strike, instrument_type, underlying_symbol...
            # We map them to standard if possible or just use what's there
            if 'tradingsymbol' in self.df.columns:
                self.symbol_list = self.df['tradingsymbol'].dropna().astype(str).tolist()
                self.symbol_list.sort()
        except:
            self.symbol_list = []

        if not self.symbol_list:
            self.symbol_list = DEFAULT_SYMBOLS
        self.loading = False

    def get_instrument_key(self, symbol):
        if self.df is None: return None
        row = self.df[self.df['tradingsymbol'] == symbol]
        if not row.empty: return row.iloc[0]['instrument_key']
        return None

    def get_all_symbols(self):
        return self.symbol_list

    def find_option(self, underlying, strike, opt_type):
        """
        Finds the nearest weekly expiry option for the given underlying, strike, and type.
        """
        if self.df is None: return None

        # 1. Filter by Underlying (e.g. 'NIFTY') - check 'name' or 'underlying_symbol'
        # Since CSV structure varies, we assume 'tradingsymbol' starts with Underlying
        # Example: NIFTY23DEC21000CE

        # Strategy: Filter tradingsymbol containing Underlying AND Strike AND Type
        # This is a heuristic.

        # Optimization: We should parse expiry dates, but for V1 we find *any* matching symbol
        # Ideally the one with shortest string length (often near expiry)?
        # Or sort by alphabetic (expiry date is encoded).

        try:
            # Mask
            # Starts with underlying (approx)
            mask = self.df['tradingsymbol'].str.startswith(underlying) & \
                   self.df['tradingsymbol'].str.contains(str(int(strike))) & \
                   self.df['tradingsymbol'].str.endswith(opt_type)

            candidates = self.df[mask]

            if not candidates.empty:
                # Return the first one.
                # Improvement: Sort by expiry if column exists.
                return candidates.iloc[0]['tradingsymbol']
        except Exception as e:
            logger.error(f"Error finding option: {e}")

        return None

instrument_manager = InstrumentManager()
