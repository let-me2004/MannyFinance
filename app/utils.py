# utils.py
# Contains utility functions, starting with our data fetcher.

import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=900)
def get_stock_info(ticker):
    """
    Fetches key stock information using the yfinance library with improved error handling.
    """
    try:
        stock = yf.Ticker(ticker)
        if stock.history(period="1d").empty:
            st.error(f"No data found for ticker '{ticker}'. It might be delisted or an invalid ticker. Please check.")
            return None
        info = stock.info
        key_info = {
            "Company Name": info.get("longName"), "Sector": info.get("sector"), "Industry": info.get("industry"),
            "Market Cap": f"₹{info.get('marketCap', 0):,}", "Price-to-Earnings (P/E) Ratio": info.get("trailingPE"),
            "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%", "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"), "Business Summary": info.get("longBusinessSummary"),
        }
        if not key_info["Company Name"]:
            st.warning(f"Successfully fetched ticker '{ticker}', but detailed information is sparse.")
        return key_info
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching data for {ticker}. Error: {e}")
        return None