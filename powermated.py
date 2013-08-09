#!/usr/bin/env python
# powermated.py

import powermate
import dbus


# Hardcoded value. Should be found dynamically.
DEFAULT_KMIX_OUTPUT_DEVICE = '/Mixers/PulseAudio__Playback_Devices_1/alsa_output_pci_0000_00_1b_0_analog_stereo'

# Codes for USB events read from Powermate HID device.
EVENT_UP = (1, 256, 0)
EVENT_DOWN = (1, 256, 1)
EVENT_LEFT = (2, 7, -1)
EVENT_RIGHT = (2, 7, 1)



class Up(object):
    def __init__(self, mapper):
        self.mapper = mapper

    def process(self, event):
        if event[2:] == EVENT_DOWN:
            self.mapper.state = self.mapper.down
        elif event[2:] == EVENT_LEFT:
            self.mapper.send_less()
        elif event[2:] == EVENT_RIGHT:
            self.mapper.send_more()


class Down(object):
    def __init__(self, mapper):
        self.mapper = mapper

    def process(self, event):
        if event[2:] == EVENT_UP:
            self.mapper.state = self.mapper.up
            self.mapper.send_click()
        elif event[2:] == EVENT_LEFT:
            self.mapper.state = self.mapper.drag_less
            self.mapper.send_drag_less()
        elif event[2:] == EVENT_RIGHT:
            self.mapper.state = self.mapper.drag_more
            self.mapper.send_drag_more()


class Drag_less(object):
    def __init__(self, mapper):
        self.mapper = mapper

    def process(self, event):
        if event[2:] == EVENT_UP:
            self.mapper.state = self.mapper.up
        elif event[2:] == EVENT_LEFT:
            self.mapper.send_drag_less()
        elif event[2:] == EVENT_RIGHT:
            self.mapper.state = self.mapper.drag_more
            self.mapper.send_drag_more()


class Drag_more(object):
    def __init__(self, mapper):
        self.mapper = mapper

    def process(self, event):
        if event[2:] == EVENT_UP:
            self.mapper.state = self.mapper.up
        elif event[2:] == EVENT_LEFT:
            self.mapper.state = self.mapper.drag_less
            self.mapper.send_drag_less()
        elif event[2:] == EVENT_RIGHT:
            self.mapper.send_drag_more()


class EventMapper(object):
    """A state machine mapping events read from the Powermate HID device
    into more elaborate events (gestures).

    Inherit the class and overwrite callbacks (methods 'send_*').
    """
    def __init__(self):
        self.up = Up(self)
        self.down = Down(self)
        self.drag_less = Drag_less(self)
        self.drag_more = Drag_more(self)

        self.state = self.up


    def process(self, event):
        self.state.process(event)

    # Callbacks. Overwrite it with your desired actions.
    def send_click(self):       pass
    def send_more(self):        pass
    def send_less(self):        pass
    def send_drag_more(self):   pass
    def send_drag_less(self):   pass




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


class EventMapperClementine (EventMapper):
    """Uses Powermate's events to control Clementine + Kmix volume.

    Adding this to ~/.kde/share/config/kmixrc may make smoother volume changes:
        VolumePercentageStep=1.2
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
        _obj_kmix = _bus.get_object('org.kde.kmix', DEFAULT_KMIX_OUTPUT_DEVICE)
        # TODO: find the real Kmix output device.
        self._kmix = dbus.Interface(_obj_kmix,
                dbus_interface='org.kde.KMix.Control')


    def send_click(self):
        self._clementine.Pause()

    def send_more(self):
        self._kmix.increaseVolume()

    def send_less(self):
        self._kmix.decreaseVolume()

    def send_drag_more(self):
        self._clementine.Next()

    def send_drag_less(self):
        self._clementine.Prev()


def main():
    pm = powermate.PowerMate("/dev/input/powermate")
    # actions = EventMapperDebug()
    actions = EventMapperClementine()

    while 1:
        actions.process(pm.WaitForEvent(-1))


if __name__ == '__main__':
    main()
