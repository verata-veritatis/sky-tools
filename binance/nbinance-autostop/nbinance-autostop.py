#######################################
# NODAL.ID BINANCE AUTOSTOP
# Version x1.21 (June 1, 2019)
#######################################

# REQUIREMENTS: python3.7 python-binance colorama

import os
import json

from colorama import Fore, Back, Style
from binance.client import Client

import threading
import requests
import operator

import textwrap
import time
import warnings
from decimal import Decimal

import sys

#######################################
# LOGGING FUNCTION
#######################################

def Logging(Level, String):

    import time

    TIME = time.strftime("%Y-%m-%d %H:%M:%S")

    if abs(Level) == 0:
        RESULT = Fore.LIGHTBLACK_EX + TIME + Style.RESET_ALL + " - INFO - " + String
    elif abs(Level) == 1:
        RESULT = TIME + " - WARN - " + String
    elif abs(Level) == 2:
        RESULT = TIME + " - ERROR - " + String
    elif abs(Level) == 3:
        RESULT = TIME + " - CRITICAL - " + String
    else:
        raise AttributeError('Improper logging level.')

    if Level >= 0:
        print(RESULT)
    if Level < 0:
        query = input(RESULT)
        return query

#######################################
# API KEY SETTINGS
#######################################

# DETERMINE FOLDER PATH
PATH = os.path.expanduser('~/.ndar/')
if not os.path.exists(PATH):
    os.makedirs(PATH)

# OPEN CONFIG FILE
try:
    with open(PATH + "binance.cfg", 'r') as CONFIG:
        USER = json.load(CONFIG)
        API_KEY = USER['APIK']
        API_SECRET = USER['SECK']

# IF NOT, CREATE CONFIG FILE
except:
    print("*** No local key file found.")
    time.sleep(1)

    API_KEY = input("API Key: ")
    API_SECRET = input("Secret Key: ")

    with open(PATH + "binance.cfg", 'w') as CONFIG:
        USER = {
        "APIK": API_KEY,
        "SECK": API_SECRET,
        }
        json.dump(USER, CONFIG)

    print("*** Key file has been created.")
    time.sleep(1)

#######################################
# IP ADDRESS POLLING
#######################################

# FETCH IP ADDRESS FROM ICANHAZIP
try:
    IP_TEST = requests.get(url = 'https://icanhazip.com')
except:
    print("")
    print("{}ERROR: A connection could not be established. Please check your internet connection and try again.{}".format(Back.RED, Style.RESET_ALL))
    print("")
    time.sleep(1)
    sys.exit()

# DECODE IP ADDRESS
IP_TEST = IP_TEST.content
IP_TEST = IP_TEST.decode()

# PRINT IP ADDRESS & ASK TO PROCEED
print("")
GATE = input("{}WARNING: Your IP address has been detected as {}. Would you like to continue? (Y or N):{} ".format(Back.BLUE, IP_TEST.rstrip(), Style.RESET_ALL))
if GATE.upper() == 'Y':
    pass
else:
    print("")
    print('Aborting connection...')
    time.sleep(1)
    sys.exit()

#######################################
# SERVER AUTHENTICATION
#######################################

print("")
Logging(0, "NODAL : Binance : Autostop Bot")
Logging(0, "x1.21 June 1, 2019")
time.sleep(1)

Logging(0, "Connecting to wss://stream.binance.com:9443...")
Binance = Client(API_KEY, API_SECRET)
Logging(0, "Datastream initiated.")
print("")

print("{}NOTE: You may type 'exit' during any inquiry to shut down the program.{}".format(Back.RED, Style.RESET_ALL))
time.sleep(1)

print("")

#######################################
# USER QUERY
#######################################

def UserQuery(StopList):

    # TICKER & TICKERSELF
    while True:
        Ticker = input("Enter the Binance pair (e.g. NEOBTC), type 'all' to show all active stops, or type 'rm' to remove a stop: ")
        Ticker = Ticker.upper()

        if Ticker == 'EXIT':
            print("")
            print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
            sys.exit()

        elif Ticker == 'ALL':
            print("")
            print("----------------------------------------------------------------------------")
            StopNr = 0

            for Stop in StopList:
                StopNr = StopNr + 1

                if Stop['type'] == 0:
                    FrmCd = 'TSSL'

                else:
                    FrmCd = 'STOP'

                if not Stop['status']:
                    SttCd = Fore.GREEN + "ACTIVE" + Style.RESET_ALL

                else:
                    SttCd = Fore.LIGHTRED_EX + "TRIGGERED" + Style.RESET_ALL

                print(str(StopNr) + ": " + SttCd + " - {} for {} {} at {}.".format(FrmCd, str(Stop['qty']), Stop['ticker'], str(Stop['price'])))

            print("----------------------------------------------------------------------------")
            print("")
            continue

        elif Ticker == 'RM':
            print("")
            print("----------------------------------------------------------------------------")

            RmdEntry = input("Which entry do you want to remove? (e.g. '4'): ")
            RmdEntry = int(RmdEntry) - 1

            print("{}DELETED{}: {}".format(Fore.LIGHTRED_EX, Style.RESET_ALL, StopList[RmdEntry]))
            print("----------------------------------------------------------------------------")
            print("")

            del StopList[RmdEntry]
            continue
        
        SanityCheck = Binance.get_symbol_info(Ticker)

        if SanityCheck != None:
            TickerSelf = SanityCheck['baseAsset']
            break

        else:
            Logging(2, "Invalid entry. Please try again")
            continue

    print("")
    print("---------------------------------- {}{}{} ----------------------------------".format(Fore.LIGHTYELLOW_EX, Ticker, Style.RESET_ALL))

    # GRAB RECENT TRADES
    Trades = Binance.get_my_trades(symbol=Ticker)

    try:
        RecentTrade = Trades[-1]
        RecentPrice = float(RecentTrade['price'])
        RecentQty = float(RecentTrade['qty'])
        RefQuery = input("Recent trade detected for {} {} at {}. Would you like to use this as a reference? (Y or N): ".format(RecentQty, TickerSelf, RecentPrice))

    except:
        RefQuery = 'N'

    # TYPE
    while True:
        print("""
Would you like to place a trailing stop/stop-loss or stoploss only?
    0: Trailing Stop + Stop-loss
    1: Stop-loss Only
        """)
        Type = input("*** Selection: ")

        try:
            Type = int(Type)
            
        except:
            try:
                if Type.upper() == 'EXIT':
                    print("")
                    print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                    sys.exit()

            except:
                Logging(2, "Invalid entry. Please try again")
                continue

            Logging(2, "Invalid entry. Please try again")
            continue

        if Type == 0 or Type == 1:
            break

        else:
            Logging(2, "Invalid entry. Please try again")
            continue

    # PRICE, TRAIL, QTY
    while True:
        if RefQuery.upper() == 'EXIT':
            print("")
            print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
            sys.exit()

        elif RefQuery.upper() == 'Y':
            Qty = RecentQty

            if Type == 0:
                while True:
                    Trail = input("By what percentage do you want to trail (e.g. '1%')?: ")

                    if Trail[-1] == '%':
                        Trail = Trail[:-1]

                    Price = RecentPrice - (RecentPrice * (float(Trail) / 100))
                    print(Price)

                    if Trail.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    try:
                        float(Trail)
                        break

                    except:
                        Logging(2, "Invalid entry. Please try again")
                        continue

                    break

            elif Type == 1:
                while True:
                    Price = input("At what price (in BTC) or percentage from entry do you want to place the stop (e.g. '0.00004806' or '5%')?: ")
                    Trail = None

                    if Price == 'EXIT' or Price == 'exit':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    try:
                        if Price.endswith('%'):
                            Price = Price[:-1]
                            Price = RecentPrice - (RecentPrice * (float(Price) / 100))

                        float(Price)
                        break

                    except:
                        Logging(2, "Invalid entry. Please try again")
                        continue

                    break

        elif RefQuery.upper() == 'N':
            if Type == 0:
                while True:
                    Price = input("What is your entry price (e.g. 0.00004608)?: ")

                    if Price.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    try:
                        float(Price)
                        break

                    except:
                        Logging(2, "Invalid price. Please try again")
                        continue

                    break

                while True:
                    Trail = input("By what percentage do you want to trail (e.g. '1%')?: ")

                    if Trail.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    if Trail.endswith('%'):
                        Trail = Trail[:-1]

                    try:
                        float(Trail)
                        Price = float(Price) - (float(Price) * (float(Trail) / 100))
                        print(Price)
                        break

                    except:
                        Logging(2, "Invalid entry. Please try again")
                        continue

                    break

                # Quantity
                while True:
                    Qty = input("Enter the desired quantity or type 'all' to use entire available {} balance: ".format(TickerSelf))

                    if Qty.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    elif Qty.upper() == 'ALL':
                        Asset = Binance.get_asset_balance(TickerSelf)
                        Qty = Asset['free']

                    else:
                        try:
                            float(Qty)
                            break

                        except:
                            Logging(2, "Invalid entry. Please try again")
                            continue

                        break

                    break

            elif Type == 1:
                while True:
                    Price = input("At what price (in BTC) do you want to place the stop (e.g. 0.00004806): ")
                    Trail = None

                    if Price.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    try:
                        float(Price)
                        break

                    except:
                        Logging(2, "Invalid price. Please try again")
                        continue

                    break

                # Quantity
                while True:
                    Qty = input("Enter the desired quantity or type 'all' to use entire available {} balance: ".format(TickerSelf))

                    if Qty.upper() == 'EXIT':
                        print("")
                        print("{}NOTE: The program has shut down. You may now close this window.{}".format(Back.RED, Style.RESET_ALL))
                        sys.exit()

                    elif Qty.upper() == 'ALL':
                        Asset = Binance.get_asset_balance(TickerSelf)
                        Qty = Asset['free']

                    else:
                        try:
                            float(Qty)
                            break

                        except:
                            Logging(2, "Invalid entry. Please try again")
                            continue

                        break

        else:
            Logging(2, "Invalid entry. Please try again")
            continue

        break

    print("----------------------------------------------------------------------------")
    print("")

    # SPECIFY ORDER SIZE PRECISION
    #########################################################
    sPrecision = Binance.get_symbol_info(symbol=Ticker)
    sPrecision = sPrecision['filters'][2]['minQty']
    sPrecision = Decimal(sPrecision).normalize()
    Qty = float(Qty) // float(sPrecision) * float(sPrecision)
    #########################################################

    return Type, Ticker, TickerSelf, Price, Trail, Qty

#######################################
# STOP LIST MANAGERS
#######################################

def Update():
    while True:
        StopList.append(Application(StopList))

def Application(StopList):
    T, K, S, P, R, Q = UserQuery(StopList)
    return ({'status': False, 'type': T, 'ticker': K, 'asset': S, 'price': float(P), 'trail': float(R), 'qty': float(Q)})

def Process(StopList):
    while True:
        if StopList != []:
            for Stop in StopList:
                if not Stop['status']:
                    QuoteArray = Binance.get_ticker(symbol=Stop['ticker'])
                    LastPrice = float(QuoteArray['lastPrice'])

                    if Stop['type'] == 0:
                        TrailingStop = LastPrice - (LastPrice * (Stop['trail'] / 100))

                        if TrailingStop > Stop['price']:
                            Stop['price'] = TrailingStop

                        else:
                            if LastPrice <= Stop['price']:
                                try:
                                    Binance.order_market_sell(symbol=Stop['ticker'], quantity=Stop['qty'])

                                except:
                                    print("{}FATAL: Binance API error detected. Please double check your assets.{}".format(Back.RED, Style.RESET_ALL))

                                Stop['status'] = True

                    else:
                        if LastPrice <= Stop['price']:
                            try:
                                Binance.order_market_sell(symbol=Stop['ticker'], quantity=Stop['qty'])

                            except:
                                print("{}FATAL: Binance API error detected. Please double check your assets.{}".format(Back.RED, Style.RESET_ALL))

                            Stop['status'] = True

#######################################
# PRIMARY THREAD
#######################################

StopList = []

Interface = threading.Thread(target=Update)
Algorithm = threading.Thread(target=Process, args=(StopList,))

Interface.start()
Algorithm.start()
