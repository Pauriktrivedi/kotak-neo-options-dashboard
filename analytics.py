import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime

def calculate_pcr(df):
    total_ce_oi = df['CE_OI'].sum()
    total_pe_oi = df['PE_OI'].sum()
    pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
    return pcr, total_ce_oi, total_pe_oi

def calculate_max_pain(df):
    strikes = df.index.values
    ce_oi = df['CE_OI'].values
    pe_oi = df['PE_OI'].values
    
    total_loss = []
    for s in strikes:
        loss = 0
        for i in range(len(strikes)):
            # Loss for CE holders if expiry is s
            if strikes[i] < s:
                loss += ce_oi[i] * (s - strikes[i])
            # Loss for PE holders if expiry is s
            if strikes[i] > s:
                loss += pe_oi[i] * (strikes[i] - s)
        total_loss.append(loss)
    
    max_pain_strike = strikes[np.argmin(total_loss)]
    return max_pain_strike

def get_support_resistance(df):
    resistance_strike = df['CE_OI'].idxmax()
    support_strike = df['PE_OI'].idxmax()
    return support_strike, resistance_strike

def classify_oi_buildup(price_change, oi_change):
    if price_change > 0 and oi_change > 0:
        return "Long Build-up"
    elif price_change < 0 and oi_change > 0:
        return "Short Build-up"
    elif price_change > 0 and oi_change < 0:
        return "Short Covering"
    elif price_change < 0 and oi_change < 0:
        return "Long Unwinding"
    else:
        return "Neutral"

# Basic Black-Scholes for IV and Greeks
def black_scholes(S, K, T, r, sigma, option_type='CE'):
    if T <= 0: return 0, 0, 0, 0, 0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'CE':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'CE' else -d2)
    
    return price, delta, gamma, vega, theta

def find_iv(market_price, S, K, T, r, option_type='CE'):
    # Newton-Raphson to find IV
    sigma = 0.2
    for i in range(100):
        price, delta, gamma, vega, theta = black_scholes(S, K, T, r, sigma, option_type)
        diff = market_price - price
        if abs(diff) < 0.01:
            return sigma
        if vega == 0: break
        sigma = sigma + diff / vega
        if sigma <= 0: sigma = 0.01
    return sigma
