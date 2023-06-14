import requests
import json
import pandas as pd
import datetime
from datetime import timedelta
from datetime import datetime


#start
#1.3.2023 12am = 1677628800000
#1.6.2023 12am = 1685577600000

# period of time 
starttime = 1677628800000
endtime = 1685577600000

df_message = []
df_message = pd.DataFrame(df_message)


##RETRIEVE BTCUSDT DATA

# Binance API endpoint for BTCUSDT historical klines

url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h"+'&startTime='+str(starttime)+'&endTime='+str(endtime)
response = requests.get(url)
data_BTC = json.loads(response.text)
df_BTC = pd.DataFrame(data_BTC)
df_BTC.columns = ['open_time', 'open', 'high', 'low', 'BTCUSDT', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'is_best_match']
df_BTC['open_time'] = pd.to_datetime(df_BTC['open_time'], unit='ms')
df_BTC['close_time'] = pd.to_datetime(df_BTC['close_time'], unit='ms')
BTC_df = df_BTC[['close_time', 'BTCUSDT']]


# Binance API endpoint for ETCUSDT futures historical klines

url = 'https://fapi.binance.com/fapi/v1/klines?symbol=ETHUSDT&interval=1h'+'&startTime='+str(starttime)+'&endTime='+str(endtime)
data_ETH = requests.get(url).json()
df_ETH = pd.DataFrame(data_ETH)
df_ETH.columns = ['open_time', 'open', 'high', 'low', 'ETHUSDT', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'is_best_match']
df_ETH['open_time'] = pd.to_datetime(df_ETH['open_time'], unit='ms')
df_ETH['close_time'] = pd.to_datetime(df_ETH['close_time'], unit='ms')
ETH_df = df_ETH[['close_time', 'ETHUSDT']]


# Join the DataFrames on the common column - dataframe with both ETH and BTC data

df = pd.merge(ETH_df, BTC_df, on='close_time')
df = df[['BTCUSDT', 'ETHUSDT']]


while True:

    # ETH fut. price now
    url = 'https://fapi.binance.com/fapi/v1/ticker/price'
    symbol = 'ETHUSDT'
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data_eth = response.json()
    price_eth = float(data_eth['price'])
    #print(f'price of now eth {price_eth}')
    # BTC price now
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data_btc = requests.get(key)
    data_btc = data_btc.json()
    price_btc = float(data_btc['price'])
   
    # create df to include new now values of ETH and BTC
    new_row = {'ETHUSDT': price_eth, 'BTCUSDT': price_btc} 
    new_row = pd.DataFrame(new_row, index=[0])
    # Add a new row to the DataFrame
    df = pd.concat([df, new_row], ignore_index=True)

    # CALCULATIONS
    df['BTCUSDT'] = df['BTCUSDT'].astype(float)
    df['ETHUSDT'] = df['ETHUSDT'].astype(float)

    # calculate correlation between ETHUSDT futures and BTCUSDT 
    correlation_matrix = df.corr()
    correlation_value = correlation_matrix.loc['ETHUSDT', 'BTCUSDT']

    # Calculate the percentage change and create a new column
    df['PercentageChange_BTCUSDT'] = df['BTCUSDT'].pct_change()
    # # percentage change of BTCUSDT * correlatiion value
    df['PercentageChange_BTCUSDT'] = df['PercentageChange_BTCUSDT'] * correlation_value
    # # Replace NaN values with 0
    df['PercentageChange_BTCUSDT'] = df['PercentageChange_BTCUSDT'].fillna(0)
    # create column for clean ETHUSDT values (without influence of BTCUSDT price movement)
    df['ETHUSDT_clean'] = df['ETHUSDT'] - df['ETHUSDT']* df['PercentageChange_BTCUSDT']

    price = df['ETHUSDT_clean'].tail(1)
    print(price.values[0])

    ## part for messaging
    current_time = datetime.now()
    df_time = {'time': current_time, 'price': float(price.iloc[0])} 
    df_time = pd.DataFrame(df_time, index=[0])
    ## Add a new row to the DataFrame
    df_message = pd.concat([df_message, df_time], ignore_index=True)
    ### Calculate the start time by subtracting 1 hour from the current time
    start_time = current_time - timedelta(minutes=60)
    ### Filter the dataframe based on the condition
    filtered_df = df_message[df_message['time'] >= start_time]
    ### Print the filtered dataframe
    tail = filtered_df['price'].tail(1)
    head = filtered_df['price'].head(1)
    if tail.iloc[0]!=head.iloc[0]:
        print(head.values[0],tail.values[0])
        result = round((tail.iloc[0]-head.iloc[0])/head.iloc[0]*100,2)
        if (abs(result)>=1):
            print('price changed on >= 1%')
    else:
        print('')
