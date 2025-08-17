# main.py
# The core code for the Manny Finance MVP (Definitive Final Version)
# As of: August 17, 2025, Chennai

import streamlit as st
import yfinance as yf
import pandas as pd
# --- CHANGE 1: Import BOTH the endpoint and the chat wrapper ---
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage
import os

# --- Page Configuration ---
st.set_page_config(page_title="Manny Finance MVP", layout="wide")
st.title("Manny Finance MVP 🚀")
st.write("A conversational AI analyst for the Indian stock market (Powered by Open Source AI).")

# --- API Key Management ---
api_key_input = st.sidebar.text_input("Enter your Hugging Face API Token", type="password")
if api_key_input:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key_input

# --- Helper Function: Data Fetching (No changes) ---
@st.cache_data(ttl=900)
def get_stock_info(ticker):
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

# --- AI Core Function ---
def get_ai_response(data, question):
    """Generates an AI response using a chat-based model on Hugging Face."""
    if not data:
        return "Could not generate a response as data fetching failed."
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        return "Hugging Face API Token is not set. Please enter it in the sidebar."

    repo_id = "HuggingFaceH4/zephyr-7b-beta"
    
    # --- CHANGE 2: The Correct Assembly ---
    # First, define the connection to the Hugging Face model endpoint.
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_new_tokens=512,
        temperature=0.1,
    )
    
    # Second, wrap the endpoint connection with the ChatHuggingFace class.
    # The error told us the 'llm' field was required, so we provide it.
    chat_model = ChatHuggingFace(llm=llm)

    # Format the prompt as a series of messages for the chat model
    system_prompt = """You are Manny, an expert financial analyst AI assistant for the Indian market. Your role is to provide clear, concise, and helpful answers based ONLY on the context data provided. Do not use any external knowledge or make up information. If the answer cannot be found in the context, clearly state "The answer is not available in the provided data." """
    human_prompt = f"CONTEXT DATA:\n{str(data)}\n\nUSER'S QUESTION:\n{question}"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    try:
        result = chat_model.invoke(messages)
        return result.content
    except Exception as e:
        st.error(f"An error occurred while communicating with the AI model: {e}")
        return "Sorry, I was unable to generate a response. This could be a temporary issue with the AI service. Please try again."

# --- Streamlit Application UI (No changes) ---
st.subheader("Analyze an Indian Stock")
ticker_input = st.text_input("Enter the NSE/BSE Ticker (e.g., RELIANCE.NS, INFY.NS, HDFCBANK.BO)", "INFY.NS")
question_input = st.text_input("What is the company's main business and what is its P/E ratio?")

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
                ai_answer = get_ai_response(stock_data, question_input)
            st.subheader("🤖 Manny's Answer:")
            st.markdown(ai_answer)