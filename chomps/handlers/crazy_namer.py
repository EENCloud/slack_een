"""
Sample Handler that will respond to a command with some random
string from crazynamer.com
"""
import re
import random
import requests
import simplejson
from lib import ChompsHandler


# Crazy namer scripts
ENTITIES = {
    'tech': {
        'scripts': [
            "from dictionary\n"
            "keep first syllable\n"
            "one of Tech Tec Tek Sys media labs\n"
            "combine",
        ]
    },
    'company': {
        'scripts': [
            "from dictionary noun-adjective-number-animal len 3-6\n"
            "from dictionary noun-adjective-number-animal len 3-5\n"
            "from dictionary tech_suffix",

            "from dictionary small\n"
            "one of Tech Tec Tek Sys media labs\n"
            "combine",
        ]
    }
}

# The methods to encode the crazynamer script and get a name back.
def encode_script(script):
    return script.replace(" ", "~20").replace("\n", "~0A")

def execute_script(script):
    url = "http://www.crazynamer.com/ajax/get/crazyapp%7Cjson/script={}".format(encode_script(script))
    resp = requests.get(url)
    if resp.status_code == 200:
        data = simplejson.loads(resp.content)
        return data.get('result', "")
    return default


# ---- This is where the party starts - The BotHandler -----
# Essentially you are defining what you trigger on and the method to generate the
# response

# define what you wanna trigger on and what you want matched in groups.
trigger = re.compile('(?:[Cc]homps) (name|say)(?:\s|$)?([0-9a-zA-Z]*)')

class NameIt(ChompsHandler):    
    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger

    def get_name(self, entity):
        """Executes a crazynamer script"""
        print "Nameit: generating a ({})".format(entity)
        # get a list of scripts for the entity - or get a random entity if entity does not exist
        entity = ENTITIES.get(entity, ENTITIES[random.choice(ENTITIES.keys())])
        # get a random script
        script = random.choice(entity['scripts'])
        #run it
        return execute_script(script)
        
    def process_message(self, match, msg):
        entity = match.groups()[1] if match.groups()[1] else 'random'
        return "*{}* _ (www.crazynamer.com)_".format(self.get_name(entity))



if __name__ == "__main__":

    namer = NameIt(None, None, None)

    tests = [
        ("Chomps name",1),
        ("chomps name", 1),
        ("Chomps say tech",1),
        ("chomps name tech", 1),
        ("chomps name anything", 1),
        ("name tech", 0),
        ("tech", 0),
        ("should find tw=100d4326 and 100d432a", 0)
    ]

    for test in tests:
        test_str = test[0]
        matches = test[1]
        print "Test: ", test_str

        for m in namer.pattern.finditer(test_str):
            matches -= 1
            print "\tFound:", m.groups()[0]

        if not matches:
            print "\tPASSED"
        else:
            print "\tFALSE"
        
    print execute_script(ENTITIES['company']['scripts'][0])


