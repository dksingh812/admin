import random
from src.broker_adapter import BrokerAdapter
from src.logger import logger

class MockBroker(BrokerAdapter):
    """Mock Broker for Testing and Paper Trading without API."""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.positions = []
        self.funds = 100000.0  # Virtual Capital
        self.mock_ltp_cache = {
            "NIFTY 50": 22000.0,
            "BANKNIFTY": 48000.0,
            "RELIANCE": 2900.0,
            "FINNIFTY": 20000.0,
            "SENSEX": 72000.0,
            "INDIA VIX": 15.0
        }

    def authenticate(self, api_key, api_secret):
        logger.info("Mock Broker: Authentication Successful")
        self.connected = True
        return True

    def get_ltp(self, symbol):
        # Simulate price movement
        base_price = self.mock_ltp_cache.get(symbol, 100.0)
        variation = random.uniform(-0.5, 0.5)
        new_price = round(base_price + variation, 2)
        self.mock_ltp_cache[symbol] = new_price

        # Calculate Mock Change
        prev_close = base_price * 0.99 # Mock prev close
        change = new_price - prev_close
        pct = (change / prev_close) * 100

        return {
            "ltp": new_price,
            "change": change,
            "pct_change": pct
        }

    def get_positions(self):
        return self.positions

    def _place_order_impl(self, symbol, quantity, side, order_type, price):
        if not self.connected:
            logger.error("Mock Broker: Not Connected")
            return None

        quote = self.get_ltp(symbol)
        ltp = quote['ltp']
        trade_value = ltp * quantity

        if side == "BUY":
            if trade_value > self.funds:
                logger.warning("Mock Broker: Insufficient Funds")
                return None
            self.funds -= trade_value
        else: # SELL
            self.funds += trade_value

        order_id = f"MOCK_{random.randint(1000, 9999)}"
        logger.info(f"Mock Order Placed: {side} {quantity} {symbol} @ {ltp}")

        # Add to positions (simplified logic)
        self.positions.append({
            "symbol": symbol,
            "quantity": quantity if side == "BUY" else -quantity,
            "avg_price": ltp,
            "ltp": ltp,
            "pnl": 0.0
        })
        return order_id

    def get_funds(self):
        return self.funds
