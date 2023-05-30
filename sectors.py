from datetime import datetime
import pandas as pd
import nest_asyncio
from binance.client import Client
import json
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
client = Client('', '')
DAYS = '2500 day ago UTC'

KLINE_INTERVAL = client.KLINE_INTERVAL_1DAY
# Resemple period days

eth = ['ETHUSDT']
btc = ['BTCUSDT']
RESEMPLE_PERIOD = 1
SYMBOLS1 = ['ALICEUSDT', 'APEUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'IMXUSDT', 'GALAUSDT', 'DARUSDT', 'GMTUSDT',
            'MAGICUSDT', 'ETHUSDT']
defi = ['UNIUSDT', 'AAVEUSDT', 'CRVUSDT', 'MKRUSDT', 'SNXUSDT', 'BALUSDT', 'CVXUSDT', 'DYDXUSDT', 'LINKUSDT',
       '1INCHUSDT', 'COMPUSDT', 'FXSUSDT', 'LDOUSDT','SUSHIUSDT', 'YFIUSDT', 'ENSUSDT', 'GMXUSDT']
LSD = ['LDOUSDT', 'FXSUSDT', 'ANKRUSDT']
l2 = ['OPUSDT', 'ARBUSDT']
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'SHIBUSDT',\
     'AVAXUSDT', 'TRXUSDT', 'FTTUSDT','LTCUSDT', 'ETCUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT', 'NEARUSDT', 'XLMUSDT',\
     'XMRUSDT', 'BCHUSDT', 'ALGOUSDT', 'APEUSDT', 'VETUSDT', 'FLOWUSDT', 'ICPUSDT', 'MANAUSDT', 'SANDUSDT', 'FXSUSDT',\
     'HBARUSDT', 'XTZUSDT', 'AXSUSDT', 'FILUSDT', 'THETAUSDT', 'EGLDUSDT', 'AAVEUSDT', 'EOSUSDT', 'HNTUSDT', \
     'BTTUSDT', 'MKRUSDT', 'FTMUSDT', 'IOTAUSDT', 'LDOUSDT', 'KLAYUSDT', 'GRTUSDT', 'RUNEUSDT', 'SNXUSDT', 'ZECUSDT', \
     'NEOUSDT', 'ARUSDT', 'GMTUSDT', 'ZILUSDT', 'KSMUSDT', 'ENJUSDT', 'WAVESUSDT', 'DASHUSDT', 'CAKEUSDT', \
     'CRVUSDT', 'LRCUSDT', 'CVXUSDT', 'XEMUSDT', 'KAVAUSDT', 'MINAUSDT', 'ONEUSDT', 'DYDXUSDT', 'GLMRUSDT', \
     'IMXUSDT', 'BALUSDT', 'GALUSDT', 'TRUUSDT', 'ALICEUSDT', 'DODOUSDT', 'STGUSDT', 'SRMUSDT',
          'APTUSDT', 'GALAUSDT', 'RAYUSDT', 'ICXUSDT']
ethereum_killers = ['AVAXUSDT', 'SUIUSDT', 'SOLUSDT', 'ATOMUSDT', 'NEARUSDT', 'DOTUSDT', 'MATICUSDT', 'APTUSDT', 'FTMUSDT', 'ALGOUSDT']
# l2 = ['OPUSDT', 'ARBUSDT']
metaverse = ['TLMUSDT','ALICEUSDT', 'APEUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'IMXUSDT', 'GALAUSDT', 'DARUSDT', 'GMTUSDT',
            'MAGICUSDT']
ZK = ['MINAUSDT', 'LRCUSDT', 'IMXUSDT', 'MATICUSDT', 'DUSKUSDT']
blockchains = ['BTCUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'APTUSDT',
              'AVAXUSDT', 'TRXUSDT','LTCUSDT', 'ETCUSDT','ATOMUSDT', 'NEARUSDT', 'XLMUSDT','XMRUSDT', 'BCHUSDT', 'ALGOUSDT',
              'FLOWUSDT', 'ICPUSDT','HBARUSDT', 'XTZUSDT','EOSUSDT','NEOUSDT','ZILUSDT','ONEUSDT', 'FTMUSDT',
              'VETUSDT', 'EGLDUSDT', 'WAVESUSDT', 'DASHUSDT']
china = ['NEOUSDT', 'QNTUSDT', 'QTUMUSDT', 'VETUSDT', 'ONTUSDT']
blockchains_old = [ 'ADAUSDT', 'XRPUSDT',
             'TRXUSDT','LTCUSDT', 'ETCUSDT','ATOMUSDT', 'NEARUSDT', 'XLMUSDT','XMRUSDT', 'BCHUSDT', 'ALGOUSDT',
               'HBARUSDT', 'XTZUSDT','EOSUSDT','NEOUSDT','ZILUSDT', 'FTMUSDT',
              'VETUSDT', 'EGLDUSDT', 'WAVESUSDT', 'DASHUSDT', 'ICXUSDT', 'OMGUSDT',
                  'ONTUSDT', 'QTUMUSDT', 'ONEUSDT', 'DOGEUSDT', 'ZECUSDT']
ai = ['FETUSDT', 'HIGHUSDT', 'AGIXUSDT', 'RNDRUSDT', 'OCEANUSDT']
MEME = ['DOGEUSDT', 'SHIBUSDT', 'PEOPLEUSDT']
# Meme = []
def get_binance_futures_tickers():
    url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
    response = requests.get(url)
    data = response.json()
    futures_tickers = []
    for ticker in data:
        if 'USDT' in ticker['symbol']:
            if ticker['symbol'].startswith("1000"):
                futures_tickers.append(ticker['symbol'][4:])  # remove '1000' from the start
            else:
                futures_tickers.append(ticker['symbol'])
    return futures_tickers


tickers = get_binance_futures_tickers()

import asyncio
import pandas as pd
from binance import AsyncClient, BinanceSocketManager


async def get_prices_klines_df(symbol, client):
    print(f"Getting data for {symbol}")
    try:
        klines = await client.get_historical_klines(symbol, KLINE_INTERVAL, DAYS)
    except Exception as e:
        print(f"Skipping symbol {symbol} {e}")
        return None
    df = pd.DataFrame(klines, columns=['date', 'open', 'high', 'low', 'close', 'volume',
                                        'close_time', 'quote_asset_volume', 'number_of_trades',
                                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df = df.set_index('date')
    df.drop(['open', 'high', 'low', 'volume', 'close_time', 'quote_asset_volume',
             'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1, inplace=True)
    df.rename(columns={'close':symbol}, inplace=True)
    df[symbol] = pd.to_numeric(df[symbol])
    return df

async def get_all_klines(symbols):
    client = await AsyncClient.create()
    tasks = [get_prices_klines_df(symbol, client) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    await client.close_connection()
    return pd.concat(results, axis=1)

def concat_df(df):
    eth_price_df = df[['ETHUSDT']]
    cols = df.columns.tolist()
    for sym in cols:
        if sym != 'ETHUSDT':
            df[sym] = df[sym].astype(float)
            df['ETHUSDT'] = df['ETHUSDT'].astype(float)
            df[sym] = df[sym] / df['ETHUSDT']
    df = df.drop(['ETHUSDT'], axis=1)
    df = pd.concat([df, eth_price_df], axis=1)
    return df




def calculate_returns_and_growth(sector_coins, prices_df):
    sector_df = prices_df[sector_coins]
    sector_returns = (sector_df.pct_change() / len(sector_df.columns)).sum(axis=1)
    # sector_log_returns = np.log(sector_returns + 1)
    sector_growth = (1 + sector_returns).cumprod()
    return sector_returns, sector_growth


def create_sectors(prices_df, sectors, risk_free_rate=0):
    sector_data = {}
    sector_growth_df = pd.DataFrame()
    total_returns = {}
    for sector, coins in sectors.items():
        try:
            sector_returns, sector_growth = calculate_returns_and_growth(coins, prices_df)
            sector_volatility = sector_returns.std() * (365 ** 0.5)
            sharpe_ratio = (sector_returns.mean() * (365) - risk_free_rate) / sector_volatility

            sector_data[sector] = [sector_volatility, sharpe_ratio, round((sector_growth[-1] - 1) * 100, 2)]
            sector_growth_df[sector] = sector_growth
            total_returns[sector] = sector_growth[-1]

        except ZeroDivisionError:
            print(f"Skipping {sector} due to division by zero error.")
            continue

    sector_data_df = pd.DataFrame(sector_data, index=['Volatility', 'Sharpe Ratio', 'Total Returns']).T
    print(sector_data_df)
    # Plot the portfolio growth for all sectors
    #     pd.DataFrame(growth_dict, index=['Growth']).T.plot(kind='bar', figsize=(12,8))
    #     plt.ylabel('Growth of $1 investment')
    #     plt.title('Sector Growth Over Time')
    #     plt.show()
    # Sort sectors by total returns
    sorted_sectors = sorted(total_returns, key=total_returns.get, reverse=True)
    sector_growth_df = sector_growth_df[sorted_sectors]

    sector_growth_df.plot(figsize=(12, 8))
    plt.title('Portfolio Growth Over Time')
    plt.ylabel('Growth')
    plt.xlabel('Date')
    plt.show()

    corr_matrix = sector_growth_df.pct_change().corr()
    sns.heatmap(corr_matrix, annot=True)
    plt.title('Correlation Matrix')
    plt.show()


sectors = {
    'defi': defi,
    'ethereum_killers': ethereum_killers,
    'metaverse': metaverse,
    'blockchains': blockchains,
    'blockchains_old': blockchains_old,
    'ai': ai,
    'l2': l2,
    'eth': eth,
    'btc': btc,
    'meme': MEME,
    'lsd': LSD,
    'zk': ZK,
    'chinese': china

}

nest_asyncio.apply()
df = asyncio.run(get_all_klines(tickers))
# df1 = concat_df(df)
df

last_week = df.index.max() - pd.DateOffset(days=90)
last_month = df.index.max() - pd.DateOffset(months=5)
# create_sectors(df.loc[last_month:], sectors)
# create_sectors(df.loc[last_week:], sectors)
create_sectors(df.loc['2021':], sectors)

