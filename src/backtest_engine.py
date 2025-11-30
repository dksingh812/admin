import pandas as pd
import time
from src.logger import logger
from src.mock_broker import MockBroker

class BacktestEngine:
    def __init__(self, data_file, strategies, initial_capital=100000):
        self.data_file = data_file
        self.strategies = strategies
        self.broker = MockBroker()
        self.broker.funds = initial_capital

        # Link strategies to this mock broker
        for s in self.strategies:
            s.broker = self.broker

    def run(self):
        logger.info(f"Starting Backtest on {self.data_file}")
        try:
            df = pd.read_csv(self.data_file)
            # Assume CSV has 'timestamp', 'open', 'high', 'low', 'close', 'volume'
            # We treat 'close' as LTP for simplicity

            for index, row in df.iterrows():
                tick_data = {
                    "symbol": "BACKTEST_SYMBOL",
                    "ltp": row['close'],
                    "timestamp": row.get('timestamp')
                }

                # Update Broker State (Simulate market)
                self.broker.mock_ltp_cache["BACKTEST_SYMBOL"] = row['close']

                # Notify Strategies
                for strategy in self.strategies:
                    strategy.active = True # Force active
                    strategy.on_tick(tick_data)

            logger.info("Backtest Completed")
            self.generate_report()

        except Exception as e:
            logger.error(f"Backtest failed: {e}")

    def generate_report(self):
        positions = self.broker.get_positions()
        final_funds = self.broker.get_funds()
        pnl = final_funds - 100000 # initial
        logger.info("------ BACKTEST REPORT ------")
        logger.info(f"Final Funds: {final_funds:.2f}")
        logger.info(f"Total PnL: {pnl:.2f}")
        logger.info(f"Total Trades: {len(positions)}")
        logger.info("-----------------------------")
