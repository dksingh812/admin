import unittest
from unittest.mock import MagicMock
from src.strategies.sma_rsi import SMARSIStrategy
from src.mock_broker import MockBroker

class TestStrategyLogic(unittest.TestCase):
    def setUp(self):
        self.broker = MockBroker()
        self.broker.place_order = MagicMock(return_value="ORD_123") # Mock order ID
        self.config = {"sma_period": 5, "rsi_period": 5}
        self.strategy = SMARSIStrategy(self.broker, self.config)
        self.strategy.set_symbol("NIFTY 50")

        # Configure a Leg: BUY NIFTY 50 ATM CE, Tgt=10%, SL=5%, Trail=2%
        # (Type, Strike, Action, Qty, Tgt, SL, Trail, Buf)
        self.strategy.legs = [("CE", "ATM", "BUY", 1, 10.0, 5.0, 2.0, 0.0)]
        self.strategy.start()

    def test_lifecycle(self):
        # 1. Trigger Entry
        # Inject prices to form a Buy Signal (Price > SMA, RSI < 30)
        # We need history.
        # Actually, simpler to test execute_legs directly to verify OMS

        # Simulate Entry at 100
        self.strategy.execute_legs("BUY", 20000) # NIFTY 20000

        # Verify Position Tracking
        self.assertEqual(len(self.strategy.active_positions), 1)
        pos = self.strategy.active_positions[0]
        self.assertEqual(pos["entry"], 20000) # Fallback to underlying price if option price not found
        # SL should be 100 * 0.95 = 95 (if entry was 100).
        # Here entry is 20000 (mock). SL = 19000. Target = 22000.
        self.assertEqual(pos["sl"], 19000.0)
        self.assertEqual(pos["tgt"], 22000.0)

        # 2. Simulate Price Move (Trailing)
        # Price moves to 21000. Trailing should move SL up.
        # High = 21000. Trail = 2%. New SL = 21000 * 0.98 = 20580.
        tick = {"symbol": pos["symbol"], "ltp": 21000.0}
        self.strategy.on_tick(tick)

        # Check SL update
        updated_pos = self.strategy.active_positions[0]
        self.assertEqual(updated_pos["highest_ltp"], 21000.0)
        self.assertEqual(updated_pos["sl"], 20580.0)

        # 3. Simulate Target Hit
        # Price moves to 22001
        tick_tgt = {"symbol": pos["symbol"], "ltp": 22001.0}
        self.strategy.on_tick(tick_tgt)

        # Check Exit
        self.assertEqual(updated_pos["status"], "CLOSED")
        # Verify Broker Sell called
        # Call 1: Entry. Call 2: Exit.
        self.assertEqual(self.broker.place_order.call_count, 2)
        # Check Args of exit
        args, _ = self.broker.place_order.call_args
        self.assertEqual(args[0], pos["symbol"])
        self.assertEqual(args[2], "SELL")

if __name__ == '__main__':
    unittest.main()
