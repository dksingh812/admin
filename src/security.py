import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.logger import logger
from src.config import DATA_DIR

KEY_FILE = DATA_DIR / ".secret.key"

def load_or_generate_key():
    """Loads existing key or generates a new one based on a machine-local salt."""
    # Ideally, we would ask the user for a master password.
    # Since we need auto-login, we'll generate a key and store it.
    # To make it slightly harder to steal, we could obfuscate it, but true security needs user input.
    # For this implementation, we stick to Fernet key generation.

    if KEY_FILE.exists():
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        # Hide the file on Windows
        try:
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(KEY_FILE), 2)
        except:
            pass
        return key

cipher_suite = Fernet(load_or_generate_key())

def encrypt_value(text):
    if not text:
        return ""
    try:
        return cipher_suite.encrypt(text.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return text

def decrypt_value(text):
    if not text:
        return ""
    try:
        return cipher_suite.decrypt(text.encode()).decode()
    except Exception as e:
        # If decryption fails (e.g., plain text or wrong key), return original
        logger.warning(f"Decryption failed, assuming plain text or empty: {e}")
        return text
