"""
    **Eagle Calendar**: Report Support engineer based on google calendar
"""
import os
import re
import random
import datetime
import logging
import calendar
from googleapiclient.discovery import build
from dateutil.relativedelta import relativedelta
import gevent

log = logging.getLogger("handler.cal")
try:
    from lib import ChompsHandler
except ImportError:
    from chomps.lib import ChompsHandler

DEV_KEY = os.environ.get("EEN_GOOGLE_DEVELOPER_KEY", None)
try:
    cal = build('calendar', 'v3', developerKey=DEV_KEY)
except:
    print "No need to hold up if we can't load google calendar api"
SUPPORT_CAL_ID = "eagleeyenetworks.com_5rmunmqvsn34i56qnqeaiid63g@group.calendar.google.com"
WORK_WEEKDAYS = 5

IGNORED_USERS = ["Peter", "Rosko"]

SPECIAL_SUPPORT_USERS = {
}

SUPPORT_USERS = [
    "George",
    "Greg",
    "Devin",
    "Jeff",
    "Ezequiel",
    "Joey",
    "Tanner",
    "Claire",
    "Alec",
    "Dailey",
    "Scott",
    "BJ",
    ]

SUPPORT_PHRASES = [
    "support all the things! :all_the_things:",
    "you have been summoned to support. :magic:",
    "try not to break anything! It's your support day.",
    "supporting by day, supporting by night.",
    "you should feel lucky! It's your support day. :four_leaf_clover:",
    "Always Support, OK! :alsok:",
    "Fixing the world one bridge at a time.",
    ]

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

COMPANY_HOLIDAYS = {
    "2017": [
        datetime.datetime(2017, 1, 2),
        datetime.datetime(2017, 5, 29),
        datetime.datetime(2017, 7, 4),
        datetime.datetime(2017, 9, 4),
        datetime.datetime(2017, 11, 23),
        datetime.datetime(2017, 11, 24),
        datetime.datetime(2017, 12, 25),
        ],
    "2018": [
        datetime.datetime(2018, 1, 1),
        ]
    }

BUSINESS_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
BUSINESS_DAYS_INDEX = [0, 1, 2, 3, 4]
SUPPORT_WEEK_FORMAT = "```{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}\n{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}```"
DEFAULT_TIMEZONE = "UTC"
def _increment_date(date, days=1):
    return date + datetime.timedelta(days=days)

def _first_wednesday_of_month(year, month):
    start = datetime.datetime(year, month, 1)
    while start.weekday() != 2:
        start = _increment_date(start)
    return start

def _valid_business_day(date):
    if date.weekday() not in BUSINESS_DAYS_INDEX:
        return False
    holidays = [holiday for year in COMPANY_HOLIDAYS.values() for holiday in year]
    if date in holidays:
        print "Skipping holiday {}".format(date)
        return False
    return True

def _get_next_fill_day(date):
    new_date = _increment_date(date)
    while not _valid_business_day(new_date):
        new_date = _increment_date(new_date)
    return new_date

def format_datetime_for_calendar_request(dt):
    return dt.isoformat("T") + "Z"

def fill_next_round_of_support_days():
    # get next x days
    last_filled_day = None
    try:
        last_filled_day = get_last_day_filled()
    except:
        pass
    if not last_filled_day:
        return "Unknown issue filling calendar"
    start_fill_day = _increment_date(last_filled_day)
    copy_support_users = SUPPORT_USERS[:]
    wed = _first_wednesday_of_month(start_fill_day.year, start_fill_day.month)
    if wed < start_fill_day:
        next_wednesday_search = start_fill_day + relativedelta(months=+1)
        wed = _first_wednesday_of_month(next_wednesday_search.year, next_wednesday_search.month)

    last_week = get_previous_week(last_filled_day)
    this_week = get_this_week(last_filled_day)
    this_week_needed = WORK_WEEKDAYS-len(this_week)

    done = False
    while not done:
        first_week = True
        random.shuffle(copy_support_users)
        for ii in xrange(this_week_needed):
            if copy_support_users[ii] in last_week or copy_support_users[ii] in this_week:
                first_week = False
        if first_week:
            next_week = copy_support_users[this_week_needed:this_week_needed+WORK_WEEKDAYS]
            if not any([each in this_week for each in next_week]):
                done = True

    # HACK until i can get oauth2 working
    ret = "```\nhttps://developers.google.com/google-apps/calendar/v3/reference/events/quickAdd?authuser=1\n"
    ret += SUPPORT_CAL_ID + "\n"
    while copy_support_users:
        # HACK change to function '_handle_special_users'
        next_user = copy_support_users.pop(0)
        cal_text = "{} on {} all day".format(next_user, start_fill_day.strftime("%B %d"))
        ret += "\n{}\n".format(cal_text)

        # Add to calendar This works once we have oauth2
        #created_event = cal.events().quickAdd(calendarId=SUPPORT_CAL_ID,
                                               #text=cal_text).execute()
        #print created_event['id']
        #copy_support_users.remove(next_user)
        start_fill_day = _get_next_fill_day(start_fill_day)

    ret += "```"
    return ret
    #return "Updated Calendar" # restore when oauth2 works

def get_last_day_filled():
    now = datetime.datetime.utcnow()
    later = now + datetime.timedelta(days=60)
    min_time = format_datetime_for_calendar_request(now)
    max_time = format_datetime_for_calendar_request(later)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID, maxResults=300, timeZone=DEFAULT_TIMEZONE,
                                timeMax=max_time, timeMin=min_time, fields="items/start", orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    last_filled_day = datetime.datetime.now().strftime("%Y-%m-%d")
    filled_days = []
    if result:
        items = result.get('items', None)
        if items:
            filled_days = [item['start']['date'] for item in items]
    try:
        last_filled_day = filled_days[-1]
    except IndexError:
        pass

    if not last_filled_day:
        return None
    last_filled_day = datetime.datetime.strptime(last_filled_day, "%Y-%m-%d")
    return last_filled_day

def get_this_week(date_to_look=datetime.datetime.utcnow()):
    """ Get support engineers from the previous week. """
    monday = date_to_look - datetime.timedelta(days=date_to_look.weekday())
    # prev
    friday = monday + datetime.timedelta(days=WORK_WEEKDAYS)
    min_time = format_datetime_for_calendar_request(monday)
    max_time = format_datetime_for_calendar_request(friday)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID,
                                maxResults=WORK_WEEKDAYS,
                                timeZone=DEFAULT_TIMEZONE,
                                timeMin=min_time,
                                timeMax=max_time,
                                fields="items/summary",
                                orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    out_list = []
    if result:
        items = result.get('items', None)
        if items:
            for each in items:
                out_list.append(each.get('summary', None))
    return [each.replace("*", "") for each in out_list if each]

def get_previous_week(date_to_look=datetime.datetime.utcnow()):
    """ Get support engineers from the previous week. """
    monday = date_to_look - datetime.timedelta(days=date_to_look.weekday())
    # prev
    monday = monday - datetime.timedelta(days=7)
    friday = monday + datetime.timedelta(days=WORK_WEEKDAYS)
    min_time = format_datetime_for_calendar_request(monday)
    max_time = format_datetime_for_calendar_request(friday)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID,
                                maxResults=WORK_WEEKDAYS,
                                timeZone=DEFAULT_TIMEZONE,
                                timeMin=min_time,
                                timeMax=max_time,
                                fields="items/summary",
                                orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    out_list = []
    if result:
        items = result.get('items', None)
        if items:
            for each in items:
                out_list.append(each.get('summary', None))
    return [each.replace("*", "") for each in out_list if each]

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

def get_support_week(col_width=15):
    """ Get this weeks support engineers. """
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(days=now.weekday())
    friday = monday + datetime.timedelta(days=WORK_WEEKDAYS)
    min_time = format_datetime_for_calendar_request(monday)
    max_time = format_datetime_for_calendar_request(friday)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID,
                                maxResults=WORK_WEEKDAYS,
                                timeZone=DEFAULT_TIMEZONE,
                                timeMin=min_time,
                                timeMax=max_time,
                                fields="items/summary",
                                orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    out_list = []
    if result:
        items = result.get('items', None)
        if items:
            for each in items:
                out_list.append(each.get('summary', None))
    if len(out_list) < WORK_WEEKDAYS:
        while len(out_list) < WORK_WEEKDAYS:
            out_list.append(None)
    ret = SUPPORT_WEEK_FORMAT.format(BUSINESS_DAYS[0],
                                     BUSINESS_DAYS[1],
                                     BUSINESS_DAYS[2],
                                     BUSINESS_DAYS[3],
                                     BUSINESS_DAYS[4],
                                     out_list[0],
                                     out_list[1],
                                     out_list[2],
                                     out_list[3],
                                     out_list[4],
                                     COL_WIDTH=col_width)
    return ret

def get_support_month(col_width=15):
    """ Get this months support engineers. """
    now = datetime.datetime.utcnow()
    this_month = calendar.monthcalendar(now.year, now.month)
    this_month_len = calendar.monthrange(now.year, now.month)
    first = now - datetime.timedelta(days=now.day -1)
    last = first + datetime.timedelta(days=this_month_len[1] -1)
    min_time = format_datetime_for_calendar_request(first)
    max_time = format_datetime_for_calendar_request(last)
    request = cal.events().list(calendarId=SUPPORT_CAL_ID,
                                maxResults=this_month_len[1],
                                timeZone=DEFAULT_TIMEZONE,
                                timeMin=min_time,
                                timeMax=max_time,
                                fields="items/summary",
                                orderBy="startTime",
                                singleEvents=True)
    result = request.execute()
    out_list = []
    if result:
        items = result.get('items', None)
        if items:
            for each in items:
                out_list.append(each.get('summary', None))
    for idx, week in enumerate(this_month):
        for idy, day in enumerate(week):
            if idy < WORK_WEEKDAYS and day != 0:
                if len(out_list) > 0:
                    this_month[idx][idy] = {'day': day, 'name': out_list.pop(0)}
    ret = "```{:^{TOTAL_WIDTH}}\n".format("{} {}".format(now.strftime("%B"), now.strftime("%Y")),
                                          TOTAL_WIDTH=col_width*WORK_WEEKDAYS)
    ret += "{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}|{:^{COL_WIDTH}}\n".format(BUSINESS_DAYS[0],
                                                                                                      BUSINESS_DAYS[1],
                                                                                                      BUSINESS_DAYS[2],
                                                                                                      BUSINESS_DAYS[3],
                                                                                                      BUSINESS_DAYS[4],
                                                                                                      COL_WIDTH=col_width)
    is_start_num = True
    is_start_name = True
    for week in this_month:
        for day in week:
            if isinstance(day, int):
                ret += "{:^{COL_WIDTH}}{}".format("", " " if is_start_num else "", COL_WIDTH=col_width)
            else:
                is_start_num = False
                ret += "{:^{COL_WIDTH}}|".format(day['day'], COL_WIDTH=col_width)
        ret = ret[:-1]
        ret += "\n"
        for day in week:
            if isinstance(day, int):
                ret += "{:^{COL_WIDTH}}{}".format("", " " if is_start_name else "", COL_WIDTH=col_width)
            else:
                is_start_name = False
                ret += "{:^{COL_WIDTH}}|".format(day['name'], COL_WIDTH=col_width)
        ret = ret[:-1]
        ret += "\n\n"
    ret += "```"
    print ret

    return ret


def findNextSevenPM():
    now =datetime.datetime.now()
    today=datetime.datetime.now()
    sevenPM = time(hour=19, minute=00, second=00)
    if now.hour < sevenPM.hour:
        sevenPM =  datetime.datetime.combine(today, sevenPM)
        duration = sevenPM - datetime.datetime.now()
        totalSeconds= duration.total_seconds()
        return totalSeconds  
    else: 
        tomorrow = today + timedelta(days=1)
        sevenPM = time(hour=19, minute=00, second=00)
        nextSevenPM =  datetime.combine(tomorrow, sevenPM)
        duration = nextSevenPM - datetime.now()
        totalSeconds= duration.total_seconds()
        return totalSeconds 




TRIGGER = re.compile(r'(?:[Ss]upport ([Dd]ay\?|[Ww]eek\?|[Mm]onth\?|[Ff]ill\?))')
class CalendarBot(ChompsHandler):
    """
        commands: ``support (day|week|month)?``
    """
    def __init__(self, client, bot_name, bot_id):
        super(ChompsHandler, self).__init__()
        pprint("start %s" % datetime.now()) 
        gevent.spawn_later(1, self.updateTopic, client)

    @property
    def call_limit(self):
        return 1

    @property
    def pattern(self):
        return TRIGGER


    def get_channel_id(self,client):
    result= client.api_call("channels.list")
    channels = result["channels"]
    for channel in channels:
        if channel["name"] == "support":
            channel = channel["id"]
            return channel 

    def get_user_id(self,client,engineer):
    users= client.api_call("users.list")
    users = users["members"]
    engineer = engineer.lower()
    engineerStandardized = USER_TRANSLATION[engineer]
    for user in users:
        if user["profile"]["display_name_normalized"] == engineerStandardized:
            return ("<@%s>" % user["id"])

    def process_message(self, match, msg=None):
        try:
            if msg:
                if 'week' in msg['text'].lower():
                    week = get_support_week()
                    return '>>> {}'.format(week)
                elif 'month' in msg['text'].lower():
                    month = get_support_month()
                    return '>>> {}'.format(month)
                elif 'day' in msg['text'].lower():
                    eng = get_user_on_support()
                    if '*' in eng:
                        eng = eng.replace("*", "")
                    user = USER_TRANSLATION.get(eng.lower(), None)
                    if user:
                        return '>>> <@{}>, {}'.format(user, random.choice(SUPPORT_PHRASES))
                    else:
                        return '>>> @{}, {}'.format(eng, random.choice(SUPPORT_PHRASES))
                else:
                    return '>>> {}'.format(fill_next_round_of_support_days())
            else:
                eng = get_user_on_support()
                return '>>> {}'.format(eng)
        except:
            log.exception("Got an error")
            return '>>> Something went wrong looking for the support engineer'

    def updateTopic(self,client):
        if datetime.datetime.now().weekday() < 5 or datetime.datetime.now().weekday() == 6 :
            engineer= get_user_on_support()
            topic = self.get_user_id(client,engineer)
            channel = self.get_channel_id(client)
            client.api_call("channels.setTopic", channel=channel, topic=topic)
            nextUpdate = findNextSevenPM()
            gevent.spawn_later(nextUpdate, self.updateTopic, client)
        elif datetime.datetime.now().weekday() == 5:
            topic= "its Saturday, no engineer on Saturday"
            channel = self.get_channel_id(client)
            client.api_call("channels.setTopic", channel=channel, topic=topic)
            nextUpdate = findNextSevenPM()
            gevent.spawn_later(nextUpdate, self.updateTopic, client)