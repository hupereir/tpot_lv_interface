#!/usr/bin/env python3

import sys
import time

from lvcontrol_hp import *
from tpot_lv_util import *

# usage
if len(sys.argv) == 1:
  print(
    'usage: \n'
    '  tpot_lv_on.py south|north|all|<fiber ids>\n'
    '\nwith\n'
    '  <fiber ids>: a list of fiber ids to turn on (0..25)')
  exit(0)

# get channel names
channel_dict = parse_arguments( sys.argv[1:] )

for crate in sorted(channel_dict.keys()):
  digital_slots = sorted(channel_dict[crate]['digital_slots'])
  analog_slots = sorted(channel_dict[crate]['analog_slots'])
  channels = sorted(channel_dict[crate]['channels'])

  print('crate: ',crate,
    ' digital slots: ',digital_slots,
    ' analog slots: ', analog_slots,
    ' channels: ',channels)
  controller = ip[crate]
  print('controller: ',controller)

  tn = lv_connect(controller)
  for slot in digital_slots:
    lv_enable_channels(tn,slot,channels)
    time.sleep(1)

  time.sleep(10)
  for slot in analog_slots:
    lv_enable_channels(tn,slot,channels)
    time.sleep(1)

  lv_disconnect(tn)
