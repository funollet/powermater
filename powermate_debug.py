#!/usr/bin/env python
# powermate_debug.py

from powermate import PowerMate, EventMapper

class EventMapperDebug (EventMapper):
    """Print information about Powermate's events. Mostly useful for debugging.
    """
    def send_click(self):
        print "button pressed"

    def send_more(self):
        print "rotate +"

    def send_less(self):
        print "rotate -"

    def send_drag_more(self):
        print "rotate + pressed"

    def send_drag_less(self):
        print "rotate - pressed"



def main():
    pm = PowerMate()
    actions = EventMapperDebug()

    while 1:
        actions.process(pm.WaitForEvent(-1))


if __name__ == '__main__':
    main()
