import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint
from datetime import datetime, timedelta

# Constants
START_DATE = '2010-01-01'
END_DATE = '2023-12-31'
REBALANCE_PERIOD = 'M'  # 'M' for monthly, 'W' for weekly

# Step 1: Retrieve historical data for all NASDAQ stocks
def get_nasdaq_tickers():
    # You should create a CSV or fetch from an API. For simplicity, using a small subset.
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]  # Changed 'FB' to 'META' for current symbol

def retrieve_nasdaq_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)
    return data['Adj Close']

# Step 2: Identify cointegrated pairs
def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    pairs = []
    keys = data.columns
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]].dropna()
            S2 = data[keys[j]].dropna()
            min_len = min(len(S1), len(S2))
            if min_len > 0:
                S1 = S1[-min_len:]
                S2 = S2[-min_len:]
                score, pvalue, _ = coint(S1, S2)
                score_matrix[i, j] = score
                pvalue_matrix[i, j] = pvalue
                if pvalue < 0.05:  # Accept pairs with p-value < 0.05
                    pairs.append((keys[i], keys[j]))
    return pairs, pvalue_matrix

# Step 3: Implement trading logic
def zscore(series):
    return (series - series.mean()) / np.std(series)

def trade_pair(data, pair, entry_z=2.0, exit_z=0.5):
    S1 = data[pair[0]].fillna(method='ffill').fillna(method='bfill')
    S2 = data[pair[1]].fillna(method='ffill').fillna(method='bfill')
    score, _, _ = coint(S1, S2)
    ratio = S1 / S2
    z = zscore(ratio)
    signals = pd.DataFrame(index=data.index)
    signals['z'] = z
    signals['long'] = (z < -entry_z).astype(int)
    signals['short'] = (z > entry_z).astype(int)
    signals['exit'] = (abs(z) < exit_z).astype(int)
    return signals

# Step 4: Handle suspended or delisted stocks
def handle_suspended_delisted(data):
    # Add logic to handle suspended/delisted stocks
    return data

# Step 5: Rebalance the portfolio
def rebalance_portfolio(data, pairs, period='M'):
    rebalanced_portfolio = []
    rebalance_dates = pd.date_range(start=START_DATE, end=END_DATE, freq=period)
    for date in rebalance_dates:
        current_data = data[:date]
        trades = []
        for pair in pairs:
            signals = trade_pair(current_data, pair)
            trades.append(signals)
        rebalanced_portfolio.append(trades)
    return rebalanced_portfolio

def main():
    # Step 1: Retrieve historical data
    tickers = get_nasdaq_tickers()
    nasdaq_data = retrieve_nasdaq_data(tickers, START_DATE, END_DATE)
    
    # Step 2: Identify cointegrated pairs
    nasdaq_data_cleaned = nasdaq_data.fillna(method='ffill').fillna(method='bfill')
    pairs, pvalues = find_cointegrated_pairs(nasdaq_data_cleaned)
    
    # Step 3: Implement trading logic
    # Initial trading logic applied to the whole dataset
    for pair in pairs:
        signals = trade_pair(nasdaq_data, pair)
        print(f"Trading signals for pair {pair}:")
        print(signals.head())
    
    # Step 4: Handle suspended or delisted stocks
    updated_data = handle_suspended_delisted(nasdaq_data)
    
    # Step 5: Rebalance the portfolio monthly
    rebalanced_portfolio = rebalance_portfolio(updated_data, pairs, REBALANCE_PERIOD)
    
    # Output the rebalanced portfolio
    for i, portfolio in enumerate(rebalanced_portfolio):
        print(f"Rebalanced portfolio for period {i}:")
        for trade in portfolio:
            print(trade.head())

if __name__ == "__main__":
    main()
