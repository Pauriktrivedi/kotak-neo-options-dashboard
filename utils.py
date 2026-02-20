import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_data(df):
    """
    Cleans and normalizes NSE data.
    - Converts columns to numeric.
    - Filters out non-stock entries (priority != 0).
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Columns to ensure are numeric
    numeric_cols = [
        'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 
        'change', 'pChange', 'totalTradedVolume', 'totalTradedValue',
        'yearHigh', 'yearLow'
    ]
    
    # Work on a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # The API response for indices usually includes the index itself with priority 1 or some other identifier
    # Actual stocks usually have priority 0 or are marked as 'EQ' (Equity)
    if 'priority' in df.columns:
        # Keep only the stocks, not the index summary if present in the data list
        df = df[df['priority'] == 0]
        
    return df

def update_history(current_history, new_df, max_points=100):
    """
    Updates the in-memory historical data.
    - current_history: DataFrame containing previous records.
    - new_df: Current snapshot of data.
    - max_points: Maximum number of historical points to keep per symbol.
    """
    if new_df.empty:
        return current_history
    
    # Select only necessary columns for history to save memory
    cols_to_keep = ['symbol', 'lastPrice', 'pChange', 'totalTradedVolume', 'fetchTimestamp']
    available_cols = [c for c in cols_to_keep if c in new_df.columns]
    snapshot = new_df[available_cols].copy()
    
    if current_history.empty:
        return snapshot
    
    updated_history = pd.concat([current_history, snapshot], ignore_index=True)
    
    # Keep only the last max_points for each symbol
    updated_history = updated_history.groupby('symbol').tail(max_points).reset_index(drop=True)
    
    return updated_history

def get_top_gainers(df, n=5):
    if df.empty: return pd.DataFrame()
    return df.sort_values(by='pChange', ascending=False).head(n)

def get_top_losers(df, n=5):
    if df.empty: return pd.DataFrame()
    return df.sort_values(by='pChange', ascending=True).head(n)
