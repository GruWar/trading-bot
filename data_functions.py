import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import pandas as pd


def get_actual_price(ticker):
    symbol = yf.Ticker(ticker)
    data = symbol.history(period="1d")
    if "Dividends" in data.columns:
        del data["Dividends"]
    if "Stock Splits" in data.columns:
        del data["Stock Splits"]
    current_price = symbol.info['regularMarketPrice']
    return current_price


def get_historical_data(ticker, start, end, interval="1mo"):
    symbol = yf.Ticker(ticker)
    data = symbol.history(start=start, end=end, interval=interval)
    print(f"Dwnloaded {len(data)} records for ticker {ticker} from {start} to {end} with interval {interval}.")
    if "Dividends" in data.columns:
        del data["Dividends"]
    if "Stock Splits" in data.columns:
        del data["Stock Splits"]
    return data


def RSI(ticker, n=14, interval="1d"):
    end_date = datetime.now()
    offset = 0

    while True:
        start_date = end_date - timedelta(days=(n + offset))

        # Získání dat v daném časovém rozmezí
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        data = get_historical_data(ticker, start_date_str, end_date_str, interval=interval)

        # Pokud máme dostatek dat, ukončíme smyčku
        if len(data) >= n:
            break

        offset += 1

    # Výpočet RSI
    delta = data["Close"].diff()

    # Výpočet průměrných zisků a ztrát pomocí SMA
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()

    # Výpočet RSI pomocí SMA
    rs = gain / loss
    rsi_sma = 100 - (100 / (1 + rs))

    # Výpočet průměrných zisků a ztrát pomocí EMA
    gain_ema = (delta.where(delta > 0, 0)).ewm(span=n, adjust=False).mean()
    loss_ema = (-delta.where(delta < 0, 0)).ewm(span=n, adjust=False).mean()

    # Výpočet RSI pomocí EMA
    rs_ema = gain_ema / loss_ema
    rsi_ema = 100 - (100 / (1 + rs_ema))

    # Přidání RSI do DataFrame
    data['RSI_SMA'] = rsi_sma
    data['RSI_EMA'] = rsi_ema

    return data


def SMA(ticker, window, interval):
    end_date = datetime.now()
    offset = 0

    while True:
        start_date = end_date - timedelta(days=(window + offset))

        # Získání dat v daném časovém rozmezí
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        data = get_historical_data(ticker, start_date_str, end_date_str, interval=interval)

        # Pokud máme dostatek dat, ukončíme smyčku
        if len(data) >= window:
            break

        offset += 1

    # Výpočet SMA
    data['SMA'] = data['Close'].rolling(window=window).mean()
 
    return data


# Příklad použití
data = SMA("TSLA", 14, "1d")
data1 = RSI("TSLA", 14, "1d")
print(data[['Close', 'SMA']].tail(1))
print(data1[['Close', 'RSI_SMA', 'RSI_EMA']].tail(1))