from data_functions import RSI
import logging
import schedule
import time


# Logging setup
logging.basicConfig(level=logging.INFO)


# trading_bot
def trading_bot(ticker, interval):
    RSI(ticker=ticker,interval=interval)

def start_new_bot(ticker, interval):
    schedule.clear()
    if interval == "1m":
        seconds = 60
    elif interval == "2m":
        seconds = 120
    elif interval == "5m":
        seconds = 300
    elif interval == "15m":
        seconds = 900
    elif interval == "30m":
        seconds = 1800
    elif interval == "1h":
        seconds = 3600
    elif interval == "1d":
        seconds = 86400
    elif interval == "5d":
        seconds = 432000
    elif interval == "1wk":
        seconds = 604800
    elif interval == "1mo":
        seconds = 2592000
    elif interval == "3mo":
        seconds = 7776000
    else:
        raise ValueError("Neplatný interval: {}".format(interval))

    schedule.every(seconds).seconds.do(trading_bot, ticker, interval)
    print("New bot running")


start_new_bot("TSLA", "5m")

while True:
    schedule.run_pending()
    time.sleep(1)
