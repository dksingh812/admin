import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import messagebox

def handle_crash(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open("crash_log.txt", "w") as f:
        f.write(error_msg)
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Application Crash", f"Error saved to 'crash_log.txt'.\n\n{exc_value}")
        root.destroy()
    except:
        pass
    print("CRITICAL ERROR: " + str(exc_value))
    sys.exit(1)

sys.excepthook = handle_crash

try:
    from src.config import load_config
    from src.logger import logger
    from src.mock_broker import MockBroker
    from src.data_engine import DataEngine
    from src.risk_engine import RiskEngine
    from src.ui.main_app import MainApp
    from src.strategies.sma_rsi import SMARSIStrategy
    from src.global_market_scraper import global_market_scraper
except ImportError as e:
    handle_crash(ImportError, e, sys.exc_info()[2])

def main():
    logger.info("Starting AlgoTech Trading Engine...")

    config = load_config()
    broker = MockBroker()

    data_engine = DataEngine(broker)
    risk_engine = RiskEngine(config, broker)
    broker.set_risk_engine(risk_engine)

    context = {
        "config": config,
        "broker": broker,
        "data_engine": data_engine,
        "risk_engine": risk_engine,
        "strategies": []
    }

    # Start Global Scraper (Background)
    global_market_scraper.start(interval=30) # Refresh every 30s

    # Subscribe to Major Indian Indices
    indices = ["NIFTY 50", "BANKNIFTY", "FINNIFTY", "SENSEX", "INDIA VIX"]
    data_engine.subscribe(indices)
    data_engine.set_interval(1.0)
    data_engine.start()

    # Initialize Default Strategy
    strategy = SMARSIStrategy(broker, config["strategies"]["sma_rsi"])
    context["strategies"].append(strategy)
    data_engine.register_strategy(strategy)

    app = MainApp(context)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    finally:
        logger.info("Shutting down...")
        data_engine.stop()
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        handle_crash(type(e), e, sys.exc_info()[2])
