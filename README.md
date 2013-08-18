Powermater
==========

A python library for using [Griffin's Powermate](http://store.griffintechnology.com/powermate)
device under Linux.


The itch
--------

Powermate is an USB HID device but its events can't be read straight into X.
It emits just four simple events:

 - Down: button has been pressed.
 - Up: button has been released.
 - Right: knob has been rotated clockwise.
 - Left: knob has been rotated counter-clockwise.


Scratch
-------

This library can read the events from the `/dev/input/` device. The
original code has been extended from:

    http://sowerbutts.com/powermate/

In addition, it maps events sequences into more useful actions; let's
call it "gestures". Each gesture can have an associated callback: an
action invoked, right now a Python function.

The implemented gestures are:

 - click (up + down)
 - more (knob right)
 - less (knob left)
 - drag more (knob right while pressed down)
 - drag less (knob left while pressed down)


Device configuration
--------------------

Linux will create an entry for your device into `/dev/input/event*`. Get an alias `/dev/input/powermate` and better permissions by adding an udev rule.

    # /etc/udev/rules.d/40-powermate.rules
    ATTRS{product}=="Griffin PowerMate" GROUP="plugdev", SYMLINK+="input/powermate", MODE="660"


Usage
-----

Mapping gestures to your own actions requires writing a little Python script.

Take a look at the provided examples.

 - `powermate_debug.py`: a dumb example, just useful for debugging, that echoes every gesture.
 - `powermate_clementine.py`: controls volume (via Kmix) and Clementine music player:
   play/pause, next song in playlist, previous song in playlist.




Finite State Machine implementation
-----------------------------------

This is a state transition table for the state machine mapping events to gestures.

| State        | Input | Output     | Next state |
| -----        | ----- | ---------  | ---------- |
| **up**       | down  |            | down       |
|              | left  | left       | up         |
|              | right | right      | up         |
| **down**     | up    | click      | up         |
|              | left  | drag-left  | drag-left  |
|              | right | drag-right | drag-right |
|**drag-left** | up    |            | up         |
|              | left  | drag-left  |            |
|              | right | drag-right | drag-right |
|**drag-right**| up    |            | up         |
|              | left  | drag-left  |            |
|              | right | drag-right | drag-right |
