#!/bin/env python3

# John Haggerty, BNL
# 2023-02-15

from lvcontrol_hp import *
import time
import argparse

crate="3A4-2"
digi_slots=[15,16]
ana_slots=[14]
channels=[4,6,7,8]

print('crate: ',crate,
      ' digital slots: ',digi_slots,
      ' analog slots: ',ana_slots,
      ' channels: ',channels)

controller = ip[crate]
print('controller: ',controller)

tn = lv_connect(controller)
# turn on digital slots first
for slot in digi_slots:
    lv_enable_channels(tn,slot,channels)
    time.sleep(1)
# as per Takao's recommendation, wait 5sec, then turn on analog
time.sleep(10)
for slot in ana_slots:
    lv_enable_channels(tn,slot,channels)
    time.sleep(1)

lv_disconnect(tn)    


