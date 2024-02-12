#!/bin/env python3

# Read all the voltages and currents from TPC distribution boards

# John Haggerty, BNL
# 2023-02-15 

from lvcontrol_hp import *
import time
import numpy as np

crate = ''
if len(sys.argv) == 2:
    crate = sys.argv[1].upper()
    print('crate: ',crate)
else:
    print('usage: tpcread.py crate')
    print('crate: ',list(ip.keys()))
    sys.exit(-1)

if not crate in ip:
    print('not a tpc crate')
    print('usage: tpcread.py crate')
    print('crate: ',list(ip.keys()))
    sys.exit(-1)

np.set_printoptions(formatter={'float': '{: 0.2f}'.format})
controller = ip[crate]
print('controller: ',controller)

tn = lv_connect(controller)
for i in range(1,17):
    voltages = lv_readv(tn,i)
    va = np.array(voltages)
#    print('Voltages Slot ',1,voltages)
#    print('Voltages Slot ',i,va)
    print('Voltages Slot ','{:02d}'.format(i),va)
    currents = lv_readi(tn,i)
    ca = np.array(currents)
#    print('Currents Slot ',i,currents)
#    print('Currents Slot ',i,ca)
    print('Currents Slot ','{:02d}'.format(i),ca)
lv_disconnect(tn)    
