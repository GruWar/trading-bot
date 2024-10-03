
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def get_actual_price(ticker):
    symbol = yf.Ticker(ticker)
    data = symbol.history(period="1d")
    del data["Dividends"]
    del data["Stock Splits"]
    return data


def get_historical_data(ticker, start, end, interval="1mo"):
    symbol = yf.Ticker(ticker)
    data = symbol.history(start=start, end=end, interval=interval)
    del data["Dividends"]
    del data["Stock Splits"]
    return data


def RSI(ticker, n=14):
    # geting prices
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=n * 2)  # Zajistíme více dat pro výpočet
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    data = get_historical_data(ticker, start_date_str, end_date_str, interval="1d")
    print(data)

    # calculating RSI
    prices = data["Close"].diff()
    prices.dropna(inplace=True)
    change_up = prices.copy()
    change_down = prices.copy()
    change_up[change_up<0] = 0
    change_down[change_down>0] = 0
    prices.equals(change_up+change_down)
    avg_up = change_up.rolling(n).mean()
    avg_down = change_down.rolling(n).mean().abs()
    rsi = 100 * avg_up / (avg_up + avg_down)
    rsi.dropna(inplace=True)
    print(rsi.tail(20))

RSI("TSLA")