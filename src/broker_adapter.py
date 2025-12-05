from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    """Abstract Base Class for Broker Integration."""

    def __init__(self):
        self.risk_engine = None

    def set_risk_engine(self, risk_engine):
        self.risk_engine = risk_engine

    @abstractmethod
    def authenticate(self, api_key, api_secret):
        pass

    @abstractmethod
    def get_ltp(self, symbol):
        pass

    @abstractmethod
    def get_positions(self):
        pass

    def place_order(self, symbol, quantity, side, order_type="MARKET", price=0.0):
        """Wrapper to enforce Risk Checks before actual placement."""
        if self.risk_engine:
            allowed = self.risk_engine.check_trade_allowed(symbol, quantity, side)
            if not allowed:
                return None

        return self._place_order_impl(symbol, quantity, side, order_type, price)

    @abstractmethod
    def _place_order_impl(self, symbol, quantity, side, order_type, price):
        """Actual implementation of order placement."""
        pass

    @abstractmethod
    def get_funds(self):
        pass
