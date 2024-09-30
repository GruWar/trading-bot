import talib
import pandas as pd
import yfinance as yf
import datetime


def historical_prices(stock_code, start_date, end_date, show=False):
    data = yf.download(stock_code, start=start_date, end=end_date)
    if show:
        print(data)
    return data


def trading_bot(stock_code, rsi_period=14, adx_period=14):
    #settings
    pd.set_option('display.max_rows', None)

    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    data = historical_prices(stock_code, '2022-01-01', today_date)

    #indicators
    data['RSI'] = talib.RSI(data['Close'], timeperiod=rsi_period)
    data['ADX'] = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=adx_period)
    data['DI+'] = talib.PLUS_DI(data['High'], data['Low'], data['Close'], timeperiod=adx_period)
    data['DI-'] = talib.MINUS_DI(data['High'], data['Low'], data['Close'], timeperiod=adx_period)

    #remove NaN
    data = data.dropna()

    #trading conditions
    data['Trade'] = 'HOLD'
    data.loc[(data['ADX'] > 25) & (data['DI+'] > data['DI-']) & (data['RSI'] < 30), 'Trade'] = 'Buy'
    data.loc[(data['ADX'] > 25) & (data['DI-'] > data['DI+']) & (data['RSI'] > 70), 'Trade'] = 'Sell'

    print(data)


trading_bot('TSLA')
