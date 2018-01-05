''' Script sells at market rate, withdraws to wallet. '''

import time
import hmac
import urllib
import requests
import hashlib
import base64
import sys
import json

# Replace with your API key and API secret.
# Obviously, do not host this file anywhere publicly
# or your key/secret will be scraped by a bot.
API_KEY = 'YOUR API KEY'
API_SECRET = 'YOUR API SECRET'

def api_query( method, req = None ):
    if not req:
            req = {}
    #print "def api_query( method = " + method + ", req = " + str( req ) + " ):"
    time.sleep( 1 )
    public_set = set([ "GetCurrencies", "GetTradePairs", "GetMarkets", "GetMarket", "GetMarketHistory", "GetMarketOrders" ])
    private_set = set([ "GetBalance", "GetDepositAddress", "GetOpenOrders", "GetTradeHistory", "GetTransactions", "SubmitTrade", "CancelTrade", "SubmitTip" ])
if method in public_set:
    url = "https://www.cryptopia.co.nz/api/" + method
    if req:
        for param in req:
            url += '/' + str( param )
    r = requests.get( url )
elif method in private_set:
    url = "https://www.cryptopia.co.nz/Api/" + method
    nonce = str( int( time.time() ) )
    post_data = json.dumps( req );
    m = hashlib.md5()
    m.update(post_data)
    requestContentBase64String = base64.b64encode(m.digest())
    signature = API_KEY + "POST" + urllib.quote_plus( url ).lower() + nonce + requestContentBase64String
    hmacsignature = base64.b64encode(hmac.new(base64.b64decode( API_SECRET ), signature, hashlib.sha256).digest())
    header_value = "amx " + API_KEY + ":" + hmacsignature + ":" + nonce
    headers = { 'Authorization': header_value, 'Content-Type':'application/json; charset=utf-8' }
    r = requests.post( url, data = post_data, headers = headers )
response = r.text
print "( Response ): " + response
return response.replace("false","False").replace("true","True").replace('":null','":None' )


# Public:
# +
# print api_query("GetCurrencies")

# +
print api_query("GetMarket", [ 100, 6 ] )
# {"Success":True,"Message":None,"Data":{"TradePairId":100,"Label":"DOT/BTC","AskPrice":0.00000020,"BidPrice":0.00000019,"Low":0.00000019,"High":0.00000021,"Volume":1263556.65136394,"LastPrice":0.00000019,"LastVolume":774.83684404,"BuyVolume":50896673.08961847,"SellVolume":33046510.52562918,"Change":0.0},"Error":None}

# Private:
print api_query("GetBalance")

# +
# print api_query("GetBalance", {'CurrencyId':2} )
