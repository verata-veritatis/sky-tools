####################################################################
# Automated Stoploss for Bittrex
#
# Author:   Anakratis / Vavrespa
# NOTE:     You must have an API key assigned, with trading and
#           viewing privileges.
#
####################################################################

import sys
import time
import datetime
import settings
import btrxapi

from btrxapi import API_V1_1, API_V2_0, BUY_ORDERBOOK
from settings import V1Bittrex, V2Bittrex

print("")
print("")
print("Gate.")
print("Programmed with love by Vavrespa")

time.sleep(1)

print("")
print("Launching...")

time.sleep(0.5)

print("")
APIKEY, SECRETKEY = settings.api_settings()

print("")
MARKET = settings.market_settings()

print("")
while True:
    STOP = input("Enter stoploss in BTC e.g. 0.00001805: ")

    print("")
    print("Confirm stoploss settings:")
    print("Stoploss: " + str(STOP) + " BTC")
    lConf = input("Y/N? ")

    if lConf == "y" or lConf == "Y":
        break

    elif lConf == "n" or lConf == "N":
        print("Please re-enter values...")
        time.sleep(1)

    else:
        print("Incorrect entry, assuming bounds are correct...")
        time.sleep(1)
        print("")

time.sleep(0.5)

print("")
print("Launching bot...")
print("")

time.sleep(0.5)

RetryCount = 0
MarketString = "BTC-" + MARKET
print(MarketString + " STOP : " + str(STOP) + " BTC")

while True:
    TradePriceArray = V1Bittrex.get_ticker(MarketString)
    TradePrice = float(TradePriceArray['result']['Last'])
    CurrentTime = str(datetime.datetime.now())

    print(MarketString + " LAST : " + str(TradePrice) + " BTC" + " " + CurrentTime + " GMT", end="\r")
    sys.stdout.flush()

    if TradePrice <= float(STOP):

        print("")
        print("Activating stoploss...")

        MarketBalanceArray = V2Bittrex.get_balance(MARKET)
        MarketBalance = MarketBalanceArray['result']['Available']

        if MarketBalance > 0:
            OpenOrders = []
            OpenOrdersArray = V2Bittrex.get_open_orders(MarketString)
            OpenOrdersNumber = len(OpenOrdersArray['result'])

            if OpenOrdersNumber > 0:
                for i in range(0, OpenOrdersNumber):
                    OpenOrdersIter = OpenOrdersArray['result'][i]['OrderUuid']
                    print(OpenOrdersIter)

                    test = V1Bittrex.cancel(OpenOrdersIter)
                    print(test)

                    print("")
                    print("All open orders in current market have been canceled.")
                    print("")

            MarketSell = V1Bittrex.get_orderbook(MarketString, depth_type=BUY_ORDERBOOK)
            MarketSellAmt = float(MarketSell['result'][-1]['Rate'])

            MarketSellOrder = V1Bittrex.sell_limit(MarketString, float(MarketBalance), MarketSellAmt)

            if MarketSellOrder['success'] == False:
                ErrorMessage = MarketSellOrder['message']
                print("")
                print("ERROR: " + ErrorMessage)
                RetryCount = RetryCount + 1

                if RetryCount == 3:
                    print("3/3 sell attempts have failed. Closing Gate...")
                    print("")
                    quit()

                else:
                    print(str(RetryCount) + "/3 sell attempts have failed. Retrying...")
                    print("")
                    continue

            StoplossUUID = MarketSellOrder['result']['uuid']
            StoplossOrder = V1Bittrex.get_order(StoplossUUID)

            while True:
                IsOpen = StoplossOrder['result']['IsOpen']

                if IsOpen == "true":
                    continue

                else:  
                    ActualRate = StoplossOrder['result']['Price']
                    print("STOPLOSS activated.")
                    print("SOLD " + MarketBalance + " " + MARKET + " at " + str(ActualRate) + " BTC")
                    quit()
