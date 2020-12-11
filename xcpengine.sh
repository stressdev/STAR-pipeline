#!/bin/bash
#
#SBATCH -J xcpengine
#SBATCH --time=10:00:00
#SBATCH -n 1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=6G
#SBATCH -p ncf
#SBATCH --account=mclaughlin_lab
# Outputs ----------------------------------
#SBATCH -o /net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab/SEA_BIDS/derivatives/output/%x-%A-%a.out
#SBATCH -e /net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab/SEA_BIDS/derivatives/output/%x-%A-%a.err

# ------------------------------------------

SDL_DIR="/net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab"
BIDS_DIR="/mnt/stressdevlab/STAR"
#CONTAINER="${BIDS_DIR}/derivatives/xcpengine-latest.simg"
CONTAINER="/mnt/stressdevlab/scripts/Containers/xcpengine-081919.simg"
ANTSPATH=${ANTSPATH}
SUBJECT=$1

cmd="singularity run --cleanenv -B /mnt/stressdevlab:/mnt/stressdevlab ${CONTAINER} -d ${BIDS_DIR}/derivatives/fc-36p.dsn -c ${BIDS_DIR}/derivatives/ind_cohort_files/sub-${SLURM_ARRAY_TASK_ID}.csv -o ${BIDS_DIR}/derivatives/fmriprep-20.0.7/xcpengine -t 2 -r ${BIDS_DIR}/derivatives"



echo Running task ${SLURM_ARRAY_TASK_ID}
echo Cluster name: ${SLURM_CLUSTER_NAME}
echo CPUs per task: ${SLURM_CPUS_PER_TASK}
echo Memory: ${SLURM_MEM_PER_NODE}
echo Node name: ${SLURMD_NODENAME}
echo Commandline: $cmd
eval $cmd
exitcode=$?
