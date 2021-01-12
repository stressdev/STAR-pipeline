#!/bin/bash
#
#SBATCH -J xcpengine
#SBATCH --time=10:00:00
#SBATCH -n 1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=20G
#SBATCH -p ncf
#SBATCH --account=mclaughlin_lab
# Outputs ----------------------------------
#SBATCH -o %x-%A-%a.out
#SBATCH -e %x-%A-%a.err

# ------------------------------------------

SDL_DIR="/net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab"
BIDS_DIR="/mnt/stressdevlab/STAR"
#CONTAINER="${BIDS_DIR}/derivatives/xcpengine-latest.simg"
CONTAINER="/mnt/stressdevlab/scripts/Containers/xcpengine-1.2.3.simg"
ANTSPATH=${ANTSPATH}
SUBJECT=$1
SCANFILES=("sub-${SUBJECT}_task-rest_dir-ap_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz" "sub-${SUBJECT}_task-rest_dir-pa_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
COHORTFILE="${BIDS_DIR}/derivatives/ind_cohort_files/sub-${SUBJECT}.csv"

if [ ! -f "${COHORTFILE}" ]; then
	echo "id0,img" > ${COHORTFILE}
	for file in ${SCANFILES[@]}; do
		echo "sub-${SUBJECT},${BIDS_DIR}/derivatives/fmriprep-20.1.1/fmriprep/sub-${SUBJECT}/func/${file}" >> ${COHORTFILE}
	done
else
	echo "Cohort file exists: ${COHORTFILE}"
fi

cmd="singularity run --cleanenv -B /mnt/stressdevlab:/mnt/stressdevlab ${CONTAINER} -d ${BIDS_DIR}/derivatives/fc-36p.dsn -c ${COHORTFILE} -o ${BIDS_DIR}/derivatives/fmriprep-20.1.1/xcpengine -t 2 -r ${BIDS_DIR}/derivatives"



echo Running task ${SLURM_ARRAY_TASK_ID}
echo Cluster name: ${SLURM_CLUSTER_NAME}
echo CPUs per task: ${SLURM_CPUS_PER_TASK}
echo Memory: ${SLURM_MEM_PER_NODE}
echo Node name: ${SLURMD_NODENAME}
echo Commandline: $cmd
eval $cmd
exitcode=$?
