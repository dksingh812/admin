import os
import json
import logging
from pathlib import Path

# Default Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
LOGS_DIR = BASE_DIR / "Logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_key": "",
    "api_secret": "",
    "redirect_uri": "http://127.0.0.1:5000/callback",
    "trading_mode": "PAPER",
    "data_path": str(DATA_DIR),
    "risk": {
        "max_loss_per_trade": 1000,
        "max_loss_per_day": 5000,
        "max_open_trades": 3,
        "global_stop_loss_enabled": True
    },
    "strategies": {
        "sma_rsi": {
            "sma_period": 14,
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "timeframe": "1min"
        }
    }
}

def load_config():
    """Loads configuration from JSON file or returns defaults."""
    # Lazy import to avoid circular dependency
    from src.security import decrypt_value

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

            # Decrypt Sensitive Fields
            if "api_secret" in config:
                config["api_secret"] = decrypt_value(config["api_secret"])

            # Merge with defaults
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """Saves configuration to JSON file."""
    from src.security import encrypt_value

    # Create a copy to encrypt
    safe_config = config.copy()
    if "api_secret" in safe_config:
        safe_config["api_secret"] = encrypt_value(safe_config["api_secret"])

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(safe_config, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving config: {e}")
        return False
