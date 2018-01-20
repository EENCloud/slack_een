
import re
import random
import requests
import simplejson
from pprint import pprint
from lib import ChompsHandler
from datetime import datetime, timedelta

from muzzle import muzzles

symbols = {"BTC" : "bitcoin",
"ETH" : "ethereum",
"XRP" : "ripple",
"BCH" : "bitcoin-cash",
"ADA" : "cardano",
"LTC" : "litecoin",
"XEM" : "nem",
"NEO" : "neo",
"XLM" : "stellar",
"MIOTA" : "iota",
"EOS" : "eos",
"DASH" : "dash",
"XMR" : "monero",
"TRX" : "tron",
"BTG" : "bitcoin-gold",
"ETC" : "ethereum-classic",
"ICX" : "icon",
"QTUM" : "qtum",
"LSK" : "lisk",
"XRB" : "raiblocks",
"OMG" : "omisego",
"ARDR" : "ardor",
"USDT" : "tether",
"ZEC" : "zcash",
"STRAT" : "stratis",
"VEN" : "vechain",
"PPT" : "populous",
"BNB" : "binance-coin",
"BCC" : "bitconnect",
"XVG" : "verge",
"SC" : "siacoin",
"BCN" : "bytecoin-bcn",
"SNT" : "status",
"KCS" : "kucoin-shares",
"BTS" : "bitshares",
"STEEM" : "steem",
"DOGE" : "dogecoin",
"WAVES" : "waves",
"REP" : "augur",
"ZRX" : "0x",
"ETN" : "electroneum",
"DRGN" : "dragonchain",
"VERI" : "veritaseum",
"KMD" : "komodo",
"QASH" : "qash",
"GAS" : "gas",
"DGB" : "digibyte",
"GNT" : "golem-network-tokens",
"ARK" : "ark",
"SALT" : "salt",
"DCR" : "decred",
"DCN" : "dentacoin",
"HSR" : "hshare",
"WAX" : "wax",
"WTC" : "walton",
"SMART" : "smartcash",
"PIVX" : "pivx",
"RHOC" : "rchain",
"ETHOS" : "ethos",
"LRC" : "loopring",
"GBYTE" : "byteball",
"BAT" : "basic-attention-token",
"ZCL" : "zclassic",
"KNC" : "kyber-network",
"AION" : "aion",
"FCT" : "factom",
"MONA" : "monacoin",
"BTM" : "bytom",
"FUN" : "funfair",
"DENT" : "dent",
"AE" : "aeternity",
"POWR" : "power-ledger",
"GXS" : "gxshares",
"XP" : "experience-points",
"SYS" : "syscoin",
"MAID" : "maidsafecoin",
"RDD" : "reddcoin",
"DGD" : "digixdao",
"REQ" : "request-network",
"SUB" : "substratum",
"NXS" : "nexus",
"ENG" : "enigma-project",
"NEBL" : "neblio",
"NXT" : "nxt",
"KIN" : "kin",
"NAS" : "nebulas-token",
"GAME" : "gamecredits",
"ELF" : "aelf",
"BNT" : "bancor",
"XZC" : "zcoin",
"MED" : "medibloc",
"ICN" : "iconomi",
"CNX" : "cryptonex",
"PART" : "particl",
"QSP" : "quantstamp",
"PAY" : "tenx",
"EMC" : "emercoin",
"LINK" : "chainlink",
"CVC" : "civic",
"GNO" : "gnosis-gno"}

odd_names = {
"Bitcoin Cash" : "bitcoin-cash",
"Bitcoin Gold" : "bitcoin-gold",
"Ethereum Classic" : "ethereum-classic",
"Binance Coin" : "binance-coin",
"Bytecoin" : "bytecoin-bcn",
"KuCoin Shares" : "kucoin-shares",
"Golem" : "golem-network-tokens",
"Byteball Bytes" : "byteball",
"Basic Attention Token" : "basic-attention-token",
"Kyber Network" : "kyber-network",
"Power Ledger" : "power-ledger",
"Request Network" : "request-network",
"Experience Points" : "experience-points",
"Enigma" : "enigma-project",
"Nebulas" : "nebulas-token",
"Gnosis" : "gnosis-gno"}


##### This is where the part starts - The BotHandler ####
# Essentially you are defining what you trigger on and the method to generate the
# response
# define what you wanna trigger on and what you want matched in groups.
trigger = re.compile('(?:[Cc]homps) [Cc]rypto ([0-9a-zA-Z]*)')

# pic_one = ":chart_with_upwards_trend:"
# pic_two = ":chart_with_upwards_trend:"
# pic_three = ":chart_with_upwards_trend:"

pprint(muzzles)

default =datetime(2018, 1, 16, 4, 15, 15, 362441)


def trend(percent):
    if percent.find("-") != -1:
        pic = ":chart_with_downwards_trend:"
    else: 
        pic = ":chart_with_upwards_trend:"
    return pic 

class MyHandler(ChompsHandler):    
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger
        
    def process_message(self, match, msg):
        channel = msg["channel"]
        muzzles.setdefault(channel, default)
        pprint("muzzled")
        pprint(muzzles)
        pprint(muzzles[channel] > datetime.now())
        if muzzles[channel] > datetime.now():
            return "still quiet time"
        else:
            pprint(match.groups()[0])
            url= "https://api.coinmarketcap.com/v1/ticker/" + match.groups()[0]
            resp = requests.get(url)
            if resp.status_code == 200:
                data = simplejson.loads(resp.content)
                pprint(msg)
                pprint(data)
            elif resp.status_code == 404:
                pprint("====")
                pprint(match.groups()[0])
                # pprint(symbols)
                holder = match.groups()[0].upper()
                pprint(holder)

                url= "https://api.coinmarketcap.com/v1/ticker/" + symbols[holder]
                resp = requests.get(url)
                if resp.status_code == 200:
                    data = simplejson.loads(resp.content)
                    pprint(msg)
                    pprint(data)
                    pprint("=========")
                else:
                    pprint(url)
                    pprint(resp.status_code) 
                    return ("I got nothing. coding is hard")
            # data[0]["percent_change_1h"] = "5.6"         
            holder = trend(data[0]["percent_change_1h"])
            holder_two = trend(data[0]["percent_change_24h"])
            holder_three = trend(data[0]["percent_change_7d"])
        return (">>>*Currency*: %s \n $ %s \n  %s *%s%%* _1hr_  %s *%s%%*  _1d_  %s *%s%%* _7d_ " %  ( data[0]["name"], data[0]["price_usd"],holder,data[0]["percent_change_1h"],holder_two,data[0]["percent_change_24h"],holder_three,data[0]["percent_change_7d"]) ) 
        


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



