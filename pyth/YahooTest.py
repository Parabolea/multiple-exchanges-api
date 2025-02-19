import yfinance as yf
import time
from datetime import datetime

tickers = ['MSFT', 'AAPL', 'T']

final_data = []

def fetch_dividend(ticker):
    global final_data
    stock = yf.Ticker(ticker)
    final_data.append({
        'ticker': ticker,
        'date': datetime.fromtimestamp(stock.info['exDividendDate']).isoformat(),
        'rate': stock.info['dividendRate'],
    })
    # Convert to DataFrame and reset the index
    # div_df = dividend.reset_index()
    # div_df.columns = ['Date', 'Dividends']  # Rename columns explicitly
    # json_dividends = div_df[['Date', 'Dividends']].to_dict(orient='records')
    # for dividend in json_dividends:
    #     final_data.append({
    #         'date': datetime.date.isoformat(dividend['Date']),
    #         'amount': dividend['Dividends']
    #     })
    # final_data = filter_future_events(final_data, 'date')
    time.sleep(2)

for ticker in tickers:
    fetch_dividend(ticker)

print(final_data)