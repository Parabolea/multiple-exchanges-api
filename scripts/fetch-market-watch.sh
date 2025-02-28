#!/bin/bash

echo "Cron automated fetching from market watch"

# Define the API URL
API_URL="https://dbapi.allview-parabolea.com/earnings-calendar/market-watch/scrape"

# Make the request
curl -X POST "$API_URL"