
import re
import random
import requests
import simplejson
from pprint import pprint
from lib import ChompsHandler
from datetime import datetime, timedelta

##### This is where the part starts - The BotHandler ####
# Essentially you are defining what you trigger on and the method to generate the
# response
# define what you wanna trigger on and what you want matched in groups.
trigger = re.compile('(?:[Cc]homps) [Cc]rypto ([0-9a-zA-Z]*)')

coins = {}


CACHE_EXPIRATION= 2

last_check = datetime.now()-timedelta(minutes=CACHE_EXPIRATION)

def trend(percent):
    if float(percent) < 0:
        pic = ":chart_with_downwards_trend:"
    else: 
        pic = ":chart_with_upwards_trend:"
    return pic 

def time_check(last_check):
    this_check = datetime.now()
    data_age = (this_check - last_check).total_seconds() / 60  # Age of data in minutes
    pprint(data_age)
    return data_age >= CACHE_EXPIRATION

def get_new_data():
    url= "https://api.coinmarketcap.com/v1/ticker/" 
    resp = requests.get(url)
    data = simplejson.loads(resp.content)
    return data

def search_coins(term):
    keys_to_check = ['id', 'name', 'symbol']
    for coin in coins:
        for key in keys_to_check:
            if coin.get(key, "").lower() == term.lower():
                return coin
    return coins # returns the last one



class crypto(ChompsHandler):    
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger
        
    def process_message(self, match, msg):
        term = match.groups()[0]
        if time_check(last_check):
            global coins, last_check
            last_check = datetime.now()
            coins = get_new_data()
        coin = search_coins(term)
        holder = trend(coin["percent_change_1h"])
        holder_two = trend(coin["percent_change_24h"])
        holder_three = trend(coin["percent_change_7d"])
        return ((">>>*Currency*: %s \n" % coin["name"])+
            ("$ %s | Symbol *%s*  \n" % (coin["price_usd"],coin["symbol"]))+ 
            ("%s *%s%%* _1hr_ " % (holder,coin["percent_change_1h"]))+
            (" %s *%s%%*  _1d_ " % (holder_two,coin["percent_change_24h"]))+
            (" %s *%s%%* _7d_ " %  (holder_three,coin["percent_change_7d"])))

