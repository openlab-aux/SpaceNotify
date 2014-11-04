#!/usr/bin/env python3

from gi.repository import Notify
import datetime
import time
import requests
import argparse
import os
from os.path import dirname, join, abspath

SPACEAPI = "https://api.openlab-augsburg.de/13"
FREQUENCY = 300



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
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Displays the space state via libnotify.')
    parser.add_argument('--watch', action='store_true', help='Periodically check for state changes. Runs until interrupted.')
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

                time.sleep(FREQUENCY)

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
