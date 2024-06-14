#!/bin/bash
# powermate.sh

device=$(ls -1 /dev/input/by-id/* | grep -i powermate | head -1)

event_down='type 1 (EV_KEY), code 256 (BTN_0), value 1'
event_up='type 1 (EV_KEY), code 256 (BTN_0), value 0'
event_incr='type 2 (EV_REL), code 7 (REL_DIAL), value 1'
event_decr='type 2 (EV_REL), code 7 (REL_DIAL), value -1'


action_down () {
  :
}

action_up () {
  ~/bin/mute-meet.sh
}

action_incr () {
  xdotool key XF86AudioRaiseVolume
}

action_decr () {
  xdotool key XF86AudioLowerVolume
}

action_hold_incr () {
  # send key '>' (speed up)
  xdotool key 'shift+period'
}

action_hold_decr () {
  # send key '<' (speed down)
  xdotool key 'shift+comma'
}


# true then the knob button is pressed
status_hold='false'

sudo evtest "$device" | while read line; do
    case $line in
        (*$event_down)
          action_down ; status_hold='true' ;;
        (*$event_up)
          action_up ; status_hold='false'  ;;
        (*$event_incr)
          case $status_hold in
            'false') action_incr ;;
            'true')  action_hold_incr ;;
          esac
          ;;
        (*$event_decr)
          case $status_hold in
            'false') action_decr ;;
            'true')  action_hold_decr ;;
          esac
          ;;
    esac
done
