from src.logger import logger

class RiskEngine:
    def __init__(self, config, broker):
        self.config = config
        self.broker = broker
        self.max_loss_per_trade = config["risk"]["max_loss_per_trade"]
        self.max_loss_daily = config["risk"]["max_loss_per_day"]
        self.max_open_trades = config["risk"]["max_open_trades"]

        self.daily_pnl = 0.0
        self.trading_allowed = True

    def check_trade_allowed(self, symbol, quantity, side):
        if not self.trading_allowed:
            logger.warning("Risk Engine: Trading halted due to risk limits.")
            return False

        positions = self.broker.get_positions()
        if len(positions) >= self.max_open_trades:
            logger.warning(f"Risk Engine: Max open trades ({self.max_open_trades}) reached.")
            return False

        # Additional Checks: Capital sufficiency, etc.
        return True

    def update_pnl(self, current_pnl):
        self.daily_pnl = current_pnl
        if self.daily_pnl <= -self.max_loss_daily:
            logger.critical(f"Risk Engine: Max Daily Loss Hit ({self.daily_pnl}). HALTING TRADING.")
            self.trading_allowed = False
            # Ideally trigger "Close All" here

    def reset_daily(self):
        self.daily_pnl = 0.0
        self.trading_allowed = True
