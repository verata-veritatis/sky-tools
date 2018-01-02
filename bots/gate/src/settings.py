####################################################################
# API and Market Settings Assembly
# Author:   Anakratis / Vavrespa
# NOTE:     You must have an API key assigned, with trading and
#           viewing privileges.
####################################################################

import time
import btrxapi
from btrxapi import API_V1_1, API_V2_0

keysAPI = open("secrets.json", "r")

APIKEY = keysAPI.read(43)
APIKEY = APIKEY[10:42]
SECRETKEY = keysAPI.read(47)
SECRETKEY = SECRETKEY[14:46]

#filename = os.path.join(os.path.dirname(sys.executable), 'secrets.json')
#keysAPI = open(filename, 'r')

V1Bittrex = btrxapi.Bittrex(APIKEY, SECRETKEY, api_version=API_V1_1)
V2Bittrex = btrxapi.Bittrex(APIKEY, SECRETKEY, api_version=API_V2_0)

keysAPI.close()

def api_settings():
    while True:
        print("Reading API keys...")
        verifyKeys = V2Bittrex.get_balance("BTC")

        if verifyKeys['message'] == "APIKEY_INVALID":
            time.sleep(1)
            print("Incorrect API key. Gate will now close...")
            print("")

            exit()

        else:
            time.sleep(1)
            print("Connected.")

            return APIKEY, SECRETKEY

def market_settings():
    while True:
        MARKET = input("Enter BTC market e.g. 'BCC': ")
        MARKET = MARKET.upper()
        TickerString = "BTC-" + MARKET

        verifyMarket = V1Bittrex.get_ticker(TickerString)
        lValueArray = V1Bittrex.get_balance(MARKET)
        if lValueArray['success'] == False:
            pass

        else:
            lValue = lValueArray['result']['Available']

        if verifyMarket['message'] == "INVALID_MARKET":
            time.sleep(1)
            print("Incorrect market handle. Please retry...")
            print("")

            continue

        elif lValue == 0:
            print("You own no assets in this market...")
            print("")
            continue

        else:
            print("Market successfully selected.")
            return MARKET
