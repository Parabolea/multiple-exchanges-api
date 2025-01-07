# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 11:37:07 2024

@author: aaron
"""
import json
import random
from ib_insync import *
import pandas as pd
import datetime as dt
import nest_asyncio
import sys
import os
from dotenv import load_dotenv

nest_asyncio.apply()
path_to_env = '/home/ubuntu/api/.env'
load_dotenv(path_to_env)

# print("Arguments passed to the script:", sys.argv[1:])

is_demo = os.getenv('DEMO')
is_demo_bool = bool(is_demo)

# Initialize the IB connection
# util.logToConsole('DEBUG')
ib = IB()
# 7496 = live, 7497 = paper
ib.connect('172.31.15.205', 7497 if is_demo_bool else 7496, clientId=999)

# List of stock symbols to analyze
stock_symbols = sys.argv[1:] if len(sys.argv) > 1 else ['AAPL', 'NVDA']

# List to store the ATM implied volatilities
atm_vol_data = []

def is_expiring_this_coming_friday(exp):
    """
    Check if the given expiration date is the upcoming Friday.

    :param exp: The expiration date in '%Y%m%d' format.
    :return: True if exp is the date of the next Friday from today, False otherwise.
    """
    today = dt.date.today()
    exp_date = dt.datetime.strptime(exp, '%Y%m%d').date()
    
    if today.weekday() == 3 or today.weekday() == 4:  # If today is Thursday (3) or Friday (4)
        days_ahead = 7 + (4 - today.weekday())  # Skip to next week's Friday
    else:
        days_ahead = 4 - today.weekday()  # Friday is 4
    if days_ahead < 0:  # If today is past Friday, adjust to the next week
        days_ahead += 7

    next_friday = today + dt.timedelta(days=days_ahead)
    
    return exp_date == next_friday

def get_random_number():
    min_val = 40
    max_val = 90
    random_num = random.uniform(min_val, max_val)
    return round(random_num, 5)

def atm_options(ib, underlying_symbol):
    market_data_type = 3 if is_demo_bool else 1
    """
    Retrieve ATM options for the given underlying symbol with week-end expiries.
    """
    # Define the underlying asset
    underlying = Stock(underlying_symbol, 'SMART', 'USD')
    ib.qualifyContracts(underlying)
    ib.reqMarketDataType(market_data_type)
    spot_ticker = ib.reqMktData(underlying, '', False, False)
    ib.sleep(1)
    
    # Get the spot price
    spot_mid = (spot_ticker.bid + spot_ticker.ask) / 2
    if spot_mid is None:
        spot_mid = spot_ticker.last
    if spot_mid is None:
        # print(f"Could not retrieve price for {underlying_symbol}. Skipping.")
        return [], []
    spot_mid = round(spot_mid, 2)
    # print(f"Mid price for {underlying_symbol}: {spot_mid}")
        
    # Set lower and upper bounds for strikes extraction
    lower_bd = round(spot_mid * 0.99, 2)  # 1% differential 
    upper_bd = round(spot_mid * 1.01, 2)  # 1% differential
        
    chains = ib.reqSecDefOptParams(underlying.symbol, '', underlying.secType, underlying.conId)

    call_options = []
    put_options = []
    for chain in chains:
        if chain.exchange == 'SMART':
            # Filter for weekly expiration dates
            weekly_expirations = [exp for exp in chain.expirations if is_expiring_this_coming_friday(exp)]

            # Process options
            for exp in weekly_expirations:
                for strike in chain.strikes:
                    if lower_bd <= strike <= upper_bd:
                        for right in ['C', 'P']:
                            option = Option(underlying_symbol, exp, strike, right, 'SMART')
                            # # print(option)
                            ib.qualifyContracts(option)
                            ib.reqMarketDataType(market_data_type)
                            market_data = ib.reqMktData(option, '101,106', False, False)
                            ib.sleep(1)  # Allow time for data to be received
                            # if market_data.modelGreeks:
                            #     delta = market_data.modelGreeks.delta
                            #     if delta is None:
                            #         delta = 0
                            if right == 'C': # and 0.45 <= delta <= 0.65 :
                                call_options.append((option, market_data))
                            elif right == 'P': # and -0.65 <= delta <= -0.45:
                                put_options.append((option, market_data))
    return call_options, put_options


for symbol in stock_symbols:
    try:
        # Get ATM options expiring this coming Friday
        call_options, put_options = atm_options(ib, symbol)
        if call_options:
            # Take the first suitable ATM call option
            option_contract, option_ticker = call_options[0]
            imp_vol = option_ticker.impliedVolatility
            if imp_vol is None:
                # print(f"Could not retrieve implied volatility for {symbol}. Skipping.")
                continue
            # Convert implied volatility to percentage
            imp_vol_percent = imp_vol * 100
            implied_vol_data = get_random_number() if is_demo_bool else imp_vol_percent
            atm_vol_data.append({"symbol": symbol, "impliedVolatility": implied_vol_data})
        elif put_options:
            # Take the first suitable ATM call option
            option_contract, option_ticker = put_options[-1]
            imp_vol = option_ticker.impliedVolatility
            if imp_vol is None:
                # print(f"Could not retrieve implied volatility for {symbol}. Skipping.")
                continue
            # Convert implied volatility to percentage
            imp_vol_percent = imp_vol * 100
            implied_vol_data = get_random_number() if is_demo_bool else imp_vol_percent
            # print(f"{symbol}: {imp_vol_percent}")
            atm_vol_data.append({"symbol": symbol, "impliedVolatility": implied_vol_data})
        else:
            # print(f"No suitable ATM call options found for {symbol}. Skipping.")
            continue

    except Exception as e:
        print(f"An error occurred for {symbol}: {e}")
        continue


# Create a DataFrame and sort by implied volatility
# atm_vol_df = pd.DataFrame(atm_vol_data)

# Display the sorted DataFrame
print(json.dumps(atm_vol_data))

# Disconnect from IB
ib.disconnect()
