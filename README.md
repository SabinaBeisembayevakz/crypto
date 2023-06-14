# crypto

Libraries used: requests, json, pandas, datetime

Calculates ETHUSDT futures prices without influence of BTCUSDT prices.

1. It creates dataframe with historical data of both ETHUSDT fut. prices and BTCUSDT prices
2. Adds current values of ETHUSDT fut. and BTCUSDT prices to existing dataframe
3. Calculates correlation value
4. Calculates percentage change of BTCUSDT prices
5. Multiplies correlation value by percentage change of BTCUSDT prices
6. Multiplies ETHUSDT fut. values by what we got in step 4
7. subtract from ETHUSDT fut. values what we got in step 6.

#step 2-7:

ETHUSDT fut prices with no influence of BTCUSDT =
[ETHUSDT fut. prices]*[1 - (perc.change of BTCUSDT)*(correlation value)]


If price changes on more that 1% in last 60 minutes it sends message: price changed on >= 1%
