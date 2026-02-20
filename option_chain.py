import pandas as pd
import numpy as np
from analytics import black_scholes, find_iv

class OptionChainManager:
    def __init__(self, index_symbol):
        self.index_symbol = index_symbol
        self.full_chain = pd.DataFrame()
        self.spot_price = 0.0
        self.atm_strike = 0.0
        self.token_map = {} # token -> (strike, type)
        
    def initialize_chain(self, instruments_df, spot_price):
        self.spot_price = spot_price
        # Filter for the selected index
        df = instruments_df[instruments_df['symbol'] == self.index_symbol].copy()
        
        # Calculate ATM
        if self.index_symbol == "NIFTY":
            step = 50
        else:
            step = 100
        self.atm_strike = round(self.spot_price / step) * step
        
        # Structure the chain
        # Columns: Strike, CE_LTP, CE_OI, CE_CHG_OI, CE_VOL, PE_LTP, PE_OI, PE_CHG_OI, PE_VOL
        strikes = sorted(df['strike_price'].unique())
        self.full_chain = pd.DataFrame(index=strikes)
        self.full_chain.index.name = 'Strike'
        
        # Add metadata like tokens
        for _, row in df.iterrows():
            strike = row['strike_price']
            otype = row['option_type']
            token = row['instrument_token']
            self.full_chain.loc[strike, f'{otype}_token'] = token
            self.token_map[token] = (strike, otype)
            
        # Initialize values
        cols = ['CE_LTP', 'CE_OI', 'CE_CHG_OI', 'CE_VOL', 'CE_BP', 'CE_AP', 'CE_IV', 'CE_Delta',
                'PE_LTP', 'PE_OI', 'PE_CHG_OI', 'PE_VOL', 'PE_BP', 'PE_AP', 'PE_IV', 'PE_Delta']
        for col in cols:
            self.full_chain[col] = 0.0
            
        return self.full_chain

    def update_tick(self, tick):
        token = tick.get('token')
        if token in self.token_map:
            strike, otype = self.token_map[token]
            try:
                if strike in self.full_chain.index:
                    new_ltp = tick.get('lp', 0)
                    new_oi = tick.get('oi', 0)
                    
                    # Calculate changes
                    if self.full_chain.loc[strike, f'{otype}_LTP'] != 0:
                        price_chg = new_ltp - self.full_chain.loc[strike, f'{otype}_LTP']
                        self.full_chain.loc[strike, f'{otype}_CHG_PRICE'] = price_chg
                    
                    if self.full_chain.loc[strike, f'{otype}_OI'] != 0:
                        oi_chg = new_oi - self.full_chain.loc[strike, f'{otype}_OI']
                        self.full_chain.loc[strike, f'{otype}_CHG_OI'] = oi_chg

                    self.full_chain.loc[strike, f'{otype}_LTP'] = new_ltp
                    self.full_chain.loc[strike, f'{otype}_OI'] = new_oi
                    self.full_chain.loc[strike, f'{otype}_VOL'] = tick.get('v', 0)
                    self.full_chain.loc[strike, f'{otype}_BP'] = tick.get('bp', 0)
                    self.full_chain.loc[strike, f'{otype}_AP'] = tick.get('ap', 0)
            except Exception:
                pass

    def calculate_greeks(self, r=0.07, t_days=7):
        T = max(t_days / 365.0, 0.0001)
        for strike in self.full_chain.index:
            for otype in ['CE', 'PE']:
                ltp = self.full_chain.loc[strike, f'{otype}_LTP']
                if ltp > 0:
                    try:
                        iv = find_iv(ltp, self.spot_price, strike, T, r, otype)
                        _, delta, gamma, vega, theta = black_scholes(self.spot_price, strike, T, r, iv, otype)
                        self.full_chain.loc[strike, f'{otype}_IV'] = round(iv * 100, 2)
                        self.full_chain.loc[strike, f'{otype}_Delta'] = round(delta, 3)
                    except Exception:
                        pass

    def get_display_chain(self, range_strikes=10):
        # Return ATM +/- range_strikes
        strikes = sorted(self.full_chain.index)
        try:
            atm_idx = strikes.index(self.atm_strike)
            start_idx = max(0, atm_idx - range_strikes)
            end_idx = min(len(strikes), atm_idx + range_strikes + 1)
            display_strikes = strikes[start_idx:end_idx]
            return self.full_chain.loc[display_strikes]
        except ValueError:
            return self.full_chain.head(range_strikes * 2)
