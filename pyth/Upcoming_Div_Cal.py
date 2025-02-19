#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 12:09:00 2025

@author: aaronng
"""

import json
import os
import sys
import time
from datetime import datetime

import requests
import yfinance as yf
from dotenv import load_dotenv
import logging
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

# Define a class combining caching and rate limiting
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

# Create the session with caching and rate limiting
session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),  # Cache storage in SQLite
)

# Set a user-agent to reduce risk of being blocked
session.headers["User-agent"] = "my-program/1.0"

logging.basicConfig(format='internal - %(asctime)s - %(levelname)s: %(message)s', level=logging.INFO, handlers=[logging.StreamHandler(sys.stderr)])

load_dotenv('../.env')

# Replace with your actual Alpha Vantage API key
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# LIST_API_KEYS = [API_KEY, 'OWQ3ON1NEEOTGTD5', 'I0JEICKWU0M3XUNZ']
LIST_API_KEYS = ['TBVXCQBCXQ4UWI1L']
current_key_index = 0
# List of stock symbols to check
# stock_symbols = ['IBM', 'AAPL', 'MSFT', 'T']
stock_symbols = json.loads(sys.argv[1])
final_data = []

logging.info(f"stock symbols: {stock_symbols}")

def yahoo_sourced_divided_data(ticker: str):
    logging.info(f"Starting yahoo fetch for {ticker}...")
    global final_data
    try:
        stock = yf.Ticker(ticker, session=session)
        logging.info("fetched yahoo data")
        result = {
            'ticker': ticker,
            'date': datetime.fromtimestamp(stock.info['exDividendDate']).isoformat(),
            'rate': stock.info['dividendRate'],
        }
        logging.info(result)
        time.sleep(1)
        return result
    except Exception as e:
        logging.error(e)
        sys.exit(1)

def get_dividend_data(symbol):
    global current_key_index
    try:
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'DIVIDENDS',
            'symbol': symbol,
            'apikey': LIST_API_KEYS[0]
        }
        response = requests.get(url, params=params)
        data = response.json()
        time.sleep(3)
        # if any("rate limit" in value.lower() for value in data.values()):
        #     if current_key_index == (len(LIST_API_KEYS) - 1):
        #         print("Max API key retries reached. Returning empty data.")
        #         exit(0)
        #     current_key_index = (current_key_index + 1)  # Update to next key
        #     print(f"API limit reached. Switching to key {current_key_index + 1} of {len(LIST_API_KEYS)}")
        #     time.sleep(3)  # Increase sleep time between retries
        #     return get_dividend_data(symbol)  # Retry with next API key

        # Check if data is returned under the expected key
        if 'data' in data:
            final_d = data['data']
            return final_d
        else:
            print(f"No dividend data found for symbol: {symbol}. Response: {data}")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Retrieve dividend data for all symbols and collect them in a list
# dividends_list = []
# for symbol in stock_symbols:
#     df_div = get_dividend_data(symbol)
#     if df_div is not None:
#         dividends_list.append(df_div)

# if dividends_list:
#     dividends_df = pd.concat(dividends_list, ignore_index=True)
#
#     # Convert dates and numeric values
#     dividends_df['ex_dividend_date'] = pd.to_datetime(dividends_df['ex_dividend_date'])
#     dividends_df['amount'] = pd.to_numeric(dividends_df['amount'], errors='coerce')
#     dividends_df.sort_values(by=['symbol', 'ex_dividend_date'], inplace=True)
#
#     # Filter for future declared dividend dates (today or later)
#     today = pd.Timestamp.today().normalize()
#     future_dividends_df = dividends_df[dividends_df['ex_dividend_date'] >= today]
#     json_result = future_dividends_df[['symbol', 'ex_dividend_date', 'amount']].to_dict(orient='records')
#     print(json_result)
# else:
#     print("No dividend data available.")

# def display_calendar_for_dividends(symbol, df):
#     """
#     For the given symbol and its future dividend events (df),
#     this function prints a text calendar for each month with upcoming dividends.
#     It marks days with a dividend event with an asterisk (*)
#     and then lists the dividend details below the calendar.
#     """
#     if df.empty:
#         print(f"\nNo upcoming dividend events for {symbol}.\n")
#         return
#
#     # Group dividend events by year and month
#     for (year, month), group in df.groupby([df['ex_dividend_date'].dt.year, df['ex_dividend_date'].dt.month]):
#         print(f"\nDividend Calendar for {symbol} - {calendar.month_name[month]} {year}")
#
#         # Create a dictionary mapping day -> list of dividend amounts
#         events = {}
#         for _, row in group.iterrows():
#             day = row['ex_dividend_date'].day
#             events.setdefault(day, []).append(row['amount'])
#
#         # Get the month’s calendar as a list of weeks (each week is a list of day numbers; 0 means no day)
#         month_calendar = calendar.monthcalendar(year, month)
#         print("Mo Tu We Th Fr Sa Su")
#         for week in month_calendar:
#             week_str = ""
#             for day in week:
#                 if day == 0:
#                     week_str += "   "  # empty day slot
#                 else:
#                     # Mark the day with an asterisk if a dividend is scheduled
#                     if day in events:
#                         day_str = f"{day:2d}*"
#                     else:
#                         day_str = f"{day:2d} "
#                     week_str += day_str + " "
#             print(week_str)
#
#         # Print out the dividend details for the marked days
#         for day, amounts in events.items():
#             amounts_str = ", ".join(map(str, amounts))
#             print(f"  {calendar.month_name[month]} {day}, {year}: Dividend(s) {amounts_str}")
#         print("\n")

# Display the calendar for future dividend events for each symbol
for symbol in stock_symbols:
    data = yahoo_sourced_divided_data(symbol)
    if data is not None:
        final_data.append(data)
print(final_data)
    # symbol_dividends = future_dividends_df[future_dividends_df['symbol'] == symbol]
    # display_calendar_for_dividends(symbol, symbol_dividends)
