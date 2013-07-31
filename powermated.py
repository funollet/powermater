#!/usr/bin/env python
# powermated.py

import powermate
import dbus


# Codes for USB events read from Powermate HID device.
EVENT_UP = (1, 256, 0)
EVENT_DOWN = (1, 256, 1)
EVENT_LEFT = (2, 7, -1)
EVENT_RIGHT = (2, 7, 1)


class EventMapper:

    def __init__(self):
        self._state = ''
        self.position = 'up'


    def set_state(self, state):
        if state == 'short_press' and (self._state == 'increment_pressed' \
                or self._state == 'decrement_pressed'):
            self._state = state
            return

        self._state = state
        getattr(self, 'callback_%s' % state)()  # callback


    def act(self, event):
        """State machine, read events and send callbacks when needed.
        """
        if event[2:] == EVENT_DOWN:
            if self.position == 'up':
                self.position = 'down'
        elif event[2:] == EVENT_UP:
            self.position = 'up'
            self.set_state('short_press')
        elif event[2:] == EVENT_RIGHT:
            if self.position == 'up':
                self.set_state('increment')
            else:
                self.set_state('increment_pressed')
        elif event[2:] == EVENT_LEFT:
            if self.position == 'up':
                self.set_state('decrement')
            else:
                self.set_state('decrement_pressed')


    # Callbacks. Overwrite it with your desired actions.
    def callback_short_press(self):
        pass
    def callback_increment(self):
        pass
    def callback_decrement(self):
        pass
    def callback_increment_pressed(self):
        pass
    def callback_decrement_pressed(self):
        pass


class EventMapperDebug (EventMapper):
    """Print information about Powermate's events. Mostly useful for debugging.
    """

    def callback_short_press(self):
        print "button pressed"

    def callback_increment(self):
        print "rotate +"

    def callback_decrement(self):
        print "rotate -"

    def callback_increment_pressed(self):
        print "rotate + pressed"

    def callback_decrement_pressed(self):
        print "rotate - pressed"



class EventMapperClementine (EventMapper):
    """Uses Powermate's events to control Clementine + Kmix volume.
    """
    def __init__(self):
        EventMapper.__init__(self)
        # DBus session.
        _bus = dbus.SessionBus()
        # DBus interface to Clementine.
        _obj_clementine = _bus.get_object('org.mpris.clementine', '/Player')
        self._clementine = dbus.Interface(_obj_clementine,
                dbus_interface='org.freedesktop.MediaPlayer')
        # DBus interface to volume controls.
        _obj_kmix = _bus.get_object('org.kde.kmix',
                '/Mixers/PulseAudio__Playback_Devices_1/alsa_output_pci_0000_00_1b_0_analog_stereo')
        self._kmix = dbus.Interface(_obj_kmix,
                dbus_interface='org.kde.KMix.Control')


    def callback_short_press(self):
        self._clementine.Pause()

    def callback_increment(self):
        self._kmix.increaseVolume()

    def callback_decrement(self):
        self._kmix.decreaseVolume()

    def callback_increment_pressed(self):
        self._clementine.Next()

    def callback_decrement_pressed(self):
        self._clementine.Prev()




pm = powermate.PowerMate("/dev/input/powermate")
# actions = EventMapperDebug()
actions = EventMapperClementine()

while 1:
    actions.act(pm.WaitForEvent(-1))
