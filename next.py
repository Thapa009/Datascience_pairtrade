import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Step 1: Fetch all NASDAQ tickers 
def get_all_nasdaq_tickers():
   
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'TSLA', 'NVDA', 'ADBE', 'PYPL']

# Step 2: Fetch historical data
def fetch_historical_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data

# Step 3: Calculate correlations and identify pairs
def identify_pairs(data, threshold=0.9):
    returns = data.pct_change().dropna()
    correlation_matrix = returns.corr()
    pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            if correlation_matrix.iloc[i, j] > threshold:
                pairs.append((correlation_matrix.columns[i], correlation_matrix.columns[j]))
    return pairs

# Step 4: Handle suspensions and delistings
def check_stock_status(ticker, date):
    
    return 'active'

def handle_suspensions_and_delistings(data, tickers):
    for ticker in tickers:
        for date in data.index:
            status = check_stock_status(ticker, date)
            if status == 'suspended':
                continue
            elif status == 'delisted':
                data[ticker].loc[date:] = 0
                break
    return data

# Step 5: Implement pair trading strategy
def zscore(series):
    return (series - series.mean()) / np.std(series)

def pair_trading_strategy(data, pairs):
    positions = {pair: 0 for pair in pairs}
    portfolio = {pair: 0 for pair in pairs}
    for pair in pairs:
        stock1, stock2 = pair
        spread = data[stock1] - data[stock2]
        zscore_spread = zscore(spread)

        for date, z in zscore_spread.items():  # Use items() instead of iteritems()
            if z > 2:
                positions[pair] = -1
            elif z < -2:
                positions[pair] = 1
            elif abs(z) < 0.5:
                positions[pair] = 0

            portfolio[pair] += positions[pair] * (data[stock1][date] - data[stock2][date])
    
    return portfolio

# Step 6: Rebalance portfolio
def rebalance_portfolio(data, pairs, rebalance_period='M'):
    rebalanced_portfolio = {pair: 0 for pair in pairs}
    monthly_data = data.resample(rebalance_period).last()
    
    for period_start, period_end in zip(monthly_data.index[:-1], monthly_data.index[1:]):
        period_data = data.loc[period_start:period_end]
        period_portfolio = pair_trading_strategy(period_data, pairs)
        
        for pair in pairs:
            rebalanced_portfolio[pair] += period_portfolio[pair]
    
    return rebalanced_portfolio

# Main script
if __name__ == "__main__":
    tickers = get_all_nasdaq_tickers()
    start_date = '1990-01-01'  # Extend the historical data period
    end_date = '2021-01-01'
    threshold = 0.7  # Adjust the correlation threshold

    # Fetch historical data
    data = fetch_historical_data(tickers, start_date, end_date)
    
    # Identify pairs
    pairs = identify_pairs(data, threshold)
    
    # If no pairs are identified, try again with a lower threshold
    if not pairs:
        print("No pairs identified with the current threshold. Trying with a lower threshold...")
        threshold = 0.6  # Adjust the threshold
        pairs = identify_pairs(data, threshold)

    # Handle suspensions and delistings
    data = handle_suspensions_and_delistings(data, tickers)
    
    # Rebalance portfolio
    rebalanced_portfolio = rebalance_portfolio(data, pairs)
    print("Identified pairs:", pairs)
    print("Rebalanced Portfolio value:", rebalanced_portfolio)
