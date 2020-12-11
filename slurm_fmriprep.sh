#!/bin/bash
#SBATCH --job-name=fmriprep
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
#SBATCH --time=02-00:30:30
#SBATCH -n 1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --partition=ncf


SUBJECT=$1
VERSION=20.1.1

cd /mnt/stressdevlab/STAR

#Make working directory 
mkdir -p /ncf/mclaughlin/STAR_fmriprep_tmp_jcf/${SUBJECT}


#Main singularity command
singularity run --cleanenv -B /ncf/mclaughlin/STAR_fmriprep_tmp_jcf/${SUBJECT}:/work -B /mnt/stressdevlab/STAR /mnt/stressdevlab/scripts/Containers/fmriprep-${VERSION}.simg/ --ignore slicetiming --participant-label ${SUBJECT} -vvv --omp-nthreads 4 --nthreads 6 -w /work --return-all-components --fd-spike-threshold 0.5 --fs-license-file /mnt/stressdevlab/STAR/derivatives/license.txt --fs-subjects-dir /mnt/stressdevlab/STAR/derivatives/fmriprep-${VERSION}/freesurfer --cifti-output 91k --output-spaces MNI152NLin6Asym:res-2 MNI152NLin2009cAsym fsnative MNIPediatricAsym:cohort-1:res-2 --skip-bids-validation /mnt/stressdevlab/STAR /mnt/stressdevlab/STAR/derivatives/fmriprep-${VERSION} participant

