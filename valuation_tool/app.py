import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from valuation_tool.engine import get_company_data, calculate_valuation
from valuation_tool.tickers import TICKERS

st.set_page_config(page_title="Valuation Dashboard", layout="wide")

def main():
    st.title("Valuation Dashboard")
    st.markdown("Search for an NSE stock to view its valuation based on EBITDA/EV multiples.")

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
        with st.spinner(f"Fetching {frequency} data for {selected_ticker}..."):
            df, info = get_company_data(selected_ticker, period_type=period_type, num_periods=num_periods)

            if df is None or df.empty:
                st.error(info if isinstance(info, str) else "No data found.")
                return

            valuation = calculate_valuation(df, info)

            # --- Layout ---

            # 1. Company Header
            st.subheader(f"{info.get('longName', selected_ticker)}")

            # 2. Valuation Summary Cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Current Price", f"₹{valuation['Current Price']:.2f}")
            with col2:
                st.metric("Entry Price (Buy)", f"₹{valuation['Entry Price']:.2f}")
            with col3:
                st.metric("Target Price", f"₹{valuation['Target Price']:.2f}")
            with col4:
                rec = valuation['Recommendation']
                color = "green" if rec == "BUY" else "orange"
                st.markdown(f"### Recommendation: :{color}[{rec}]")

            # 3. Main Data Table
            st.markdown(f"### {frequency} Financials & Valuation")

            # Formatting DataFrame for Display
            display_df = df[['Period', 'Enterprise Value', 'EBITDA', 'EV/EBITDA (X)', 'Growth in EBITDA (%)']].copy()

            # Add Projected Column
            # Create a new row for the "Projected" period

            # Determine label for projected period
            last_period_label = display_df.iloc[0]['Period'] # Newest is top
            if period_type == "quarterly":
                # Try to parse "2025 Q2" -> Next is 2025 Q3
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
                # Annual
                try:
                    year = int(last_period_label)
                    next_label = f"{year + 1} (Proj)"
                except:
                    next_label = "Next Year (Proj)"


            new_row = {
                'Period': next_label,
                'Enterprise Value': valuation['Forecasted EV'],
                'EBITDA': valuation['Expected EBITDA'], # Note: For Quarterly, this is Qtr EBITDA. EV calc handled appropriately.
                'EV/EBITDA (X)': valuation['Current EV/EBITDA'],
                'Growth in EBITDA (%)': valuation['Avg Growth (%)']
            }

            # Add to dataframe at the top
            display_df = pd.concat([pd.DataFrame([new_row]), display_df], ignore_index=True)

            # Transpose to match screenshot (Periods as Columns)
            display_df.set_index('Period', inplace=True)
            display_df_t = display_df.transpose()

            # Styling
            st.dataframe(
                display_df_t.style.format("{:,.2f}")
                .set_properties(**{'background-color': '#f0f2f6', 'color': 'black'})
                .highlight_max(axis=1, color='#d1e7dd'),
                use_container_width=True
            )

            # 4. Valuation Details & Chart
            st.markdown("---")
            c1, c2 = st.columns([1, 2])

            with c1:
                st.markdown("### Valuation Logic")
                st.write(f"**Avg Growth:** {valuation['Avg Growth (%)']:.2f}%")
                st.write(f"**Expected EBITDA:** ₹{valuation['Expected EBITDA']:,.2f}")
                if valuation.get('Is Quarterly'):
                     st.caption("(Quarterly Expected. Annualized for EV calc.)")

                st.write(f"**Forecasted EV:** ₹{valuation['Forecasted EV']:,.2f}")
                st.write(f"**Shares Outstanding:** {info.get('sharesOutstanding'):,}")
                st.divider()
                st.write(f"**Target Price:** ₹{valuation['Target Price']:.2f}")
                st.write(f"**Margin of Safety:** 25%")
                st.write(f"**Entry Price:** ₹{valuation['Entry Price']:.2f}")

            with c2:
                st.markdown("### EBITDA Projection")

                # Chart Data
                # Use original df for history
                per_hist = df['Period'].tolist()
                ebitda_hist = df['EBITDA'].tolist()

                # Projected
                per_proj = [next_label]
                ebitda_proj = [valuation['Expected EBITDA']]

                # Combine (Reverse hist so it's ascending left to right)
                # df is Descending (Newest first). So reverse it.
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
