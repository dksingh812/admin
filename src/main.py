import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import messagebox

# Global Error Handler
def handle_crash(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # 1. Write to file
    with open("crash_log.txt", "w") as f:
        f.write(error_msg)

    # 2. Try to show popup if TK is available
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Application Crash", f"The application crashed!\n\nError saved to 'crash_log.txt'.\n\nDetails:\n{exc_value}")
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
except ImportError as e:
    # Catch import errors (missing libraries) before main logic
    handle_crash(ImportError, e, sys.exc_info()[2])

def main():
    logger.info("Starting AlgoTech Trading Engine...")

    # 1. Load Configuration
    config = load_config()

    # 2. Initialize Core Components
    broker = MockBroker()

    data_engine = DataEngine(broker)
    risk_engine = RiskEngine(config, broker)

    # Link Risk Engine to Broker
    broker.set_risk_engine(risk_engine)

    # Context Dictionary
    context = {
        "config": config,
        "broker": broker,
        "data_engine": data_engine,
        "risk_engine": risk_engine,
        "strategies": []
    }

    # 3. Start Data Engine
    data_engine.subscribe(["NIFTY 50", "BANKNIFTY", "RELIANCE"])
    data_engine.set_interval(1.0)
    data_engine.start()

    # 4. Initialize Strategy
    strategy = SMARSIStrategy(broker, config["strategies"]["sma_rsi"])
    context["strategies"].append(strategy)
    data_engine.register_strategy(strategy)

    # 5. Start GUI
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
