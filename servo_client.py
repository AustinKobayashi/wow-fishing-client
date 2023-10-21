import json
import time
import requests
import logger as lg

SERVER_URL = 'http://192.168.1.235:5000/click'
HEADERS = {'Content-Type': 'application/json'}

TIMEOUT = 1

SERVO_CLICK = 1650
SERVO_NEUTRAL = 1500


def set_neutral():
    try:
        response = requests.post(SERVER_URL, data=json.dumps({'click': SERVO_NEUTRAL}), headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except Exception as e:
        lg.log('Error setting neutral position: {}'.format(e))


def press_fishing_button(action):
    lg.log('Pressing {} button...'.format(action))

    try:
        response = requests.post(SERVER_URL, data=json.dumps({'click': SERVO_CLICK}), headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        set_neutral()
    except Exception as e:
        lg.log('Error pressing {} button: {}'.format(action, e))
