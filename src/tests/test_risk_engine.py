import unittest
from src.risk_engine import RiskEngine
from src.mock_broker import MockBroker

class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.config = {
            "risk": {
                "max_loss_per_trade": 100,
                "max_loss_per_day": 500,
                "max_open_trades": 2,
                "global_stop_loss_enabled": True
            }
        }
        self.broker = MockBroker()
        self.risk_engine = RiskEngine(self.config, self.broker)

    def test_max_open_trades(self):
        # Simulate 2 open positions
        self.broker.positions = [{"symbol": "A"}, {"symbol": "B"}]
        allowed = self.risk_engine.check_trade_allowed("C", 1, "BUY")
        self.assertFalse(allowed, "Should reject trade when max open trades reached")

        # Simulate 1 open position
        self.broker.positions = [{"symbol": "A"}]
        allowed = self.risk_engine.check_trade_allowed("B", 1, "BUY")
        self.assertTrue(allowed, "Should allow trade when below max open trades")

    def test_daily_loss_limit(self):
        self.risk_engine.update_pnl(-400)
        self.assertTrue(self.risk_engine.trading_allowed)

        self.risk_engine.update_pnl(-501)
        self.assertFalse(self.risk_engine.trading_allowed, "Should halt trading if daily loss exceeded")

if __name__ == '__main__':
    unittest.main()
