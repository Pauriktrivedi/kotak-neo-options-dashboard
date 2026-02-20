import requests
import pandas as pd
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NSEFetcher:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._init_session()

    def _init_session(self):
        """Initializes the session by visiting the home page to get cookies."""
        logger.info("Initializing NSE session...")
        try:
            # First hit the main page to get cookies
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            # Sometimes another hit to a common page helps
            self.session.get(f"{self.base_url}/market-data/live-equity-market", timeout=15)
            logger.info("Session initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing session: {e}")

    def fetch_equity_market_data(self, category="NIFTY 50"):
        """
        Fetches market data for a given category.
        Categories can be: 'NIFTY 50', 'NIFTY NEXT 50', 'NIFTY BANK', etc.
        """
        category_encoded = category.replace(' ', '%20')
        url = f"{self.base_url}/api/equity-stockIndices?index={category_encoded}"
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code in [401, 403]:
                logger.warning(f"Access denied (status {response.status_code}). Retrying after session re-init...")
                self._init_session()
                response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data. Status code: {response.status_code}")
                return pd.DataFrame()

            data = response.json()
            if 'data' not in data:
                logger.error("Response JSON does not contain 'data' key.")
                return pd.DataFrame()
                
            df = pd.DataFrame(data['data'])
            # Add a timestamp for when this data was fetched
            df['fetchTimestamp'] = pd.Timestamp.now()
            return df
            
        except Exception as e:
            logger.error(f"Exception while fetching data for {category}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    fetcher = NSEFetcher()
    df = fetcher.fetch_equity_market_data("NIFTY 50")
    if not df.empty:
        print(f"Successfully fetched {len(df)} rows for NIFTY 50.")
        print(df[['symbol', 'lastPrice', 'pChange']].head())
    else:
        print("Failed to fetch data.")
