# Dictionary mapping Common Symbols to Upstox Instrument Keys
# This acts as a robust fallback if the CSV download fails.

DEFAULT_SYMBOLS = {
    # Indices
    "NIFTY 50": "NSE_INDEX|Nifty 50",
    "BANKNIFTY": "NSE_INDEX|Nifty Bank",
    "FINNIFTY": "NSE_INDEX|Nifty Fin Service",
    "INDIA VIX": "NSE_INDEX|India VIX",
    "SENSEX": "BSE_INDEX|SENSEX",

    # Top Stocks (Equity) - Keys usually NSE_EQ|ISIN or similar.
    # For Upstox API v2, simple symbol 'NSE_EQ|RELIANCE' often works if ISIN logic is complex to hardcode.
    # We will try the symbol format first.
    "RELIANCE": "NSE_EQ|INE002A01018",
    "HDFCBANK": "NSE_EQ|INE040A01034",
    "ICICIBANK": "NSE_EQ|INE090A01021",
    "INFY": "NSE_EQ|INE009A01021",
    "TCS": "NSE_EQ|INE467B01029",
    "LT": "NSE_EQ|INE018A01030",
    "SBIN": "NSE_EQ|INE062A01020",
    "AXISBANK": "NSE_EQ|INE238A01034",
    "KOTAKBANK": "NSE_EQ|INE237A01028",
    "ITC": "NSE_EQ|INE154A01025",

    # Fallbacks that might need CSV to be perfect, but we try standard ISIN/Symbol patterns
    "BHARTIARTL": "NSE_EQ|INE397D01024",
    "BAJFINANCE": "NSE_EQ|INE296A01024",
    "MARUTI": "NSE_EQ|INE585B01010",
    "TITAN": "NSE_EQ|INE280A01028"
}

# List version for Dropdowns (Keys of the dict)
DEFAULT_SYMBOL_LIST = sorted(list(DEFAULT_SYMBOLS.keys()))
