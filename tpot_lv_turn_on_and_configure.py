#!/usr/bin/env python3
import subprocess
import re
import argparse

from lvcontrol_hp import *
from tpot_lv_util import *

#######################
def get_down_channels():
    # get FEE link status from ebdc39
    result = subprocess.run( ['ssh', 'ebdc39', '-x', '/home/phnxrc/operations/TPOT/tpot_daq_interface/get_rx_ready.py'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    rx_ready = re.findall( "(0|1)", output )

    # these are TPOT links
    fee_list = [0, 1, 5, 6, 7, 8, 9, 12, 14, 15, 18, 19, 21, 23, 24, 25]
    
    # check which links are down (rx_ready = 0)
    down_channels = []
    for i, row in enumerate(rx_ready):
        if i in fee_list and not eval(row):
            down_channels.append(str(i))

    return down_channels

#######################
def resynchronize_clocks():
    # run the tpot_gtm_fee_init script, on ebdc39
    print( 'synchronizing FEE clocks' )
    result = subprocess.run( ['ssh', 'ebdc39', '-x', '/home/phnxrc/operations/TPOT/tpot_daq_interface/tpot_gtm_fee_init.sh'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    print( output )


#######################
def configure_all_fee():

    print( 'configuring all FEE' )

    fee_init_command = '/home/phnxrc/operations/TPOT/tpot_daq_interface/tpot_fee_init.py'
    result = subprocess.run( [fee_init_command], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    print( output )

#####################
def main():

    parser = argparse.ArgumentParser(
        prog = 'tpot_lv_turn_on_and_configure',
        description = 'Turn ON all TPOT FEE and configure',
        epilog = '')
    parser.add_argument('-f', '--force', action='store_true', help='do not ask for confirmation')
    args = parser.parse_args()

    # check if channels are not already on
    if not get_down_channels():
        exit(0)
    
    # ask for confirmation
    print( f'this will turn ON all TPOT FEE, and configure them. ' )
    if not args.force:
        reply = input('confirm (y/n) ? ')
        if reply != 'y' and reply != 'yes':
            exit(0)

    ### turn on all FEE
    result = subprocess.run( ['/home/phnxrc/operations/TPOT/tpot_lv_interface/tpot_lv_on.py', 'all'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    print( output )

    ### make three attempts at recovering all links
    for i in range(0,3):
        down_channels = get_down_channels()

        # find matching lv channels
        channel_dict = parse_arguments( down_channels )
        for crate in sorted(channel_dict.keys()):
            digital_slots = sorted(channel_dict[crate]['digital_slots'])
            analog_slots = sorted(channel_dict[crate]['analog_slots'])
            channels = sorted(channel_dict[crate]['channels'])

            # print crate, slots, channels, controller
            print('crate: ',crate,
                  ' digital slots: ',digital_slots,
                  ' analog slots: ', analog_slots,
                  ' channels: ',channels)
            controller = ip[crate]
            print('controller: ',controller)

            # turn OFF
            print( 'turning off LV' )
            tn = lv_connect(controller)
            for slot in analog_slots+digital_slots:
                lv_disable_channels(tn,slot,channels)
                time.sleep(1)

            time.sleep(1)

            # turn ON
            print( 'turning back on' )
            for slot in digital_slots:
                lv_enable_channels(tn,slot,channels)
                time.sleep(1)
            
            time.sleep(10)
            for slot in analog_slots:
                lv_enable_channels(tn,slot,channels)
                time.sleep(1)
            
            # disconnect
            lv_disconnect(tn)

            # update down channels and stop here if none is found
            down_channels = get_down_channels()
            if not down_channels:
                break

    # get list of channels that could not be recovered
    down_channels = get_down_channels()
    if down_channels:
        print( 'Not all channels could be recovered: ', down_channels )

    # need to re-synchronize all clocks
    resynchronize_clocks()

    # and re-initialize
    configure_all_fee()

    print( 'Done' )

if __name__ == '__main__':
  main()
