import os
import sys

import gevent
from gevent import monkey
monkey.patch_all()
os.environ['MONKEY'] = "True"


import re
import time
import logging
import logging.config
import settings
import traceback
from pprint import pprint, pformat
from slackclient import SlackClient
from lib import HandlerRegistry


logging.config.dictConfig(settings.LOGGING)

################################################################################
# Setup a new bot in your slack
# https://<your_slack>.slack.com/apps/manage/custom-integrations
################################################################################

# @name of bot if you see @chomps online in your config put 'chomps' here
BOT_NAME = settings.SLACK_BOT_NAME

# Bot ID         **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
BOT_ID = settings.SLACK_BOT_ID

# Bot API Token  **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
SLACK_BOT_TOKEN = settings.SLACK_BOT_TOKEN

slack_client = SlackClient(SLACK_BOT_TOKEN)

READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

# Load the plugins
pwd = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.join(pwd, settings.HANDLER_DIR)
handlers = HandlerRegistry([plugin_dir], slack_client, BOT_NAME, BOT_ID)
handlers.load_plugins()

#empty dict that will fill as a message for muzzle or speak is recieved
muzzles= {}

def simple_response(response, channel):
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def muzzle_handler(msg, text):
    
    trigger = re.compile('(?:[Cc]homps) ([Mm]uzzle|[Ss]peak|[Oo]n|[Oo]ff)\Z')
    result= trigger.match(text)
    #  ^ checks the regex expression for a match, returns none if not found
    channel=msg.get('channel')
    #  ^ pulls out the unique channel name as string
    muzzles.setdefault(channel, False)
    if result != None:
        command= result.groups()[0].lower() 
        if command == "muzzle" or command == "off":
            muzzles[channel] = True
            # ^ defines the channel name where the command was recieved as true if muzzled or silent
            print("chomps is silent")
            response = "Quiet Time!"
            simple_response(response, msg['channel'])
        elif command == "speak" or command == "on":
            muzzles[channel] = False
            # ^ defines the channel name where the command was recieved as false if speaking
            print("chomps is loud")
            response = "Chomps is loose!"
            simple_response(response, msg['channel'])
        return muzzles[channel]

def is_muzzled(msg):
    channel = msg.get('channel')
    if muzzles[channel]:
        print("quiet time")
        return False
    else:
        return True



if __name__ == "__main__":
    try:
        if slack_client.rtm_connect():
            print("Chomps: connected and running!")
            while True:
                rtm = slack_client.rtm_read()
                if rtm and len(rtm) > 0:
                    try:
                        # For each message read - do the NEW HANDLERS
                        for msg in rtm:
                            # Do not respond to message from ourselves
                            if msg.get('user') == BOT_ID:
                                continue

                            text = msg.get('text', '')
                            muzzle_handler(msg,text)
                            if is_muzzled(msg):
                                if text:
                                    print "CHANNEL: {} => Message: {}".format(msg['channel'], text.encode('ascii', 'ignore'))
                                    for handler in handlers:
                                        count = 0
                                        for match in handler.pattern.finditer(text):
                                            count += 1
                                            if count <= handler.call_limit:
                                                #gevent.spawn(handle, handler, match, msg)
                                                response = handler.process_message(match, msg)
                                                if response:
                                                    simple_response(response, msg['channel'])
                                            else:
                                                break

                    except Exception as e:
                        print("Error {} {}".format(type(e), e.message))
                        traceback.print_exc()

                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
    except KeyboardInterrupt:
        # Clean up greenlets
        import gc
        from greenlet import greenlet
        try:
            gevent.killall([obj for obj in gc.get_objects() if isinstance(obj, greenlet)])
        except:
            pass

