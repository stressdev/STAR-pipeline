import pandas as pd
import os, sys
import yaxil
import subprocess
import glob as glob

auth = yaxil.XnatAuth(cfg='~/.xnat_auth')

## VARS
cbs_id = str(sys.argv[1])
subnum = cbs_id.split('_')[2]
session = cbs_id.split('_')[3]
bids_id = 'sub-' + subnum + session
source_dir = '/mnt/stressdevlab/STAR/sourcedata/' + bids_id
#source_dir = bids_id
outcmds = source_dir + '/' + bids_id + '_conv_cmds.txt'
outyaml = source_dir + '/' + bids_id + '.yaml'
outdf = source_dir + '/' + bids_id + '.csv'

#MAKE SOURCE DIR
for dirname in ['func', 'anat', 'dwi', 'fmap']:
    if not os.path.exists(source_dir + '/' + dirname):
        os.makedirs(source_dir + '/' + dirname)

## USING YAXIL TO GET SCANS FROM CBS
all_scan_data = []
with yaxil.session(auth) as sess:
  # get all subjects for given project
  for subject in sess.subjects(project='STAR_Study'):
        if subject[1] == 'STAR_' + subnum:
            for experiment in sess.experiments(subject=subject):
                if experiment[1] == cbs_id :
                    for scan in sess.scans(experiment=experiment):
                        all_scan_data += [pd.DataFrame.from_dict(scan, orient = 'index')]
df = pd.concat(all_scan_data, axis = 1).T
df['scan_num'] = pd.to_numeric(df['id'])
df.sort_values('scan_num')
df.to_csv(outdf, header = True, index = False, sep = ',')


## MAKING CUSTOM YAML FOR YAXIL 
scan_types = {
    'rfMRI_REST_AP': ('func', 'ap', 'rest', 'bold'),
    'rfMRI_REST_PA': ('func', 'pa', 'rest', 'bold'),
    'tfMRI_CARIT_AP': ('func', 'ap', 'carit', 'bold'),
    'tfMRI_CARIT_PA': ('func', 'pa', 'carit', 'bold'),
    'tfMRI_EMOTION_PA': ('func', 'pa', 'emotion', 'bold'),
    'tfMRI_GUESSING_AP': ('func', 'ap', 'guessing', 'bold'),
    'tfMRI_GUESSING_PA': ('func', 'pa', 'guessing', 'bold'),
    'tfMRI_WM_PA': ('func', 'pa', 'wm', 'bold'),
    'tfMRI_CARIT_AP_SBRef': ('func', 'ap', 'carit', 'sbref'),
    'tfMRI_GUESSING_AP_SBRef': ('func', 'ap', 'guessing', 'sbref'),
    'tfMRI_WM_PA_SBRef': ('func', 'pa', 'wm', 'sbref'),
    'rfMRI_REST_AP_SBRef': ('func','ap', 'rest', 'sbref'),
    'tfMRI_CARIT_PA_SBRef': ('func', 'pa', 'carit', 'sbref'),
    'tfMRI_EMOTION_PA_SBRef': ('func', 'pa', 'emotion', 'sbref'),
    'rfMRI_REST_PA_SBRef': ('func', 'pa', 'rest', 'sbref'),
    'tfMRI_GUESSING_PA_SBRef': ('func', 'pa', 'guessing', 'sbref'),
    'dMRI_2mm_S3_b0_PA_SBRef': ('dwi', 'pa', 'sbref'), 
    'dMRI_2mm_S3_b0_PA': ('dwi', 'pa', 'dwi'),
    'dMRI_2mm_S3_ABCD102_AP': ('dwi', 'ap', 'dwi'),
    'dMRI_2mm_S3_ABCD102_AP_SBRef': ('dwi', 'ap', 'sbref')
  }

cmds = []

for scan_name, scan_data in scan_types.items():
    temp = df[df['series_description'] == scan_name]
    
    if 'fMRI' in scan_name:
        modality, direction, task, scan_type = scan_data
    elif 'dMRI' in scan_name:
        modality, direction, scan_type = scan_data
    
    run = 1
    for row in temp.iterrows():
        sid = row[1]['id']
        dicom_dir = source_dir + '/' + row[1]['id']
        print(dicom_dir)
        os.makedirs(dicom_dir)
        sess.download(cbs_id, scan_ids = [sid], out_dir = dicom_dir)
        
        if modality == 'func':
            ofile = source_dir + '/' + modality + '/' + bids_id + '_task-' + task + '_dir-' + str(direction) + '_run-' + str(run)  + '_' + scan_type
        elif modality == 'dwi':
            ofile = source_dir + '/' + modality + '/' + bids_id + '_dir-' + str(direction) + '_run-' + str(run) + '_' + scan_type
        
        cmd = ['dcm2niix', '-s', 'y', '-b', 'y', '-z', 'y', '-f', os.path.basename(ofile),'-o',os.path.dirname(ofile), dicom_dir]
        cmds += [' '.join(cmd)]
        #subprocess.check_call(' '.join(cmd), shell = True)
        
        run += 1

#SAVE COMMANDS FOR COPYING FREESURFER MORPHOMETRICS DIR
fs_dir = '/mnt/stressdevlab/STAR/derivatives/fmriprep-20.0.7/freesurfer'
morpho_dir = glob.glob('/ncf/nrg/pipelines/CBSCentral/Morphometrics3/STAR_Study/' + cbs_id + '/*/morphometrics')[0]
cmds += [' '.join(['mkdir','-p',fs_dir + '/temp-' + bids_id])]
cmds += [' '.join(['cp','-r',morpho_dir,fs_dir + '/temp-' + bids_id + '/'])]
cmds += [' '.join(['mv',fs_dir + '/temp-' + bids_id + '/morphometrics', fs_dir + '/' + bids_id])]
cmds += [' '.join(['mri_convert',fs_dir + '/' + bids_id + '/mri/T1.mgz', source_dir + '/anat/' + bids_id + '_T1w.nii.gz'])]

#WRITE COMMANDS OUT TO FILE
with open(outcmds, 'w') as ofile:
    for cmd in cmds:
        ofile.write(cmd + '\n')


