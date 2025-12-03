import unittest
from unittest.mock import MagicMock
from src.strategies.sma_rsi import SMARSIStrategy
from src.mock_broker import MockBroker

class TestStrategyLogic(unittest.TestCase):
    def setUp(self):
        self.broker = MockBroker()
        self.broker.place_order = MagicMock(return_value="ORD_123")
        self.config = {"sma_period": 5, "rsi_period": 5}
        self.strategy = SMARSIStrategy(self.broker, self.config)
        self.strategy.set_symbol("NIFTY 50")

        # Configure a Leg with Units:
        # BUY NIFTY 50 ATM CE, Qty 1
        # Tgt=10%, SL=5%, Trail=2%
        # Format: (Type, Strike, Action, Qty, Tgt, U_Tgt, SL, U_SL, Trail, U_Trail, Buf, U_Buf)
        self.strategy.legs = [("CE", "ATM", "BUY", 1, 10.0, "%", 5.0, "%", 2.0, "%", 0.0, "%")]
        self.strategy.start()

    def test_lifecycle(self):
        # 1. Trigger Entry at 20000
        self.strategy.execute_legs("BUY", 20000)

        pos = self.strategy.active_positions[0]
        self.assertEqual(pos["entry"], 20000)

        # SL calculation: 5% of 20000 = 1000. SL = 19000.
        self.assertEqual(pos["sl"], 19000.0)

        # 2. Simulate Price Move (Trailing)
        # Price moves to 21000. High = 21000.
        # Trailing Logic (Linear): High - (Entry * Trail%)
        # 21000 - (20000 * 0.02) = 21000 - 400 = 20600.
        tick = {"symbol": pos["symbol"], "ltp": 21000.0}
        self.strategy.on_tick(tick)

        self.assertEqual(pos["sl"], 20600.0)

        # 3. Simulate Target Hit
        # Target = 10% = 22000.
        # Price moves to 22001.
        tick_tgt = {"symbol": pos["symbol"], "ltp": 22001.0}
        self.strategy.on_tick(tick_tgt)

        self.assertEqual(pos["status"], "CLOSED")

    def test_points_logic(self):
        # Clear positions from setup
        self.strategy.active_positions = []

        # Test Points based SL
        # Tgt=100 Pts, SL=50 Pts
        self.strategy.legs = [("CE", "ATM", "BUY", 1, 100.0, "Pts", 50.0, "Pts", 0.0, "%", 0.0, "%")]
        self.strategy.execute_legs("BUY", 20000)

        pos = self.strategy.active_positions[0]
        self.assertEqual(pos["sl"], 19950.0) # 20000 - 50
        self.assertEqual(pos["tgt"], 20100.0) # 20000 + 100

if __name__ == '__main__':
    unittest.main()
