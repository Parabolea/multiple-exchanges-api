# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 17:20:26 2024

@author: aaron
"""

import asyncio
import websockets
import json
import nest_asyncio
import os
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv('../.env')


class DeribitUIBase:

    def __init__(self, client_id, client_secret, live=False):

        if not live:
            self.url = 'wss://test.deribit.com/ws/api/v2'
        elif live:
            self.url = 'wss://www.deribit.com/ws/api/v2'
        else:
            raise Exception('live must be a bool, True=real, False=paper')

        print(f"URL:{self.url}")
        print(f"Client_ID:{client_id}")
        print(f"Client_Secret:{client_secret}")

        self.client_id = client_id
        self.client_secret = client_secret

        self.auth_creds = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        }

        self.test_creds()

        self.msg = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": None,
        }

    async def pub_api(self, msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(msg)
            while websocket.open:
                response = await websocket.recv()
                return json.loads(response)

    async def priv_api(self, msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(self.auth_creds))
            while websocket.open:
                response = await websocket.recv()
                await websocket.send(msg)
                response = await websocket.recv()
                break
            return json.loads(response)

    @staticmethod
    def async_loop(api, message):
        return asyncio.get_event_loop().run_until_complete(api(message))

    def test_creds(self):
        response = self.async_loop(self.pub_api, json.dumps(self.auth_creds))
        if 'error' in response.keys():
            raise Exception(f"Auth failed with error {response['error']}")
        else:
            print("Auth creds are good, it worked")

    # account methods
    def account_summary(self, currency, extended=True):
        params = {
            "currency": currency,
            "extended": extended
        }

        self.msg["method"] = "private/get_account_summary"
        self.msg["params"] = params
        print('will fetch now')
        summary = self.async_loop(self.priv_api, json.dumps(self.msg))
        return summary

    def account_balance(self, currency):
        summary = self.account_summary(currency)['result']['balance']
        return summary

    def account_delta(self, currency):
        summary = self.account_summary(currency)['result']['delta_total']
        return summary

    def account_vega(self, currency):
        summary = self.account_summary(currency)['result']['options_vega']
        return summary

    def account_theta(self, currency):
        summary = self.account_summary(currency)['result']['options_theta']
        return summary

    def account_margin(self, currency, extended=True):
        margin = self.account_summary(currency)['result']['initial_margin']
        equity = self.account_summary(currency)['result']['equity']
        try:
            return (margin / equity) * 100
        except ZeroDivisionError:
            return 0

    def account_pnl(self, currency, extended=True):
        pnl = self.account_summary(currency)['result']['total_pl']
        return pnl

    def account_unrealised_pnl(self, currency, extended=True):
        upnl = self.account_summary(currency)['result']['session_upl']
        return upnl

    def get_positions(self, currency, kind="future"):
        params = {
            "currency": currency,
            "kind": kind
        }
        self.msg["method"] = "private/get_positions"
        self.msg["params"] = params
        positions = self.async_loop(self.priv_api, json.dumps(self.msg))
        return positions['result']

    def get_positions_opt(self, currency, kind="option"):
        params = {
            "currency": currency,
            "kind": kind
        }
        self.msg["method"] = "private/get_positions"
        self.msg["params"] = params
        positions = self.async_loop(self.priv_api, json.dumps(self.msg))
        return positions['result']

    def get_position(self, instrument):
        params = {
            "instrument_name": instrument
        }
        self.msg["method"] = "private/get_position"
        self.msg["params"] = params
        position = self.async_loop(self.priv_api, json.dumps(self.msg))
        return position['result']

    def get_spot_price(self, currency):
        params = {
            "index_name": f"{currency.lower()}_usd"
        }
        msg = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "public/get_index_price",
            "params": params
        }
        response = self.async_loop(self.pub_api, json.dumps(msg))
        return response['result']['index_price']

    # Function to check if an option is ITM
    def is_ITM(self, instrument_name, spot_price):
        # Instrument name format: "BTC-30DEC22-18000-P"
        try:
            parts = instrument_name.split('-')
            if len(parts) != 4:
                return 'N/A'
            currency, expiry, strike, option_type = parts
            strike_price = float(strike)
            option_type = option_type.upper()

            if option_type == 'C':  # Call option
                return 'Yes' if spot_price > strike_price else 'No'
            elif option_type == 'P':  # Put option
                return 'Yes' if spot_price < strike_price else 'No'
            else:
                return 'N/A'
        except Exception as e:
            print(f"Error determining ITM status for {instrument_name}: {e}")
            return 'N/A'


if __name__ == "__main__":
    client_id = os.getenv('DERIBIT_CLIENT_ID')
    client_secret = os.getenv('DERIBIT_CLIENT_SECRET')

    # Get method and parameters from command line arguments
    method = 'account_summary'
    currency = "BTC"

    # Initialize the class
    deribit = DeribitUIBase(client_id, client_secret, True)

    # Call the method dynamically
    result = deribit.account_pnl("BTC")

    # Return the result as a JSON response
    print(json.dumps(result))