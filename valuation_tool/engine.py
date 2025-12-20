import yfinance as yf
import pandas as pd
import numpy as np

def get_company_data(ticker_symbol):
    """
    Fetches and processes financial data for a given ticker to compile a 6-year history
    (including projections if we decide to handle them here, but primarily historicals).
    """
    ticker = yf.Ticker(ticker_symbol)

    # Fetch Data
    try:
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        info = ticker.info
        # Fetch enough history to cover the last 6-7 years of year-end prices
        history = ticker.history(period="10y")
    except Exception as e:
        return None, f"Error fetching data from yfinance: {e}"

    if financials.empty or balance_sheet.empty:
        return None, "Financials or Balance Sheet data is empty."

    # Extract Constants
    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')

    if not shares_outstanding:
        return None, "Shares Outstanding not available."

    # Align Data (Financials and BS usually have same columns - dates)
    # We want to iterate through the columns (years) common to both or present in financials
    years = financials.columns

    data_list = []

    # Iterate through each year (column) in financials
    # Usually sorted descending (newest first). We take up to 6.
    for date in years[:6]:
        year_label = date.year

        # EBITDA
        try:
            ebitda = financials.loc['EBITDA', date]
        except KeyError:
             # Fallback if specific EBITDA key is missing or named differently
             try:
                 ebitda = financials.loc['Normalized EBITDA', date]
             except KeyError:
                 ebitda = np.nan

        # Debt & Cash
        try:
            debt = balance_sheet.loc['Total Debt', date]
        except KeyError:
            debt = 0 # Assume 0 if missing, or handle error

        try:
            cash = balance_sheet.loc['Cash And Cash Equivalents', date]
        except KeyError:
            # Fallback
            try:
                cash = balance_sheet.loc['Cash Cash Equivalents And Short Term Investments', date]
            except KeyError:
                cash = 0

        # Stock Price at Year End
        # We need the close price on 'date' or the closest trading day before 'date'
        # 'date' in financials is usually YYYY-MM-DD.
        # history index is DateTime.

        # Ensure date is timezone aware if history is, or vice versa
        # yfinance history is usually tz-aware (Asia/Kolkata for .NS)
        # financials columns are usually just Timestamps (naive or UTC)

        # Let's try to locate the date in history
        # We use 'asof' logic or simple search
        target_date = pd.Timestamp(date).tz_localize(None)

        # Filter history to dates <= target_date
        # Ensure history index is tz-naive for comparison to avoid issues
        history_naive = history.copy()
        history_naive.index = history_naive.index.tz_localize(None)

        past_data = history_naive[history_naive.index <= target_date]

        if not past_data.empty:
            close_price = past_data.iloc[-1]['Close']
        else:
            close_price = np.nan

        # Calculate Metrics
        if not np.isnan(close_price):
            market_cap = close_price * shares_outstanding
            ev = market_cap + debt - cash
        else:
            ev = np.nan

        # EV/EBITDA
        if ebitda and ebitda != 0 and not np.isnan(ev):
            ev_to_ebitda = ev / ebitda
        else:
            ev_to_ebitda = np.nan

        data_list.append({
            'Year': year_label,
            'Enterprise Value': ev,
            'EBITDA': ebitda,
            'EV/EBITDA (X)': ev_to_ebitda,
            'Date': date # Keep full date for sorting/debug
        })

    # Create DataFrame
    df = pd.DataFrame(data_list)

    # Sort by Year Descending (Newest First)
    df = df.sort_values(by='Year', ascending=False)

    # Calculate Growth in EBITDA
    # Growth = (Current - Previous) / Previous
    # Since df is Newest -> Oldest, Previous is the next row (i+1)

    growth_list = []
    for i in range(len(df)):
        if i < len(df) - 1:
            current_ebitda = df.iloc[i]['EBITDA']
            prev_ebitda = df.iloc[i+1]['EBITDA']

            if prev_ebitda and prev_ebitda != 0:
                growth = ((current_ebitda - prev_ebitda) / prev_ebitda) * 100
            else:
                growth = np.nan
        else:
            # Oldest year has no growth metric
            growth = np.nan
        growth_list.append(growth)

    df['Growth in EBITDA (%)'] = growth_list

    return df, info

def calculate_valuation(df, info):
    """
    Performs the valuation logic based on the processed historical dataframe.
    """
    if df is None or df.empty:
        return None

    # Constants
    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')
    # Use latest available annual EV/EBITDA or TTM from info?
    # Prompt says: "Use the current EV/EBITDA multiple".
    # Usually 'enterpriseToEbitda' in info is the TTM/Current one.
    current_ev_ebitda = info.get('enterpriseToEbitda')

    # Fallback if info is missing it, use latest from history (though history is lagged)
    if not current_ev_ebitda and not df.empty:
         current_ev_ebitda = df.iloc[0]['EV/EBITDA (X)']

    # 1. Avg 3Y Growth
    # Get last 3 available growth numbers (excluding NaN)
    # df is sorted Newest first.
    # Rows: 0 (Latest Year), 1 (Year-1), 2 (Year-2)...
    # Growth column corresponds to growth *of* that year *over* previous.
    # So Row 0 growth is Year N vs Year N-1.
    growth_values = df['Growth in EBITDA (%)'].dropna().head(3)
    avg_growth = growth_values.mean()

    # 2. Expected EBITDA
    # "Current EBITDA * (1 + Avg Growth)"
    # Prompt says "Current EBITDA". Is this TTM EBITDA or Last Reported Annual?
    # Usually for forward projection from annual data, we use Last Annual EBITDA.
    # Let's use Last Annual EBITDA from the dataframe (Row 0).
    last_annual_ebitda = df.iloc[0]['EBITDA']

    # Convert avg_growth from percentage (e.g. 12.5) to decimal (0.125)
    expected_ebitda = last_annual_ebitda * (1 + (avg_growth / 100))

    # 3. Forecasted EV
    # "Use the current EV/EBITDA multiple multiplied by the Expected EBITDA"
    forecasted_ev = current_ev_ebitda * expected_ebitda

    # 4. Target Price
    target_price = forecasted_ev / shares_outstanding

    # 5. Entry Price
    entry_price = target_price * 0.75

    results = {
        'Avg 3Y Growth (%)': avg_growth,
        'Expected EBITDA': expected_ebitda,
        'Forecasted EV': forecasted_ev,
        'Target Price': target_price,
        'Entry Price': entry_price,
        'Current Price': current_price,
        'Current EV/EBITDA': current_ev_ebitda,
        'Recommendation': 'BUY' if current_price < entry_price else 'WAIT'
    }

    return results
