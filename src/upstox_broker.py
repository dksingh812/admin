import urllib.parse
from src.broker_adapter import BrokerAdapter
from src.logger import logger
from src.instrument_manager import instrument_manager
import upstox_client
from upstox_client.rest import ApiException

class UpstoxBroker(BrokerAdapter):
    """Real Upstox Integration."""

    def __init__(self, redirect_uri):
        super().__init__()
        self.api_client = None
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.connected = False

    def get_login_url(self, api_key):
        """Generates the OAuth2 Login URL."""
        base_url = "https://api.upstox.com/v2/login/authorization/dialog"
        params = {
            "response_type": "code",
            "client_id": api_key,
            "redirect_uri": self.redirect_uri,
        }
        return f"{base_url}?{urllib.parse.urlencode(params)}"

    def authenticate(self, api_key, api_secret, code=None):
        """Exchanges Auth Code for Access Token."""
        if not code:
            logger.error("Upstox Broker: No auth code provided")
            return False

        try:
            import requests
            url = 'https://api.upstox.com/v2/login/authorization/token'
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = {
                'code': code,
                'client_id': api_key,
                'client_secret': api_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
            }

            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                json_response = response.json()
                self.access_token = json_response.get('access_token')
                self.connected = True

                configuration = upstox_client.Configuration()
                configuration.access_token = self.access_token
                self.api_client = upstox_client.ApiClient(configuration)

                logger.info("Upstox Broker: Authentication Successful")
                return True
            else:
                logger.error(f"Upstox Auth Failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Upstox Broker Auth Error: {e}")
            return False

    def get_ltp(self, symbol):
        if not self.connected:
            return 0.0

        key = instrument_manager.get_instrument_key(symbol)
        if not key:
            # Fallback if we can't find it, or maybe the symbol IS the key
            key = symbol

        try:
            # Market Quote API
            api_instance = upstox_client.MarketQuoteApi(self.api_client)
            api_response = api_instance.get_market_quote_ltp(symbol=key)
            # Response structure: { status: 'success', data: { 'NSE_EQ:RELIANCE': { last_price: 2400 } } }
            if api_response.data:
                # The key in data might be slightly different
                for k, v in api_response.data.items():
                    return v.last_price
            return 0.0
        except Exception as e:
            logger.error(f"Upstox get_ltp error: {e}")
            return 0.0

    def get_positions(self):
        if not self.connected:
            return []
        try:
            api_instance = upstox_client.PortfolioApi(self.api_client)
            api_response = api_instance.get_positions()
            return api_response.data
        except ApiException as e:
            logger.error(f"Upstox get_positions error: {e}")
            return []

    def _place_order_impl(self, symbol, quantity, side, order_type, price):
        if not self.connected:
            logger.error("Upstox Broker: Not Connected")
            return None

        key = instrument_manager.get_instrument_key(symbol)
        if not key:
            logger.error(f"Instrument Key not found for {symbol}")
            return None

        try:
            api_instance = upstox_client.OrderApi(self.api_client)
            body = upstox_client.PlaceOrderRequest(
                quantity=quantity,
                product='D', # Delivery, or 'I' for Intraday
                validity='DAY',
                price=price if order_type == 'LIMIT' else 0.0,
                tag='algo_order',
                instrument_token=key,
                order_type=order_type,
                transaction_type=side,
                disclosed_quantity=0,
                trigger_price=0.0,
                is_amo=False
            )
            api_response = api_instance.place_order(body, api_version='2.0')
            logger.info(f"Order Placed: {api_response.data.order_id}")
            return api_response.data.order_id

        except Exception as e:
            logger.error(f"Upstox Place Order Error: {e}")
            return None

    def get_funds(self):
        if not self.connected:
            return 0.0
        try:
            api_instance = upstox_client.UserApi(self.api_client)
            api_response = api_instance.get_user_fund_margin(segment="SEC") # Securities
            return api_response.data.funds.available_margin
        except Exception as e:
            logger.error(f"Upstox get_funds error: {e}")
            return 0.0
