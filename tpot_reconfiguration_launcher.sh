#!/bin/bash
echo "Running TPOT Reconfiguration Wizard on remote host ebdc39"
ssh -t phnxrc@ebdc39.sphenix.bnl.gov  "bash -l /home/phnxrc/operations/TPOT/tpot_lv_interface/tpot_reconfiguration_wizard.sh"  | tee -a /home/phnxrc/operations/TPOT/logs/tpot_remote_launch_$(date +%Y%m%d_%H%M%S).log
ssh_exit=${PIPESTATUS[0]}
if [[ $ssh_exit -ne 0 ]]; then
  echo "Reconfiguration failed. Call expert."
  exit 1
fi
echo "Remote reconfiguration complete. Connection closed."

