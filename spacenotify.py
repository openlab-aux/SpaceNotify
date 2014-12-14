#!/usr/bin/env python3

from gi.repository import Notify
import datetime
import time
import requests
import argparse
from argparse import ArgumentParser, ArgumentTypeError
import re
import os
from os.path import dirname, join, abspath
import sys

SPACEAPI = "https://api.openlab-augsburg.de/13"


def notify(state, lastchange):
    iconPath = abspath(join(dirname(__file__),"icon"))

    if(state):
        msg = "Das OpenLab ist seit " + lastchange + " geöffnet!"
        icon = "file://" + join(iconPath, "open.png")
    elif(state == False):
        msg = "Das OpenLab wurde um " + lastchange + " Uhr geschlossen."
        icon = "file://" + join(iconPath, "closed.png")
    elif(state == None):
        msg = "Status unbekannt :("
        icon = "file://" + join(iconPath, "unknown.png")

    notification = Notify.Notification.new("Raumstatus", msg, icon)
    notification.show ()



def callSpaceAPI():
    rq = requests.get(SPACEAPI)
    if(rq.status_code != 200):
        raise Exception("Bad response: " + str(rq.status_code))

    data = rq.json()
    return data['state']['open'], data['state']['lastchange']
    
def convert_frequencystr(frequency):
    x = 0
    pattern = re.compile('^(?P<value>\d+)(?P<unit>[smh]?)$')
    match = pattern.match(frequency)

    if match:
        groupdict = match.groupdict()
        value = int(groupdict['value'])
        unit = groupdict['unit']

        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 60 * 60
        else:
            return value
    else:
        raise ArgumentTypeError('Invalid argument. Valid values are positive integers, optionally '
                                'appended by (s)econds, (m)inutes or (h)ours.')


if __name__ == '__main__':
    parser = ArgumentParser(description='Displays the space state via libnotify.')
    parser.add_argument('--watch', action='store_true',
                        help='Periodically check for state changes. Runs until interrupted.')
    parser.add_argument('--frequency', default='300', type=convert_frequencystr,
                        help='Set a frequency at which the API is called. Default: 5 minutes.')
    args = parser.parse_args()

    Notify.init("SpaceNotify")

    if(args.watch):
        try:
            lastState, _ = callSpaceAPI()
            while(True):
                state, lastchange = callSpaceAPI()

                if(state != lastState):
                    lastState = state
                    timestr = datetime.datetime.fromtimestamp(
                        int(lastchange)
                    ).strftime('%H:%M')

                    notify(state, timestr)

                time.sleep(args.frequency)

        except (KeyboardInterrupt, SystemExit):
            print("\nReceived interrupt, bye o/")
            exit(0)

        except Exception as e:
            print(e)

    else:
        try:
            # one shot
            state, lastchange = callSpaceAPI()

            timestr = datetime.datetime.fromtimestamp(
                int(lastchange)
            ).strftime('%H:%M')

            notify(state, timestr)
        except Exception as e:
            print(e)
