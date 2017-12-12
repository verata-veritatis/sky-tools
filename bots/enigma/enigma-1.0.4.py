##############################################################
# Bittrex API Wrapper (Eric Somdahl)
#
# Thank you Eric for making my life so much easier. See more
# information at https://bittrex.com/Home/Api. You can
# also find Eric's wrapper at 
# https://github.com/ericsomdahl/python-bittrex.
#
##############################################################

from __future__ import print_function

import hmac
import hashlib
import time
import sys

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

try:
    from Crypto.Cipher import AES
except ImportError:
    encrypted = False
else:
    import getpass
    import ast
    import json

    encrypted = True

import requests

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

TICKINTERVAL_ONEMIN = 'oneMin'
TICKINTERVAL_FIVEMIN = 'fiveMin'
TICKINTERVAL_HOUR = 'hour'
TICKINTERVAL_THIRTYMIN = 'thirtyMin'
TICKINTERVAL_DAY = 'Day'

ORDERTYPE_LIMIT = 'LIMIT'
ORDERTYPE_MARKET = 'MARKET'

TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED'
TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL'
TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'

CONDITIONTYPE_NONE = 'NONE'
CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN'
CONDITIONTYPE_LESS_THAN = 'LESS_THAN'
CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED'
CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'

API_V1_1 = 'v1.1'
API_V2_0 = 'v2.0'

BASE_URL_V1_1 = 'https://bittrex.com/api/v1.1{path}?'
BASE_URL_V2_0 = 'https://bittrex.com/api/v2.0{path}?'

PROTECTION_PUB = 'pub'  # public methods
PROTECTION_PRV = 'prv'  # authenticated methods


def encrypt(api_key, api_secret, export=True, export_fn='secrets.json'):
    cipher = AES.new(getpass.getpass(
        'Input encryption password (string will not show)'))
    api_key_n = cipher.encrypt(api_key)
    api_secret_n = cipher.encrypt(api_secret)
    api = {'key': str(api_key_n), 'secret': str(api_secret_n)}
    if export:
        with open(export_fn, 'w') as outfile:
            json.dump(api, outfile)
    return api


def using_requests(request_url, apisign):
    return requests.get(
        request_url,
        headers={"apisign": apisign}
    ).json()


class Bittrex(object):

    def __init__(self, api_key, api_secret, calls_per_second=1, dispatch=using_requests, api_version=API_V1_1):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.dispatch = dispatch
        self.call_rate = 1.0 / calls_per_second
        self.last_call = None
        self.api_version = api_version

    def decrypt(self):
        if encrypted:
            cipher = AES.new(getpass.getpass(
                'Input decryption password (string will not show)'))
            try:
                if isinstance(self.api_key, str):
                    self.api_key = ast.literal_eval(self.api_key)
                if isinstance(self.api_secret, str):
                    self.api_secret = ast.literal_eval(self.api_secret)
            except Exception:
                pass
            self.api_key = cipher.decrypt(self.api_key).decode()
            self.api_secret = cipher.decrypt(self.api_secret).decode()
        else:
            raise ImportError('"pycrypto" module has to be installed')

    def wait(self):
        if self.last_call is None:
            self.last_call = time.time()
        else:
            now = time.time()
            passed = now - self.last_call
            if passed < self.call_rate:
                # print("sleep")
                time.sleep(self.call_rate - passed)

            self.last_call = time.time()

    def _api_query(self, protection=None, path_dict=None, options=None):

        if not options:
            options = {}

        if self.api_version not in path_dict:
            raise Exception('method call not available under API version {}'.format(self.api_version))

        request_url = BASE_URL_V2_0 if self.api_version == API_V2_0 else BASE_URL_V1_1
        request_url = request_url.format(path=path_dict[self.api_version])

        nonce = str(int(time.time() * 1000))

        if protection != PROTECTION_PUB:
            request_url = "{0}apikey={1}&nonce={2}&".format(request_url, self.api_key, nonce)

        request_url += urlencode(options)

        try:
           apisign = hmac.new(self.api_secret.encode(),
                              request_url.encode(),
                              hashlib.sha512).hexdigest()

           self.wait()

           return self.dispatch(request_url, apisign)

        except:
            return {
               'success' : False,
               'message' : 'NO_API_RESPONSE',
               'result'  : None
            }

    def get_markets(self):
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarkets',
            API_V2_0: '/pub/Markets/GetMarkets'
        }, protection=PROTECTION_PUB)

    def get_currencies(self):
        return self._api_query(path_dict={
            API_V1_1: '/public/getcurrencies',
            API_V2_0: '/pub/Currencies/GetCurrencies'
        }, protection=PROTECTION_PUB)

    def get_ticker(self, market):
        return self._api_query(path_dict={
            API_V1_1: '/public/getticker',
        }, options={'market': market}, protection=PROTECTION_PUB)

    def get_market_summaries(self):
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarketsummaries',
            API_V2_0: '/pub/Markets/GetMarketSummaries'
        }, protection=PROTECTION_PUB)

    def get_marketsummary(self, market):
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarketsummary',
            API_V2_0: '/pub/Market/GetMarketSummary'
        }, options={'market': market, 'marketname': market}, protection=PROTECTION_PUB)

    def get_orderbook(self, market, depth_type=BOTH_ORDERBOOK):
        return self._api_query(path_dict={
            API_V1_1: '/public/getorderbook',
            API_V2_0: '/pub/Market/GetMarketOrderBook'
        }, options={'market': market, 'marketname': market, 'type': depth_type}, protection=PROTECTION_PUB)

    def get_market_history(self, market):
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarkethistory',
            API_V2_0: '/pub/Market/GetMarketHistory'
        }, options={'market': market, 'marketname': market}, protection=PROTECTION_PUB)

    def buy_limit(self, market, quantity, rate):
        return self._api_query(path_dict={
            API_V1_1: '/market/buylimit',
        }, options={'market': market,
                    'quantity': quantity,
                    'rate': rate}, protection=PROTECTION_PRV)

    def sell_limit(self, market, quantity, rate):
        return self._api_query(path_dict={
            API_V1_1: '/market/selllimit',
        }, options={'market': market,
                    'quantity': quantity,
                    'rate': rate}, protection=PROTECTION_PRV)

    def cancel(self, uuid):
        return self._api_query(path_dict={
            API_V1_1: '/market/cancel',
            API_V2_0: '/key/market/cancel'
        }, options={'uuid': uuid, 'orderid': uuid}, protection=PROTECTION_PRV)

    def get_open_orders(self, market=None):
        return self._api_query(path_dict={
            API_V1_1: '/market/getopenorders',
            API_V2_0: '/key/market/getopenorders'
        }, options={'market': market, 'marketname': market} if market else None, protection=PROTECTION_PRV)

    def get_balances(self):
        return self._api_query(path_dict={
            API_V1_1: '/account/getbalances',
            API_V2_0: '/key/balance/getbalances'
        }, protection=PROTECTION_PRV)

    def get_balance(self, currency):
        return self._api_query(path_dict={
            API_V1_1: '/account/getbalance',
            API_V2_0: '/key/balance/getbalance'
        }, options={'currency': currency, 'currencyname': currency}, protection=PROTECTION_PRV)

    def get_deposit_address(self, currency):
        return self._api_query(path_dict={
            API_V1_1: '/account/getdepositaddress',
            API_V2_0: '/key/balance/getdepositaddress'
        }, options={'currency': currency, 'currencyname': currency}, protection=PROTECTION_PRV)

    def withdraw(self, currency, quantity, address):
        return self._api_query(path_dict={
            API_V1_1: '/account/withdraw',
            API_V2_0: '/key/balance/withdrawcurrency'
        }, options={'currency': currency, 'quantity': quantity, 'address': address}, protection=PROTECTION_PRV)

    def get_order_history(self, market=None):
        return self._api_query(path_dict={
            API_V1_1: '/account/getorderhistory',
            API_V2_0: '/key/orders/getorderhistory'
        }, options={'market': market, 'marketname': market} if market else None, protection=PROTECTION_PRV)

    def get_order(self, uuid):
        return self._api_query(path_dict={
            API_V1_1: '/account/getorder',
            API_V2_0: '/key/orders/getorder'
        }, options={'uuid': uuid, 'orderid': uuid}, protection=PROTECTION_PRV)

    def get_withdrawal_history(self, currency=None):
        return self._api_query(path_dict={
            API_V1_1: '/account/getwithdrawalhistory',
            API_V2_0: '/key/balance/getwithdrawalhistory'
        }, options={'currency': currency, 'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def get_deposit_history(self, currency=None):
        return self._api_query(path_dict={
            API_V1_1: '/account/getdeposithistory',
            API_V2_0: '/key/balance/getdeposithistory'
        }, options={'currency': currency, 'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def list_markets_by_currency(self, currency):
        return [market['MarketName'] for market in self.get_markets()['result']
                if market['MarketName'].lower().endswith(currency.lower())]

    def get_wallet_health(self):
        return self._api_query(path_dict={
            API_V2_0: '/pub/Currencies/GetWalletHealth'
        }, protection=PROTECTION_PUB)

    def get_balance_distribution(self):
        return self._api_query(path_dict={
            API_V2_0: '/pub/Currency/GetBalanceDistribution'
        }, protection=PROTECTION_PUB)

    def get_pending_withdrawals(self, currency=None):
        return self._api_query(path_dict={
            API_V2_0: '/key/balance/getpendingwithdrawals'
        }, options={'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def get_pending_deposits(self, currency=None):
        return self._api_query(path_dict={
            API_V2_0: '/key/balance/getpendingdeposits'
        }, options={'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def generate_deposit_address(self, currency):
        return self._api_query(path_dict={
            API_V2_0: '/key/balance/getpendingdeposits'
        }, options={'currencyname': currency}, protection=PROTECTION_PRV)

    def trade_sell(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                   condition_type=None, target=0.0):
        return self._api_query(path_dict={
            API_V2_0: '/key/market/tradesell'
        }, options={
            'marketname': market,
            'ordertype': order_type,
            'quantity': quantity,
            'rate': rate,
            'timeInEffect': time_in_effect,
            'conditiontype': condition_type,
            'target': target
        }, protection=PROTECTION_PRV)

    def trade_buy(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                  condition_type=None, target=0.0):
        return self._api_query(path_dict={
            API_V2_0: '/key/market/tradebuy'
        }, options={
            'marketname': market,
            'ordertype': order_type,
            'quantity': quantity,
            'rate': rate,
            'timeInEffect': time_in_effect,
            'conditiontype': condition_type,
            'target': target
        }, protection=PROTECTION_PRV)

    def get_candles(self, market, tick_interval):

        return self._api_query(path_dict={
            API_V2_0: '/pub/market/GetTicks'
        }, options={
            'marketName': market, 'tickInterval': tick_interval
        }, protection=PROTECTION_PUB)

##############################################################
# Enigma Quickfire Trading Bot for Bittrex (Anakratis)
#
# Inspired by Enigma of Enhanced Investor
#
# This is the first scrypt as part of the Vavrespa-series of
# useful Bittrex bots. This bot allows you to trade more
# rapidly and efficiently thanks to simple hotkey trading.
#
# NOTE: You must have an API key assigned, with trading and
# viewing privileges.
#
##############################################################

def api_settings():

    while True:

        APIKEY = raw_input("Enter your Bittrex API key: ")
        SECRETKEY = raw_input("Enter your Bittrex Secret Key: ")

        print("Locating socket...")
        V1Bittrex = Bittrex(APIKEY, SECRETKEY, api_version=API_V1_1)
        V2Bittrex = Bittrex(APIKEY, SECRETKEY, api_version=API_V2_0)

        IntegrityAPI = V2Bittrex.get_balance("BTC")

        if IntegrityAPI['message'] == "APIKEY_INVALID":

            time.sleep(1)
            print("Incorrect API key. Please retry...")
            print("")

            continue

        else:

            time.sleep(1)
            print("Connected.")

            return APIKEY, SECRETKEY

def market_settings():

    while True:

        print("")
        MARKET = raw_input("Enter BTC market to trade e.g. 'BCC': ")
        TickerString = "BTC-" + MARKET
        IntegrityMarket = V1Bittrex.get_ticker(TickerString)

        if IntegrityMarket['message'] == "INVALID_MARKET":

            time.sleep(1)
            print("Incorrect market handle. Please retry...")

            continue

        else:

            time.sleep(1)
            print("Market successfully selected.")

            return MARKET    

print("")
print("")
print("Enigma 0.2")
print("Programmed with love by Vavrespa, inspired by Enigma")
print("Enhanced Investor Network")

time.sleep(1)

print("")
print("Launching...")

time.sleep(1)

APIKEY, SECRETKEY = api_settings()
V1Bittrex = Bittrex(APIKEY, SECRETKEY, api_version=API_V1_1)
V2Bittrex = Bittrex(APIKEY, SECRETKEY, api_version=API_V2_0)

time.sleep(0.5)

MARKET = market_settings()
MarketString = "BTC-" + MARKET
MarketSwap = 0
FailedHandle = 0

print("Let's play ball.")
print("")

time.sleep(0.5)

print("NOTE: All orders are market. You've been warned.")
print("")

time.sleep(0.5)

UserSelection = None

while True:

    if MarketSwap == 1:
        MarketString = "BTC-" + MARKET
        MarketSwap = 0
    
    if UserSelection == None:
        pass
    else:
        del UserSelection

    BTCBalanceArray = V2Bittrex.get_balance('BTC')
    BTCBalance = BTCBalanceArray['result']['Available']
    AltBalanceArray = V2Bittrex.get_balance(MARKET)

    if AltBalanceArray['result'] == None:
        AltBalance = 0.0
    else:
        AltBalance = AltBalanceArray['result']['Available']

    print(MarketString)
    print(str(AltBalance) + " " + str(MARKET) + " available")
    print("")
    print("Press the corresponding number to take an action, or enter a market to swap to.")
    print("1 = Buy, 1% ")
    print("2 = Buy, 5% ")
    print("3 = Buy, 10% ")
    print("4 = Buy, 50% ")
    print("5 = Sell, 10% ")
    print("6 = Sell, 25% ")
    print("7 = Sell, 50% ")
    print("8 = Sell, 75% ")
    print("9 = Buy, All ")
    print("0 = Sell, All ")
    print("Enter a ticker to swap markets (e.g. BCC).")
    print("Press 'x' to exit.")
    print("")
    UserSelection = raw_input("")

    if UserSelection == "1":
        MarketBuy = V1Bittrex.get_orderbook(MarketString, depth_type=SELL_ORDERBOOK)
        MarketBuyAmt = float(MarketBuy['result'][0]['Rate'])

        BTCTrade = float(BTCBalance * 0.01) / MarketBuyAmt

        V1Bittrex.buy_limit(MarketString, BTCTrade, MarketBuyAmt)

    elif UserSelection == "2":
        MarketBuy = V1Bittrex.get_orderbook(MarketString, depth_type=SELL_ORDERBOOK)
        MarketBuyAmt = float(MarketBuy['result'][0]['Rate'])

        BTCTrade = float(BTCBalance * 0.05) / MarketBuyAmt

        V1Bittrex.buy_limit(MarketString, BTCTrade, MarketBuyAmt)

    elif UserSelection == "3":
        MarketBuy = V1Bittrex.get_orderbook(MarketString, depth_type=SELL_ORDERBOOK)
        MarketBuyAmt = float(MarketBuy['result'][0]['Rate'])

        BTCTrade = float(BTCBalance * 0.1) / MarketBuyAmt

        V1Bittrex.buy_limit(MarketString, BTCTrade, MarketBuyAmt)

    elif UserSelection == "4":
        MarketBuy = V1Bittrex.get_orderbook(MarketString, depth_type=SELL_ORDERBOOK)
        MarketBuyAmt = float(MarketBuy['result'][0]['Rate'])

        BTCTrade = float(BTCBalance * 0.5) / MarketBuyAmt

        V1Bittrex.buy_limit(MarketString, BTCTrade, MarketBuyAmt)

    elif UserSelection == "5":        
        AltTrade = float(AltBalance * 0.1)

        MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
        MarketSellAmt = float(MarketSell['result'][0]['Rate'])

        V1Bittrex.sell_limit(MarketString, AltTrade, MarketSellAmt)

    elif UserSelection == "6":
        AltTrade = float(AltBalance * 0.25)

        MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
        MarketSellAmt = float(MarketSell['result'][0]['Rate'])

        V1Bittrex.sell_limit(MarketString, AltTrade, MarketSellAmt)

    elif UserSelection == "7":
        AltTrade = float(AltBalance * 0.5)

        MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
        MarketSellAmt = float(MarketSell['result'][0]['Rate'])

        V1Bittrex.sell_limit(MarketString, AltTrade, MarketSellAmt)

    elif UserSelection == "8":
        AltTrade = float(AltBalance * 0.75)

        MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
        MarketSellAmt = float(MarketSell['result'][0]['Rate'])

        V1Bittrex.sell_limit(MarketString, AltTrade, MarketSellAmt)

    elif UserSelection == "9":
        MarketBuy = V1Bittrex.get_orderbook(MarketString, depth_type=SELL_ORDERBOOK)
        MarketBuyAmt = float(MarketBuy['result'][0]['Rate'])

        BTCTrade = float(BTCBalance * 0.98) / MarketBuyAmt

        results = V1Bittrex.buy_limit(MarketString, BTCTrade, MarketBuyAmt)

        print(results)

    elif UserSelection == "0":
        AltTrade = float(AltBalance)

        MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
        MarketSellAmt = float(MarketSell['result'][0]['Rate'])

        V1Bittrex.sell_limit(MarketString, AltTrade, MarketSellAmt)
    
    elif UserSelection == "x" or UserSelection == "X":
        break

    else:
        while True:

            if FailedHandle == 1:
                UserSelection = raw_input("")

            TickerString = "BTC-" + UserSelection
            IntegrityMarket = V1Bittrex.get_ticker(TickerString)

            if IntegrityMarket['message'] == "INVALID_MARKET":

                FailedHandle = 1
                print("Incorrect market handle. Please retry...")
                print("")

                continue

            else:
                MARKET = UserSelection
                MarketSwap = 1
                print("Swapping markets...")
                print("")
                
                break

    if UserSelection == "9" or UserSelection == "1" or UserSelection == "2" or UserSelection == "3" or UserSelection == "4":
        print("")
        print("BOUGHT " + str(BTCTrade) + " " + str(MARKET) + " at " + str(MarketBuyAmt) + " BTC")
        print("Required price " + str(MarketBuyAmt * 1.0025) +  " BTC or above to make profit.")
        print("")
        time.sleep(0.2)
    
    elif UserSelection == "0" or UserSelection == "5" or UserSelection == "6" or UserSelection ==  "7" or UserSelection == "8":
        print("")
        print("SOLD " + str(AltTrade) + " " + str(MARKET) + " at " + str(MarketSellAmt) + " BTC")
        print("")
        time.sleep(0.2)
