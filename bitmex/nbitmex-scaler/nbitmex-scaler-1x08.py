#######################################
# NODAL.ID BITMEX ORDER SCALER
# Version x1.08 (May 27, 2019)
#######################################

# To install all dependencies, paste the following into your CLI:
# pip install colorama requests bitmex

import os
import json

from colorama import Fore, Back, Style
import bitmex
import requests

import math
import operator

import textwrap
import time
import warnings

#######################################
# LOGGING FUNCTION
#######################################

warnings.filterwarnings("ignore")

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

PATH = os.path.expanduser('~/.ndar/')
if not os.path.exists(PATH):
    os.makedirs(PATH)

try:
    with open(PATH + "bitmex.cfg", 'r') as CONFIG:
        USER = json.load(CONFIG)
        API_KEY = USER['APIK']
        API_SECRET = USER['SECK']

except:
    print("*** No local key file found.")
    time.sleep(1)

    API_KEY = input("API Key: ")
    API_SECRET = input("Secret Key: ")

    with open(PATH + "bitmex.cfg", 'w') as CONFIG:
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

try:
    IP_TEST = requests.get(url = 'https://icanhazip.com')
except:
    print("")
    print("{}ERROR: A connection could not be established. Please check your internet connection and try again.{}".format(Back.RED, Style.RESET_ALL))
    print("")
    time.sleep(1)
    exit()

IP_TEST = IP_TEST.content
IP_TEST = IP_TEST.decode()

print("")
GATE = input("{}WARNING: Your IP address has been recorded as {}. Would you like to continue? (Y or N):{} ".format(Back.RED, IP_TEST.rstrip(), Style.RESET_ALL))
if GATE.upper() == 'Y':
    pass
else:
    print("")
    print('Aborting connection...')
    time.sleep(1)
    exit()

#######################################
# SERVER AUTHENTICATION
#######################################

print("")
Logging(0, "NODAL : BITMEX : Scaling Bot")
Logging(0, "x1.01 May 27, 2019")

Logging(0, "Connecting to wss://bitmex.com:9443...")
Client = bitmex.bitmex(test=False, api_key=API_KEY, api_secret=API_SECRET)
Logging(0, "Datastream initiated.")

#######################################
# DEFAULT VARIABLES
#######################################

MARKET = 'XBTUSD'
ORDERS = 1
SCALING = 0

#######################################
# USER QUERY
#######################################

def OrderHandler(U, L, D, S, C, M):

    # HANDLE ALL NUMERALS
    U = float(U)
    L = float(L)
    D = int(D)
    S = int(S)
    C = int(C)

    # INITIATE SEQUENCES
    P = []
    A = []

    # CREATE PRICE SCALE
    for X in range(D):
        P.append(U-((U-L)/(D-1))*(X))

    # IF SCALING IS CONSTANT
    if S == 0:
        for Y in range(D):
            A.append(C/D)

    # IF SCALING IS ADDITIVE
    if S == 1:

        # CALCULATE INITIAL UNIT
        I = (2*C)/(D+(D**2))

        # CREATE CONTRACT SCALE
        for Y in range(D):
            A.append(I*(Y+1))

    # IF SCALING IS MULTIPLICATIVE
    if S == 2:

        # CALCULATE INITIAL UNIT
        I = -C/(1-(2**D))

        # CREATE CONTRACT SCALE
        for Y in range(D):
            A.append(I*(2**Y))

    # INVERT SCALES IF LONG
    if C < 0:
        P = P[::-1]

    for B in range(D):
        print("{orderQty = " + str(int(math.floor(A[B]))) + ", price = " + str(int(math.floor(P[B]))) + ", symbol = " + MARKET.upper() + "}")

    # CREATE ORDERS
    try:
        for Z in range(D):
            Client.Order.Order_new(orderQty = int(math.floor(A[Z])), price = int(math.floor(P[Z])), symbol = MARKET.upper()).result()
    except:
        print("")
        print("{}ERROR: Not enough XBT to place order!{}".format(Back.RED, Style.RESET_ALL))

    return

while True:

    print("""

    0. Create Orders Using Existing Settings (Select 3 to Setup)
    1. Create Orders With New Settings
    2. Cancel All Orders
    3. Settings
    4. Quit
    """)

    SELECT = input("Please make a selection: ")

    if SELECT == '0':
        print("")
        print("{}NOTE: A positive number of contracts places long orders, while a negative number places short orders.{}".format(Back.RED, Style.RESET_ALL))

        while True:
            CONTRACTS = input("Number of contracts to trade: ")
            try:
                int(CONTRACTS)
            except:
                print("{}ERROR: Input must be a number. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                time.sleep(1)
                continue
            break

        print("")

        while True:
            UPPER = input("Upper bound on " + MARKET + ": ")
            try:
                int(UPPER)
            except:
                print("{}ERROR: The upper bound must be a number. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                time.sleep(1)
                continue
            break

        while True:
            LOWER = input("Lower bound on " + MARKET + ": ")
            try:
                int(LOWER)
            except:
                print("{}ERROR: The lower bound must be a number. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                time.sleep(1)
                continue
            break

        print("")

        OrderHandler(UPPER, LOWER, ORDERS, SCALING, CONTRACTS, MARKET)

    elif SELECT == '1':
        Client.Order.Order_cancelAll().result()
        print("{}All orders have been canceled!{}".format(Back.RED, Style.RESET_ALL))
        time.sleep(1)

    elif SELECT == '2':
        Client.Order.Order_cancelAll().result()
        print("")
        print("{}All orders have been canceled!{}".format(Back.RED, Style.RESET_ALL))
        time.sleep(1)
        print("")

    elif SELECT == '3':

        while True:

            print("""

    0. Market Selection
    1. Number of Orders
    2. Contract Number Scaling
    3. Exit
            """)

            SETTING = input("Please make a selection: ")

            if SETTING == '0':
                print("")
                MARKET = input("What's the BITMEX market you'd like to play? (e.g. XBTUSD): ")

            elif SETTING == '1':
                print("")

                while True:
                    try:
                        ORDERS = abs(int(input("How many orders would you like to create? (e.g. 8): ")))
                        break
                    except:
                        print("{}ERROR: The number of orders must be an integer. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                        time.sleep(1)
                        continue

            elif SETTING == '2':

                print("""

    0: Fixed number of contracts per order (e.g. 10, 10, 10, 10).
    1: Contract number increases additively (e.g. 10, 20, 30, 40).
    2: Contract number increases multiplicatively (e.g. 10, 20, 40, 80).
                """)

                while True:
                    try:
                        SCALING = int(input("Please make a selection: "))
                    except:
                        print("{}ERROR: The scaling setting must be an integer. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                        time.sleep(1)
                        continue
                    if SCALING > 2 or SCALING < 0:
                        print("{}ERROR: Invalid setting. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                        time.sleep(1)
                        continue
                    else:
                        break

            elif SETTING == '3':
                break

            else:
                print("")
                print("{}ERROR: Invalid entry. Please try again...{}".format(Back.RED, Style.RESET_ALL))
                time.sleep(1)
                continue

    elif SELECT == '4':
        print("")
        CONFIRM_QUIT = input("Quitting DOES NOT cancel your open orders. Are you sure you'd like to quit? (Y or N): ")
        if CONFIRM_QUIT.upper() == 'Y':
            print("")
            print("{}Quitting the application...{}".format(Back.RED, Style.RESET_ALL))
            time.sleep(1)
            print("")
            break
    
    else:
        print("")
        print("{}ERROR: Invalid entry. Please try again...{}".format(Back.RED, Style.RESET_ALL))
        time.sleep(1)
        continue
