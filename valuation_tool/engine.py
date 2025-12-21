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
        pd.DataFrame, dict, pd.DataFrame: Processed dataframe, info dictionary, and cashflow dataframe.
    """
    ticker = yf.Ticker(ticker_symbol)

    # Fetch Data based on period type
    try:
        if period_type == "quarterly":
            financials = ticker.quarterly_financials
            balance_sheet = ticker.quarterly_balance_sheet
            cashflow = ticker.quarterly_cashflow
        else: # annual
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow

        info = ticker.info
        history = ticker.history(period="10y") # Fetch plenty of history
    except Exception as e:
        return None, f"Error fetching data from yfinance: {e}", None

    if financials.empty:
        return None, f"Financials data ({period_type}) is empty.", None

    # Extract Constants
    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')

    if not shares_outstanding:
        return None, "Shares Outstanding not available.", None

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

        # EPS (Basic EPS)
        try:
            eps = financials.loc['Basic EPS', date]
        except KeyError:
            eps = np.nan

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
            'EPS': eps,
            'Close Price': close_price,
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

    return df, info, cashflow

def calculate_graham_number(info):
    """
    Calculates Benjamin Graham's 'Fair Value' = Sqrt(22.5 * EPS * BVPS)
    """
    inputs = {'formula': 'Sqrt(22.5 * EPS * BVPS)'}
    try:
        eps = info.get('trailingEps')
        bvps = info.get('bookValue')
        inputs['EPS (TTM)'] = eps
        inputs['Book Value (BVPS)'] = bvps

        if eps and bvps and eps > 0 and bvps > 0:
            val = np.sqrt(22.5 * eps * bvps)
            return {'value': val, 'inputs': inputs}
    except:
        pass
    return {'value': None, 'inputs': inputs}

def calculate_dcf(info, cashflow, growth_rate_pct=10, discount_rate=0.12, terminal_growth=0.03, years=5):
    """
    Simple DCF Calculation.
    FCF = Free Cash Flow
    Projects FCF for 'years' at 'growth_rate_pct'.
    Calculates Terminal Value at 'terminal_growth'.
    Discounts to present value.
    """
    inputs = {
        'formula': 'Sum(FCF / (1+r)^t) + TermVal',
        'Discount Rate': f"{discount_rate*100}%",
        'Terminal Growth': f"{terminal_growth*100}%"
    }

    try:
        # Get latest FCF
        if cashflow is None or cashflow.empty:
            latest_fcf = info.get('freeCashflow')
        else:
            if 'Free Cash Flow' in cashflow.index:
                latest_fcf = cashflow.loc['Free Cash Flow'].iloc[0]
            elif 'Operating Cash Flow' in cashflow.index and 'Capital Expenditure' in cashflow.index:
                ocf = cashflow.loc['Operating Cash Flow'].iloc[0]
                capex = cashflow.loc['Capital Expenditure'].iloc[0]
                latest_fcf = ocf + capex
            else:
                latest_fcf = None

        if not latest_fcf or np.isnan(latest_fcf):
            inputs['Error'] = "No FCF data found"
            return {'value': None, 'inputs': inputs}

        inputs['Latest FCF'] = latest_fcf

        # Cap growth rate for safety (e.g. max 15%)
        safe_growth = min(growth_rate_pct / 100.0, 0.15)
        # Floor growth rate (e.g. min 2%)
        safe_growth = max(safe_growth, 0.02)

        inputs['Assumed Growth Rate'] = f"{safe_growth*100:.2f}% (Capped 15%)"

        shares = info.get('sharesOutstanding')
        if not shares:
            inputs['Error'] = "No Share Count"
            return {'value': None, 'inputs': inputs}

        # Projection
        future_fcfs = []
        current_fcf = latest_fcf

        for i in range(1, years + 1):
            current_fcf = current_fcf * (1 + safe_growth)
            future_fcfs.append(current_fcf)

        # Terminal Value
        last_fcf = future_fcfs[-1]
        terminal_value = (last_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)

        # Discounting
        dcf_value = 0
        for i, fcf in enumerate(future_fcfs):
            dcf_value += fcf / ((1 + discount_rate) ** (i + 1))

        dcf_value += terminal_value / ((1 + discount_rate) ** years)

        fair_value_per_share = dcf_value / shares
        return {'value': fair_value_per_share, 'inputs': inputs}

    except Exception as e:
        inputs['Error'] = str(e)
        return {'value': None, 'inputs': inputs}

def calculate_peg_valuation(info, growth_rate_pct):
    """
    Estimates Price based on PEG = 1 (Fair Value).
    Fair Price = Growth Rate * EPS.
    """
    inputs = {'formula': 'Fair P/E * EPS (where Fair P/E = Growth Rate)'}
    try:
        eps = info.get('trailingEps')
        inputs['EPS (TTM)'] = eps
        inputs['Growth Rate Input'] = f"{growth_rate_pct:.2f}%"

        if eps and eps > 0 and growth_rate_pct > 0:
            # Limit growth rate impact
            safe_growth_pe = min(growth_rate_pct, 35.0)
            safe_growth_pe = max(safe_growth_pe, 5.0)

            inputs['Applied P/E Multiple'] = safe_growth_pe

            val = safe_growth_pe * eps
            return {'value': val, 'inputs': inputs}
    except:
        pass
    return {'value': None, 'inputs': inputs}

def calculate_mean_reversion(df, info, lookback_years=5):
    """
    Calculates Target Price based on Mean Reversion of P/E.
    Target = Current EPS * Average Historical P/E (N-Year).
    """
    inputs = {'formula': f'Current EPS * {lookback_years}-Year Avg P/E'}
    try:
        eps_ttm = info.get('trailingEps')
        inputs['EPS (TTM)'] = eps_ttm

        pe_list = []
        # Calculate P/E for each year
        for index, row in df.iterrows():
            if row['EPS'] and row['EPS'] > 0 and row['Close Price'] and row['Close Price'] > 0:
                pe = row['Close Price'] / row['EPS']
                pe_list.append(pe)

        # Filter based on requested lookback (pe_list is newest first)
        pe_list_slice = pe_list[:lookback_years]

        if not pe_list_slice:
             inputs['Error'] = "Not enough historical P/E data"
             return {'value': None, 'inputs': inputs}

        # Calculate Average P/E
        avg_pe = sum(pe_list_slice) / len(pe_list_slice)
        inputs[f'Historical P/E (Avg {len(pe_list_slice)} Yrs)'] = avg_pe
        inputs['Data Points Used'] = len(pe_list_slice)

        if eps_ttm and eps_ttm > 0:
            target = eps_ttm * avg_pe
            return {'value': target, 'inputs': inputs}
        else:
             inputs['Error'] = "Current EPS invalid"
             return {'value': None, 'inputs': inputs}

    except Exception as e:
         inputs['Error'] = str(e)
         return {'value': None, 'inputs': inputs}

def calculate_valuation(df, info, cashflow=None, overrides=None):
    """
    Performs valuation logic.
    Args:
        overrides (dict): Optional manual overrides for 'growth_rate', 'ev_ebitda', 'mr_period'.
    """
    if df is None or df.empty:
        return None

    overrides = overrides or {}

    shares_outstanding = info.get('sharesOutstanding')
    current_price = info.get('currentPrice')

    # --- EV/EBITDA Override Logic ---
    current_ev_ebitda = info.get('enterpriseToEbitda')
    if not current_ev_ebitda and not df.empty:
         current_ev_ebitda = df.iloc[0]['EV/EBITDA (X)']

    if overrides.get('ev_ebitda') is not None:
        current_ev_ebitda = overrides['ev_ebitda'] # User override

    # 1. Avg Growth (Last 3 periods)
    growth_values = df['Growth in EBITDA (%)'].dropna().head(3)
    avg_growth = growth_values.mean() if not growth_values.empty else 0.0

    # --- Growth Rate Override Logic ---
    if overrides.get('growth_rate') is not None:
        effective_growth_rate = overrides['growth_rate']
    else:
        effective_growth_rate = avg_growth

    # 2. Expected EBITDA
    valid_ebitda_rows = df[df['EBITDA'].notna() & (df['EBITDA'] != 0)]
    if not valid_ebitda_rows.empty:
        last_actual_ebitda = valid_ebitda_rows.iloc[0]['EBITDA']
    else:
        last_actual_ebitda = 0

    # Calculate Expected EBITDA using the effective (possibly overridden) growth rate
    expected_ebitda = last_actual_ebitda * (1 + (effective_growth_rate / 100))

    # 3. Forecasted EV (EV/EBITDA Model)
    is_quarterly = "Q" in str(df.iloc[0]['Period'])

    if is_quarterly:
        valuation_ebitda = expected_ebitda * 4
    else:
        valuation_ebitda = expected_ebitda

    if current_ev_ebitda:
        forecasted_ev = current_ev_ebitda * valuation_ebitda
        target_price_ev = forecasted_ev / shares_outstanding
    else:
        forecasted_ev = 0
        target_price_ev = 0

    entry_price_ev = target_price_ev * 0.75

    ev_inputs = {
        'Current EV/EBITDA': current_ev_ebitda,
        'Expected EBITDA': expected_ebitda,
        'Annualization Factor': 4 if is_quarterly else 1,
        'Shares': shares_outstanding,
        'Used Growth Rate': f"{effective_growth_rate:.2f}%"
    }

    # --- Advanced Models ---

    # Graham Number
    graham_res = calculate_graham_number(info)

    # DCF (Use Effective Growth Rate)
    dcf_res = calculate_dcf(info, cashflow, growth_rate_pct=effective_growth_rate)

    # PEG Model (Use Effective Growth Rate)
    peg_res = calculate_peg_valuation(info, growth_rate_pct=effective_growth_rate)

    # Mean Reversion (Use Override Period)
    mr_years = overrides.get('mr_period', 5)
    mr_res = calculate_mean_reversion(df, info, lookback_years=mr_years)

    results = {
        'Avg Growth (%)': effective_growth_rate, # Return effective growth for display
        'Expected EBITDA': expected_ebitda,
        'Forecasted EV': forecasted_ev,
        'Target Price': target_price_ev,
        'Entry Price': entry_price_ev,
        'Current Price': current_price,
        'Current EV/EBITDA': current_ev_ebitda,
        'Recommendation': 'BUY' if current_price < entry_price_ev else 'WAIT',
        'Is Quarterly': is_quarterly,

        # New Detailed Models
        'Model: EV/EBITDA': {'value': target_price_ev, 'inputs': ev_inputs},
        'Model: Graham': graham_res,
        'Model: DCF': dcf_res,
        'Model: PEG': peg_res,
        'Model: Mean Reversion': mr_res
    }

    return results
