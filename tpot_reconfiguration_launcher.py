#!/usr/bin/env python3
import subprocess
import datetime
import sys
import os
#from lvcontrol_hp import *
#from tpot_lv_util import * 

def main():
    # Logging setup
    log_dir = "/home/phnxrc/operations/TPOT/logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"tpot_remote_launch_{timestamp}.log")

    print("Running TPOT Reconfiguration Wizard on remote host ebdc39")

    # SSH command to execute remote reconfiguration wizard
    cmd = [ "ssh", "phnxrc@ebdc39.sphenix.bnl.gov","-x", "bash -l /home/phnxrc/operations/TPOT/tpot_lv_interface/tpot_reconfiguration_wizard.sh"]

    process = subprocess.run( cmd, stdout=subprocess.PIPE)
    # Open the log file and run the SSH command, streaming output
    #with open(log_path, "a") as logfile:
        #process = subprocess.run( cmd, stdout=subprocess.PIPE) 

        # process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True )

        # Stream output to both console and logfile
        #for line in process.stdout.decode('utf8'):
        #    sys.stdout.write(line)
        #    logfile.write(line)
        #    logfile.flush()

        #process.wait()
        #ssh_exit = process.returncode

    ssh_exit = process.returncode
    
    # Handle exit status
    if ssh_exit != 0:
        msg = "Could not connect to ebdc39 or remote operation failed. Call expert."
        print(msg)
    #    with open(log_path, "a") as logfile:
    #        logfile.write(msg + "\n")
        sys.exit(1)

    print("Remote reconfiguration complete. Connection closed.")
    #with open(log_path, "a") as logfile:
     #   logfile.write("Remote reconfiguration complete. Connection closed.\n")


if __name__ == "__main__":
    main()
