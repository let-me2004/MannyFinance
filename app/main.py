# app/main.py
# The definitive, final version for the Manny Finance MVP.
# This file includes fixes for Python imports and Streamlit state management.
# As of: August 17, 2025, Chennai

# --- FIX 1: The Definitive Import Fix ---
# This block programmatically adds the project's root directory to Python's path.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- END OF IMPORT FIX ---

import streamlit as st

# Import our separated logic using the absolute imports that now work
from app.utils import get_stock_info
from app.ai_core import get_ai_response

# --- Page Configuration ---
st.set_page_config(page_title="Manny Finance MVP", layout="wide")
st.title("Manny Finance MVP 🚀")
st.write("A conversational AI analyst for the Indian stock market (Powered by Open Source AI).")

# --- FIX 2: Session State for Robustness ---
# Initialize Session State to hold the AI answer.
if 'ai_answer' not in st.session_state:
    st.session_state.ai_answer = ""

# --- API Key Management ---
api_key_input = st.sidebar.text_input("Enter your Hugging Face API Token", type="password")
if api_key_input:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key_input

# --- Streamlit Application UI ---
st.subheader("Analyze an Indian Stock")
ticker_input = st.text_input("Enter the NSE/BSE Ticker (e.g., RELIANCE.NS, INFY.NS, HDFCBANK.BO)", "INFY.NS")
question_input = st.text_input("What would you like to know?", "What is the company's main business and what is its P/E ratio?")

if st.button("Ask Manny"):
    if not ticker_input:
        st.error("Please enter a stock ticker.")
    elif not api_key_input:
        st.error("Please enter your Hugging Face API Token in the sidebar to begin.")
    else:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            stock_data = get_stock_info(ticker_input)
        
        if stock_data:
            st.subheader("📊 Raw Data Fetched from yfinance:")
            st.json(stock_data)
            with st.spinner("Manny is analyzing the data..."):
                # Store the result directly into the session state
                st.session_state.ai_answer = get_ai_response(stock_data, question_input)
        else:
            # Clear previous answer if data fetching fails
            st.session_state.ai_answer = ""

# --- Display the AI's Answer from Session State ---
if st.session_state.ai_answer:
    st.subheader("🤖 Manny's Answer:")
    st.markdown(st.session_state.ai_answer)