
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

coin= {}


last_check = datetime.now()-timedelta(minutes=2)

def trend(percent):
    if percent.find("-") != -1:
        pic = ":chart_with_downwards_trend:"
    else: 
        pic = ":chart_with_upwards_trend:"
    return pic 

def time_check(last_check):
    this_check = datetime.now()
    pprint("this time")
    pprint(this_check.minute)
    pprint("Last time")
    pprint(last_check.minute)
    if int(this_check.minute) - int(last_check.minute) >= 2 or int(this_check.minute) == 0  :
        last_check = datetime.now()
        # pprint("last check now")
        # pprint(last_check)
        return True
    else:
        return False

def get_new_data():
    url= "https://api.coinmarketcap.com/v1/ticker/" 
    resp = requests.get(url)
    global coins
    coins = simplejson.loads(resp.content)
    return coins

def search_coins(coins,term):
    lower = term.lower()
    upper = term.upper()
    for coin in coins:
        if coin["name"] == term:
            global coin
            return coin
        elif coin["id"] == lower:
            global coin
            return coin
        elif coin["symbol"] == upper:
            global coin
            return coin
        elif coin['rank'] == "100":
            global coin
            coin = {}
            return coin



class MyHandler(ChompsHandler):    
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger
        
    def process_message(self, match, msg):
        term = match.groups()[0]
        # pprint("last")
        # pprint(last_check)
        # pprint("Time Check") 
        # pprint(time_check(last_check))
        if time_check(last_check):
            global last_check
            last_check = datetime.now()
            get_new_data()
            search_coins(coins,term)
            
            pprint("New Coin")
            pprint(coin)
            last_check = datetime.now()
            pprint(last_check)

            holder = trend(coin["percent_change_1h"])
            holder_two = trend(coin["percent_change_24h"])
            holder_three = trend(coin["percent_change_7d"])
            return ((">>>*Currency*: %s \n" % coin["name"])+
                ("$ %s \n" % coin["price_usd"]) +
                ("%s *%s%%* _1hr_ " % (holder,coin["percent_change_1h"]))+
                (" %s *%s%%*  _1d_ " % (holder_two,coin["percent_change_24h"]))+
                (" %s *%s%%* _7d_ " %  (holder_three,coin["percent_change_7d"])))
        else:
            search_coins(coins,term)
            pprint(coin)
            pprint("old coin")
            holder = trend(coin["percent_change_1h"])
            holder_two = trend(coin["percent_change_24h"])
            holder_three = trend(coin["percent_change_7d"])
            return ((">>>*Currency*: %s \n" % coin["name"])+
                ("$ %s \n" % coin["price_usd"]) +
                ("%s *%s%%* _1hr_ " % (holder,coin["percent_change_1h"]))+
                (" %s *%s%%*  _1d_ " % (holder_two,coin["percent_change_24h"]))+
                (" %s *%s%%* _7d_ " %  (holder_three,coin["percent_change_7d"])))



if __name__ == "__main__":

    namer = MyHandler(None, None, None)

    tests = [
        ("chomps marco",1),
        ("chomps name", 0),
        ("marco",0),
    ]

    for test in tests:
        test_str = test[0]
        matches = test[1]
        print "Test: ", test_str

        for m in namer.pattern.finditer(test_str):
            matches -= 1
            print "\tFound:"

        if not matches:
            print "\tPASSED"
        else:
            print "\tFALSE"



