#!/bin/env python3

# John Haggerty, BNL
# 2023-02-15

# Hugo Pereira Da Costa, LANL
# 2023-03-24

from lvcontrol_hp import *
import time

class crate_data:
    def __init__( self, crate, slots, channels ):
        self.crate = crate
        self.slots = slots
        self.channels = channels
    crate = ""
    slots = []
    channels = []

south = crate_data("3A4-2", [14,15,16], [4,6,7,8] )
north = crate_data("3C4-2", [13,14,15], [4,6,7,8] )
crate_data_list = [ south, north ]

for crate_data in crate_data_list:
    crate = crate_data.crate
    slots = crate_data.slots
    channels = crate_data.channels
    print('crate: ',crate,
          ' slots: ',slots,
          ' channel: ',channels)

    controller = ip[crate]
    print('controller: ',controller)

    tn = lv_connect(controller)
    for slot in slots:
        lv_disable_channels(tn,slot,channels)
        time.sleep(1)

    lv_disconnect(tn)    

