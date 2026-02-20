import time
import pandas as pd
import random
import logging
from datetime import datetime, timedelta

try:
    from neo_api_client import NeoAPI
except ImportError:
    NeoAPI = None

class KotakNeoClient:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.is_logged_in = False
        self.instruments = pd.DataFrame()
        
    def login(self, mobile_number=None, mpin=None, api_key=None, api_secret=None, ucc=None, totp=None):
        if self.config.DEMO_MODE:
            logging.info("Running in DEMO MODE. No actual login performed.")
            self.is_logged_in = True
            return True, "Success (Demo Mode)"
        
        if NeoAPI is None:
            return False, "NeoAPI client not installed."
        
        try:
            self.client = NeoAPI(
                consumer_key=api_key or self.config.API_KEY,
                environment='prod'
            )
            
            # Step 1: Login with Mobile and TOTP
            self.client.login(
                mobile_number=mobile_number or self.config.MOBILE_NUMBER,
                password=self.config.PASSWORD
            )
            # Some versions use totp_login
            # self.client.totp_login(mobile_number=mobile_number, ucc=ucc, totp=totp)
            
            # Step 2: Validate with MPIN
            self.client.session_2fa(mpin=mpin or self.config.PASSWORD)
            
            self.is_logged_in = True
            return True, "Logged in successfully"
        except Exception as e:
            return False, f"Login failed: {str(e)}"

    def get_instruments(self):
        if self.config.DEMO_MODE:
            return self._generate_mock_instruments()
        
        try:
            # Fetch instrument master for NFO
            self.client.get_scrip_master(exchange="NFO")
            # The SDK usually saves this to a file or returns it.
            # We'll assume it returns a path or we read it from the default location.
            # For brevity, let's assume we can load it.
            df = pd.read_csv("nfo_scrip.csv")
            return df
        except Exception as e:
            logging.error(f"Failed to fetch instruments: {e}")
            return pd.DataFrame()

    def _generate_mock_instruments(self):
        # Generate some mock NIFTY/BANKNIFTY option instruments
        data = []
        indices = ["NIFTY", "BANKNIFTY"]
        spot_prices = {"NIFTY": 22000, "BANKNIFTY": 47000}
        
        # Current Thursday or next Thursday for expiry
        today = datetime.now()
        days_until_thursday = (3 - today.weekday()) % 7
        expiry = (today + timedelta(days=days_until_thursday)).strftime("%d%b%y").upper()
        
        for index in indices:
            spot = spot_prices[index]
            step = 50 if index == "NIFTY" else 100
            # Generate 10 strikes above and below ATM
            atm = round(spot / step) * step
            for i in range(-10, 11):
                strike = atm + (i * step)
                for option_type in ["CE", "PE"]:
                    data.append({
                        "trading_symbol": f"{index}{expiry}{strike}{option_type}",
                        "symbol": index,
                        "strike_price": float(strike),
                        "option_type": option_type,
                        "expiry": expiry,
                        "instrument_token": f"{index}_{strike}_{option_type}",
                        "lot_size": 50 if index == "NIFTY" else 15
                    })
        return pd.DataFrame(data)

    def subscribe_quotes(self, tokens, callback):
        from live_data import LiveDataManager
        ldm = LiveDataManager()
        
        if self.config.DEMO_MODE:
            if not hasattr(self, 'subscribed_tokens'):
                self.subscribed_tokens = set()
            
            self.subscribed_tokens.update(tokens)

            # In demo mode, we'll start a background simulator
            import threading
            def simulate():
                while True:
                    # Use a copy of tokens to avoid runtime error during iteration
                    current_tokens = list(self.subscribed_tokens)
                    for token in current_tokens:
                        # Randomize some values
                        price = 100 + random.uniform(-5, 5)
                        oi = 100000 + random.randint(-5000, 5000)
                        msg = {
                            "token": token,
                            "lp": price,
                            "oi": oi,
                            "v": random.randint(1000, 5000),
                            "bp": price - 0.5,
                            "ap": price + 0.5
                        }
                        ldm.update_tick(token, msg)
                    time.sleep(1)
            
            if not hasattr(self, '_simulator_started'):
                thread = threading.Thread(target=simulate, daemon=True)
                thread.start()
                self._simulator_started = True
            return
        
        # Real implementation:
        # self.client.subscribe(instrument_tokens=tokens, callback=callback)
        pass
