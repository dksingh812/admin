import yfinance as yf
import pandas as pd
import numpy as np

def get_company_data(ticker_symbol, period_type="annual", num_periods=6):
    """
    Fetches and processes financial data for a given ticker to compile history.

    Args:
        ticker_symbol (str): Ticker symbol (e.g., 'RELIANCE.NS').
        period_type (str): 'annual' or 'quarterly'.
        num_periods (int): Number of periods to fetch.

    Returns:
        pd.DataFrame, dict: Processed dataframe and info dictionary.
    """
    ticker = yf.Ticker(ticker_symbol)

    # Fetch Data based on period type
    try:
        if period_type == "quarterly":
            financials = ticker.quarterly_financials
            balance_sheet = ticker.quarterly_balance_sheet
        else: # annual
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet

        info = ticker.info
        history = ticker.history(period="10y") # Fetch plenty of history
    except Exception as e:
        return None, f"Error fetching data from yfinance: {e}"

    if financials.empty:
        return None, f"Financials data ({period_type}) is empty."

    # Extract Constants
    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')

    if not shares_outstanding:
        return None, "Shares Outstanding not available."

    # Align Data
    # Financials columns are dates.
    # Take the requested number of periods
    years = financials.columns[:num_periods]

    data_list = []

    for date in years:
        if period_type == "quarterly":
            # For quarterly, label might be "Q3 '24" or just the date
            label = f"{date.year} Q{pd.Timestamp(date).quarter}"
        else:
            label = date.year

        # EBITDA
        try:
            ebitda = financials.loc['EBITDA', date]
        except KeyError:
             try:
                 ebitda = financials.loc['Normalized EBITDA', date]
             except KeyError:
                 ebitda = np.nan

        # Debt & Cash
        # For Quarterly, balance sheet might have missing columns compared to financials.
        # We try to find the exact date match. If missing, we might forward fill or find closest previous.
        # Simple approach: Exact match first, then most recent available in BS if missing.

        if date in balance_sheet.columns:
            bs_col = date
        else:
            # Find closest date in balance_sheet columns that is <= date
            # BS columns usually sorted descending (newest first).
            # Convert to timestamps
            bs_dates = pd.to_datetime(balance_sheet.columns)
            valid_dates = bs_dates[bs_dates <= pd.Timestamp(date)]
            if not valid_dates.empty:
                # Take the max (closest to date)
                bs_col = valid_dates.max()
            else:
                # If no previous date, take the oldest available if reasonable?
                # Or just NaN. Let's try to take the nearest even if future (unlikely) or just skip.
                # Let's fallback to the *newest* available if we are looking at recent quarters and BS is lagged?
                # Actually, standard practice: if BS missing for Q3, take Q2.
                bs_col = None

        if bs_col is not None:
            try:
                debt = balance_sheet.loc['Total Debt', bs_col]
            except KeyError:
                debt = 0

            try:
                cash = balance_sheet.loc['Cash And Cash Equivalents', bs_col]
            except KeyError:
                try:
                    cash = balance_sheet.loc['Cash Cash Equivalents And Short Term Investments', bs_col]
                except KeyError:
                    cash = 0
        else:
            # Fallback if absolutely no BS data correlates
            debt = 0
            cash = 0


        # Stock Price at Period End
        target_date = pd.Timestamp(date)
        if target_date.tzinfo is not None:
            target_date = target_date.tz_localize(None)

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
            'Period': label,
            'Enterprise Value': ev,
            'EBITDA': ebitda,
            'EV/EBITDA (X)': ev_to_ebitda,
            'Date': date
        })

    # Create DataFrame
    df = pd.DataFrame(data_list)

    # Sort by Date Descending
    df = df.sort_values(by='Date', ascending=False)

    # Calculate Growth in EBITDA
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
            growth = np.nan
        growth_list.append(growth)

    df['Growth in EBITDA (%)'] = growth_list

    return df, info

def calculate_valuation(df, info):
    """
    Performs valuation logic. Works for both Annual and Quarterly df.
    """
    if df is None or df.empty:
        return None

    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')
    current_ev_ebitda = info.get('enterpriseToEbitda')

    if not current_ev_ebitda and not df.empty:
         current_ev_ebitda = df.iloc[0]['EV/EBITDA (X)']

    # 1. Avg Growth (Last 3 periods)
    growth_values = df['Growth in EBITDA (%)'].dropna().head(3)
    # If fewer than 3 periods, take mean of what's available
    avg_growth = growth_values.mean() if not growth_values.empty else 0.0

    # 2. Expected EBITDA (Next Period)
    last_actual_ebitda = df.iloc[0]['EBITDA']
    expected_ebitda = last_actual_ebitda * (1 + (avg_growth / 100))

    # 3. Forecasted EV
    # CAREFUL: Current EV/EBITDA (TTM) applies to Annualized EBITDA.
    # If we are using Quarterly EBITDA, we shouldn't multiply Quarterly EBITDA by TTM EV/EBITDA multiple directly
    # to get Full Enterprise Value, unless the multiple is also quarterly-based (it's usually not).
    # However, 'info.enterpriseToEbitda' is usually EV / TTM_EBITDA.
    # If our 'df' is Quarterly, 'last_actual_ebitda' is ~1/4th of annual.
    # If we use that * TTM Multiple, we get ~1/4th of Target EV.
    # So we should probably Annualize the Expected EBITDA if using a TTM multiple.
    # OR: The prompt doesn't specify this nuance.
    # Logic: Target EV = Target EBITDA * Multiple.
    # If multiple is TTM (Price / Annual EBITDA), then Target EBITDA must be Annual.
    # If the user selects "Quarterly", they see Quarterly EBITDA.
    # "Expected EBITDA" for the next quarter.
    # If we want Target Stock Price, we need Target EV for the whole company.
    # So we should take (Expected Quarterly EBITDA * 4) * TTM Multiple?
    # Or just assume the user wants the raw math as per the excel sheet logic:
    # "Forecasted EV = Current EV/EBITDA * Expected EBITDA"
    # If the excel sheet row is Annual, this works.
    # If the excel sheet row is Quarterly, this math implies the multiple is a "Quarterly Multiple" (which is 4x larger than Annual multiple).
    # Since yfinance returns TTM multiple (Annual), we must adjust.

    # Heuristic: Detect if data is Quarterly (by checking info or period label)
    # But `calculate_valuation` just sees `df`.
    # Let's check the period label of the first row.
    is_quarterly = "Q" in str(df.iloc[0]['Period'])

    if is_quarterly:
        # Annualize the expected EBITDA for valuation purposes
        valuation_ebitda = expected_ebitda * 4
    else:
        valuation_ebitda = expected_ebitda

    forecasted_ev = current_ev_ebitda * valuation_ebitda

    target_price = forecasted_ev / shares_outstanding
    entry_price = target_price * 0.75

    results = {
        'Avg Growth (%)': avg_growth, # Label changed to generic "Avg Growth"
        'Expected EBITDA': expected_ebitda,
        'Forecasted EV': forecasted_ev,
        'Target Price': target_price,
        'Entry Price': entry_price,
        'Current Price': current_price,
        'Current EV/EBITDA': current_ev_ebitda,
        'Recommendation': 'BUY' if current_price < entry_price else 'WAIT',
        'Is Quarterly': is_quarterly
    }

    return results
