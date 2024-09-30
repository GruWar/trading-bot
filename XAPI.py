import enum
import json
import websocket
from datetime import datetime

# version
__version__ = '1.0.0'


class CMD(enum.Enum):
    """
    CMD defines trade order types (buy, sell, buy limit, sell limit, buy stop, sell stop, balance, credit)
    enter the parameter as CMD.x.value
    """
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5
    BALANCE = 6
    CREDIT = 7


class TRADETYPE(enum.Enum):
    """
    TRADETYPE defines trade types (open, pending, closed, modified, deleted).
    enter the parameter as TRADETYPE.x.value
    """
    OPEN = 0
    PENDING = 1
    CLOSE = 2
    MODIFY = 3
    DELETE = 4


class XTB:
    """
    The XTB class is used to connect to the XTB API and allows communication with the server.
    parameters are account id and password in string format
    """
    def __init__(self, uid, psw):
        self.id = uid
        self.psw = psw
        self.ws = None

    # websocket connection
    def connect(self, srv):
        """
        The function creates a connection to the xtb server using a websocket.
        srv parameter is "demo" or "real" depends on account type.
        """
        try:
            self.ws = websocket.create_connection(f"wss://ws.xtb.com/{srv}")
            # Success
        except Exception as e:
            # Error
            print("Error {}".format(e))

    def disconnect(self):
        """
        The function terminates a connection from the xtb server using a websocket.
        """
        try:
            self.ws.close()
            # Success
        except Exception as e:
            # Error
            print("Error {}".format(e))

    def send(self, command):
        """
        Function send the command in json format to the XTB server and returns the response in json
        """
        command_json = json.dumps(command)
        self.ws.send(command_json)
        response = json.loads(self.ws.recv())
        return response

    # login
    def login(self):
        """
        Function will log in you to the xtb account depends on type of server by ID and PSW.
        """
        command = {
            "command": "login",
            "arguments": {
                "userId": self.id,
                "password": self.psw,
            }
        }
        response = self.send(command)
        if response["status"]:
            pass
        else:
            print("Error")

    def logout(self):
        """
        Function will log out you from the xtb account.
        """
        command = {
            "command": "logout",
        }
        response = self.send(command)
        if response["status"]:
            pass
        else:
            print("Error")

    def ping(self):
        """
        Regularly calling this function is enough to refresh the internal state of all the components in the system.
        It is recommended that any application that does not execute other commands, should call this command at least
        once every 10 minutes.
        """
        command = {
            "command": "ping"
        }
        response = self.send(command)
        return response

    # functions
    def get_balance(self):
        """
        Returns various account indicators.
        Response:
        balance	        /Floating number/	balance in account currency
        credit	        /Floating number/	credit
        currency	    /String/	        user currency
        equity	        /Floating number/	sum of balance and all profits in account currency
        margin	        /Floating number/	margin requirements in account currency
        margin_free	    /Floating number/	free margin in account currency
        margin_level	/Floating number/	margin level percentage
        """
        command = {
            "command": "getMarginLevel"
        }
        response = self.send(command)
        return response

    def get_all_symbols(self, show=False):
        """
        Returns array of all symbols available for the user.
        """
        command = {
            "command": "getAllSymbols",
        }
        response = self.send(command)
        if show:
            symbol_records = response["returnData"]
            for symbol_record in symbol_records:
                print("Symbol:", symbol_record["symbol"])
                print("Description:", symbol_record["description"])
                print("Category:", symbol_record["categoryName"])
                print("Currency:", symbol_record["currency"])
                print("Currency Pair:", symbol_record["currencyPair"])
                print("Leverage:", symbol_record["leverage"])
                # next keys...
                print()
        return response

    def get_server_time(self):
        """
        Returns current time on trading server.
        """
        command = {
            "command": "getServerTime"
        }
        response = self.send(command)
        time = response["returnData"]["time"]
        return time

    def get_chart_last_request(self, period, symbol, qty_candles):
        """
        Returns chart info, from start date to the current time.
        Response:
        close	    /Floating number/	Value of close price (shift from open price)
        ctmString	/String/            representation of the 'ctm' field
        high	    /Floating number/	Highest value in the given period (shift from open price)
        low	        /Floating number/	Lowest value in the given period (shift from open price)
        open	    /Floating number/	Open price (in base currency * 10 to the power of digits)
        """
        minutes = 0
        period = self.period(period)
        minutes += period * qty_candles
        start = self.get_server_time() - self.to_milliseconds(minutes)
        info = {
            "period": period,
            "start": start,
            "symbol": symbol
        }
        command = {
            "command": "getChartLastRequest",
            "arguments": {
                "info": info
            }
        }
        response = self.send(command)
        return response

    def get_candles_in_range(self, period, symbol, start, end, tick=0):
        """
        Returns chart info with data between given start and end dates.
        Response:
        close	    /Floating number/	Value of close price (shift from open price)
        ctmString	/String/            representation of the 'ctm' field
        high	    /Floating number/	Highest value in the given period (shift from open price)
        low	        /Floating number/	Lowest value in the given period (shift from open price)
        open	    /Floating number/	Open price (in base currency * 10 to the power of digits)
        """
        period = self.period(period)
        start = self.time_conversion(start)
        end = self.time_conversion(end)
        info = {
            "end": end,
            "period": period,
            "start": start,
            "symbol": symbol,
            "ticks": tick,
        }
        command = {
            "command": "getChartRangeRequest",
            "arguments": {
                "info": info
            }
        }
        response = self.send(command)
        return response

    def get_symbol(self, symbol):
        """
        Returns information about symbol available for the user.
        """
        command = {
            "command": "getSymbol",
            "arguments": {
                "symbol": symbol
            }
        }
        response = self.send(command)
        return response

    def trade(self, symbol, volume, cmd, trade_type, comment="", sl=0, tp=0, order=0, expiration=0):

        price = self.get_candles("M1", symbol, qty_candles=1)
        price = price[0]["open"] + price[0]["close"]
        trade_info = {
            "cmd": cmd,
            "customComment": comment,
            "expiration": expiration,
            "offset": -1,
            "order": order,
            "price": price,
            "sl": sl,
            "symbol": symbol,
            "tp": tp,
            "type": trade_type,
            "volume": volume,
        }
        command = {
            "command": "tradeTransaction",
            "arguments": {
                "tradeTransInfo": trade_info
            }
        }
        response = self.send(command)
        return response

    def trade_check(self, order):
        command = {
            "command": "tradeTransactionStatus",
            "arguments": {
                "order": order
            }
        }
        response = self.send(command)
        response = response["returnData"]["requestStatus"]
        if response == 0:
            response = "error"
        elif response == 1:
            response = "pending"
        elif response == 3:
            response = "The transaction has been executed successfully"
        elif response == 4:
            response = "The transaction has been rejected"
        return response

    def get_trades(self):
        command = {
            "command": "getTrades",
            "arguments": {
                "openedOnly": True,
            }
        }
        response = self.send(command)
        return response

    def get_trades_history(self, start=0, end=0):
        if start != 0:
            start = self.time_conversion(start)
        if end != 0:
            end = self.time_conversion(end)
        command = {
            "command": "getTradesHistory",
            "arguments": {
                "end": end,
                "start": start,
            }
        }
        response = self.send(command)
        return response

    def calc_profit(self, symbol, volume, cmd, op, cp):
        command = {
            "command": "getProfitCalculation",
            "arguments": {
                "closePrice": cp,
                "cmd": cmd,
                "openPrice": op,
                "symbol": symbol,
                "volume": volume
            }
        }
        response = self.send(command)
        return response

    def calc_commission(self, symbol, volume):
        command = {
            "command": "getCommissionDef",
            "arguments": {
                "symbol": symbol,
                "volume": volume,
            }
        }
        response = self.send(command)
        return response

    def calc_margin(self, symbol, volume):
        command = {
            "command": "getMarginTrade",
            "arguments": {
                "symbol": symbol,
                "volume": volume,
            }
        }
        response = self.send(command)
        return response

    def user_data(self):
        """
        Returns information about account currency, and account leverage.
        Response:
        companyUnit	        /Number/	    Unit the account is assigned to.
        currency	        /String/	    account currency
        group	            /String/	    group
        ibAccount	        /Boolean/	    Indicates whether this account is an IB account.
        leverage	        /Number/	    This field should not be used. It is inactive and its value is always 1.
        leverageMultiplier	/Floating/    number	The factor used for margin calculations. The actual value of leverage
        can be calculated by dividing this value by 100.
        spreadType	        /String/	    spreadType, null if not applicable
        trailingStop	    /Boolean/	    Indicates whether this account is enabled to use trailing stop.
        """
        command = {
            "command": "getCurrentUserData",
        }
        response = self.send(command)
        return response

    # static functions
    @staticmethod
    def to_milliseconds(minutes, hours=0, days=0):
        """
        Convert input to milliseconds
        """
        milliseconds = (days * 24 * 60 * 60 * 1000) + (hours * 60 * 60 * 1000) + (minutes * 60 * 1000)
        return milliseconds

    @staticmethod
    def period(period):
        """
        Converts the format period(M1, M5, M10, M15, M30, H1, H4, D1, W1, MN1) to a number understood by the api.
        """
        if period == "M1":
            period = 1
        elif period == "M5":
            period = 5
        elif period == "M15":
            period = 15
        elif period == "M30":
            period = 30
        elif period == "H1":
            period = 60
        elif period == "H4":
            period = 240
        elif period == "D1":
            period = 1440
        elif period == "W1":
            period = 10080
        elif period == "MN1":
            period = 43200
        return period

    @staticmethod
    def get_time():
        """
        Return the actual time
        """
        time = datetime.today().strftime('%m/%d/%Y %H:%M:%S%f')
        time = datetime.strptime(time, '%m/%d/%Y %H:%M:%S%f')
        return time

    @staticmethod
    def time_conversion(date):
        """
        Convert the time string format M/D/Y H:M:S to milliseconds
        """
        start = "01/01/1970 00:00:00"
        start = datetime.strptime(start, '%m/%d/%Y %H:%M:%S')
        date = datetime.strptime(date, '%m/%d/%Y %H:%M:%S')
        final_date = date - start
        temp = str(final_date)
        temp1, temp2 = temp.split(", ")
        hours, minutes, seconds = temp2.split(":")
        days = final_date.days
        days = int(days)
        hours = int(hours)
        hours -= 2
        minutes = int(minutes)
        seconds = int(seconds)
        time = (days * 24 * 60 * 60 * 1000) + (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000)
        return time

    @staticmethod
    def get_data(data, key):
        response_data = data['returnData']
        rate_infos = response_data['rateInfos']
        info = [x[f'{key}'] for x in rate_infos]
        return info
