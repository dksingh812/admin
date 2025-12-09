# Dictionary mapping Common Symbols to Upstox Instrument Keys
# This acts as a robust fallback if the CSV download fails.

DEFAULT_SYMBOLS = {
    # Indices - Upstox V2 Keys (NSE_INDEX|Token)
    # Nifty 50 Token: 17
    # Bank Nifty Token: 23
    # Finnifty Token: 27
    # India VIX Token: 21
    "NIFTY 50": "NSE_INDEX|17",
    "BANKNIFTY": "NSE_INDEX|23",
    "FINNIFTY": "NSE_INDEX|27",
    "INDIA VIX": "NSE_INDEX|21",
    "SENSEX": "BSE_INDEX|1",

    # Top Stocks (Equity)
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

    "BHARTIARTL": "NSE_EQ|INE397D01024",
    "BAJFINANCE": "NSE_EQ|INE296A01024",
    "MARUTI": "NSE_EQ|INE585B01010",
    "TITAN": "NSE_EQ|INE280A01028"
}

# List version for Dropdowns (Keys of the dict)
DEFAULT_SYMBOL_LIST = sorted(list(DEFAULT_SYMBOLS.keys()))
