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
import asyncio
import pandas as pd
from binance import AsyncClient, BinanceSocketManager

##################Settings here###########################################
client = Client('', '')
DAYS = '15 day ago UTC'
KLINE_INTERVAL = '5m'
# Resemple period days
RESEMPLE_PERIOD = 1
#we convert 5minutes to day
convert_rate= 12*24
#define sectors
eth = ['ETHUSDT']
btc = ['BTCUSDT']
defi = ['UNIUSDT', 'AAVEUSDT', 'CRVUSDT', 'MKRUSDT', 'SNXUSDT', 'BALUSDT', 'CVXUSDT', 'DYDXUSDT', 'LINKUSDT',
       '1INCHUSDT', 'COMPUSDT', 'FXSUSDT', 'LDOUSDT','SUSHIUSDT', 'YFIUSDT', 'ENSUSDT', 'GMXUSDT']
LSD = ['LDOUSDT', 'FXSUSDT', 'ANKRUSDT']
l2 = ['OPUSDT', 'ARBUSDT']
china = ['NEOUSDT', 'QNTUSDT', 'QTUMUSDT', 'VETUSDT', 'ONTUSDT']
ethereum_killers = ['AVAXUSDT', 'SUIUSDT', 'SOLUSDT', 'ATOMUSDT', 'NEARUSDT', 'DOTUSDT', 'MATICUSDT', 'APTUSDT', 'FTMUSDT', 'ALGOUSDT']
metaverse = ['TLMUSDT','ALICEUSDT', 'APEUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'IMXUSDT', 'GALAUSDT', 'DARUSDT', 'GMTUSDT',
            'MAGICUSDT']
ZK = ['MINAUSDT', 'LRCUSDT', 'IMXUSDT', 'MATICUSDT', 'DUSKUSDT']
blockchains = ['BTCUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'APTUSDT',
              'AVAXUSDT', 'TRXUSDT','LTCUSDT', 'ETCUSDT','ATOMUSDT', 'NEARUSDT', 'XLMUSDT','XMRUSDT', 'BCHUSDT', 'ALGOUSDT',
              'FLOWUSDT', 'ICPUSDT','HBARUSDT', 'XTZUSDT','EOSUSDT','NEOUSDT','ZILUSDT','ONEUSDT', 'FTMUSDT',
              'VETUSDT', 'EGLDUSDT', 'WAVESUSDT', 'DASHUSDT']
blockchains_old = [ 'ADAUSDT', 'XRPUSDT',
             'TRXUSDT','LTCUSDT', 'ETCUSDT','ATOMUSDT', 'NEARUSDT', 'XLMUSDT','XMRUSDT', 'BCHUSDT', 'ALGOUSDT',
               'HBARUSDT', 'XTZUSDT','EOSUSDT','NEOUSDT','ZILUSDT', 'FTMUSDT',
              'VETUSDT', 'EGLDUSDT', 'WAVESUSDT', 'DASHUSDT', 'ICXUSDT', 'OMGUSDT',
                  'ONTUSDT', 'QTUMUSDT', 'ONEUSDT', 'DOGEUSDT', 'ZECUSDT']
ai = ['FETUSDT', 'HIGHUSDT', 'AGIXUSDT', 'RNDRUSDT', 'OCEANUSDT']
MEME = ['DOGEUSDT', 'SHIBUSDT', 'PEOPLEUSDT', 'PEPEUSDT', 'FLOKIUSDT']
# football = ['FOOTBALLUSDT', 'CHZUSDT']


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



def calculate_market_returns_and_growth(prices_df):
    market_returns = (prices_df.pct_change() / len(prices_df.columns)).sum(axis=1)
    market_growth = (1 + market_returns).cumprod()
    return market_returns, market_growth

def calculate_returns_and_growth(sector_coins, prices_df):
    sector_df = prices_df[sector_coins]
    sector_returns = (sector_df.pct_change() / len(sector_df.columns)).sum(axis=1)
    # sector_log_returns = np.log(sector_returns + 1)
    sector_growth = (1 + sector_returns).cumprod()
    return sector_returns, sector_growth


def create_sectors(prices_df, sectors):
    sector_data = {}
    sector_growth_df = pd.DataFrame()
    total_returns = {}

    # Calculate the entire market's returns and growth
    market_returns, market_growth = calculate_market_returns_and_growth(prices_df)
    market_volatility = market_returns.std() * ((365*convert_rate) ** 0.5)
    market_sharpe_ratio = (market_returns.mean() * (365*convert_rate)) / market_volatility
    sector_data['market'] = [market_volatility, market_sharpe_ratio, round((market_growth[-1] - 1) * 100, 2)]
    sector_growth_df['market'] = market_growth
    total_returns['market'] = market_growth[-1]

    for sector, coins in sectors.items():
        try:
            sector_returns, sector_growth = calculate_returns_and_growth(coins, prices_df)
            sector_volatility = sector_returns.std() * ((365*convert_rate) ** 0.5)
            sharpe_ratio = (sector_returns.mean() * (365*convert_rate)) / sector_volatility

            sector_data[sector] = [sector_volatility, sharpe_ratio, round((sector_growth[-1] - 1) * 100, 2)]
            sector_growth_df[sector] = sector_growth
            total_returns[sector] = sector_growth[-1]

        except ZeroDivisionError:
            print(f"Skipping {sector} due to division by zero error.")
            continue

    sector_data_df = pd.DataFrame(sector_data, index=['Volatility', 'Sharpe Ratio', 'Total Returns']).T
    print(sector_data_df)

    sorted_sectors = sorted(total_returns, key=total_returns.get, reverse=True)
    sector_growth_df = sector_growth_df[sorted_sectors]
    for sector in sector_growth_df.columns:
        if sector in ["eth", "btc"]:
            sector_growth_df[sector].plot(figsize=(12, 8), linewidth=2.5)
        else:
            sector_growth_df[sector].plot(figsize=(12, 8))
    plt.title('Portfolio Growth Over Time')
    plt.ylabel('Growth')
    plt.xlabel('Date')
    plt.legend()
    # Add a grid
    plt.grid(True)
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
async def run_analysis():
    tickers = get_binance_futures_tickers()
    nest_asyncio.apply()
    df = asyncio.run(get_all_klines(tickers))
    df
    # last_day = df.index.max() - pd.DateOffset(days=1)
    last_6hour = df.index.max() - pd.DateOffset(hours=6)
    create_sectors(df.loc[last_6hour:], sectors)
    # create_sectors(df.loc[last_day:], sectors)

asyncio.run(run_analysis())