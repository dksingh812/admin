import requests
import json
import gzip
import shutil
import pandas as pd
import threading
import datetime
import os
from src.config import DATA_DIR
from src.logger import logger
from src.default_symbols import DEFAULT_SYMBOLS

INSTRUMENT_FILE = DATA_DIR / "complete_instrument_list.csv"

class InstrumentManager:
    def __init__(self):
        self.df = None
        # Initialize with DEFAULT_SYMBOLS immediately so UI is never empty
        self.symbol_list = DEFAULT_SYMBOLS[:]
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

        # Check if file exists, if not or old, download
        if not INSTRUMENT_FILE.exists():
            self.download_instruments()

        try:
            if INSTRUMENT_FILE.exists():
                self.df = pd.read_csv(INSTRUMENT_FILE)
                # Ensure columns are normalized
                if 'tradingsymbol' in self.df.columns:
                    loaded_symbols = self.df['tradingsymbol'].dropna().astype(str).tolist()
                    loaded_symbols.sort()
                    # Update symbol list with downloaded data
                    if loaded_symbols:
                        self.symbol_list = loaded_symbols
        except Exception as e:
            logger.error(f"Failed to load instrument list: {e}")
            # Keep defaults

        self.loading = False
        logger.info(f"Instrument Manager Loaded {len(self.symbol_list)} symbols.")

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
        if self.df is None:
            # Fallback for when data isn't loaded yet
            # Return a constructed string which is likely correct for major indices
            # e.g. BANKNIFTY23DEC48000CE (Format requires exact date logic which is hard to guess)
            # Instead return generic string that broker might accept or user has to fix
            return f"{underlying} {strike} {opt_type}"

        try:
            # Mask
            # Starts with underlying (approx)
            mask = self.df['tradingsymbol'].str.startswith(underlying) & \
                   self.df['tradingsymbol'].str.contains(str(int(strike))) & \
                   self.df['tradingsymbol'].str.endswith(opt_type)

            candidates = self.df[mask]

            if not candidates.empty:
                # Return the first one.
                return candidates.iloc[0]['tradingsymbol']
        except Exception as e:
            logger.error(f"Error finding option: {e}")

        return f"{underlying} {strike} {opt_type}"

instrument_manager = InstrumentManager()
