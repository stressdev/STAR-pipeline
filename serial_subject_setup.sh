#!/bin/bash
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
