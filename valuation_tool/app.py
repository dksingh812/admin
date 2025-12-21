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
        with st.spinner(f"Fetching {frequency} data for {selected_ticker}..."):
            df, info, cashflow = get_company_data(selected_ticker, period_type=period_type, num_periods=num_periods)

            if df is None or df.empty:
                st.error(info if isinstance(info, str) else "No data found.")
                return

            valuation = calculate_valuation(df, info, cashflow)

            # --- Layout ---

            # 1. Company Header
            st.subheader(f"{info.get('longName', selected_ticker)}")

            # 2. Main Valuation (EV/EBITDA)
            col1, col2, col3, col4 = st.columns(4)

            current_price = valuation['Current Price']

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

            # Prepare Data for Comparison
            model_data = []

            # Helper to add model if valid
            def add_model(name, target, desc):
                if target and not np.isnan(target):
                    diff = ((target - current_price) / current_price) * 100
                    status = "Undervalued" if diff > 0 else "Overvalued"
                    model_data.append({
                        "Model": name,
                        "Estimated Value (₹)": f"{target:,.2f}",
                        "Upside/Downside": f"{diff:+.2f}%",
                        "Status": status,
                        "Description": desc
                    })

            add_model("EV / EBITDA", valuation['Target Price'], "Based on operating profitability (Good for debt-heavy/manufacturing)")
            add_model("Graham Number", valuation['Graham Number'], "Benjamin Graham's 'Safety' price (Strict Value)")
            add_model("DCF (Discounted Cash Flow)", valuation['DCF Value'], "Intrinsic value based on future free cash flow (Gold Standard)")
            add_model("PEG Fair Value", valuation['PEG Fair Value'], "Peter Lynch's Growth-adjusted value (Good for high growth)")

            if model_data:
                res_df = pd.DataFrame(model_data)

                # Consensus
                valid_targets = [float(d["Estimated Value (₹)"].replace(",","")) for d in model_data]
                consensus = sum(valid_targets) / len(valid_targets)
                con_diff = ((consensus - current_price) / current_price) * 100

                c1, c2 = st.columns([2, 1])
                with c1:
                    st.dataframe(res_df, use_container_width=True)
                with c2:
                    st.markdown("### Consensus Target")
                    st.metric("Average Fair Value", f"₹{consensus:,.2f}", f"{con_diff:+.2f}%")

                    if con_diff > 15:
                        st.success("Consensus: STRONG BUY")
                    elif con_diff > 0:
                        st.info("Consensus: BUY/HOLD")
                    else:
                        st.warning("Consensus: WAIT / OVERVALUED")
            else:
                st.warning("Not enough data to run advanced models.")

            # 3. Main Data Table (Historical)
            st.markdown("---")
            st.markdown(f"### {frequency} Financials & Analysis")

            # Formatting DataFrame for Display
            display_df = df[['Period', 'Enterprise Value', 'EBITDA', 'EV/EBITDA (X)', 'Growth in EBITDA (%)']].copy()

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
