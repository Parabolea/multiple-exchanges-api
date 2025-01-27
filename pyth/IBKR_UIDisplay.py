
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:42:01 2023

@author: aaronng
"""
import os
from ib_insync import *
import nest_asyncio
from dotenv import load_dotenv
from utils import safe_json_dumps


nest_asyncio.apply()
load_dotenv('/home/ubuntu/api/.env')

class UIBaseIBKR:

    def __init__(self, host, port, client_id, is_demo=False):
        
        self.client_id = client_id
        self.ib = IB()
        self.is_demo = is_demo
        try:
            self.ib.connect(host, port, clientId=self.client_id)
            # print("Connection established with IB.")
        except Exception as e:
            print(f"Failed to connect to IB: {e}")
        # Additional initialization as required

    def test_positions(self):
        positions = self.ib.positions()
        account_values = self.ib.accountValues()
        # print(f"positions: {positions}")
        # print(f"account_values: {account_values}")

    def manage_port(self):
        positions = self.ib.positions()
        account_values = self.ib.accountValues()
        # Initialize sums for delta and theta
        total_delta = 0
        total_theta = 0

        options = []
        stocks = []
        futures = []

        # Calculate account metrics
        margin = next((float(av.value) for av in account_values if av.tag == 'MaintMarginReq'), None)
        equity = next((float(av.value) for av in account_values if av.tag == 'NetLiquidation'), None)
        account_margin = (margin / equity) * 100 if equity else 0
        options_count = 0
        stocks_count = 0
        futures_count = 0
        # Group positions by underlying instrument symbol
        positions_by_symbol = {}
        for position in positions:
            symbol = position.contract.symbol
            if symbol not in positions_by_symbol:
                positions_by_symbol[symbol] = []
            positions_by_symbol[symbol].append(position)

        # interface Position {
        #     contract: {
        #         symbol: string;
        #         secType: string;
        #         currency: string;
        #         exchange: string;
        # // Add other contract details here as needed
        #      };
        #     position: number;
        #     avgCost: number;
        # }
        # Object<symbol, Array<Position>>

        # Process positions for each instrument
        for symbol, symbol_positions in positions_by_symbol.items():
            # print(f"\nInstrument: {symbol}")
            instrument_total_notional = 0

            for position in symbol_positions:
                size = position.position
                direction = 'BUY' if position.position > 0 else 'SELL'
                avg_price = position.avgCost / 100
                instrument = self.ib.qualifyContracts(position.contract)[0]
                self.ib.reqMarketDataType(3 if self.is_demo else 1)
                market_data = self.ib.reqMktData(instrument, '106', False, False)
                self.ib.sleep(1)
                mark_price = market_data.close
                delta = 0
                theta = 0

                # Initialize variables for strike, ITM status, and total notional
                strike = ''
                itm = ''
                total_notional = ''
                option_type_full = ''

                # Get additional info if the position is an option
                # print(f"secType: {position.contract.secType}")
                if position.contract.secType == 'OPT':
                    # Get strike price and option type
                    strike = position.contract.strike
                    option_type = position.contract.right  # 'C' for Call, 'P' for Put
                    
                    # Map 'C' and 'P' to 'Call' and 'Put'
                    if option_type == 'C':
                        option_type_full = 'Call'
                    elif option_type == 'P':
                        option_type_full = 'Put'
                    else:
                        option_type_full = 'Unknown'

                    expiry_date = position.contract.lastTradeDateOrContractMonth

                    # Get underlying price
                    underlying_contract = Stock(symbol, 'SMART', 'USD')
                    # print(f"underlying_contract: {underlying_contract}")
                    self.ib.qualifyContracts(underlying_contract)
                    self.ib.reqMarketDataType(3 if self.is_demo else 1)
                    underlying_market_data = self.ib.reqMktData(underlying_contract, '', False, False)
                    self.ib.sleep(1)
                    # print(f"underlying_market_data: {underlying_market_data}")
                    underlying_price = underlying_market_data.last or underlying_market_data.close
                    # print(f"underlying_price: {underlying_price}")

                    # Check if the option is ITM
                    if option_type == 'C':
                        itm = 'Yes' if underlying_price > strike else 'No'
                    elif option_type == 'P':
                        itm = 'Yes' if underlying_price < strike else 'No'
                    else:
                        itm = 'Unknown'
                        
                    # Calculate the distance from spot to strike (%)
                    # If strike is above underlying_price => distance is positive; below => negative
                    distance_percent = ((strike - underlying_price) / underlying_price) * 100
                    # print(f"strike: {strike}, underlying_price: {underlying_price}, distance_percent: {distance_percent}")

                    # Calculate total notional value
                    total_notional = abs(size) * strike * 100
                    instrument_total_notional += total_notional

                    if market_data.modelGreeks:
                        delta = market_data.modelGreeks.delta
                        theta = market_data.modelGreeks.theta
                        total_delta += (delta * position.position if delta else 0)
                        total_theta += (theta * position.position if theta else 0)
                        # print(f"Delta for {symbol} {strike}: {delta}, Theta: {theta}")
                    # else:
                        # print(f"Greeks not available for {symbol} {strike}")

                    # Display position information with strike, ITM status, distance, and total notional
                    # print(
                    #     f"  Option Type: {option_type_full}, "
                    #     f"Strike: {strike}, Size: {size}, Direction: {direction}, "
                    #     f"Avg Price: {avg_price}, Current Price: {mark_price}, "
                    #     f"ITM: {itm}, Distance: {distance_percent:.2f}%, "
                    #     f"Notional: {total_notional}"
                    # )
                    options_count += 1
                    options.append({
                        "symbol": symbol,
                        "options": option_type_full,
                        "strike": strike,
                        "size": size,
                        "direction": direction,
                        "avg_price": avg_price,
                        "current_price": mark_price,
                        "itm": itm,
                        "distance": f"{distance_percent:2f}%",
                        "notional": total_notional,
                        "delta": delta,
                        "theta": theta,
                        "expiry_date": expiry_date,
                        "current_spot_price": underlying_price
                    })

                elif position.contract.secType == 'FUT':
                    # print(f"future contract check: {position}")
                    # append position to futures array
                    futures_count += 1
                    futures.append({
                        'symbol': position.contract.symbol,
                        'position': position.position,
                        'avg_cost': position.avgCost,
                    })
                else:
                    # For non-option positions (e.g., stocks)
                    avg_price = position.avgCost
                    total_notional = abs(size) * mark_price
                    instrument_total_notional += total_notional
                    stocks_count += 1
                    stocks.append({
                        'symbol': symbol,
                        'size': size,
                        'direction': direction,
                        'avg_price': avg_price,
                        'current_price': mark_price,
                        'notional': total_notional,
                    })
                    # print(f"  Size: {size}, Direction: {direction}, Avg Price: {avg_price}, Current Price: {mark_price}, Notional: {total_notional}")

            # Display total notional for the instrument
            # print(f"Total Notional for {symbol}: {instrument_total_notional}")

        # Display overall portfolio information
#         print(f"\nCurrent Portfolio Margin (%): {account_margin}, Total Delta: {total_delta}, Total Theta: {total_theta}")
        print(safe_json_dumps({
            "account_overall": {
                "account_margin": account_margin,
                "maintenance_margin": margin,
                "equity": equity,
                "total_delta": total_delta,
                "total_theta": total_theta,
                "options_count": options_count,
                "stocks_count": stocks_count,
                "futures_count": futures_count,
            },
            "options": options,
            "stocks": stocks,
            "futures": futures
        }))

        #disconnect IB connection
        self.ib.disconnect()
        
        
# Instantiate and use the strategy
if __name__ == "__main__":
    demo_env = os.getenv('DEMO', 'false').strip().lower()
    is_demo_bool = True if demo_env in ('1', 'true', 'yes', 'on') else False
    host = os.getenv('IB_IP')
    port = os.getenv('IB_PORT')
    strategy = UIBaseIBKR(host, port, client_id=997, is_demo=is_demo_bool)
    # Run the strategy or call its methods
    # For example:
    strategy.manage_port()
    # strategy.test_positions()
