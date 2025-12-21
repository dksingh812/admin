import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from valuation_tool.engine import get_company_data, calculate_valuation, calculate_piotroski_f_score, calculate_technicals
from valuation_tool.tickers import TICKERS

st.set_page_config(page_title="Valuation Dashboard", layout="wide")

def main():
    st.title("Valuation Dashboard")
    st.markdown("Search for an NSE stock to view its valuation based on EBITDA/EV multiples and other advanced models.")

    # Sidebar Controls
    with st.sidebar:
        st.header("Settings")
        frequency = st.radio("Frequency", ["Annual", "Quarterly"])

        if frequency == "Annual":
            num_periods = st.selectbox("Lookback Period (Years)", [3, 5, 8, 10], index=1) # Default 5
            period_type = "annual"
        else:
            num_periods = st.selectbox("Lookback Period (Quarters)", [4, 8, 12], index=1) # Default 8
            period_type = "quarterly"

    # Main Selection
    selected_ticker = st.selectbox("Select Company:", TICKERS, index=TICKERS.index("RELIANCE.NS") if "RELIANCE.NS" in TICKERS else 0)

    if st.button("Analyze"):
        st.session_state['data_fetched'] = True
        st.session_state['ticker'] = selected_ticker
        st.session_state['freq'] = frequency

    if st.session_state.get('data_fetched') and st.session_state.get('ticker') == selected_ticker:
        with st.spinner(f"Fetching {frequency} data for {selected_ticker}..."):
            df, info, cashflow = get_company_data(selected_ticker, period_type=period_type, num_periods=num_periods)

            if df is None or df.empty:
                st.error(info if isinstance(info, str) else "No data found.")
                return

            # --- Model Assumptions UI (Sidebar) ---
            with st.sidebar:
                st.markdown("---")
                with st.expander("🔧 Model Assumptions", expanded=True):
                    base_val = calculate_valuation(df, info, cashflow)
                    natural_growth = base_val['Avg Growth (%)']
                    natural_multiple = base_val['Current EV/EBITDA'] or 0.0

                    st.caption("Customize the inputs below to see how valuation changes.")

                    custom_growth = st.number_input(
                        "Growth Rate (%)",
                        value=float(f"{natural_growth:.2f}"),
                        step=0.5
                    )

                    custom_multiple = st.number_input(
                        "EV/EBITDA Multiple",
                        value=float(f"{natural_multiple:.2f}"),
                        step=0.5
                    )

                    mr_period_map = {"3-Year Avg": 3, "5-Year Avg": 5, "10-Year Avg": 10}
                    mr_choice = st.selectbox("Mean Reversion P/E", list(mr_period_map.keys()), index=1)

                    overrides = {
                        'growth_rate': custom_growth,
                        'ev_ebitda': custom_multiple,
                        'mr_period': mr_period_map[mr_choice]
                    }

            # Calculate Final Valuation
            valuation = calculate_valuation(df, info, cashflow, overrides)
            current_price = valuation['Current Price']

            # --- Layout ---
            st.subheader(f"{info.get('longName', selected_ticker)}")

            # Use Tabs for Organization
            tab_val, tab_health, tab_tech = st.tabs(["💰 Valuation", "🏥 Health & Quality", "📈 Momentum & Risk"])

            # --- TAB 1: Valuation ---
            with tab_val:
                # Main Valuation (EV/EBITDA)
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Current Price", f"₹{current_price:.2f}")
                with col2: st.metric("Entry Price (Buy)", f"₹{valuation['Entry Price']:.2f}")
                with col3: st.metric("Target Price (EV/EBITDA)", f"₹{valuation['Target Price']:.2f}")
                with col4:
                    rec = valuation['Recommendation']
                    color = "green" if rec == "BUY" else "orange"
                    st.markdown(f"### Rec: :{color}[{rec}]")

                st.markdown("---")
                st.header("🤖 Comprehensive Valuation Models")

                # Consensus Logic
                models = [
                    ("EV / EBITDA", valuation['Model: EV/EBITDA']),
                    ("Graham Number", valuation['Model: Graham']),
                    ("DCF (Intrinsic)", valuation['Model: DCF']),
                    ("PEG Fair Value", valuation['Model: PEG']),
                    ("Mean Reversion (P/E)", valuation['Model: Mean Reversion'])
                ]

                valid_targets = []
                for name, res in models:
                    if res['value'] and not np.isnan(res['value']):
                        valid_targets.append(res['value'])

                if valid_targets:
                    consensus = sum(valid_targets) / len(valid_targets)
                    con_diff = ((consensus - current_price) / current_price) * 100

                    st.markdown(f"### Consensus Target: **₹{consensus:,.2f}** ({con_diff:+.2f}%)")
                    if con_diff > 15: st.success("Consensus says: **STRONG BUY** (Undervalued)")
                    elif con_diff > 0: st.info("Consensus says: **BUY/HOLD** (Fairly Valued)")
                    else: st.warning("Consensus says: **WAIT** (Overvalued)")

                # Model Cards
                cols = st.columns(3)
                for i, (name, res) in enumerate(models):
                    with cols[i % 3]:
                        val = res['value']
                        inputs = res['inputs']
                        if val and not np.isnan(val):
                            diff = ((val - current_price) / current_price) * 100
                            color = "green" if diff > 0 else "red"
                            st.markdown(f"""
                            <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px">
                                <h4>{name}</h4>
                                <h2 style="color:{color}">₹{val:,.2f}</h2>
                                <p>Upside: {diff:+.2f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                            with st.expander("See Calculation"):
                                st.write(f"**Formula:** {inputs.get('formula', 'N/A')}")
                                st.divider()
                                for k, v in inputs.items():
                                    if k != 'formula': st.write(f"**{k}:** {v}")
                        else:
                            st.info(f"{name}: Data Unavailable")

                # Historical Table
                st.markdown("---")
                st.markdown(f"### {frequency} Financials & Analysis")
                display_df = df[['Period', 'Enterprise Value', 'EBITDA', 'EV/EBITDA (X)', 'EPS', 'Close Price', 'Growth in EBITDA (%)']].copy()
                last_period_label = display_df.iloc[0]['Period']

                # Proj Label Logic
                if period_type == "quarterly":
                    try:
                        parts = str(last_period_label).split(' Q')
                        year = int(parts[0])
                        qtr = int(parts[1])
                        next_label = f"{year + 1} Q1 (Proj)" if qtr == 4 else f"{year} Q{qtr + 1} (Proj)"
                    except: next_label = "Next Qtr (Proj)"
                else:
                    try:
                        year = int(last_period_label)
                        next_label = f"{year + 1} (Proj)"
                    except: next_label = "Next Year (Proj)"

                new_row = {
                    'Period': next_label,
                    'Enterprise Value': valuation['Forecasted EV'],
                    'EBITDA': valuation['Expected EBITDA'],
                    'EV/EBITDA (X)': valuation['Current EV/EBITDA'],
                    'Growth in EBITDA (%)': valuation['Avg Growth (%)']
                }
                display_df = pd.concat([pd.DataFrame([new_row]), display_df], ignore_index=True)
                display_df.set_index('Period', inplace=True)
                st.dataframe(display_df.transpose().style.format("{:,.2f}"), use_container_width=True)

            # --- TAB 2: Health & Quality (Piotroski) ---
            with tab_health:
                if period_type == "annual":
                    # Fetch fresh data for full health check (need Balance Sheet etc)
                    # We reuse what we have in 'df', 'info', 'cashflow' but engine needs raw
                    # Actually engine's get_company_data returns processed df.
                    # We need raw financials for F-Score.
                    # Let's call a specific health function or re-fetch inside engine?
                    # Engine has 'get_company_data' returning (df, info, cashflow).
                    # df is processed.
                    # We need RAW financials.
                    # Let's update `get_company_data` to return raw or calc F-score inside engine.
                    # I added `calculate_piotroski_f_score` to engine but it needs raw dfs.
                    # Let's re-fetch raw inside the app for this tab or update get_company_data to return them.
                    # Since I can't easily change get_company_data signature without breaking stuff,
                    # I will fetch raw data again briefly here or better: modify get_company_data to calculate score.
                    # Actually, I can just fetch the ticker object again here. It's cached by yfinance.
                    ticker_obj = yf.Ticker(selected_ticker)
                    # Annual is best for F-Score
                    f_score, f_details = calculate_piotroski_f_score(ticker_obj.financials, ticker_obj.balance_sheet, ticker_obj.cashflow)

                    st.header(f"Piotroski F-Score: {f_score} / 9")

                    if f_score >= 8:
                        st.success("Health: VERY STRONG (Safe to Buy)")
                    elif f_score >= 5:
                        st.info("Health: STABLE (Average)")
                    else:
                        st.error("Health: WEAK (High Risk / Value Trap)")

                    st.markdown("### Score Breakdown")
                    c1, c2, c3 = st.columns(3)

                    # Distribute checks
                    checks = list(f_details.items())
                    for i, (k, v) in enumerate(checks):
                        if k == 'Error': continue
                        col = [c1, c2, c3][i % 3]
                        if v:
                            col.success(f"✅ {k}")
                        else:
                            col.warning(f"❌ {k}")
                else:
                    st.warning("Piotroski F-Score is best calculated on Annual data. Please switch Frequency to 'Annual' to view Financial Health.")

            # --- TAB 3: Momentum & Risk ---
            with tab_tech:
                techs = calculate_technicals(selected_ticker)

                if techs and 'Error' not in techs:
                    st.header("Technical Indicators")

                    # 1. RSI Gauge
                    rsi = techs['RSI']
                    fig_rsi = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = rsi,
                        title = {'text': "RSI (14-Day)"},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "black"},
                            'steps': [
                                {'range': [0, 30], 'color': "green"},
                                {'range': [30, 70], 'color': "lightgray"},
                                {'range': [70, 100], 'color': "red"}],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': rsi}}))

                    c1, c2 = st.columns(2)
                    with c1:
                        st.plotly_chart(fig_rsi, use_container_width=True)
                        if rsi < 30: st.success("Oversold (Good Entry)")
                        elif rsi > 70: st.warning("Overbought (Wait)")
                        else: st.info("Neutral")

                    with c2:
                        st.metric("Trend (200 DMA)", techs['Trend'])
                        st.metric("50 DMA", f"₹{techs['50 DMA']:.2f}")
                        st.metric("200 DMA", f"₹{techs['200 DMA']:.2f}")
                        st.metric("Beta (Volatility)", f"{techs['Beta']:.2f}" if techs['Beta'] else "N/A")
                        st.caption("Beta > 1 means more volatile than market.")

                    st.markdown("---")
                    st.markdown("### Institutional Holding")
                    # Try to fetch
                    t_obj = yf.Ticker(selected_ticker)
                    inst_hold = t_obj.info.get('heldPercentInstitutions')
                    if inst_hold:
                        st.progress(inst_hold)
                        st.write(f"**{inst_hold*100:.2f}%** held by Institutions (FII/DII)")
                    else:
                        st.write("Institutional holding data not available.")
                else:
                    st.error("Could not fetch technical data.")

if __name__ == "__main__":
    main()
