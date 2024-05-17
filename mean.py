import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

# Step 1: Collect Data
def fetch_stock_data(stocks, start_date, end_date):
    data = yf.download(stocks, start=start_date, end=end_date)['Adj Close']
    returns = data.pct_change().dropna()
    return returns

# List of stock symbols
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  

# Fetch historical data from Yahoo Finance
returns = fetch_stock_data(stocks, '2020-01-01', '2023-01-01')
print("Stock Returns:\n", returns.head())

# Step 2: Identify Pairs
def identify_pairs(returns, threshold=0.01):
    pca = PCA(n_components=2)
    pca.fit(returns)
    first_pc = pca.components_[0]
    pairs = []
    for i in range(len(first_pc)):
        for j in range(i + 1, len(first_pc)):
            if abs(first_pc[i] - first_pc[j]) < threshold:
                pairs.append((returns.columns[i], returns.columns[j]))
    return pairs

pairs = identify_pairs(returns)
print("Identified Pairs:\n", pairs)

# Step 3: Implement Pairs Trading Strategy
def pairs_trading_strategy(returns, pair, threshold=1.0):
    spread = returns[pair[0]] - returns[pair[1]]
    position = 0
    pnl = []
    for s in spread:
        if position == 0:
            if s > threshold:
                position = -1  # Short the spread
            elif s < -threshold:
                position = 1  # Long the spread
        elif position == 1:
            if s > 0:
                pnl.append(s)
                position = 0
        elif position == -1:
            if s < 0:
                pnl.append(-s)
                position = 0
    return np.sum(pnl)

def evaluate_strategy(returns, pairs, threshold=1.0):
    results = {}
    for pair in pairs:
        pnl = pairs_trading_strategy(returns, pair, threshold)
        results[pair] = pnl
    return results

results = evaluate_strategy(returns, pairs)
print("Strategy Results:\n", results)

# Step 4: Present Results
def calculate_performance_metrics(returns, results):
    performance = []
    for pair, pnl in results.items():
        mean_return = pnl / len(returns)
        std_dev = returns[list(pair)].std().sum()
        sharpe_ratio = mean_return / std_dev if std_dev != 0 else np.nan
        performance.append((pair, pnl, mean_return, std_dev, sharpe_ratio))
    
    results_df = pd.DataFrame(performance, columns=['Pair', 'PnL', 'Mean Return', 'Standard Deviation', 'Sharpe Ratio'])
    return results_df

performance_df = calculate_performance_metrics(returns, results)
print("Performance Metrics:\n", performance_df)
