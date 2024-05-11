import time 
import datetime
import pandas as pd

ticker= 'AAPL'
period1= int(time.mktime(datetime.datetime (2018, 1, 2, 23, 59).timetuple()))
period2= int(time.mktime(datetime.datetime(2024, 5, 11, 23, 59).timetuple()))
interval= '1d' # id, im 
query_string= f'https://query1.finance.yahoo.com/v7/finance/download/0P000070MY.TO?period1={1514903400}&period2={1715420195}&interval=1wk&events=history&includeAdjustedClose=true'

df = pd.read_csv(query_string)
print(df)
#df.to_csv()
#df.to_ecelimport()
