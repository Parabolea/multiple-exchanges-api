#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 14:39:48 2024

@author: aaronng
"""
import sys
from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

# Alpha Vantage API key
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

mock_data = {
    "name": "Real Gross Domestic Product",
    "interval": "annual",
    "unit": "billions of dollars",
    "data": [
        {
            "date": "2023-01-01",
            "value": "22671.096"
        },
        {
            "date": "2022-01-01",
            "value": "22034.828"
        },
        {
            "date": "2021-01-01",
            "value": "21494.798"
        },
        {
            "date": "2020-01-01",
            "value": "20267.585"
        },
        {
            "date": "2019-01-01",
            "value": "20715.671"
        },
        {
            "date": "2018-01-01",
            "value": "20193.896"
        },
        {
            "date": "2017-01-01",
            "value": "19612.102"
        },
        {
            "date": "2016-01-01",
            "value": "19141.672"
        },
        {
            "date": "2015-01-01",
            "value": "18799.622"
        },
        {
            "date": "2014-01-01",
            "value": "18261.714"
        },
        {
            "date": "2013-01-01",
            "value": "17812.167"
        },
        {
            "date": "2012-01-01",
            "value": "17442.759"
        },
        {
            "date": "2011-01-01",
            "value": "17052.41"
        },
        {
            "date": "2010-01-01",
            "value": "16789.75"
        },
        {
            "date": "2009-01-01",
            "value": "16349.11"
        },
        {
            "date": "2008-01-01",
            "value": "16781.485"
        },
        {
            "date": "2007-01-01",
            "value": "16762.445"
        },
        {
            "date": "2006-01-01",
            "value": "16433.148"
        },
        {
            "date": "2005-01-01",
            "value": "15987.957"
        },
        {
            "date": "2004-01-01",
            "value": "15449.757"
        },
        {
            "date": "2003-01-01",
            "value": "14877.312"
        },
        {
            "date": "2002-01-01",
            "value": "14472.712"
        },
        {
            "date": "2001-01-01",
            "value": "14230.726"
        },
        {
            "date": "2000-01-01",
            "value": "14096.033"
        },
        {
            "date": "1999-01-01",
            "value": "13543.774"
        },
        {
            "date": "1998-01-01",
            "value": "12924.876"
        },
        {
            "date": "1997-01-01",
            "value": "12370.299"
        },
        {
            "date": "1996-01-01",
            "value": "11843.599"
        },
        {
            "date": "1995-01-01",
            "value": "11413.012"
        },
        {
            "date": "1994-01-01",
            "value": "11114.647"
        },
        {
            "date": "1993-01-01",
            "value": "10684.179"
        },
        {
            "date": "1992-01-01",
            "value": "10398.046"
        },
        {
            "date": "1991-01-01",
            "value": "10044.238"
        },
        {
            "date": "1990-01-01",
            "value": "10055.129"
        },
        {
            "date": "1989-01-01",
            "value": "9869.003"
        },
        {
            "date": "1988-01-01",
            "value": "9519.427"
        },
        {
            "date": "1987-01-01",
            "value": "9137.745"
        },
        {
            "date": "1986-01-01",
            "value": "8832.611"
        },
        {
            "date": "1985-01-01",
            "value": "8537.004"
        },
        {
            "date": "1984-01-01",
            "value": "8195.295"
        },
        {
            "date": "1983-01-01",
            "value": "7642.266"
        },
        {
            "date": "1982-01-01",
            "value": "7307.314"
        },
        {
            "date": "1981-01-01",
            "value": "7441.485"
        },
        {
            "date": "1980-01-01",
            "value": "7257.316"
        },
        {
            "date": "1979-01-01",
            "value": "7275.999"
        },
        {
            "date": "1978-01-01",
            "value": "7052.711"
        },
        {
            "date": "1977-01-01",
            "value": "6682.804"
        },
        {
            "date": "1976-01-01",
            "value": "6387.437"
        },
        {
            "date": "1975-01-01",
            "value": "6060.875"
        },
        {
            "date": "1974-01-01",
            "value": "6073.363"
        },
        {
            "date": "1973-01-01",
            "value": "6106.371"
        },
        {
            "date": "1972-01-01",
            "value": "5780.048"
        },
        {
            "date": "1971-01-01",
            "value": "5491.445"
        },
        {
            "date": "1970-01-01",
            "value": "5316.391"
        },
        {
            "date": "1969-01-01",
            "value": "5306.594"
        },
        {
            "date": "1968-01-01",
            "value": "5145.914"
        },
        {
            "date": "1967-01-01",
            "value": "4904.864"
        },
        {
            "date": "1966-01-01",
            "value": "4773.931"
        },
        {
            "date": "1965-01-01",
            "value": "4478.555"
        },
        {
            "date": "1964-01-01",
            "value": "4205.277"
        },
        {
            "date": "1963-01-01",
            "value": "3976.142"
        },
        {
            "date": "1962-01-01",
            "value": "3810.124"
        },
        {
            "date": "1961-01-01",
            "value": "3590.066"
        },
        {
            "date": "1960-01-01",
            "value": "3500.272"
        },
        {
            "date": "1959-01-01",
            "value": "3412.421"
        },
        {
            "date": "1958-01-01",
            "value": "3191.216"
        },
        {
            "date": "1957-01-01",
            "value": "3215.065"
        },
        {
            "date": "1956-01-01",
            "value": "3148.765"
        },
        {
            "date": "1955-01-01",
            "value": "3083.026"
        },
        {
            "date": "1954-01-01",
            "value": "2877.708"
        },
        {
            "date": "1953-01-01",
            "value": "2894.411"
        },
        {
            "date": "1952-01-01",
            "value": "2764.803"
        },
        {
            "date": "1951-01-01",
            "value": "2656.32"
        },
        {
            "date": "1950-01-01",
            "value": "2458.532"
        },
        {
            "date": "1949-01-01",
            "value": "2261.928"
        },
        {
            "date": "1948-01-01",
            "value": "2274.627"
        },
        {
            "date": "1947-01-01",
            "value": "2184.614"
        },
        {
            "date": "1946-01-01",
            "value": "2209.911"
        },
        {
            "date": "1945-01-01",
            "value": "2500.057"
        },
        {
            "date": "1944-01-01",
            "value": "2524.752"
        },
        {
            "date": "1943-01-01",
            "value": "2338.761"
        },
        {
            "date": "1942-01-01",
            "value": "1998.542"
        },
        {
            "date": "1941-01-01",
            "value": "1681.049"
        },
        {
            "date": "1940-01-01",
            "value": "1428.075"
        },
        {
            "date": "1939-01-01",
            "value": "1312.365"
        },
        {
            "date": "1938-01-01",
            "value": "1214.869"
        },
        {
            "date": "1937-01-01",
            "value": "1256.503"
        },
        {
            "date": "1936-01-01",
            "value": "1195.251"
        },
        {
            "date": "1935-01-01",
            "value": "1058.836"
        },
        {
            "date": "1934-01-01",
            "value": "972.263"
        },
        {
            "date": "1933-01-01",
            "value": "877.431"
        },
        {
            "date": "1932-01-01",
            "value": "888.414"
        },
        {
            "date": "1931-01-01",
            "value": "1019.977"
        },
        {
            "date": "1930-01-01",
            "value": "1089.785"
        },
        {
            "date": "1929-01-01",
            "value": "1191.124"
        }
    ]
}

def fetch_economic_data(function_name, params=None):
    base_url = 'https://www.alphavantage.co/query?'
    url = f'{base_url}function={function_name}&apikey={API_KEY}'
    if params:
        for key, value in params.items():
            url += f'&{key}={value}'
    response = requests.get(url)
    data = response.json()
    # Handle API rate limits
    if 'Note' in data:
        print('API rate limit reached. Waiting for 60 seconds...')
        time.sleep(60)
        response = requests.get(url)
        data = response.json()
    return data

def plot_data(df, title, ylabel, fn_name):
    output_dir = './graphs'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f'{fn_name}.png')

    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['value'], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    # plt.show()

def process_and_plot(function_name, title, ylabel, params=None):
    orig_data = fetch_economic_data(function_name, params)
    # Check if 'data' key is in the response
    if 'data' not in orig_data:
        print(f"No data found for {title}. Response: {orig_data}")
        return
    data = filter_data_by_date(orig_data['data'], '2010-01-01')

    print(f'fetched {function_name} data successfully')
    print(data)

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True)
    df.sort_values('date', inplace=True)
    plot_data(df, title, ylabel, function_name)
    # Sleep to avoid hitting rate limits
    time.sleep(2)  

# List of economic indicators to fetch and plot
indicators = [
    {
        'function_name': 'REAL_GDP',
        'title': 'Real GDP Trending',
        'ylabel': 'GDP (Billions of Dollars)'
    },
    {
        'function_name': 'REAL_GDP_PER_CAPITA',
        'title': 'Real GDP per Capita',
        'ylabel': 'GDP per Capita (Dollars)'
    },
    {
        'function_name': 'TREASURY_YIELD',
        'title': '10-Year Treasury Yield Trending',
        'ylabel': 'Yield (%)',
        'params': {'interval': 'monthly', 'maturity': '10year'}
    },
    {
        'function_name': 'FEDERAL_FUNDS_RATE',
        'title': 'Federal Funds (Interest) Rate',
        'ylabel': 'Rate (%)'
    },
    {
        'function_name': 'CPI',
        'title': 'Consumer Price Index (CPI)',
        'ylabel': 'CPI'
    },
    {
        'function_name': 'INFLATION',
        'title': 'Inflation Rate',
        'ylabel': 'Inflation Rate (%)'
    },
    {
        'function_name': 'RETAIL_SALES',
        'title': 'Retail Sales',
        'ylabel': 'Retail Sales (Millions of Dollars)'
    },
    {
        'function_name': 'DURABLES',
        'title': 'Durable Goods Orders',
        'ylabel': 'Durable Goods Orders (Millions of Dollars)'
    },
    {
        'function_name': 'UNEMPLOYMENT',
        'title': 'Unemployment Rate',
        'ylabel': 'Unemployment Rate (%)'
    },
    {
        'function_name': 'NONFARM_PAYROLL',
        'title': 'Nonfarm Payroll',
        'ylabel': 'Number of Employees (Thousands)'
    }
]

def filter_data_by_date(data, limit_date):
    # Convert the limit date string to a datetime object
    limit_date_obj = datetime.strptime(limit_date, '%Y-%m-%d')

    # Filter the data to include only items with dates >= limit_date
    filtered_data = [
        item for item in data
        if datetime.strptime(item['date'], '%Y-%m-%d') >= limit_date_obj
    ]

    return filtered_data

# Fetch, process, and plot each indicator
# for indicator in indicators:
#     process_and_plot(
#         function_name=indicator['function_name'],
#         title=indicator['title'],
#         ylabel=indicator['ylabel'],
#         params=indicator.get('params', None)
#     )

if __name__ == "__main__":
    # print(filter_data_by_date(mock_data.get('data'), '2010-01-01'))
    for indicator in indicators:
        process_and_plot(
            function_name=indicator['function_name'],
            title=indicator['title'],
            ylabel=indicator['ylabel'],
            params=indicator.get('params', None)
        )
    print('done')
    sys.exit()

