import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_stock_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    # Send an HTTP GET request to the URL
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing the historical stock price data
        table = soup.find('table')
        
        if table:
            # Extract data from the table
            rows = table.find_all('tr')
            data = []
            for row in rows[1:]:  # Skip the header row
                cols = row.find_all('td')
                cols = [col.text.strip() for col in cols]
                data.append(cols)
            
            # Create a DataFrame from the extracted data
            headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            df = pd.DataFrame(data, columns=headers)
            
            # Convert date column to datetime format
            df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
            
            return df
        else:
            print("Failed to find the table containing stock data.")
            return None
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None

# URL of the Yahoo Finance page
url = 'https://finance.yahoo.com/quote/0P000070MY.TO/history?period1={1514903400}&period2={1683763200}&frequency=1wk'

# Get historical stock price data
stock_data = get_stock_data(url)

# Check if data retrieval was successful before accessing attributes
if stock_data is not None:
    # Display the first few rows of the DataFrame
    print(stock_data.head())
else:
    print("Failed to retrieve historical stock price data.")
