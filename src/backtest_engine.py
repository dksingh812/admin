import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import collections
from src.logger import logger
from src.strategies.indicators import Indicators

# --- Helper Classes for Results ---

class Trade:
    def __init__(self, entry_time, symbol, side, qty, entry_price):
        self.entry_time = entry_time
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.entry_price = entry_price
        self.exit_time = None
        self.exit_price = 0.0
        self.status = "OPEN"
        self.pnl = 0.0
        self.max_profit = 0.0
        self.max_loss = 0.0

    def close(self, exit_time, exit_price):
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.status = "CLOSED"

        multiplier = 1 if self.side == "BUY" else -1
        self.pnl = (self.exit_price - self.entry_price) * self.qty * multiplier

    def update_mfe_mae(self, current_price):
        multiplier = 1 if self.side == "BUY" else -1
        current_pnl = (current_price - self.entry_price) * self.qty * multiplier
        if current_pnl > self.max_profit: self.max_profit = current_pnl
        if current_pnl < self.max_loss: self.max_loss = current_pnl

class BacktestBroker:
    def __init__(self, capital=100000.0):
        self.capital = capital
        self.initial_capital = capital
        self.cash = capital
        self.trades = []  # List of Trade objects
        self.orders_queue = collections.deque()
        self.open_positions = [] # List of Trade objects currently open

    def place_order(self, symbol, qty, side):
        # In a real broker, this returns an ID immediately.
        # Here we queue it for the next "match_orders" cycle (or immediate).
        order = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": "MARKET" # Assuming Market for V1
        }
        self.orders_queue.append(order)
        return f"ORD_{len(self.orders_queue)}"

    def match_orders(self, timestamp, current_price):
        # Process Queue
        while self.orders_queue:
            order = self.orders_queue.popleft()

            # Check if this is an Exit or Entry?
            # Simple Logic:
            # If we have an open position in the SAME symbol but OPPOSITE side -> Close it (FIFO).
            # Else -> Open new position.

            qty_remaining = order['qty']
            side = order['side']

            # Try to close existing positions
            for pos in self.open_positions[:]: # Copy to modify
                if pos.symbol == order['symbol'] and pos.side != side:
                    # Match!
                    matched_qty = min(pos.qty, qty_remaining)

                    # Log Partial Close if needed (Not supported in V1, assuming full exits usually)
                    # For V1: If partial close, we'd need to split the Trade object.
                    # Let's assume full close for simplicity or 1 trade = 1 position

                    if matched_qty == pos.qty:
                        pos.close(timestamp, current_price)
                        self.cash += pos.pnl # PnL is added to cash
                        self.open_positions.remove(pos)
                        qty_remaining -= matched_qty
                    else:
                        # Partial Close logic would go here
                        pass

                if qty_remaining == 0: break

            # If qty still remaining, open new position
            if qty_remaining > 0:
                new_trade = Trade(timestamp, order['symbol'], side, qty_remaining, current_price)
                self.open_positions.append(new_trade)
                self.trades.append(new_trade)

    def mark_to_market(self, current_price):
        unrealized_pnl = 0.0
        for pos in self.open_positions:
            pos.update_mfe_mae(current_price)
            multiplier = 1 if pos.side == "BUY" else -1
            unrealized_pnl += (current_price - pos.entry_price) * pos.qty * multiplier
        return self.cash + unrealized_pnl

class BacktestEngine:
    def __init__(self):
        pass

    def download_data(self, symbol, period="1mo", interval="15m"):
        logger.info(f"Downloading data for {symbol}...")
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if df.empty: return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df.columns = [c.lower() for c in df.columns]
            return df
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def run(self, strategy_class, config, symbol, df):
        logger.info("Starting Backtest Simulation...")
        broker = BacktestBroker(capital=100000.0) # Fixed capital for now

        strategy = strategy_class(broker, config)
        strategy.set_symbol(symbol)
        strategy.active = True

        equity_curve = []
        equity_timestamps = []

        # We need a rolling window for the strategy
        # Assuming strategy handles history internally via on_tick -> histories

        total_ticks = len(df)
        logger.info(f"Processing {total_ticks} candles...")

        for index, row in df.iterrows():
            timestamp = index
            price = row['close'] # Proxy for LTP

            tick_data = {
                "symbol": symbol,
                "ltp": price,
                "timestamp": timestamp
            }

            # 1. Strategy Logic
            strategy.on_tick(tick_data)

            # 2. Broker Matching
            # Since strategy calls broker.place_order(), orders are in queue.
            # We match them immediately at CLOSE price of this candle.
            broker.match_orders(timestamp, price)

            # 3. Record Equity
            current_equity = broker.mark_to_market(price)
            equity_curve.append(current_equity)
            equity_timestamps.append(timestamp)

        # Force Close All at End
        last_price = df.iloc[-1]['close']
        last_time = df.index[-1]
        for pos in broker.open_positions:
            pos.close(last_time, last_price)
            broker.cash += pos.pnl
        broker.open_positions.clear()

        # --- Metrics Calculation ---
        trades = broker.trades
        closed_trades = [t for t in trades if t.status == "CLOSED"]

        win_trades = [t for t in closed_trades if t.pnl > 0]
        loss_trades = [t for t in closed_trades if t.pnl <= 0]

        total_pnl = sum([t.pnl for t in closed_trades])
        max_profit = max([t.pnl for t in closed_trades]) if closed_trades else 0
        max_loss = min([t.pnl for t in closed_trades]) if closed_trades else 0

        win_rate = (len(win_trades) / len(closed_trades) * 100) if closed_trades else 0.0

        # Drawdown
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.cummax()
        drawdown = equity_series - rolling_max
        max_drawdown = drawdown.min()

        # Daywise PnL (for Heatmap)
        day_pnl = {}
        for t in closed_trades:
            day_str = t.exit_time.strftime("%Y-%m-%d")
            day_pnl[day_str] = day_pnl.get(day_str, 0.0) + t.pnl

        return {
            "metrics": {
                "total_trades": len(closed_trades),
                "win_trades": len(win_trades),
                "loss_trades": len(loss_trades),
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "max_drawdown": max_drawdown,
                "avg_profit": (sum([t.pnl for t in win_trades]) / len(win_trades)) if win_trades else 0,
                "avg_loss": (sum([t.pnl for t in loss_trades]) / len(loss_trades)) if loss_trades else 0,
            },
            "equity_curve": {
                "time": [t.strftime("%Y-%m-%d %H:%M") for t in equity_timestamps],
                "equity": equity_curve
            },
            "day_pnl": day_pnl,
            "trades": [
                {
                    "entry_time": t.entry_time.strftime("%Y-%m-%d %H:%M"),
                    "exit_time": t.exit_time.strftime("%Y-%m-%d %H:%M"),
                    "symbol": t.symbol,
                    "side": t.side,
                    "entry": t.entry_price,
                    "exit": t.exit_price,
                    "pnl": t.pnl
                } for t in closed_trades
            ]
        }
