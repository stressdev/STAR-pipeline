#!/bin/sh

module load Anaconda3/2019.10 python/3.7.7-fasrc01
module load centos6/0.0.1-fasrc01  ncf/1.0.0-fasrc01 dcm2niix/2019_09_04-ncf freesurfer/6.0.0-ncf fsl/6.0.2-ncf

CBS_ID=$1
SUBJECT=`echo $CBS_ID | awk -F "_" '{print "sub-"$3$4}'`
STAR_DIR="/mnt/stressdevlab/STAR"
STAR_SUB_DIR="${STAR_DIR}/${SUBJECT}"
SOURCE_SUB_DIR="${STAR_DIR}/sourcedata/${SUBJECT}"
echo $SUBJECT

#Activate py37
source activate star

#Get scans from CBSCentral
python ${STAR_DIR}/derivatives/yaxil_dl.py ${CBS_ID}

#Run commands outputted from yaxildl
cd ${SOURCE_SUB_DIR}
while read line; do
    eval $line
done < ${SUBJECT}_conv_cmds.txt
    
#Copy files to subject directory
mkdir -p ${STAR_SUB_DIR}
for d in func dwi anat; do
    cp -r ${d}/ ${STAR_SUB_DIR}/
done

#Prep fmap files
python ${STAR_DIR}/derivatives/prep_fmap.py ${SUBJECT}

#Move fmap files
while read line ; do
    eval $line
done < ${STAR_SUB_DIR}/fmap_cmds.txt
    

