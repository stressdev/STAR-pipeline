#!/bin/bash
#SBATCH --job-name=fmriprep
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
#SBATCH --time=00-64:30:30
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --partition=ncf


SUBJECT=$1
VERSION=20.0.7

cd /mnt/stressdevlab/STAR

singularity run --cleanenv -B /mnt/stressdevlab/STAR /mnt/stressdevlab/scripts/Containers/fmriprep-${VERSION}.simg/ --ignore slicetiming --participant-label ${SUBJECT} -vvv --nthreads 4 -w ${SCRATCH}/fmriprep-${VERSION}-test2/${SUBJECT} --return-all-components --fd-spike-threshold 0.5 --fs-license-file /mnt/stressdevlab/STAR/derivatives/license.txt --fs-subjects-dir /mnt/stressdevlab/STAR/derivatives/fmriprep-${VERSION}/freesurfer --cifti-output 91k --output-spaces MNI152NLin6Asym:res-2 MNI152NLin2009cAsym fsnative MNIPediatricAsym:cohort-1:res-2 --skip-bids-validation /mnt/stressdevlab/STAR /mnt/stressdevlab/STAR/derivatives/fmriprep-${VERSION} participant

