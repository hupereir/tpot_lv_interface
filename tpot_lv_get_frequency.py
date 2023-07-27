#!/usr/bin/env python3
import subprocess
import re
import argparse

from lvcontrol_hp import *
from tpot_lv_util import *

#######################
def get_stuck_channels():
    # get FEE link status from ebdc39

    # make a first reading of the FEEs number of events
    result = subprocess.run( ['ssh', 'ebdc39', '-x', '/home/phnxrc/operations/TPOT/tpot_daq_interface/get_rx_sob.py'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    rx_sob_begin = re.findall( "(\d+)", output )

    # wait 5s
    sample_time = 5
    time.sleep(sample_time)

    # redo
    result = subprocess.run( ['ssh', 'ebdc39', '-x', '/home/phnxrc/operations/TPOT/tpot_daq_interface/get_rx_sob.py'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    rx_sob_end = re.findall( "(\d+)", output )

    # threshold for stuck channel
    n_channels=256
    max_frequency = 5000
   
    # these are TPOT links
    fee_list = [0, 1, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 23, 24, 25]
   
    # calculate frequencies, check which links are above threshold
    down_channels = []
    for i, (begin,end) in enumerate(zip(rx_sob_begin, rx_sob_end)):
        if not i in fee_list:
            continue

        difference = eval(end)-eval(begin)
        frequency = difference/(n_channels*sample_time);
        print( f'channel: {i}, difference: {difference}, frequency: {frequency}' )
        if difference > max_frequency*sample_time*n_channels:
            down_channels.append(str(i))
        
    return down_channels
    
#####################
def main():
    
    get_stuck_channels()
    
if __name__ == '__main__':
  main()
