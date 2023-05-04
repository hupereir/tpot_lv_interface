#!/bin/env python3

# John Haggerty, BNL
# 2023-02-15

from lvcontrol_hp import *
import time
import argparse

CLI=argparse.ArgumentParser()

CLI.add_argument(
  "crate",
  type=str,
  choices = list( ip.keys() ),
  default='',
)

CLI.add_argument(
  "--slots",            # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",            # 0 or more values expected => creates a list
  type=int,
  default=range(1,16),    # default if nothing is provided
)

CLI.add_argument(
  "--channels",            # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",            # 0 or more values expected => creates a list
  type=int,
)

args = CLI.parse_args()
print('command line crate: ',args.crate,
      ' command line slots: ',args.slots,
      ' command line channel: ',args.channels)

controller = ip[ args.crate ]
print('controller: ',controller)

tn = lv_connect(controller)
for i in args.slots:
    lv_disable_channels(tn,i,args.channels)
    time.sleep(1)

lv_disconnect(tn)    
