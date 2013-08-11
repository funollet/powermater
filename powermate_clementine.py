#!/usr/bin/env python
# powermate_clementine.py

from powermate import PowerMate, EventMapper
import dbus
import time


# Hardcoded value. Should be found dynamically.
DEFAULT_KMIX_OUTPUT_DEVICE = '/Mixers/PulseAudio__Playback_Devices_1/alsa_output_pci_0000_00_1b_0_analog_stereo'

# Events drag_more() and drag_less() won't make any action until this time (seconds) has passed
# since last time they were invoked.
MIN_EVENT_INTERVAL = 0.7



class Timer(object):
    """Count elapsed time."""
    def __init__(self):
        self.last = 0

    def reset(self):
        self.last = time.time()

    def duration(self):
        return time.time() - self.last



class EventMapperClementine (EventMapper):
    """Uses Powermate's events to control Clementine + Kmix volume.

    Tricks:

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

        self.last_drag_more = Timer()
        self.last_drag_more.reset()
        self.last_drag_less = Timer()
        self.last_drag_less.reset()


    def send_click(self):
        self._clementine.Pause()

    def send_more(self):
        self._kmix.increaseVolume()

    def send_less(self):
        self._kmix.decreaseVolume()

    def send_drag_more(self):
        # Do not act more than once every MIN_EVENT_INTERVAL seconds.
        if self.last_drag_more.duration() > MIN_EVENT_INTERVAL:
            self._clementine.Next()
            self.last_drag_more.reset()

    def send_drag_less(self):
        # Do not act more than once every MIN_EVENT_INTERVAL seconds.
        if self.last_drag_less.duration() > MIN_EVENT_INTERVAL:
            self._clementine.Prev()
            self.last_drag_less.reset()


def main():
    pm = PowerMate()
    actions = EventMapperClementine()

    while 1:
        actions.process(pm.WaitForEvent(-1))


if __name__ == '__main__':
    main()
