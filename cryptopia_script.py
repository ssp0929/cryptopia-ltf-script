#!/usr/bin/env python

'''
Script sells at market rate, withdraws to wallet.
'''

# pylint: disable=C0301, C0103, R0914, E0401

import time
import requests
from cryptopia_api import Api

def main():

    ''' Program driver: Input your configuration below '''

    # Replace with your API key and API secret.
    # Do not host this file anywhere publicly
    # or your key/secret will be scraped by a bot.
    API_KEY = '6ce2486a3d3942e191cb27a87dba1be7'
    API_SECRET = 'LN9ddMXRPE2u2c2B3vNLC7FMC3i6XP55YJynGy4kn/A='

    # Replace with your wallet address.
    WALLET_ADDRESS = '14mTzZvZPJ2dydYBLqU68hGHhjNTG2Hqwu'

    # Replace with coin you want to check balance of and sell to BTC.
    SELL_CURRENCY = 'LTC'

    # Symbol of currency you wish to withdraw from the exchange
    WITHDRAW_CURRENCY = 'BTC'

    # Sell balance threshold i.e. balance of SELL_CURRENCY must be above SELL_THRESHOLD to sell.
    SELL_THRESHOLD = .0001

    # Withdraw balance threshold i.e. balance of WITHDRAW_CURRENCY must be above WITHDRAW_THRESHOLD to withdraw.
    WITHDRAW_THRESHOLD = .000001

    # How often to execute the script? i.e. input of 5 will run the script every 5 seconds
    SECONDS_TO_SLEEP = 10

    # ----------------Don't change values below----------------------

    # Initialize API with key and secret values
    api = Api(API_KEY, API_SECRET)

    # Balance check loop
    script_running = True
    while script_running:
        market = SELL_CURRENCY + '/BTC'

        # Check if balances meet requirements to sell/withdraw
        print '\nPreparing to check balance of ' + SELL_CURRENCY + ' you have deposited to the exchange...\n'
        balance, error = api.get_balance(SELL_CURRENCY)
        print '\nYou have a balance of ' + str(balance['Available']) + ' ' + SELL_CURRENCY + '.\n'
        if error:
            print '\nError getting balance for ' + SELL_CURRENCY + '.'
            print 'Error message: ' + error + '.\n'
        elif balance['Available'] > SELL_THRESHOLD:
            # Request LTC/BTC market data
            url = 'https://www.cryptopia.co.nz/api/GetMarkets/BTC'
            response = requests.get(url).json()
            data = response['Data']

            # Find LTC/BTC row
            for item in data:
                if item['Label'] == 'LTC/BTC':
                    rate = item['AskPrice']
                    break

            # Check if minimum trading limit is met
            min_check = '{0:f}'.format(rate*balance['Available'])
            min_to_meet_limit = '{0:f}'.format((rate*balance['Available'])/.0005)
            print '\nPreparing to check if minimum trading limit is met...\n'
            if rate*balance['Available'] < .0005:
                print '\nSorry, minimum trading limit is the equivalent of .0005 BTC.'
                print 'You are currently attempting to trade the equivalent of ' + str(min_check) + ' BTC.'
                print 'You would need to trade at least ' + str(min_to_meet_limit) + ' ' + SELL_CURRENCY + '.\n'
            else:
                # Create sell order.
                print '\nMinimum trading limit met.'
                print '\nCreating sell order for ' + str(balance['Available']) + \
                    ' ' + SELL_CURRENCY + ' at market asking price of ' + \
                    str(rate) + ' BTC to 1 ' + SELL_CURRENCY + '.\n'
                result, error = api.submit_trade(market, 'Sell', rate, balance['Available'])
                if error:
                    print '\nError while attempting to create sell order.'
                    print 'Error message: ' + error + '.\n'
                else:
                    print '\nSell successful.'
                    print 'Response received: ' + result + '.\n'

                # DEBUG exit after submitting trade
                break

        # Slow script for now for debugging purposes.
        time.sleep(100)

        balance, error = api.get_balance(WITHDRAW_CURRENCY)
        if error:
            print 'Error getting balance for ' + WITHDRAW_CURRENCY + '.'
        if balance > WITHDRAW_THRESHOLD:
            api.submit_withdraw(WITHDRAW_CURRENCY, WALLET_ADDRESS, amount)

        # Sleep for allotted time.
        time.sleep(SECONDS_TO_SLEEP)

if __name__ == '__main__':
    main()
