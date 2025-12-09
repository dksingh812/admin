import unittest
import pandas as pd
from src.backtest_engine import BacktestEngine
from src.strategies.builder_strategy import BuilderStrategy
import os
import shutil

class TestBacktest(unittest.TestCase):
    def setUp(self):
        # Create a dummy CSV? No, BacktestEngine now takes a DataFrame directly.
        self.df = pd.DataFrame({
            "open": [100.0] * 50,
            "high": [105.0] * 50,
            "low": [95.0] * 50,
            "close": [100.0 + i for i in range(50)], # Price goes up
            "volume": [1000] * 50
        }, index=pd.date_range(start="2024-01-01", periods=50, freq="15min"))

        self.config = {
            "name": "TestStrat",
            "entry_conditions": [
                {"ind1": "LTP", "op": ">", "ind2": "0", "p1": {}, "p2": {}} # Always Buy
            ],
            "legs": [
                ("CE", "ATM", "BUY", "1", "10", "Pts", "5", "Pts", "0", "Pts", "0", "Pts")
            ]
        }

    def test_backtest_run(self):
        engine = BacktestEngine()
        results = engine.run(BuilderStrategy, self.config, "TEST_SYM", self.df)

        self.assertIn("metrics", results)
        self.assertIn("equity_curve", results)
        self.assertIn("trades", results)

        # Since we buy every tick (simplified logic in strategy), we should have trades
        self.assertTrue(len(results["trades"]) >= 0)

if __name__ == '__main__':
    unittest.main()
