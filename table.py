import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering

# Step 1: Fetch Historical Data
def fetch_stock_data(stocks, start_date, end_date):
    data = yf.download(stocks, start=start_date, end=end_date)['Adj Close']
    returns = data.pct_change().dropna()
    return returns

# List of stock symbols
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # Sample list for demonstration

# Fetch historical data from Yahoo Finance
returns = fetch_stock_data(stocks, '2020-01-01', '2023-01-01')
print("Stock Returns:\n", returns.head())

# Step 2: Perform Clustering
def perform_clustering(returns, method='kmeans', n_clusters=3, eps=0.5, min_samples=5):
    if method == 'kmeans':
        model = KMeans(n_clusters=n_clusters, random_state=0)
    elif method == 'dbscan':
        model = DBSCAN(eps=eps, min_samples=min_samples)
    elif method == 'agglomerative':
        model = AgglomerativeClustering(n_clusters=n_clusters)
    else:
        raise ValueError("Invalid clustering method")
    
    clusters = model.fit_predict(returns.T)
    return clusters

# Step 3: Calculate Clustering Metrics
def calculate_clustering_metrics(stocks, clusters):
    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    n_stocks = len(stocks)
    n_stocks_in_clusters = sum(clusters != -1)
    n_outliers = sum(clusters == -1)
    
    cluster_sizes = pd.Series(clusters).value_counts()
    cluster_sizes = cluster_sizes[cluster_sizes != -1]
    
    biggest_cluster_size = cluster_sizes.max()
    second_biggest_cluster_size = cluster_sizes.nlargest(2).iloc[1] if len(cluster_sizes) > 1 else 0
    third_biggest_cluster_size = cluster_sizes.nlargest(3).iloc[2] if len(cluster_sizes) > 2 else 0

    return {
        "Number of clusters": n_clusters,
        "Number of stocks in total": n_stocks,
        "Number of stocks in clusters": f"{n_stocks_in_clusters} ({n_stocks_in_clusters / n_stocks * 100:.2f}%)",
        "Number of outliers": f"{n_outliers} ({n_outliers / n_stocks * 100:.2f}%)",
        "Number of stocks in the biggest cluster": f"{biggest_cluster_size} ({biggest_cluster_size / n_stocks * 100:.2f}%)",
        "Number of stocks in the second biggest cluster": f"{second_biggest_cluster_size} ({second_biggest_cluster_size / n_stocks * 100:.2f}%)",
        "Number of stocks in the third biggest cluster": f"{third_biggest_cluster_size} ({third_biggest_cluster_size / n_stocks * 100:.2f}%)",
    }

# Perform clustering using k-means, DBSCAN, and Agglomerative Clustering
kmeans_clusters = perform_clustering(returns, method='kmeans', n_clusters=3)
dbscan_clusters = perform_clustering(returns, method='dbscan', eps=0.5, min_samples=2)
agg_clusters = perform_clustering(returns, method='agglomerative', n_clusters=3)

# Calculate metrics for each clustering method
kmeans_metrics = calculate_clustering_metrics(stocks, kmeans_clusters)
dbscan_metrics = calculate_clustering_metrics(stocks, dbscan_clusters)
agg_metrics = calculate_clustering_metrics(stocks, agg_clusters)

# Step 4: Present Results as Table 1
print("\nTable 1: Clustering Characteristics")
clustering_methods = ['k-means', 'DBSCAN', 'Agglomerative']
metrics = ['Number of clusters', 'Number of stocks in total', 'Number of stocks in clusters', 
           'Number of outliers', 'Number of stocks in the biggest cluster', 
           'Number of stocks in the second biggest cluster', 'Number of stocks in the third biggest cluster']

table_data = pd.DataFrame({
    'Metric': metrics,
    'k-means': [kmeans_metrics[m] for m in metrics],
    'DBSCAN': [dbscan_metrics[m] for m in metrics],
    'Agglomerative': [agg_metrics[m] for m in metrics]
})

print(table_data)
