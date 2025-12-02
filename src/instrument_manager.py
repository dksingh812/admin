import requests
import json
import gzip
import shutil
import pandas as pd
import threading
from src.config import DATA_DIR
from src.logger import logger
from src.default_symbols import DEFAULT_SYMBOLS

INSTRUMENT_FILE = DATA_DIR / "complete_instrument_list.csv"

class InstrumentManager:
    def __init__(self):
        self.df = None
        self.symbol_list = []
        self.loading = False
        # Start loading in background
        self.loader_thread = threading.Thread(target=self.load_instruments, daemon=True)
        self.loader_thread.start()

    def download_file(self, url, dest_name):
        try:
            logger.info(f"Downloading {dest_name}...")
            # Set timeout to prevent hanging forever. User-Agent helps avoid 403 sometimes.
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
        self.loading = True
        success = False
        if not INSTRUMENT_FILE.exists():
            success = self.download_instruments()
        else:
            success = True

        if success:
            try:
                logger.info("Loading Instrument CSV into memory...")
                self.df = pd.read_csv(INSTRUMENT_FILE)
                if 'tradingsymbol' in self.df.columns:
                    self.symbol_list = self.df['tradingsymbol'].dropna().astype(str).tolist()
                    self.symbol_list.sort()
                    logger.info(f"Loaded {len(self.symbol_list)} instruments.")
                else:
                    self.symbol_list = []
            except Exception as e:
                logger.error(f"Error loading instrument file: {e}")
                self.symbol_list = []

        # Fallback if list is empty (Download failed)
        if not self.symbol_list:
            logger.warning("Using Default Fallback Symbol List")
            self.symbol_list = DEFAULT_SYMBOLS

        self.loading = False

    def get_instrument_key(self, symbol):
        if self.df is None:
            return None

        row = self.df[self.df['tradingsymbol'] == symbol]
        if not row.empty:
            return row.iloc[0]['instrument_key']
        return None

    def get_all_symbols(self):
        return self.symbol_list

# Singleton
instrument_manager = InstrumentManager()
