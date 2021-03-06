#!/bin/bash
set -axo pipefail
set +eu

source PYTHON_MODULES.txt

set -eu

for i in `ls /mnt/stressdevlab/STAR/derivatives/fmriprep-20.1.1/fmriprep/sub-${1}/func/sub-${1}_task*desc-confounds_regressors.tsv`; do 
	echo "python filter_confounds.py ${i}"
	python filter_confounds.py ${i}  
done
