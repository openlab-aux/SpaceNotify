SpaceNotify
===========

a simple python script that can watch a SpaceAPI instance for state changes and
displays it via libnotify.

![screenshot](misc/screenshot_gnome.png)

## Usage
cd into the directory. Then type
```bash
./spacenotify.py
```
to run it in "one shot" mode. This immidiately calls the API and displays the
returned state and lastchange via libnotify. The process exits afterwards. In
addition you can run it in watch mode with
```bash
./spacenotify.py --watch
```
SpaceNotify will then call the API periodically to watch for changes. If the
state has changed since the last call a notification is displayed via
libnotify.

You can change the default check frequency of 5 minutes to something else:
```bash
./spacenotify.py --watch --frequency 23m
```
