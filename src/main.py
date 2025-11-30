import sys
import threading
import time
from src.config import load_config
from src.logger import logger
from src.mock_broker import MockBroker
from src.data_engine import DataEngine
from src.risk_engine import RiskEngine
from src.ui.main_app import MainApp
from src.strategies.sma_rsi import SMARSIStrategy

def main():
    logger.info("Starting AlgoTech Trading Engine...")

    # 1. Load Configuration
    config = load_config()

    # 2. Initialize Core Components
    # Default to Mock Broker initially, Login Tab will switch it
    broker = MockBroker()

    data_engine = DataEngine(broker)
    risk_engine = RiskEngine(config, broker)

    # Link Risk Engine to Broker
    broker.set_risk_engine(risk_engine)

    # Context Dictionary to share state across UI and Backend
    context = {
        "config": config,
        "broker": broker,
        "data_engine": data_engine,
        "risk_engine": risk_engine,
        "strategies": []
    }

    # 3. Start Data Engine (Background Polling)
    # We subscribe to a few default indices
    data_engine.subscribe(["NIFTY 50", "BANKNIFTY", "RELIANCE"])
    data_engine.start_polling(interval=1.0)

    # 4. Initialize Strategy (Example)
    # In a real scenario, this is added via UI dynamically, but here we preload one.
    strategy = SMARSIStrategy(broker, config["strategies"]["sma_rsi"])
    context["strategies"].append(strategy)

    # IMPORTANT: Register strategy with Data Engine so it receives ticks
    data_engine.register_strategy(strategy)

    # 5. Start GUI (Main Thread)
    app = MainApp(context)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    finally:
        # Cleanup
        logger.info("Shutting down...")
        data_engine.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
