import unittest
from unittest.mock import MagicMock
from src.data_engine import DataEngine
from src.strategies.sma_rsi import SMARSIStrategy
from src.mock_broker import MockBroker

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.broker = MockBroker()
        self.strategy = SMARSIStrategy(self.broker, {"sma_period": 5, "rsi_period": 5})
        self.data_engine = DataEngine(self.broker)
        self.data_engine.register_strategy(self.strategy)

    def test_on_tick_called(self):
        # Mock the on_tick method to verify it's called
        self.strategy.on_tick = MagicMock()

        # Activate strategy
        self.strategy.start()

        # Simulate one poll loop iteration
        # Instead of running the thread, we call the logic directly or wait
        # Here we just manually trigger what the loop does to verify wiring

        tick_data = {"symbol": "TEST", "ltp": 100.0, "change": 0.0}

        # Simulate Data Engine broadcasting
        for strat in self.data_engine.strategies:
            if strat.active:
                strat.on_tick(tick_data)

        self.strategy.on_tick.assert_called_with(tick_data)

    def test_risk_blocking(self):
        # Setup Risk Engine
        from src.risk_engine import RiskEngine
        config = {
            "risk": {
                "max_loss_per_trade": 100,
                "max_loss_per_day": 100, # Small limit
                "max_open_trades": 5,
                "global_stop_loss_enabled": True
            }
        }
        risk = RiskEngine(config, self.broker)
        self.broker.set_risk_engine(risk)

        # Simulate a loss that hits daily limit
        risk.update_pnl(-200)

        # Try to place order
        order_id = self.broker.place_order("TEST", 1, "BUY")

        self.assertIsNone(order_id, "Order should be blocked by Risk Engine")

if __name__ == '__main__':
    unittest.main()
