#!/bin/bash
set -axo pipefail
set +eu

echo "Loading modules..."
module load Anaconda3/2019.10 python/3.7.7-fasrc01
source activate star

set -eu

echo "Running scripts in OnsetScripts/"
for pyfile in `ls OnsetScripts/*py`; do
	echo "${pyfile} ${1};"	
	python ${pyfile} ${1}; 
done
