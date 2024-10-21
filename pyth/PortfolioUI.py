# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 17:08:26 2024

@author: aaron
"""
import json

from DeribitUIBase import DeribitUIBase
from dotenv import load_dotenv
import os

load_dotenv('./.env')


class Portfolio:

    def __init__(self, client_id, client_secret, currency, live=False):
        self.WS = DeribitUIBase(client_id, client_secret, live)
        self.currency = currency

    def display_portfolio(self, custom_currency):
        account_equity = str(self.WS.account_balance(custom_currency))
        account_margin = str(self.WS.account_margin(custom_currency))
        account_delta = str(self.WS.account_delta(custom_currency))
        account_vega = str(self.WS.account_vega(custom_currency))
        account_theta = str(self.WS.account_theta(custom_currency))
        account_pnl = str(self.WS.account_pnl(custom_currency))
        account_upnl = str(self.WS.account_unrealised_pnl(custom_currency))
        return {
            "equity": account_equity,
            "margin": account_margin,
            "delta": account_delta,
            "vega": account_vega,
            "theta": account_theta,
            "pnl": account_pnl,
            "upnl": account_upnl
        }

    def display_positions(self, custom_currency):
        positions = self.WS.get_positions_opt(custom_currency)
        pos_count = len(positions)
        final_positions = []

        for i in range(pos_count):
            instrument_name = str(positions[i]['instrument_name'])
            size = str(positions[i]['size'])
            direction = str(positions[i]['direction'])
            current_price = float(self.WS.get_spot_price(custom_currency))
            avg_price = str(positions[i]['average_price'])
            avg_price_usd = str(positions[i]['average_price_usd'])
            pnl = str(positions[i]['total_profit_loss'])
            mark_price = str(positions[i]['mark_price'])
            delta = str(positions[i]['delta'])
            vega = str(positions[i]['vega'])
            theta = str(positions[i]['theta'])
            itm = str(self.WS.is_ITM(str(positions[i]['instrument_name']), current_price))

            # Display information of positions on telegram in portfolio format
            final_positions.append({
                    "instrument_name": instrument_name,
                    "size": size,
                    "direction": direction,
                    "current_price": current_price,
                    "avg_price": avg_price,
                    "avg_price_usd": avg_price_usd,
                    "pnl": pnl,
                    "mark_price": mark_price,
                    "delta": delta,
                    "theta": theta,
                    "vega": vega,
                    "itm": itm
            })

        return final_positions


    def manage_port(self):
        positions = self.WS.get_positions_opt(self.currency)
        pos_count = len(positions)
        positions_fut = self.WS.get_positions(self.currency)
        pos_fut_count = len(positions_fut)
        account_margin = str(self.WS.account_margin(self.currency))
        account_delta = str(self.WS.account_delta(self.currency))
        account_vega = str(self.WS.account_vega(self.currency))
        account_theta = str(self.WS.account_theta(self.currency))
        account_pnl = str(self.WS.account_pnl(self.currency))

        print("Current Positions in: " + str(self.currency))

        # Iterate through positions and display current positions and respective risk metrics
        for i in range(pos_count):
            instrument_name = str(positions[i]['instrument_name'])
            size = str(positions[i]['size'])
            direction = str(positions[i]['direction'])
            avg_price = str(positions[i]['average_price'])
            avg_price_usd = str(positions[i]['average_price_usd'])
            pnl = str(positions[i]['total_profit_loss'])
            mark_price = str(positions[i]['mark_price'])
            delta = str(positions[i]['delta'])
            vega = str(positions[i]['vega'])
            theta = str(positions[i]['theta'])

            # Display information of positions on telegram in portfolio format
            print(
                "Instrument: " + instrument_name +
                ", Size: " + size +
                ", Direction: " + direction +
                " @ avg_price: " + avg_price +
                " / USD: " + avg_price_usd +
                ", PnL: " + pnl +
                ", Current price: " + mark_price +
                ", Delta: " + delta +
                ", Theta: " + theta +
                ", Vega: " + vega
            )

        # Display hedge position
        for i in range(pos_fut_count):
            instrument_fut = str(positions_fut[i]['instrument_name'])
            size_fut = str(positions_fut[i]['size'])
            direction_fut = str(positions_fut[i]['direction'])
            avg_price_fut = str(positions_fut[i]['average_price'])
            pnl_fut = str(positions_fut[i]['total_profit_loss'])
            mark_price_fut = str(positions_fut[i]['mark_price'])

            # Display information of positions on telegram in portfolio format
            print(
                "Instrument_fut: " + instrument_fut + ", " + "Size: " + size_fut + ", " + "Direction: " + direction_fut + " @ avg_price: " + avg_price_fut + ", PnL: " + pnl_fut + ", Current price: " + mark_price_fut)

        # Display overall portfolio information
        print(
            "Current Portfolio Margin (%): " + account_margin + " / Delta: " + account_delta + " / Vega: " + account_vega + " / Theta: " + account_theta + " / PnL: " + account_pnl)


if __name__ == '__main__':
    client_id = os.getenv('DERIBIT_CLIENT_ID')
    client_secret = os.getenv('DERIBIT_CLIENT_SECRET')

    currency = 'BTC'
    live = True  # Set to False if you're testing with testnet credentials

    portfolio = Portfolio(client_id, client_secret, currency, live=live)

    output = {
        "portfolio": {
            "btc": portfolio.display_portfolio("BTC"),
            "eth": portfolio.display_portfolio("ETH")
        },
        "positions": {
            "btc": portfolio.display_positions("BTC"),
            "eth": portfolio.display_positions("ETH")
        }
    }
    print(json.dumps(output))