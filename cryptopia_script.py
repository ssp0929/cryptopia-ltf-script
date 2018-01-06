#!/usr/bin/env python

'''
Script sells at market rate, withdraws to wallet.
'''

# pylint: disable=C0301, C0103, R0914, E0401, R0912, R0915, W0612

import time
import requests
from cryptopia_api import Api

def main():

    ''' Program driver: Input your configuration below '''

    # Replace with your API key and API secret.
    # Do not host this file anywhere publicly
    # or your key/secret will be scraped by a bot.
    # API KEY and SECRET CAN BE FOUND AT https://www.cryptopia.co.nz/Security
    # Remember to check 'Enable API'
    # Remember to check 'Enable Withdrawal'
    # Remember to check 'AddressBook Withdraw Only'
    API_KEY = 'Your API key'
    API_SECRET = 'Your API secret'

    # Replace with your wallet address.
    # Make sure you add this wallet address to your withdraw address book in https://www.cryptopia.co.nz/Security
    WALLET_ADDRESS = 'Wallet Address'

    # Replace with coin you want to check balance of and sell to BTC.
    SELL_CURRENCY = 'LTC'

    # Symbol of currency you wish to withdraw from the exchange
    WITHDRAW_CURRENCY = 'BTC'

    # Sell balance threshold i.e. balance of SELL_CURRENCY must be above SELL_THRESHOLD to sell.
    SELL_THRESHOLD = .0005

    # Withdraw balance threshold i.e. balance of WITHDRAW_CURRENCY must be above WITHDRAW_THRESHOLD to withdraw.
    WITHDRAW_THRESHOLD = .0011

    # How often to execute the script? i.e. input of 5 will run the script every 5 seconds
    SECONDS_TO_SLEEP = 10

    # ----------------    DO change values ABOVE ---------------------------
    # ---------------- DON'T change values BELOW ----------------------

    # Initialize API with key and secret values
    api = Api(API_KEY, API_SECRET)

    # Balance check loop
    script_running = True
    market = SELL_CURRENCY + '/BTC'
    while script_running:
        print "\n--------------------------------\n"
        print 'Starting next cycle...'

        # Check if balances meet requirements to sell
        print "\n--------------------------------\n"
        print 'Preparing to check balance of ' + SELL_CURRENCY + ' you have deposited to the exchange...'
        balance, error = api.get_balance(SELL_CURRENCY)
        if error:
            print 'Error getting balance for ' + SELL_CURRENCY + '.'
            print 'Error message: ' + error + '.'
        else:
            print 'You have a balance of ' + str(balance['Available']) + ' ' + SELL_CURRENCY + '.'
            # Check if balance is above sell threshold
            if balance['Available'] > SELL_THRESHOLD:
                # Request SELL_CURRENCY/BTC market data
                url = 'https://www.cryptopia.co.nz/api/GetMarkets/BTC'
                response = requests.get(url).json()
                data = response['Data']

                # Find SELL_CURRENCY/BTC row
                for item in data:
                    if item['Label'] == market:
                        rate = item['AskPrice']
                        break

                # Check if minimum trading limit is met
                min_check = '{0:f}'.format(rate*balance['Available'])
                min_to_meet_limit = '{0:f}'.format((.0005*balance['Available'])/(rate*balance['Available']))
                print '\nPreparing to check if minimum trading limit is met...'
                if rate*balance['Available'] < .0005:
                    print 'Sorry, minimum trading limit is the equivalent of .0005 BTC.'
                    print 'You are currently attempting to trade the equivalent of ' + str(min_check) + ' BTC.'
                    print 'You would need to trade at least ' + str(min_to_meet_limit) + ' ' + SELL_CURRENCY + '.\n'
                else:
                    # Create sell order.
                    print 'Minimum trading limit met.'
                    print 'Creating sell order for ' + str(balance['Available']) + \
                        ' ' + SELL_CURRENCY + ' at market asking price of ' + \
                        str(rate) + ' BTC to 1 ' + SELL_CURRENCY + '.'
                    result, error = api.submit_trade(market, 'Sell', rate, balance['Available'])
                    if error:
                        print 'Error while attempting to create sell order.'
                        print 'Error message: ' + error + '.'
                    else:
                        print 'Sell order successful.'

        # Check if balances meet requirements to withdraw
        print "\n--------------------------------\n"
        print 'Preparing to check balance of ' + WITHDRAW_CURRENCY + ' you have deposited to the exchange...'
        balance, error = api.get_balance(WITHDRAW_CURRENCY)
        if error:
            print 'Error getting balance for ' + WITHDRAW_CURRENCY + '.'
            print 'Error message: ' + error + '.'
        else:
            print 'You have a balance of ' + str(balance['Available']) + ' ' + WITHDRAW_CURRENCY + '.'
            # Check if balance is above withdraw threshold
            if balance['Available'] > WITHDRAW_THRESHOLD:
                # Check if balance is above minimum withdraw limit
                if balance['Available'] < .0011:
                    print 'Sorry, minimum withdrawal limit is .0011 BTC.'
                    print 'You are currently attempting to withdraw ' + str(balance['Available']) + ' BTC.'
                else:
                    print 'Withdrawing ' + str(balance['Available']) + WITHDRAW_CURRENCY + \
                        ' to wallet address: ' + WALLET_ADDRESS + '.'
                    result, error = api.submit_withdraw(WITHDRAW_CURRENCY, WALLET_ADDRESS, balance['Available'])
                    if error:
                        print 'Error while attempting to withdraw to wallet.'
                        print 'Error message: ' + error + '.'
                    else:
                        print 'Withdraw order successful.'

        # Sleep for allotted time.
        print "\n--------------------------------\n"
        print "Cycle complete, sleeping for " + str(SECONDS_TO_SLEEP) + " seconds."
        time.sleep(SECONDS_TO_SLEEP)

if __name__ == '__main__':
    main()
