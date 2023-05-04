#!/bin/env python3

# John Haggerty, BNL
# 2023-02-15

from lvcontrol_hp import *
import time
import argparse

crate="3C4-2"
slots=[13,14,15]
channels=[4,6,7,8]

print('command line crate: ',crate,
      ' command line slots: ',slots,
      ' command line channel: ',channels)

controller = ip[crate]
print('controller: ',controller)

tn = lv_connect(controller)
for slot in slots:
    lv_disable_channels(tn,slot,channels)
    time.sleep(1)

lv_disconnect(tn)    
