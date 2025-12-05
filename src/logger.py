import logging
import os
from datetime import datetime
from src.config import LOGS_DIR

def setup_logger():
    """Sets up the application logger."""

    log_filename = datetime.now().strftime("algotech_%Y-%m-%d.log")
    log_path = LOGS_DIR / log_filename

    logger = logging.getLogger("AlgoTech")
    logger.setLevel(logging.INFO)

    # File Handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
