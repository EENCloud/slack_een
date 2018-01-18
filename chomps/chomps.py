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


EEN_SLACK_API_KEY= 'xoxb-56033804049-sEA5bOB8tqNTbcKrnynwqAF9'

EEN_SLACKBOT_ID= 'U1N0ZPN1F'

logging.config.dictConfig(settings.LOGGING)

################################################################################
# Setup a new bot in your slack
# https://<your_slack>.slack.com/apps/manage/custom-integrations
################################################################################

# @name of bot if you see @chomps online in your config put 'chomps' here
BOT_NAME = settings.SLACK_BOT_NAME

# Bot ID         **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
BOT_ID = "U1N0ZPN1F"

# Bot API Token  **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
SLACK_BOT_TOKEN = "xoxb-56033804049-sEA5bOB8tqNTbcKrnynwqAF9"

slack_client = SlackClient(SLACK_BOT_TOKEN)

READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

# Load the plugins
pwd = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.join(pwd, "handlers")
handlers = HandlerRegistry([plugin_dir], slack_client, BOT_NAME, BOT_ID)
handlers.load_plugins()

def simple_response(response, channel):
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def handle(handler, match, msg):
    response = handler.process_message(match, msg)
    if response:
        simple_response(response, msg['channel'])

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

