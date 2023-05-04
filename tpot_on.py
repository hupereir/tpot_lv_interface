#!/bin/env python3

# John Haggerty, BNL
# 2023-02-15

# Hugo Pereira Da Costa, LANL
# 2023-03-24

from lvcontrol_hp import *
import time

class crate_data:
    def __init__( self, crate, digi_slots, ana_slots, channels ):
        self.crate = crate
        self.digi_slots = digi_slots
        self.ana_slots = ana_slots
        self.channels = channels
    crate = ""
    digi_slots = []
    ana_slots = []
    channels = []

south = crate_data("3A4-2", [15,16], [14], [4,6,7,8] )
north = crate_data("3C4-2", [14,15], [13], [4,6,7,8] )
crate_data_list = [ south, north ]

for crate_data in crate_data_list:
    crate = crate_data.crate
    digi_slots = crate_data.digi_slots
    ana_slots = crate_data.ana_slots
    channels = crate_data.channels
    print('crate: ',crate,
          ' digital slots: ',digi_slots,
          ' analog slots: ', ana_slots,
          ' channels: ',channels)

    controller = ip[crate]
    print('controller: ',controller)

    tn = lv_connect(controller)
    for slot in digi_slots:
        lv_enable_channels(tn,slot,channels)
        time.sleep(1)

    time.sleep(10)
    for slot in ana_slots:
        lv_enable_channels(tn,slot,channels)
        time.sleep(1)

    lv_disconnect(tn)
