
import re
import random
import requests
import simplejson
from datetime import datetime, timedelta
from pprint import pprint
from lib import ChompsHandler

trigger = re.compile('(?:[Cc]homps) [Mm]uzzle ([0-9]*) ([Mm]inutes|[Hh]ours|[Dd]ays|[Mm]ins|[Hh]rs|d|hr|min)')

default =datetime(2018, 1, 16, 4, 15, 15, 362441)

# muzzles = {muzzle.setdefault(channel, default)}

muzzles = {}

class muzzle(ChompsHandler):
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger

    def process_message(self, match, msg):
     	pprint(match.groups()[0])
     	pprint("=========")
     	pprint(match.groups()[1])
     	number = match.groups()[0]
     	number = int(number)
     	pprint(msg['channel'])
     	channel = msg['channel']
     	increment = match.groups()[1].lower()
     	# pprint('{:%a %I:%M %p }'.format(muzzles[channel]))
     	pprint('{:%a %I:%M %p }'.format(datetime.now()))
     	muzzles.setdefault(channel, default)
     	pprint(muzzles[channel] < datetime.now())
	if muzzles[channel] < datetime.now():
		if increment == "minutes" or increment == "mins" or increment == "min":
			muzzle = datetime.now() + timedelta(minutes=number)
			pretty = '{:%I:%M %p }'.format(muzzle)
			muzzles[channel] = muzzle
			pprint(muzzles)
			return "I will speak again at %s" % pretty
		elif increment == "days" or increment == "d":
			muzzle = datetime.now() + timedelta(days=number)
			pretty = '{:%a %I:%M %p }'.format(muzzle)
			muzzles[channel] = muzzle
			pprint(muzzles)
			return "I will speak again at %s" % pretty
		elif increment == "hours" or increment ==  "hrs" or increment ==  "hr":
			muzzle = datetime.now() + timedelta(hours=number)
			pretty = '{:%I:%M %p}'.format(muzzle)
			muzzles[channel] = muzzle
			pprint(muzzles)
			return "I will speak again at %s" % pretty
	else:
		pprint("trigger")
		pretty = '{:%a %I:%M %p}'.format(muzzles[channel])
		pprint(pretty)
		return  "quiet time till %s" % pretty
		# else:
		# 	return "WRONGO"


if __name__ == "__main__":

    namer = Muzzle(None, None, None)

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