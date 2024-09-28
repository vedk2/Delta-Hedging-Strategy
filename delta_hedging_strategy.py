
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt

# Black-Scholes delta calculation
def calculate_delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d1)
    elif option_type == 'put':
        return norm.cdf(d1) - 1

# Fetch stock and option data
def fetch_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Hedging function
def delta_hedging(stock_data, K, T, r, sigma, option_type='call'):
    hedge_positions = []
    portfolio_values = []
    previous_delta = 0
    
    for index, row in stock_data.iterrows():
        S = row['Close']
        current_delta = calculate_delta(S, K, T, r, sigma, option_type)
        shares_to_trade = current_delta - previous_delta
        hedge_positions.append(shares_to_trade)
        portfolio_value = current_delta * S
        portfolio_values.append(portfolio_value)
        previous_delta = current_delta
        
        # Decrease time to expiration
        T -= 1 / 252
    
    stock_data['Hedge Positions'] = hedge_positions
    stock_data['Portfolio Value'] = portfolio_values
    return stock_data

# Example parameters
ticker = 'AAPL'
start_date = '2023-01-01'
end_date = '2023-12-31'
strike_price = 150
time_to_expiration = 30 / 252  # 30 days in trading years
risk_free_rate = 0.05
volatility = 0.2

# Fetch data and apply hedging
data = fetch_data(ticker, start_date, end_date)
hedged_data = delta_hedging(data, strike_price, time_to_expiration, risk_free_rate, volatility)

# Plot results
plt.figure(figsize=(12, 6))
plt.plot(hedged_data.index, hedged_data['Close'], label='Stock Price')
plt.plot(hedged_data.index, hedged_data['Portfolio Value'], label='Hedged Portfolio Value')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.title('Delta Hedging Strategy Performance')
plt.show()
