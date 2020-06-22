#!/bin/sh

CBS_ID=$1
SUBJECT=`echo $CBS_ID | awk -F "_" '{print "sub-"$3$4}'`
STAR_DIR="/mnt/stressdevlab/STAR"
STAR_SUB_DIR="${STAR_DIR}/${SUBJECT}"
SOURCE_SUB_DIR="${STAR_DIR}/sourcedata/${SUBJECT}"
echo $SUBJECT

#Activate py37
source activate py37

#Get scans from CBSCentral
python ${STAR_DIR}/derivatives/yaxildl.py ${CBS_ID}

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
python ${STAR_DIR}/derivatives/PrepFmap.py ${SUBJECT}

#Move fmap files
while read line ; do
    eval $line
done < ${STAR_SUB_DIR}/fmap_cmds.txt
    

