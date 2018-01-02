##############################################################
# Bittrex API Wrapper (Eric Somdahl)
#
# Thank you Eric for making my life so much easier. See more
# information at https://bittrex.com/Home/Api. You can
# also find Eric's wrapper at 
# https://github.com/ericsomdahl/python-bittrex.
#
##############################################################

import hmac
import hashlib
import time

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


#def encrypt(api_key, api_secret, export=True, export_fn='secrets.json'):
#    cipher = AES.new(getpass.getpass(
#        'Input encryption password (string will not show)'))
#    api_key_n = cipher.encrypt(api_key)
#    api_secret_n = cipher.encrypt(api_secret)
#    api = {'key': str(api_key_n), 'secret': str(api_secret_n)}
#    if export:
#        with open(export_fn, 'w') as outfile:
#            json.dump(api, outfile)
#    return api


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
