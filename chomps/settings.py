import os
import sys

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_BOT_ID = os.environ.get('SLACK_BOT_ID')
SLACK_BOT_NAME = os.environ.get('SLACK_BOT_NAME', 'chomps')
SLACK_NOTIF_CHANNEL = os.environ.get('SLACK_NOTIF_CHANNEL')
SLACK_OPEN_CHANNEL = os.environ.get('SLACK_PUB_CHANNEL')
SLACK_DEBUG_CHANNEL = os.environ.get('SLACK_NOTIF_DEBUG_CHANNEL')

EEN_USERNAME = os.environ.get('EEN_USERNAME')
EEN_PASSWORD = os.environ.get('EEN_PASSWORD')
EEN_CAM_IDS = os.environ.get('EEN_CAM_IDS', "").split(',') 

EEN_ALERT_RESET = int(os.environ.get('EEN_ALERT_RESET', 90))
EEN_ALERT_REGION = os.environ.get('EEN_ALERT_REGION', 'op_boomstick')

CLARIFAI_SECRET = os.environ.get('CLARIFAI_SECRET')
CLARIFAI_APP_ID = os.environ.get('CLARIFAI_APP_ID')
CUSTOM_MODEL = os.environ.get('CUSTOM_MODEL')
CUSTOM_MODEL = None
SHOW_TAGS = os.environ.get('SHOW_TAGS') == 'True'

HANDLER_DIR = os.environ.get('PLUGIN_DIR', 'handlers')


__LOG_FORMAT = os.environ.get('EEN_LOG_FORMAT', '%(asctime)s.%(msecs).03d[%(levelname)0.3s] %(name)s:%(funcName)s.%(lineno)d %(message)s')
__DATE_FORMAT = os.environ.get('EEN_LOG_DATE_FORMAT', '%m-%d %H:%M:%S')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': __LOG_FORMAT,
            'datefmt': __DATE_FORMAT
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'stdout':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        }
    },
    'loggers': {

        ### Any message not caught by a lower level logger OR 
        ### Propagates the message to this level will be filtered at
        ### the root.
        '' : {
            'handlers': ['stdout'],
            'level': os.environ.get('LOGLEVEL_ROOT', 'INFO'),
            'propagate': False,
        },
        'requests' : {
            'handlers': ['stdout'],
            'level': os.environ.get('LOGLEVEL_ROOT', 'ERROR'),
            'propagate': False,
        },        
    }
}