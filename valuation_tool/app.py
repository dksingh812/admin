import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from valuation_tool.engine import get_company_data, calculate_valuation
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
        # We use session state to persist data so changing sidebar assumptions doesn't re-fetch
        st.session_state['data_fetched'] = True
        st.session_state['ticker'] = selected_ticker
        st.session_state['freq'] = frequency

    if st.session_state.get('data_fetched') and st.session_state.get('ticker') == selected_ticker:
        with st.spinner(f"Fetching {frequency} data for {selected_ticker}..."):
            # Fetch only if needed or rely on caching (get_company_data uses yfinance which caches internally usually, but we call it fresh)
            # ideally we cache this call
            df, info, cashflow = get_company_data(selected_ticker, period_type=period_type, num_periods=num_periods)

            if df is None or df.empty:
                st.error(info if isinstance(info, str) else "No data found.")
                return

            # --- Model Assumptions UI (Sidebar) ---
            with st.sidebar:
                st.markdown("---")
                with st.expander("🔧 Model Assumptions", expanded=True):
                    # 1. Calc Initial Values for defaults
                    # We run a temporary calc to get the 'natural' values
                    base_val = calculate_valuation(df, info, cashflow)
                    natural_growth = base_val['Avg Growth (%)']
                    natural_multiple = base_val['Current EV/EBITDA'] or 0.0

                    st.caption("Customize the inputs below to see how valuation changes.")

                    custom_growth = st.number_input(
                        "Growth Rate (%)",
                        value=float(f"{natural_growth:.2f}"),
                        step=0.5,
                        help="Affects DCF, PEG, and EBITDA Projection."
                    )

                    custom_multiple = st.number_input(
                        "EV/EBITDA Multiple",
                        value=float(f"{natural_multiple:.2f}"),
                        step=0.5,
                        help="The multiple applied to projected EBITDA."
                    )

                    mr_period_map = {"3-Year Avg": 3, "5-Year Avg": 5, "10-Year Avg": 10}
                    mr_choice = st.selectbox("Mean Reversion P/E", list(mr_period_map.keys()), index=1) # Default 5-Year

                    overrides = {
                        'growth_rate': custom_growth,
                        'ev_ebitda': custom_multiple,
                        'mr_period': mr_period_map[mr_choice]
                    }

            # Calculate Final Valuation with Overrides
            valuation = calculate_valuation(df, info, cashflow, overrides)
            current_price = valuation['Current Price']

            # --- Layout ---

            # 1. Company Header
            st.subheader(f"{info.get('longName', selected_ticker)}")

            # 2. Main Valuation (EV/EBITDA) - Legacy Top View
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"₹{current_price:.2f}")
            with col2:
                st.metric("Entry Price (Buy)", f"₹{valuation['Entry Price']:.2f}")
            with col3:
                st.metric("Target Price (EV/EBITDA)", f"₹{valuation['Target Price']:.2f}")
            with col4:
                rec = valuation['Recommendation']
                color = "green" if rec == "BUY" else "orange"
                st.markdown(f"### Rec: :{color}[{rec}]")

            # --- AI / Comprehensive Valuation Section ---
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
                if con_diff > 15:
                    st.success("Consensus says: **STRONG BUY** (Undervalued)")
                elif con_diff > 0:
                    st.info("Consensus says: **BUY/HOLD** (Fairly Valued)")
                else:
                    st.warning("Consensus says: **WAIT** (Overvalued)")

            st.markdown("### Detailed Model Cards")

            # Display Cards Grid
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
                                if k != 'formula':
                                    st.write(f"**{k}:** {v}")
                    else:
                        st.markdown(f"""
                        <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px; opacity:0.6">
                            <h4>{name}</h4>
                            <h2>N/A</h2>
                            <p>{inputs.get('Error', 'Insufficient Data')}</p>
                        </div>
                        """, unsafe_allow_html=True)


            # 3. Main Data Table (Historical)
            st.markdown("---")
            st.markdown(f"### {frequency} Financials & Analysis")

            # Formatting DataFrame for Display
            display_df = df[['Period', 'Enterprise Value', 'EBITDA', 'EV/EBITDA (X)', 'EPS', 'Close Price', 'Growth in EBITDA (%)']].copy()

            # Add Projected Column logic
            last_period_label = display_df.iloc[0]['Period']
            if period_type == "quarterly":
                try:
                    parts = str(last_period_label).split(' Q')
                    year = int(parts[0])
                    qtr = int(parts[1])
                    if qtr == 4:
                        next_label = f"{year + 1} Q1 (Proj)"
                    else:
                        next_label = f"{year} Q{qtr + 1} (Proj)"
                except:
                    next_label = "Next Qtr (Proj)"
            else:
                try:
                    year = int(last_period_label)
                    next_label = f"{year + 1} (Proj)"
                except:
                    next_label = "Next Year (Proj)"

            new_row = {
                'Period': next_label,
                'Enterprise Value': valuation['Forecasted EV'],
                'EBITDA': valuation['Expected EBITDA'],
                'EV/EBITDA (X)': valuation['Current EV/EBITDA'],
                'Growth in EBITDA (%)': valuation['Avg Growth (%)']
            }

            display_df = pd.concat([pd.DataFrame([new_row]), display_df], ignore_index=True)
            display_df.set_index('Period', inplace=True)
            display_df_t = display_df.transpose()

            st.dataframe(
                display_df_t.style.format("{:,.2f}")
                .set_properties(**{'background-color': '#f0f2f6', 'color': 'black'})
                .highlight_max(axis=1, color='#d1e7dd'),
                use_container_width=True
            )

            # 4. Charts
            st.markdown("### EBITDA Projection")

            # Chart Data
            per_hist = df['Period'].tolist()
            ebitda_hist = df['EBITDA'].tolist()
            per_proj = [next_label]
            ebitda_proj = [valuation['Expected EBITDA']]
            per_all = per_hist[::-1] + per_proj
            ebitda_all = ebitda_hist[::-1] + ebitda_proj

            colors = ['#1f77b4'] * len(per_hist) + ['#2ca02c']

            fig = go.Figure(data=[
                go.Bar(x=per_all, y=ebitda_all, marker_color=colors)
            ])
            fig.update_layout(title="Historical vs Expected EBITDA", xaxis_title="Period", yaxis_title="EBITDA")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
