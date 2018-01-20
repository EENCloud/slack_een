
import re
from pprint import pprint
from lib import ChompsHandler


# ---- This is where the party starts - The BotHandler -----
# Essentially you are defining what you trigger on and the method to generate the
# response

# define what you wanna trigger on and what you want matched in groups.
trigger = re.compile('chomps marco')


class MyHandler(ChompsHandler):
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger

    def process_message(self, match, msg):
        pprint(msg)
        return "*POLO*"


if __name__ == "__main__":

    namer = MyHandler(None, None, None)

    tests = [
        ("chomps marco", 1),
        ("chomps name", 0),
        ("marco", 0),
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
