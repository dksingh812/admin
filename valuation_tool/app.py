import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from valuation_tool.engine import get_company_data, calculate_valuation
from valuation_tool.tickers import TICKERS

st.set_page_config(page_title="Valuation Dashboard", layout="wide")

def main():
    st.title("Valuation Dashboard")
    st.markdown("Search for an NSE stock to view its 5-year valuation based on EBITDA/EV multiples.")

    # Sidebar / Top Selection
    selected_ticker = st.selectbox("Select Company:", TICKERS, index=TICKERS.index("RELIANCE.NS") if "RELIANCE.NS" in TICKERS else 0)

    if st.button("Analyze"):
        with st.spinner(f"Fetching data for {selected_ticker}..."):
            df, info = get_company_data(selected_ticker)

            if df is None or df.empty:
                st.error(info)
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
            st.markdown("### Historical Financials & Valuation")

            # Formatting DataFrame for Display
            display_df = df[['Year', 'Enterprise Value', 'EBITDA', 'EV/EBITDA (X)', 'Growth in EBITDA (%)']].copy()

            # Add Projected Column
            # Create a new row for the "Projected" year
            projected_year_label = "2026 (Est)" # Or "Projected"
            # If the latest actual year is 2025, projected is 2026.
            # We can just check the max year in df.
            latest_year = display_df['Year'].max()
            projected_year = latest_year + 1

            new_row = {
                'Year': projected_year,
                'Enterprise Value': valuation['Forecasted EV'],
                'EBITDA': valuation['Expected EBITDA'],
                'EV/EBITDA (X)': valuation['Current EV/EBITDA'], # Using current/entry multiple
                'Growth in EBITDA (%)': valuation['Avg 3Y Growth (%)'] # Expected growth
            }

            # Add to dataframe at the top (since we sort descending)
            display_df = pd.concat([pd.DataFrame([new_row]), display_df], ignore_index=True)

            # Transpose to match screenshot (Years as Columns)
            display_df.set_index('Year', inplace=True)
            display_df_t = display_df.transpose()

            # Styling
            # 1. Background color for rows (Green/Yellow highlights mentioned in prompt)
            # The prompt mentioned "highlighted Green/Yellow rows for the final results" (Target Price, Entry Price).
            # Those are in the Summary section, but let's style the main table rows with alternating colors.
            # 2. Header Colors (Orange/Blue). Streamlit supports Styler.

            def style_dataframe(styler):
                # Header styling is tricky in Streamlit, it often overrides it.
                # We focus on cell styling.
                styler.format("{:,.2f}")
                styler.background_gradient(cmap="Blues", axis=None, subset=pd.IndexSlice[:, display_df_t.columns])
                return styler

            # Custom styling using function
            st.dataframe(
                display_df_t.style.format("{:,.2f}")
                .set_properties(**{'background-color': '#f0f2f6', 'color': 'black'})
                .highlight_max(axis=1, color='#d1e7dd'), # Highlight max values slightly green
                use_container_width=True
            )

            # 4. Valuation Details & Chart
            st.markdown("---")
            c1, c2 = st.columns([1, 2])

            with c1:
                st.markdown("### Valuation Logic")
                st.write(f"**Avg 3Y Growth:** {valuation['Avg 3Y Growth (%)']:.2f}%")
                st.write(f"**Expected EBITDA:** ₹{valuation['Expected EBITDA']:,.2f}")
                st.write(f"**Forecasted EV:** ₹{valuation['Forecasted EV']:,.2f}")
                st.write(f"**Shares Outstanding:** {info.get('sharesOutstanding'):,}")
                st.divider()
                st.write(f"**Target Price:** ₹{valuation['Target Price']:.2f}")
                st.write(f"**Margin of Safety:** 25%")
                st.write(f"**Entry Price:** ₹{valuation['Entry Price']:.2f}")

            with c2:
                st.markdown("### EBITDA Projection")

                # Prepare Chart Data
                # Historical
                # Filter out the projected row we just added to display_df for the 'historical' part of chart
                # Actually, display_df has it. Let's use the original 'df' for history.

                years_hist = df['Year'].tolist()
                ebitda_hist = df['EBITDA'].tolist()

                # Projected
                years_proj = [projected_year]
                ebitda_proj = [valuation['Expected EBITDA']]

                # Combine (Reverse hist so it's ascending left to right)
                years_all = years_hist[::-1] + years_proj
                ebitda_all = ebitda_hist[::-1] + ebitda_proj

                colors = ['#1f77b4'] * len(years_hist) + ['#2ca02c'] # Blue for hist, Green for proj

                fig = go.Figure(data=[
                    go.Bar(x=years_all, y=ebitda_all, marker_color=colors)
                ])
                fig.update_layout(title="Historical vs Expected EBITDA", xaxis_title="Year", yaxis_title="EBITDA")
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
