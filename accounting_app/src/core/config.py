import os
import sys

if sys.platform == 'win32':
    APP_DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'ParigantavyaAccounting')
else:
    APP_DATA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'ParigantavyaAccounting')

DB_PATH = os.path.join(APP_DATA_DIR, 'accounting.db')
os.makedirs(APP_DATA_DIR, exist_ok=True)

class Config:
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    SECRET_KEY = "dummy_secret_for_now_replace_in_production"
