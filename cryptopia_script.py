#!/usr/bin/env python

'''
Script sells at market rate, withdraws to wallet.
'''

# pylint: disable=C0301, C0103, R0914, E0401

import time
import random
import hmac
import hashlib
import base64
import json
import requests

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

    # Balance check loop
    script_running = True
    balance = []
    while script_running:
        # Reset variables
        do_sell = False
        do_withdraw = False

        # Get relevent balances.
        balance = check_exchange_balance(API_KEY, API_SECRET, SELL_CURRENCY, WITHDRAW_CURRENCY)
        time.sleep(3)

        # Check if balances meet requirements to sell/withdraw
        if balance[0] > SELL_THRESHOLD:
            do_sell = True
        if balance[1] > WITHDRAW_THRESHOLD:
            do_withdraw = True

        # DEBUG
        market_rate_sell(API_KEY, API_SECRET, SELL_CURRENCY, balance[0])
        withdraw_to_address(API_KEY, API_SECRET, WALLET_ADDRESS, WITHDRAW_CURRENCY, balance[1])

        # Sell and/or withdraw if requirements met.
        if do_sell:
            # Sell at market rate
            market_rate_sell(API_KEY, API_SECRET, SELL_CURRENCY, balance[0])
            time.sleep(3)
        elif do_withdraw:
            # Withdraw to wallet
            withdraw_to_address(API_KEY, API_SECRET, WALLET_ADDRESS, WITHDRAW_CURRENCY, balance[1])

        # Sleep for allotted time.
        time.sleep(SECONDS_TO_SLEEP)

def generate_header(API_KEY, API_SECRET, url, post_data):

    ''' Generate secure header for private API calls '''

    # Generate a Request Time Stamp and use as a nonce, UNIQUE
    nonce = str(int(time.time())) + '.' + str(random.randint(0, 1000))

    # Generate signature data (API_KEY/SECRET, RequestURL+Method, Nonce, base64string)
    md5 = hashlib.md5()
    md5.update(post_data.encode('UTF-8'))
    b64 = base64.b64encode(md5.digest())
    request_signature = API_KEY + 'POST' + url + nonce + b64.decode("UTF-8")

    # Sign using HMAC-SHA256
    hmacraw = hmac.new(API_SECRET, request_signature, hashlib.sha256).digest()
    sign = base64.b64encode(hmacraw)

    # Combine into request header
    request_header = 'amx ' + API_KEY + ':' + sign + ':' + nonce
    print request_header + '\n'

    return {'Authorization': request_header, 'Content-Type': 'application/json; charset=utf-8'}

def check_exchange_balance(API_KEY, API_SECRET, SELL_CURRENCY, WITHDRAW_CURRENCY, req=None):

    ''' Check balance of COIN_SYMBOL and BTC in exchange '''

    # Generate header and send POST request
    url = 'https://www.cryptopia.co.nz/Api/GetBalance'
    post_data = json.dumps(req)
    headers = generate_header(API_KEY, API_SECRET, url, post_data)
    response = requests.post(url, data=post_data, headers=headers)
    response.encoding = 'utf-8-sig'

    # Grab balances from response
    data = json.loads(response.text)
    print data
    data = data['Data']

    for currency in data:
        if data['Symbol'] == SELL_CURRENCY:
            sell_balance = currency['Available']
        if data['Symbol'] == WITHDRAW_CURRENCY:
            withdraw_balance = currency['Available']

    return [sell_balance, withdraw_balance]

def withdraw_to_address(API_KEY, API_SECRET, WALLET_ADDRESS, WITHDRAW_CURRENCY, withdraw_amount):

    ''' Withdraw to wallet address given '''

    # Build request object
    req = {
        'Currency': WITHDRAW_CURRENCY,
        'Address': WALLET_ADDRESS,
        'Amount': withdraw_amount
    }

    # POST REQUEST URL
    url = 'https://www.cryptopia.co.nz/Api/SubmitWithdraw'

    # Generate request signature and send post request
    nonce = str(int(time.time()))
    post_data = json.dumps(req)
    m = hashlib.md5()
    m.update(post_data.encode('utf-8'))
    requestContentBase64String = str(base64.b64encode(m.digest()))
    signature = API_KEY + 'POST' + url + nonce + requestContentBase64String
    hmacsignature = str(base64.b64encode(hmac.new(base64.b64decode(API_SECRET), signature.encode('utf-8'), hashlib.sha256).digest()))
    header_value = 'amx ' + API_KEY + ':' + hmacsignature + ':' + nonce
    headers = {'Authorization': header_value, 'Content-Type':'application/json; charset=utf-8'}
    response = requests.post(url, data=post_data, headers=headers)

    # Print response to terminal.
    print('\nAPI call response:\n\n', response.text)

def market_rate_sell(API_KEY, API_SECRET, SELL_CURRENCY, amount):

    ''' Sell coin at market rate. '''

    # Get market rate of SELL_CURRENCY/BTC asking price.
    response = requests.get('https://www.cryptopia.co.nz/api/GetMarket/LTC_BTC')
    data = json.loads(response.text)

    # Build request object
    req = {
        'Market': SELL_CURRENCY + '/BTC',
        'Type': 'Sell',
        'Rate': data,
        'Amount': amount
    }

    # POST REQUEST URL
    url = 'https://www.cryptopia.co.nz/Api/SubmitTrade'

    # Generate request signature and send post request
    nonce = str(int(time.time()))
    post_data = json.dumps(req)
    m = hashlib.md5()
    m.update(post_data.encode('utf-8'))
    requestContentBase64String = str(base64.b64encode(m.digest()))
    signature = API_KEY + 'POST' + url + nonce + requestContentBase64String
    hmacsignature = str(base64.b64encode(hmac.new(base64.b64decode(API_SECRET), signature.encode('utf-8'), hashlib.sha256).digest()))
    header_value = 'amx ' + API_KEY + ':' + hmacsignature + ':' + nonce
    headers = {'Authorization': header_value, 'Content-Type':'application/json; charset=utf-8'}
    response = requests.post(url, data=post_data, headers=headers)

    # Print response to terminal.
    print('\nAPI call response:\n\n', response.text)


if __name__ == '__main__':
    main()
