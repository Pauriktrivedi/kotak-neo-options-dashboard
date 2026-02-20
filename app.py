import streamlit as st
import pandas as pd
import time
from kotak_api import KotakNeoClient
from option_chain import OptionChainManager
from analytics import calculate_pcr, calculate_max_pain, get_support_resistance
from ui_components import render_metric_cards, render_option_chain_table, render_oi_charts, render_oi_heatmap
from live_data import LiveDataManager
import config

st.set_page_config(page_title="Kotak Neo Live Options Dashboard", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if 'client' not in st.session_state:
    st.session_state.client = KotakNeoClient(config)
if 'managers' not in st.session_state:
    st.session_state.managers = {index: OptionChainManager(index) for index in config.INDICES}
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Sidebar
st.sidebar.title("🚀 Kotak Neo Options")
st.sidebar.markdown("---")

demo_mode = st.sidebar.toggle("Demo Mode", value=config.DEMO_MODE)
config.DEMO_MODE = demo_mode

if not st.session_state.client.is_logged_in:
    if demo_mode:
        # Auto-login for demo mode
        st.session_state.client.login()
        st.rerun()
    else:
        st.sidebar.subheader("Login")
        api_key = st.sidebar.text_input("API Key", value=config.API_KEY, type="password")
        api_secret = st.sidebar.text_input("API Secret", value=config.API_SECRET, type="password")
        mobile = st.sidebar.text_input("Mobile", value=config.MOBILE_NUMBER)
        password = st.sidebar.text_input("Password/MPIN", value=config.PASSWORD, type="password")
        
        if st.sidebar.button("Login"):
            success, msg = st.session_state.client.login(mobile, password, api_key, api_secret)
            if success:
                st.sidebar.success(msg)
                st.session_state.initialized = False # Trigger re-init
            else:
                st.sidebar.error(msg)

if st.session_state.client.is_logged_in and not st.session_state.initialized:
    with st.spinner("Fetching instruments and initializing..."):
        instruments = st.session_state.client.get_instruments()
        for index in config.INDICES:
            spot = 22000 if index == "NIFTY" else 47000 # Default/Fetch spot
            st.session_state.managers[index].initialize_chain(instruments, spot)
            
            # Subscribe to tokens
            tokens = []
            df = st.session_state.managers[index].full_chain
            for _, row in df.iterrows():
                if pd.notnull(row['CE_token']): tokens.append(row['CE_token'])
                if pd.notnull(row['PE_token']): tokens.append(row['PE_token'])
            
            def make_callback(idx):
                def callback(tick):
                    st.session_state.managers[idx].update_tick(tick)
                return callback
            
            st.session_state.client.subscribe_quotes(tokens, make_callback(index))
            
        st.session_state.initialized = True

# Main Dashboard
if st.session_state.client.is_logged_in:
    selected_index = st.sidebar.selectbox("Select Index", config.INDICES)
    days_to_expiry = st.sidebar.number_input("Days to Expiry", value=7, min_value=1, max_value=365)
    manager = st.session_state.managers[selected_index]
    
    # Update manager with latest ticks from LiveDataManager
    ldm = LiveDataManager()
    ticks = ldm.get_all_ticks()
    for token, tick in ticks.items():
        manager.update_tick(tick)
    
    # Calculate Greeks periodically (e.g., every 5 seconds to save CPU)
    if time.time() - st.session_state.last_update > 5:
        manager.calculate_greeks(t_days=days_to_expiry)
        st.session_state.last_update = time.time()
        
    # Analytics
    df = manager.full_chain
    pcr, total_ce, total_pe = calculate_pcr(df)
    max_pain = calculate_max_pain(df)
    support, resistance = get_support_resistance(df)
    
    # Header
    st.title(f"📊 {selected_index} Real-Time Dashboard")
    
    # Metrics
    render_metric_cards(manager.spot_price, manager.atm_strike, pcr, max_pain, support, resistance)
    
    # Layout
    tab1, tab2, tab3 = st.tabs(["Option Chain", "OI Analytics", "Alerts & Signals"])
    
    with tab1:
        render_option_chain_table(manager.get_display_chain(), manager.atm_strike)
        
    with tab2:
        render_oi_charts(df)
        render_oi_heatmap(df)
        
    with tab3:
        st.subheader("Smart Alerts")
        if pcr > 1.2:
            st.warning(f"Bullish sentiment detected: PCR is {pcr:.2f}")
        elif pcr < 0.8:
            st.error(f"Bearish sentiment detected: PCR is {pcr:.2f}")
        else:
            st.info("Sentiment is Neutral")
            
        # Major OI Shift
        st.info("No major OI shifts detected in last 5 mins (Demo)")

    # Auto-refresh logic
    time.sleep(config.UPDATE_INTERVAL)
    st.rerun()

else:
    st.warning("Please login or enable Demo Mode to view the dashboard.")
    st.image("https://via.placeholder.com/800x400.png?text=Kotak+Neo+Options+Dashboard", use_container_width=True)
