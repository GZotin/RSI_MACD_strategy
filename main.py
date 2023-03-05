from keys import API_key,secret_key
from binance.client import Client
import pandas as pd
import pandas_ta as ta
from matplotlib import pyplot as plt
import numpy as np


## Script
# Binance API connection
client = Client(API_key,secret_key)

## Wallet - if you want to know your balance
# print("\nBinance Wallet:")
# info = client.get_account()
# assets = info['balances']
# for asset in assets:
#     if float(asset['free']) > 0:
#         print("%s: %.2f" % (asset['asset'],float(asset['free'])))
#         wallet = float(asset['free'])
        
# currency
currency = "BTCUSDT"

# currency records
klines = client.get_historical_klines(currency, Client.KLINE_INTERVAL_1HOUR, "512 hours ago")

df = pd.DataFrame(klines, dtype = 'float')
df = df.drop([5,6,7,8,9,10,11],axis=1)
df.rename(columns = {0:'unix', 1:'open', 2:'high', 3:'low', 4:'close'}, inplace = True)

df['date'] = pd.to_datetime(df.unix,unit = 'ms')

# RSI - pandas TA
df['RSI_10'] = ta.rsi(df.close, length=10)

# MACD - pandas TA
df.ta.macd(close='close', fast=8, slow=21, signal=5, append=True)

# Buy and Sell Strategy
buy_signals = np.array([])
buy_confirmations = np.array([])
sell_signals = np.array([])
sell_confirmations = np.array([])

buy_confirmation = False
buy_signal = False
sell_signal = False
RSI_below_30 = False

print('\n' + 10*'-' + "Operations Records" + 10*'-')

for i in range(len(df)):
    ## Buy
    # Buy signal
    if df.RSI_10[i] < 30.0 and RSI_below_30 == False and buy_confirmation == False:
        RSI_below_30 = True

    if df.RSI_10[i] > 30.0 and RSI_below_30 == True:
        buy_signal = True
        i_buy_signal = i
        buy_signals = np.append(buy_signals, i)

    # Buy Confirmation
    if buy_signal == True:
        for j in range(len(df)-i): # def qtd
            if df.MACD_8_21_5[i_buy_signal+j] > df.MACDs_8_21_5[i_buy_signal+j]:
                print('BUY  -  %s  -  BTC: R$%.2f' % (df.date[i], df.close[i]))
                buy_confirmations = np.append(buy_confirmations, i_buy_signal+j)
                buy_confirmation = True
                break
        buy_signal = False
        RSI_below_30 = False

    ## Sell
    # Sell signal
    if df.RSI_10[i] >= 70 and sell_signal == False and buy_confirmation == True:
        sell_signal = True
        i_sell_signal = i
        sell_signals = np.append(sell_signals, i)

    # Sell confirmation
    if sell_signal == True:
        for j in range(len(df)-i): # definir a qtd
            if df.MACD_8_21_5[i_sell_signal+j] < df.MACDs_8_21_5[i_sell_signal+j]:
                print('SELL -  %s  -  BTC: R$%.2f' % (df.date[i], df.close[i]))
                sell_confirmations = np.append(sell_confirmations, i_sell_signal+j)
                buy_confirmation = False
                break
        sell_signal = False
        
## Simulation
print('\n' + 10*'-' + ' Results ' + 10*'-')

#sim = wallet
sim_i = 500
sim = sim_i

for i in range(len(sell_confirmations)):
    sim = sim/df.close[buy_confirmations[i]]
    sim = sim*df.close[sell_confirmations[i]]

profit = sim-sim_i
profit_p = 100*(sim-sim_i)/sim_i
print("Initial Wallet: $%.2f" % (sim_i))
print("Post-operations Wallet: $%.2f" % (sim))
print("Profit: $%.2f" % (profit))
print("Percentage of profit: %.2f%%" % (profit_p))


## Plots
plt.subplot(2,1,1)
plt.title('Buy and Sell Signals')
plt.ylabel('RSI')
plt.plot(df.date, df.RSI_10, label = 'RSI', zorder = 1)
plt.scatter(df.date[buy_signals], df.RSI_10[buy_signals], color = 'g', marker = 'x', zorder = 2)
plt.scatter(df.date[sell_signals], df.RSI_10[sell_signals], color = 'r', marker = 'x', zorder = 2)
plt.plot([df.date[0],df.date[len(df)-1]],[30, 30], marker = ',', color = 'g', linewidth = 1)
plt.plot([df.date[0],df.date[len(df)-1]],[70, 70], marker = ',', color = 'r', linewidth = 1)
plt.xlim([df.date[0],df.date[len(df)-1]])
#plt.xticks(rotation=45)

plt.subplot(2,1,2)
plt.title('Buy and Sell Confirmations')
plt.ylabel("MACD")
plt.plot(df.date, df.MACD_8_21_5, label = 'MACD line')
plt.plot(df.date, df.MACDs_8_21_5, label = 'MACD signal')
plt.scatter(df.date[buy_confirmations], df.MACD_8_21_5[buy_confirmations], color = 'g', marker = 'x', zorder = 2)
plt.scatter(df.date[sell_confirmations], df.MACD_8_21_5[sell_confirmations], color = 'r', marker = 'x', zorder = 2)
#plt.xticks(rotation=45)
plt.legend()
plt.xlim([df.date[0],df.date[len(df)-1]])

plt.show()