#!/bin/bash
# ==============================================================
# The "Bade wants to sleep" script
# This script is supposed to go with a reconfiguration wizard.
# It starts with phase1_run() where it runs the usual local junk
# runs to check counts
# Then it takes the output from the monitoring status info and
# checks if any of the runs are outside of the tolerance
# If it is, then it reconfigures again and tries again
# for now, up to 3 times
# ==============================================================

set -euo pipefail

#Connect to ebdc39
#REMOTE_USER="phnxrc"
#REMOTE_HOST="ebdc39.sphenix.bnl.gov"
# I'm actually gonna just put these in a launcher
#echo "SSH-ing into ebdc39"
#ssh phnxrc@ebdc39.sphenix.bnl.gov

LOG_DIR="$HOME/operations/TPOT/logs"                                                                                                                                                                                     
mkdir -p "$LOG_DIR"                                                                                                                                                                                                             
STATUS_FILE="$HOME/operations/TPOT/logs/tpot_reconfig_status.txt"                                                                                                                                                               
TMP_STATUS="$HOME/operations/TPOT/logs/tpot_fee_status.out"                                                                                                                                                                      
TMP_SOF="$HOME/operations/TPOT/logs/tpot_fee_sof.out"                                                                                                                                                                        
LOGFILE="$LOG_DIR/tpot_reconfig_$(date +'%Y%m%d_%H%M%S').log"     


MAX_ITER=3

timestamp() { date +"[%Y-%m-%d %H:%M:%S]"; }

log() {
    echo "$(timestamp) $*" | tee -a "$LOGFILE"
}

report_failure() {
    local step="$1"
    local cmd="$2"
    log "Wizard failed at step $step: $cmd"
    echo "Wizard failed at step $step: $cmd" > "$STATUS_FILE"
    exit 1
}

trap 'report_failure $LINENO "$BASH_COMMAND"' ERR

phase1_run() {
    log "Starting Local RCDAQ Run"
    #bash /home/phnxrc/samfred/quickscripts/rc_setup_local.sh 12 ebdc39
    
    #log "Step 1: ebdc39_setup.sh"
    #sh ~/operations/TPOT/ebdc39_setup.sh x  >>"$LOGFILE" 2>&1
    RCDAQHOST=ebdc39 sh  /home/phnxrc/operations/TPOT/ebdc39_setup.sh x>>"$LOGFILE" 2>&1  
    
    log "Step 2: tpot_clock.sh"
    bash ~/operations/TPOT/tpot_clock.sh    >>"$LOGFILE" 2>&1

    log "Step 3: rc_setup.sh"
    #bash ~/operations/TPOT/rc_setup.sh      >>"$LOGFILE" 2>&1

    log "Step 4: daq_set_runtype junk"
    rc_client rc_set_runtype junk                    >>"$LOGFILE" 2>&1

    log "Step 5: rc_open"
    rc_client rc_open                                 >>"$LOGFILE" 2>&1

    log "Step 6: rc_begin"
    rc_client rc_begin                                >>"$LOGFILE" 2>&1

    log "Step 7: wait 10 seconds"
    sleep 10

    log "Step 8: rc_end"
    rc_client rc_end                                  >>"$LOGFILE" 2>&1

    log "Junk Run completed successfully."
}

phase2_verify() {
    log "Starting FEE RX SOF Verification"
    script -q -c "~/operations/TPOT/tpot_daq_interface/fee_status_local --region TPOT" "$TMP_STATUS" 2>>"$LOGFILE"

    #Taking the counts from the monitoring output
    #awk '/^[ 0-9]/ {print $3}' "$TMP_STATUS" > "$TMP_SOF"
    
    sed -i 's/\x1B\[[0-9;]*[a-zA-Z]//g' "$TMP_STATUS"
    awk '/Up/ {print $3}' "$TMP_STATUS" > "$TMP_SOF"
    
    
    local count
    count=$(wc -l < "$TMP_SOF")
    if [[ $count -eq 0 ]]; then
        log "No Rx SOF data found."
        return 1
    fi

    #Find the median, have a 1/8th tolerance and check that all the FEE are within the boundaries.This would for example mean 1/8 of detector missing.

    mapfile -t sorted < <(sort -n "$TMP_SOF")
    local count=${#sorted[@]}
    local median

    if (( count % 2 == 0 )); then
        local mid=$((count/2))
        median=$(echo "(${sorted[mid-1]} + ${sorted[mid]}) / 2" | bc -l)
    else
        local mid=$(((count+1)/2))
        median=${sorted[mid-1]}
    fi

    local tolerance
    tolerance=$(echo "$median / 8" | bc -l)

    log "Median Rx SOF: $median (tolerance ±$tolerance)"

    local failed=()
    local idx=0

    while read -r val; do
        diff=$(echo "$val - $median" | bc -l)
        absdiff=$(echo "${diff#-}")
        if (( $(echo "$absdiff > $tolerance" | bc -l) )); then
            failed+=("$idx")
        fi
        ((idx++))
    done < "$TMP_SOF"

    #FEE mapping)
    TPOT_FEES=(0 1 5 6 7 8 9 12 14 15 18 19 21 23 24 25)

    
    if (( ${#failed[@]} == 0 )); then
        log "All FEEs within tolerance."
        echo "Wizard status: SUCCESS | All FEEs preoperly configured." > "$STATUS_FILE"

	#Load the beam scheduler back in
	log "Executing standard_beam.scheduler"
        gl1_gtm_client gtm_load_modebits 12 /home/phnxrc/operations/TPOT/schedulers/standard_beam.scheduler >>"$LOGFILE" 2>&1 || log "gl1_gtm_client command failed. Run physics setup again"
        return 0
    else
	local fee_list=()
	for idx in "${failed[@]}"; do
            fee_list+=("${TPOT_FEES[$idx]}")
	done

	log "Misconfigured FEE numbers: ${fee_list[*]}"
	echo "Wizard status: Iteration $ITER | Out of tolerance FEEs: ${fee_list[*]}" > "$STATUS_FILE"
        log "Attempting to reinitialize FEEs: ${fee_list[*]}"

        /home/phnxrc/operations/TPOT/tpot_daq_interface/fee_init_local triggered_zsup --connect-tpot --pre-samples 76 --samples 25 --shape-gain 6 --thres 520 --thresvar /home/phnxrc/operations/TPOT/tpot_daq_interface/TPOT_thresholds.json --fee "${fee_list[@]}" --no-stream-enable >>"$LOGFILE" 2>&1

        log "FEE reinitialization complete."
        return 1
    fi
}

log "TPOT Reconfiguration Wizard started at $(timestamp)"

ITER=1
while (( ITER <= MAX_ITER )); do
    log "ITERATION $ITER of $MAX_ITER"

    phase1_run
    if phase2_verify; then
        log "Operation successful on iteration $ITER."
        exit 0
    fi

    log "Repeating configuration after recovery."
    ((ITER++))
done

log "Wizard reached maximum iterations ($MAX_ITER). Exiting with failure."
echo "Wizard status: FAILED | Max iterations reached." > "$STATUS_FILE"
exit 1
