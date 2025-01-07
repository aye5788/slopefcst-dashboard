import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# API Configuration
API_TOKEN = "a2e070f3-4a5b-4e71-8290-839ae321f64b"  # Replace with your ORATS API token
BASE_URL = "https://api.orats.io/datav2/indicators"

# Function to Fetch Data
def fetch_related_indicators(ticker):
    """
    Fetch slopeFcst and related indicators for the given ticker.
    """
    params = {
        "token": API_TOKEN,
        "ticker": ticker,
        "fields": "slopeFcst,slopeFcstInf,slopeFcst_slope,slopeFcst_slope_ratioTo3dAvg,"
                  "slopeFcst_slope_ratioTo5dAvg,slopeFcst_slope_ratioTo10dAvg,slopeFcst_slope_ratioTo20dAvg"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json().get('data', []))
    else:
        st.error(f"Failed to fetch data for {ticker}. HTTP {response.status_code}")
        return pd.DataFrame()

# Streamlit App Title and Sidebar
st.title("SlopeFcst Interactive Dashboard")
st.sidebar.header("Settings")

# User Input: Ticker Symbol
ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g., AAPL)", value="AAPL")

# Fetch Data
st.write(f"Fetching data for: {ticker}")
data = fetch_related_indicators(ticker)

# Check if Data is Available
if not data.empty:
    # Convert Dates to Datetime Format
    data['tradeDate'] = pd.to_datetime(data['tradeDate'])

    # Display Raw Data
    st.write("Raw Data Table", data)

    # Plot SlopeFcst and Related Indicators
    fig = px.line(data, x='tradeDate', y=['slopeFcst', 'slopeFcst_slope'], 
                  labels={'value': 'Indicator Value', 'variable': 'Indicator', 'tradeDate': 'Date'}, 
                  title=f"SlopeFcst and Slope for {ticker}")
    st.plotly_chart(fig)

    # Add Ranking by Ratios (e.g., 10-Day Moving Average Ratio)
    st.write("Top Indicators by Ratio to Moving Averages")
    ranking_table = data[['tradeDate', 'slopeFcst', 'slopeFcst_slope_ratioTo10dAvg', 'slopeFcst_slope_ratioTo20dAvg']].sort_values(
        by='slopeFcst_slope_ratioTo10dAvg', ascending=False
    )
    st.dataframe(ranking_table)
else:
    st.warning("No data available for the given ticker. Please try another ticker.")
