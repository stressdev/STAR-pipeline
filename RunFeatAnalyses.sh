#!/bin/bash
#SBATCH --job-name=star_feat
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
#SBATCH --time=00-24:30:30
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=ncf



SUBJECT=$1
DERIV_DIR="/mnt/stressdevlab/STAR/derivatives"
SUB_FEAT="${DERIV_DIR}/fmriprep-20.0.7/feat_analyses/sub-${SUBJECT}"

#CARIT
mkdir -p ${SUB_FEAT}/carit
for run in 1 2 ; do
    template=${DERIV_DIR}/FSF/CARIT_Run_${run}-template.fsf
    outfsf=${SUB_FEAT}/carit/CARIT_Run_${run}.fsf
    sed -e "s|SUBJECT|${SUBJECT}|g" -e "s|RUN|${run}|g" ${template} > ${outfsf}
    bash /mnt/stressdevlab/scripts/Preprocessing/CheckEmptyFiles.sh ${outfsf}
    feat ${outfsf}
done

#GUESSING
mkdir -p ${SUB_FEAT}/guessing
for run in 1 2; do
    template=${DERIV_DIR}/FSF/GUESSING_Run_${run}-template.fsf
    outfsf=${SUB_FEAT}/guessing/GUESSING_Run_${run}.fsf
    sed -e "s|SUBJECT|${SUBJECT}|g" -e "s|RUN|${run}|g" ${template} > ${outfsf}
    bash /mnt/stressdevlab/scripts/Preprocessing/CheckEmptyFiles.sh ${outfsf}
    feat ${outfsf}
done

#WM
mkdir -p ${SUB_FEAT}/wm
for run in 1; do
    template=${DERIV_DIR}/FSF/WM-template.fsf
    outfsf=${SUB_FEAT}/wm/WM_Run_${run}.fsf
    sed -e "s|SUBJECT|${SUBJECT}|g" -e "s|RUN|${run}|g" ${template} > ${outfsf}
    bash /mnt/stressdevlab/scripts/Preprocessing/CheckEmptyFiles.sh ${outfsf}
    feat ${outfsf}
done

#EMOTION
mkdir -p ${SUB_FEAT}/emotion
for run in 1; do
    template=${DERIV_DIR}/FSF/EMOTION-template.fsf
    outfsf=${SUB_FEAT}/emotion/EMOTION_Run_${run}.fsf
    sed -e "s|SUBJECT|${SUBJECT}|g" -e "s|RUN|${run}|g" ${template} > ${outfsf}
    bash /mnt/stressdevlab/scripts/Preprocessing/CheckEmptyFiles.sh ${outfsf}
    feat ${outfsf}
done

#
