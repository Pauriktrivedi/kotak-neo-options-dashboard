# Live NSE Market Dashboard

A real-time Python dashboard that fetches market data directly from the NSE website and displays it dynamically using Streamlit and Plotly.

## Features
- **Live NSE Data**: Fetches data for various indices (NIFTY 50, NIFTY BANK, etc.) directly from NSE API.
- **In-Memory Storage**: Uses pandas DataFrames to maintain rolling historical data during runtime (no Excel or file storage).
- **Auto-Refresh**: Dashboard updates automatically at a configurable interval (5–60 seconds).
- **Interactive Visualizations**: Includes live data tables with color-coded changes and trend charts for price and percentage change.
- **Robust Fetching**: Handles NSE anti-bot protection using proper headers, session management, and automatic retries with Brotli decoding.

## Project Structure
- `dashboard.py`: The Streamlit application containing the UI and refresh logic.
- `fetcher.py`: Modular component for handling requests to NSE and session management.
- `utils.py`: Utility functions for data cleaning, metric calculation, and historical data management.
- `requirements.txt`: List of required Python libraries.

## How it Works
### Data Fetching
The `NSEFetcher` class initializes a `requests.Session` with browser-like headers. It first visits the NSE home page to obtain necessary cookies and then makes requests to the JSON API endpoints used by the NSE website. It specifically handles `401` and `403` status codes by re-initializing the session. Data is decoded using `brotli` to handle the compression used by NSE.

### Dashboard Refresh
The dashboard uses Streamlit's `st.rerun()` mechanism combined with `time.sleep()` to create a live update loop. Historical data is persisted across reruns using `st.session_state`, allowing the trend charts to populate as long as the application is running.

## Setup and Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

3. **Access the App**:
   Open your browser and navigate to `http://localhost:8501`.

## Assumptions and Limitations
- **Market Hours**: Data is live during NSE market hours (9:15 AM to 3:30 PM IST, Monday-Friday). Outside these hours, the dashboard will show the last available snapshot.
- **NSE Throttling**: NSE may occasionally block or throttle requests if the refresh interval is too aggressive or if many requests originate from the same IP. The fetcher includes basic retry logic, but persistent blocks may require manual session reset (or waiting).
- **Memory Usage**: Historical data is kept in memory. While it is limited to a rolling window (default 100 points), keeping the app running for extremely long periods with many symbols may increase memory consumption.
