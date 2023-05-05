#!/bin/env python3

import sys
import telnetlib
import sqlite3
import time
import os.path
import time
import re
from datetime import datetime
from array import array

# John Haggerty, BNL, 2020.09.16

PORT = 9760

ip = { '3A3-1':'10.20.34.126', 
       '3A3-2':'10.20.34.127', 
       '3A4-1':'10.20.34.128', 
       '3A4-2':'10.20.34.129', 
       '3C3-1':'10.20.34.130', 
       '3C3-2':'10.20.34.131', 
       '3C4-1':'10.20.34.132', 
       '3C4-2':'10.20.34.133' } 

def lv_connect(HOST):
    try:
        tn = telnetlib.Telnet(HOST,PORT)
    except Exception as ex:
        print(ex)
        print("cannot connect to controller... give up")
        sys.exit()

    return tn

def lv_disconnect(tn):
    tn.close()

def lv_readv(tn,slot):

    command = '$V'+f"{slot:02d}"
    tn.write(command.encode('ascii')+b"\n\r")
    x = tn.read_until(b'>')
#    print(x)
    
# the returned data look like this:
#    b'V01\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r0.000V\n\r'    
    line = x.decode('ascii')
# delete up to the V01 in above example
# re.DOTALL lets the match traverse \n and \r
#    line = re.sub('^.*?'+command[1:]+'\n\r', '', line, flags=re.DOTALL)
# remove some characters from the string that we don't need    
    line = line.replace('\n\r>', '')
    line = line.replace(',>', '')
    line = line.replace('\r', '')
    line = line.replace('V', '')
# split the string into strings of voltages    
    vstring = line.split(',')
# get rid of blanks if they're there
    try:
        vstring.remove('')
        vstring.remove(' ')
    except ValueError:
        pass
#    print(vstring)
# convert the voltages as strings to floats    
    voltages = [float(v) for v in vstring]
#    print('voltages: ',voltages)
    return voltages

def lv_readi(tn,slot):

    command = '$I'+f"{slot:02d}"
    tn.write(command.encode('ascii')+b"\n\r")
    x = tn.read_until(b">")
    line = x.decode('ascii')
# delete up to the V01 in above example
# re.DOTALL lets the match traverse \n and \r
#    line = re.sub('^.*?'+command[1:]+'\n\r', '', line, flags=re.DOTALL)
# remove some characters from the string that we don't need    
    line = line.replace('\n\r>', '')
    line = line.replace(',>', '')
    line = line.replace('\r', '')
    line = line.replace('A', '')
# split the string into strings of voltages    
    istring = line.split(',')
# get rid of blanks if they're there
    try:
        istring.remove('')
        istring.remove(' ')
    except ValueError:
        pass
# convert the voltages as strings to floats    
    currents = [float(i) for i in istring]
#    print('currents: ',currents)
    return currents

# returns bitwise or of which channels are on
def lv_readstatus(tn,slot):
    voltages=lv_readv(tn,slot)
    currents=lv_readi(tn,slot)
    mask=0
    for c in range(10):
        voltage=voltages[c]
        current=currents[c]
        if voltage>0.05 or current>0.05:
            mask=mask|(1<<c)
    return mask

def lv_enable(tn,slot,onoroff):

    if onoroff == 0:
        command = '$E'+f"{slot:02d}"+str('00')
    else:
        command = '$E'+f"{slot:02d}"+str('3FF')
         
    print(command)
    tn.write(command.encode('ascii')+b"\n\r")
    tn.read_until(b'>')

def lv_enable_channels(tn,slot,channels):
    mask = lv_readstatus(tn,slot)
    for c in range(10):
        if c in channels:
            mask = mask | (1<<c)
    command = '$E'+f'{slot:02d}'+f'{mask:03x}'    
    print(command)
    tn.write(command.encode('ascii')+b"\n\r")
    tn.read_until(b'>')

def lv_disable_channels(tn,slot,channels):
    mask = lv_readstatus(tn,slot)
    for c in range(10):
        if c in channels:
            mask = mask & ~(1<<c)
    command = '$E'+f'{slot:02d}'+f'{mask:03x}'    
    print(command)
    tn.write(command.encode('ascii')+b"\n\r")
    tn.read_until(b'>')

def lv_reset(tn):

    command = '$R'     
    print(command)
    tn.write(command.encode('ascii')+b"\n\r")

# main

def main():
    
    if len(sys.argv) == 1:
        slot = 1
        HOST = '10.20.34.125'
    if len(sys.argv) == 2:
        slot = int(sys.argv[1])
        HOST = '10.20.34.125'
    if len(sys.argv) == 3:
        slot = int(sys.argv[1])
        HOST = sys.argv[2]
       
    tn = lv_connect(HOST)   
    v = lv_readv(tn,slot)
    print(v)

if __name__ == "__main__":
    main()
