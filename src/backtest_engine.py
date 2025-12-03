import pandas as pd
import yfinance as yf
from src.logger import logger
from src.strategies.indicators import Indicators
import datetime

class MockBroker:
    def __init__(self):
        self.orders = []
        self.trades = []

    def place_order(self, symbol, qty, side):
        # We just record the intent. The Backtester handles execution price.
        order_id = f"ORD_{len(self.orders)+1}"
        self.orders.append({
            "id": order_id,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "time": datetime.datetime.now() # Placeholder
        })
        return order_id

class BacktestEngine:
    def __init__(self):
        self.results = {}

    def download_data(self, symbol, period="1mo", interval="15m"):
        logger.info(f"Downloading data for {symbol}...")
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty:
                logger.error("Downloaded data is empty.")
                return None

            # YFinance multi-index columns fix
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            df.columns = [c.lower() for c in df.columns]
            return df
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def run(self, strategy_class, config, symbol, df):
        logger.info("Starting Backtest...")
        broker = MockBroker()

        # Instantiate strategy with Mock Broker
        strategy = strategy_class(broker, config)
        strategy.set_symbol(symbol)
        strategy.active = True

        capital = 100000.0
        equity_curve = []
        trades = []

        # Simulation Loop
        # We need to feed enough history for indicators to warm up
        # Then start feeding ticks

        history_buffer = []

        for index, row in df.iterrows():
            price = row['close']
            tick = {
                "symbol": symbol,
                "ltp": price,
                "timestamp": index
            }

            # Hack: Manually feed history to strategy to speed up warmup
            # (Assuming strategy has a simple history list)
            if hasattr(strategy, 'histories'):
                if symbol not in strategy.histories: strategy.histories[symbol] = []
                strategy.histories[symbol].append(price)
                if len(strategy.histories[symbol]) > 500: strategy.histories[symbol].pop(0)

            # Execute Strategy Logic
            strategy.on_tick(tick)

            # Process Orders generated in this tick
            while broker.orders:
                order = broker.orders.pop(0)
                # Assume immediate fill at Close price
                # For Options, we Approximate:
                # Delta 0.5 for ATM.
                # Leg symbol string parsing needed?
                # For simplicity in V1: Treat everything as Underlying movement * Qty

                trade = {
                    "entry_time": index,
                    "symbol": order['symbol'],
                    "side": order['side'],
                    "entry_price": price, # Spot Price Proxy
                    "qty": order['qty'],
                    "status": "OPEN",
                    "pnl": 0.0
                }
                trades.append(trade)

            # Update Open Positions PnL (Mark to Market)
            # Strategy.active_positions tracks the logical stops
            # We need to sync with that or just track PnL here?
            # actually strategy.active_positions has the logic.

            # Check for Exits in Strategy
            # Strategy calls place_order(SELL) to exit.
            # We need to match sells to buys.

            current_equity = capital + sum([t['pnl'] for t in trades])
            equity_curve.append(current_equity)

        # Post-Processing
        # This basic loop is insufficient because Strategy.on_tick manages the exits internally
        # by calling place_order.
        # We need a robust matching engine.

        # SIMPLIFIED APPROACH:
        # We will track the Strategy's internal "active_positions" list.
        # When an item moves from OPEN to CLOSED in that list, we log a trade.

        final_trades = []
        # Since strategy object persists, we can inspect it after run?
        # But we need to capture PnL over time.

        return {
            "equity": equity_curve,
            "trades": len(trades) # Placeholder
        }
