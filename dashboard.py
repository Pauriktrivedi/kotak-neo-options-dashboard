import streamlit as st
import pandas as pd
import time
from fetcher import NSEFetcher
from utils import clean_data, update_history, get_top_gainers, get_top_losers
import plotly.express as px

st.set_page_config(page_title="NSE Live Dashboard", layout="wide")

# Initialize Fetcher and State in session_state so they persist across reruns
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = NSEFetcher()
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame()
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None

# Sidebar Controls
st.sidebar.title("NSE Dashboard Settings")
index_choice = st.sidebar.selectbox(
    "Select Index", 
    ["NIFTY 50", "NIFTY NEXT 50", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO", "NIFTY PHARMA"]
)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)

if st.sidebar.button("Clear History"):
    st.session_state.history = pd.DataFrame()
    st.rerun()

# Main Title
st.title(f"Live NSE Market Dashboard - {index_choice}")

# Data Fetching Container
def load_data():
    df_raw = st.session_state.fetcher.fetch_equity_market_data(index_choice)
    df_cleaned = clean_data(df_raw)
    if not df_cleaned.empty:
        st.session_state.history = update_history(st.session_state.history, df_cleaned)
        st.session_state.last_update_time = time.strftime('%H:%M:%S')
        return df_cleaned
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # Top Row Metrics
    m1, m2, m3, m4 = st.columns(4)
    
    avg_pchange = df['pChange'].mean()
    m1.metric("Avg % Change", f"{avg_pchange:.2f}%")
    
    gainer = get_top_gainers(df, 1).iloc[0]
    m2.metric("Top Gainer", gainer['symbol'], f"{gainer['pChange']}%")
    
    loser = get_top_losers(df, 1).iloc[0]
    m3.metric("Top Loser", loser['symbol'], f"{loser['pChange']}%")
    
    m4.metric("Last Update", st.session_state.last_update_time)

    # Historical Trends
    st.divider()
    st.subheader("Performance Trends")
    
    if len(st.session_state.history) > 0:
        # Filter history for top symbols to keep chart clean
        top_symbols = get_top_gainers(df, 5)['symbol'].tolist()
        plot_data = st.session_state.history[st.session_state.history['symbol'].isin(top_symbols)]
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            fig_price = px.line(
                plot_data, x='fetchTimestamp', y='lastPrice', color='symbol',
                title="Price Trend (Top 5 Current Gainers)",
                labels={'fetchTimestamp': 'Time', 'lastPrice': 'Price'}
            )
            st.plotly_chart(fig_price, width='stretch')
            
        with col_c2:
            fig_pchange = px.line(
                plot_data, x='fetchTimestamp', y='pChange', color='symbol',
                title="% Change Trend (Top 5 Current Gainers)",
                labels={'fetchTimestamp': 'Time', 'pChange': '% Change'}
            )
            st.plotly_chart(fig_pchange, width='stretch')
    else:
        st.info("Collecting historical data points for trends...")

    # Data Table
    st.divider()
    st.subheader("Current Market Snapshot")
    
    # Highlight positive/negative changes
    def color_pchange(val):
        color = 'green' if val > 0 else 'red' if val < 0 else 'white'
        return f'color: {color}'

    display_df = df[['symbol', 'lastPrice', 'change', 'pChange', 'totalTradedVolume', 'dayHigh', 'dayLow']]
    st.dataframe(
        display_df.style.map(color_pchange, subset=['pChange', 'change']),
        width='stretch',
        hide_index=True
    )

else:
    st.warning("No data available. Market might be closed or NSE is throttling requests.")
    if st.button("Retry Now"):
        st.rerun()

# Auto-refresh mechanism
st.caption(f"Next refresh in {refresh_interval} seconds...")
time.sleep(refresh_interval)
st.rerun()
