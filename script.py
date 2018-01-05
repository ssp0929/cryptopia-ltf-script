#!/usr/bin/env python

'''
Script sells at market rate, withdraws to wallet.
'''

# pylint: disable=C0301, C0103, R0914

import time
import hmac
from urllib import parse
import hashlib
import base64
import json
import requests

def withdraw_to_address(API_KEY, API_SECRET, WALLET_ADDRESS, withdraw_currency, withdraw_amount):

    ''' Withdraw to wallet address given '''

    # Build request object
    req = {
        'Currency': withdraw_currency,
        'Address': WALLET_ADDRESS,
        'Amount': withdraw_amount
    }

    # POST REQUEST URL
    url = "https://www.cryptopia.co.nz/Api/SubmitWithdraw"

    # Generate request signature and send post request
    nonce = str(int(time.time()))
    post_data = json.dumps(req)
    m = hashlib.md5()
    m.update(post_data.encode('utf-8'))
    requestContentBase64String = str(base64.b64encode(m.digest()))
    signature = API_KEY + 'POST' + parse.quote_plus(url).lower() + nonce + requestContentBase64String
    hmacsignature = str(base64.b64encode(hmac.new(base64.b64decode(API_SECRET), signature.encode('utf-8'), hashlib.sha256).digest()))
    header_value = 'amx ' + API_KEY + ':' + hmacsignature + ':' + nonce
    headers = {'Authorization': header_value, 'Content-Type':'application/json; charset=utf-8'}
    response = requests.post(url, data=post_data, headers=headers)

    # Print response to terminal.
    print("\nAPI call response:\n\n", response.text)

def market_rate_sell():

    ''' Sell coin at market rate. '''

    # url = "https://www.cryptopia.co.nz/Api/" + method

def main():

    ''' Program driver '''

    # Replace with your API key and API secret.
    # Do not host this file anywhere publicly
    # or your key/secret will be scraped by a bot.
    API_KEY = 'b086d180adeb44b69fcc2403baa62317'
    API_SECRET = 'LnKdFQYr1F3OpTdOs7iQHx9BG8czyZWzfx497zEQgQo='

    # Replace with your wallet address.
    WALLET_ADDRESS = 'Your wallet address.'

    # User prompt loop
    not_done = True
    while not_done:
        user_choice = int(input('\nWhat do you wish to do?\n1) Create sell order\n2) Withdraw to wallet\n3) Exit program\n'))
        if user_choice == 1:
            sell_currency = input('\nWhat currency do you wish to sell?\n')
            # Sell at market rate.
            # market_rate_sell()
        elif user_choice == 2:
            withdraw_currency = input('\nWhat currency do you wish to withdraw?\n')
            withdraw_amount = input('\nHow much ' + withdraw_currency + ' do you wish to withdraw?\n')
            # Withdraw to wallet address.
            withdraw_to_address(API_KEY, API_SECRET, WALLET_ADDRESS, withdraw_currency, withdraw_amount)
        elif user_choice == 3:
            print("\nExiting program.\n")
            not_done = False
        else:
            print("\nInvalid choice. Please try again.\n")

if __name__ == '__main__':
    main()
