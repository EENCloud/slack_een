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

BOT_NAME = settings.SLACK_BOT_NAME
BOT_ID = settings.SLACK_BOT_ID
SLACK_BOT_TOKEN=settings.SLACK_BOT_TOKEN
slack_client = SlackClient(SLACK_BOT_TOKEN)

READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

# Load the plugins
pwd = os.path.dirname(os.path.abspath(__file__))
plugin_dir = os.path.join(pwd, "een_handlers")
handlers = HandlerRegistry([plugin_dir], slack_client, BOT_NAME, BOT_ID)
handlers.load_plugins()

def simple_response(response, channel):
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def handle(handler, match, msg):
    response = handler.process_message(match, msg)
    if response:
        simple_response(response, msg['channel'])

if __name__ == "__main__":
    
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
    