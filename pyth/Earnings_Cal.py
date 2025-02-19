import uuid
import json
import sys
import csv
from enum import Enum

import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
from utils import safe_json_dumps
load_dotenv('../.env')

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# print(f"arg: {json.loads(sys.argv[1])}")
# print(f"second arg: {sys.argv[2]}")

# List of stock symbols
# stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'YINN', 'MU', 'COIN', 'TSM', 'SPY', 'TSLA']  # Add your desired stock symbols here
stock_symbols = json.loads(sys.argv[1])

# Today's date
today = datetime.today()

class DateRange(Enum):
    week = 7
    month = 30
    quarter = 91

range_value = getattr(DateRange, sys.argv[2])

# Date one week from now
one_week_later = today + timedelta(days=range_value.value)

# Convert dates to string format 'YYYY-MM-DD'
today_str = today.strftime('%Y-%m-%d')
one_week_later_str = one_week_later.strftime('%Y-%m-%d')

# Function to get earnings calendar
def get_earnings_calendar():
    url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey={API_KEY}'
    response = requests.get(url)
    decoded_content = response.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    earnings_list = list(cr)
    return earnings_list

# Fetch the earnings calendar data
earnings_data = get_earnings_calendar()

# Store earnings data
earnings_calendar = []

# Parse CSV data
# The first row contains headers
headers = earnings_data[0]
data_rows = earnings_data[1:]

for row in data_rows:
    # Create a dictionary for each row
    event = dict(zip(headers, row))
    symbol = event['symbol']
    report_date_str = event['reportDate']
    report_date = datetime.strptime(report_date_str, '%Y-%m-%d')

    # Check if the symbol is in our list and the report date is within the next week
    if (symbol in stock_symbols) and (today <= report_date <= one_week_later):
        earnings_calendar.append({
            'id': str(uuid.uuid4()),
            'symbol': symbol,
            'reportDate': report_date_str,
            'fiscalDateEnding': event.get('fiscalDateEnding', ''),
            'estimate': event.get('estimate', '')
        })

# Print the earnings calendar
# print("Upcoming Earnings in the Next Week:")
# if earnings_calendar:
#     for event in earnings_calendar:
#         print(f"Symbol: {event['symbol']}, Report Date: {event['reportDate']}, Estimate: {event['estimate']}")
# else:
#     print("No upcoming earnings in the next week for the specified symbols.")
print(safe_json_dumps(earnings_calendar))
sys.exit(0)