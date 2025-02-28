#!/bin/bash


# Define the API URL
API_URL="https://dbapi.allview-parabolea.com/earnings-calendar/market-watch/scrape"

# Make the request
curl -X POST "$API_URL"

# If authentication is required, use:
# curl -X GET -H "Authorization: Bearer YOUR_TOKEN" "$API_URL"