#!/bin/bash
#
# Purpose: Create jobs that download subject data from CBS central and create onsets.
# Usage: bash serial_subject_setup.sh <input file>
# Input: <input file> is the name of a text file with 1 CBS id per line.
# Details: It schedules jobs 20 mintues apart, because that's about how long it takes 
#          to donwload one subject. This may not be strictly necessary, but I've found
#          that other xnat databases may begin to reject requests if too many are made
#          at once.


set -axo pipefail
set -eu

filename="${1}"
list=($(cat ${filename}))
i=0
for cbs in ${list[@]}; do
	mins=$((i*20))
	ID=`echo $cbs | awk -F "_" '{print $3$4}'`
	if [ i == 0 ]; then
		begin="now"
	else
		begin="now+${mins}minutes"
	fi
	sbatch --begin="${begin}" -J "s${ID}-setup" subject_setup.sh ${cbs}
	i=$((i+1))
done
