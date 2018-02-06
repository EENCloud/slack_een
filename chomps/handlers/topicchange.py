
import re
import random
import requests
import simplejson
from pprint import pprint
from lib import ChompsHandler
import os
import datetime
from googleapiclient.discovery import build
from dateutil.relativedelta import relativedelta
import gevent
import settings

from slackclient import SlackClient

# @name of bot if you see @chomps online in your config put 'chomps' here
BOT_NAME = settings.SLACK_BOT_NAME

# Bot ID         **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
BOT_ID = settings.SLACK_BOT_ID

# Bot API Token  **Note: do not publish this (we advise making this an ENV and populating this with os.environ.get(<ENV_NAME>, "")
SLACK_BOT_TOKEN = settings.SLACK_BOT_TOKEN

slack_client = SlackClient(SLACK_BOT_TOKEN)

READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

DEV_KEY = os.environ.get("EEN_GOOGLE_DEVELOPER_KEY", None)
try:
    cal = build('calendar', 'v3', developerKey=DEV_KEY)
except:
    print "No need to hold up if we can't load google calendar api"
SUPPORT_CAL_ID = "eagleeyenetworks.com_5rmunmqvsn34i56qnqeaiid63g@group.calendar.google.com"
DEFAULT_TIMEZONE = "UTC"

USER_TRANSLATION = {
    'ben'     : 'bnewland',
    'brandon' : 'breybrey',
    'devin'   : 'devin',
    'eric'    : 'eric.janik',
    'eze'     : 'ezequiel',
    'ezequiel': 'ezequiel',
    'jeff'    : 'jeffry.ratcliff',
    'joey'    : 'joey',
    'george'  : 'gkarr',
    'greg'    : 'greg_slomin',
    'peter'   : 'peter',
    'ray'     : 'rmartinez-een',
    'rosko'   : 'rosko',
    'steve'   : 'rosko',
    'tanner'  : 'tanner',
    'tim'     : 'nacnudmit',
    'cortez'  : 'michael.cortez',
    'claire'  : 'claireamalfitano',
    'alec'    : 'arobinson',
    'dailey'  : 'dailey-report',
    'scott'   : 'scottdavison',
    'bj'      : 'bjblack',
    }


def simple_topic_change(response,channel):
    slack_client.api_call("channels.setTopic", channel=channel, topic=response)


def format_datetime_for_calendar_request(dt):
    return dt.isoformat("T") + "Z"

def get_user_on_support():
    """ Get todays support engineer. """
    now = datetime.datetime.utcnow()
    min_time = format_datetime_for_calendar_request(now)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID,
                                maxResults=1,
                                timeZone=DEFAULT_TIMEZONE,
                                timeMin=min_time,
                                fields="items/summary",
                                orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    if result:
        items = result.get('items', None)
        if items:
            return items[0].get('summary', None)


trigger = re.compile('(?:[Cc]homps) [Tt]opic ([\W|\w\s]+)')


class CalendarBot(ChompsHandler):
    def __init__(self, client, bot_name, bot_id):
        gevent.spawn_later(10,self.updateTopic)
        super(CalendarBot, self).__init__(client, bot_name, bot_id) 


    @property
    def pattern(self):
        """This is called by the chomps engine to get the pattern for the function"""
        return trigger

    def process_message(self, match, msg):
        topic = match.groups()[0]
        pprint(topic)
        pprint(match.groups())
        topic= get_user_on_support()
        return ' @{}'.format(USER_TRANSLATION.get(topic.lower()))

    def updateTopic(nothing):
        topic= get_user_on_support()
        pprint(topic)
        slack_client.api_call("channels.setTopic", channel="C8YJCQF19", topic=topic)
        gevent.spawn_later(10, updateTopic())
        



