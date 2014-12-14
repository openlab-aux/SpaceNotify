#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
import datetime
import os
from os.path import dirname, join, abspath
import re
import time
from gi.repository import Notify
import requests

SPACEAPI = "https://api.openlab-augsburg.de/13"


def notify(state, lastchange):
    iconpath = abspath(join(dirname(__file__), "icon"))

    if state:
        msg = "Das OpenLab ist seit " + lastchange + " geöffnet!"
        icon = "file://" + join(iconpath, "open.png")
    elif state is False:
        msg = "Das OpenLab wurde um " + lastchange + " Uhr geschlossen."
        icon = "file://" + join(iconpath, "closed.png")
    elif state is None:
        msg = "Status unbekannt :("
        icon = "file://" + join(iconpath, "unknown.png")

    notification = Notify.Notification.new("Raumstatus", msg, icon)
    notification.show()


def call_spaceapi():
    rq = requests.get(SPACEAPI)
    if rq.status_code != 200:
        raise Exception("Bad response: " + str(rq.status_code))

    data = rq.json()
    return data['state']['open'], data['state']['lastchange']


def convert_frequencystr(frequency):
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

    if args.watch:
        try:
            laststate, _ = call_spaceapi()
            while True:
                state, lastchange = call_spaceapi()

                if state != laststate:
                    laststate = state
                    timestr = datetime.datetime.fromtimestamp(
                        int(lastchange)
                    ).strftime('%H:%M')

                    notify(state, timestr)

                time.sleep(args.frequency)

        except(KeyboardInterrupt, SystemExit):
            print("\nReceived interrupt, bye o/")
            exit(0)

        except Exception as e:
            print(e)

    else:
        try:
            # one shot
            state, lastchange = call_spaceapi()

            timestr = datetime.datetime.fromtimestamp(
                int(lastchange)
            ).strftime('%H:%M')

            notify(state, timestr)
        except Exception as e:
            print(e)
