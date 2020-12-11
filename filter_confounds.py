import pandas as pd
import sys
import numpy as np
import glob

#ifile = 'sub-100301_task-wm_run-001_desc-confounds_regressors.tsv'
subject_id = str(sys.argv[1])
ifiles = glob.glob('/mnt/stressdevlab/STAR/derivatives/fmriprep-20.1.1/fmriprep/' + subject_id + '/func/' + subject_id + '*task*desc-confounds_regressors.tsv')

for ifile in ifiles:
    df = pd.read_csv(ifile, sep = '\t')
    df.reset_index(inplace = True)
    nine_params = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z', 'csf', 'white_matter', 'global_signal']
    df[nine_params].to_csv(ifile.replace('.tsv', '-9p.txt'), header = None, index = None, sep = ' ')

    #Get framewise displacement > 0.5
    fd_outliers = df[df['framewise_displacement'] > 0.5][['index','framewise_displacement']]
    fd_ofile = ifile.replace('confounds_regressors.tsv','fd_outliers_0pt5.txt')
    fd_outliers[['index']].to_csv(fd_ofile, index = False, header = False)

    #Get dvars outliers (> 75th percentile + (1.5 * IQR))
    dvars = [float(x) for x in df['dvars'].values[1:]]
    q25, q75 = np.percentile(dvars, 25), np.percentile(dvars, 75)
    iqr = q75 - q25
    cut_off = iqr * 1.5
    lower, upper = q25 - cut_off, q75 + cut_off
    dvars_outliers = df[df['dvars'] > upper][['dvars','index']]
    dvars_ofile = ifile.replace('confounds_regressors.tsv','dvars_outliers.txt')
    dvars_outliers[['index']].to_csv(dvars_ofile, index = False, header = False)

