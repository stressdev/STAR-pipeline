import pandas as pd
import os, sys
import yaxil
import subprocess
import glob as glob

def download_beh_file(sess,
                      uri,
                      out_dir='.',
                      overwrite=False,
                      **kwargs):
    rename_dict = {
        'CARIT_RUN1' : 'CARIT_Run_1',
        'CARIT_RUN2' : 'CARIT_Run_2',
        'EMOTION' : 'EMOTION_Run_1',
        'GUESSING_RUN1' : 'GUESSING_Run_1',
        'GUESSING_RUN2' : 'GUESSING_Run_2',
        'WORKING_MEMORY' : 'WM_Run_1'}
    basename = uri.split('files/')[-1]
    new_basename = rename_dict[basename.upper()]
    fname = os.path.join(out_dir, new_basename)
    dirname = os.path.dirname(fname)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    try:
        _, result = yaxil._get(
            sess._auth,
            uri,
            yaxil.Format.JSON,  # Format is ignored for _file_ downloads
            autobox=False)
    except RestApiError as err:
        # Empty responses are acceptable for some scripts and onset files
        if 'response is empty' in str(err):
            result = bytes('', 'utf8')
        else:
            raise

    with open(fname, 'wb') as f:
        print("Writing to " + fname)
        f.write(result)

auth = yaxil.auth(alias='cbscentral', cfg='~/.cbsauth')

## VARS

cbs_id = str(sys.argv[1])
print('Downloading ' + cbs_id)
redownload = False
if len(sys.argv) > 2 and str(sys.argv[3]) == 'redownload':
    redownload = True
    print("Redownloading is set. Will try to redownload the data even if directories already exist.")
subnum = cbs_id.split('_')[2]
session = cbs_id.split('_')[3]
bids_id = 'sub-' + subnum + session
source_dir = '/net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab/STAR/sourcedata/' + bids_id
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

## GET BEHAVIORAL DATA
with yaxil.session(auth) as sess:
  # get all subjects for given project
  for subject in sess.subjects(project='STAR_Study'):
        if subject[1] == 'STAR_' + subnum:
            for experiment in sess.experiments(subject=subject):
                if experiment[1] == cbs_id :
                    _, response = yaxil._get(sess._auth, experiment.uri + '/files', yaxil.Format.JSON)
                    file_list = [res for res in response['ResultSet']['Result'] if res['collection'] == 'behavioral_task_data']
                    for fileinfo in file_list:
                        fileinfo['uri'] = fileinfo.pop('URI')
                        download_beh_file(sess, out_dir = source_dir + '/behavioral_files', **fileinfo)


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
        if not os.path.isdir(dicom_dir):
            os.makedirs(dicom_dir)
            sess.download(cbs_id, scan_ids = [sid], out_dir = dicom_dir, progress=True)
        else:
            print("Directory already exists.")
            if redownload:
                print("Re-downloading anyway!")
                sess.download(cbs_id, scan_ids = [sid], out_dir = dicom_dir, progress=True)
            else:
                print("Skipping!")
        
        if modality == 'func':
            ofile = source_dir + '/' + modality + '/' + bids_id + '_task-' + task + '_dir-' + str(direction) + '_run-' + str(run)  + '_' + scan_type
        elif modality == 'dwi':
            ofile = source_dir + '/' + modality + '/' + bids_id + '_dir-' + str(direction) + '_run-' + str(run) + '_' + scan_type
        
        cmd = ['dcm2niix', '-s', 'y', '-b', 'y', '-z', 'y', '-f', os.path.basename(ofile),'-o',os.path.dirname(ofile), dicom_dir]
        cmds += [' '.join(cmd)]
        #subprocess.check_call(' '.join(cmd), shell = True)
        
        run += 1

#SAVE COMMANDS FOR COPYING FREESURFER MORPHOMETRICS DIR
fs_dir = '/mnt/stressdevlab/STAR/derivatives/fmriprep-20.1.1/freesurfer'
morpho_dir = glob.glob('/ncf/nrg/pipelines/CBSCentral/Morphometrics3/STAR_Study/' + cbs_id + '/*/morphometrics')[0]
cmds += [' '.join(['mkdir','-p',fs_dir + '/temp-' + bids_id])]
cmds += [' '.join(['cp','-r',morpho_dir,fs_dir + '/temp-' + bids_id + '/'])]

mv_cmd = """
file1="{file1}"
file2_chk="{file2_chk}"
file2="{file2}"
if [ ! -e ${{file1}} ]
then
    echo >&2 There is no file ${{file1}}
else 
    if [ ! -e ${{file2_chk}} ] && [ ! -L ${{file2_chk}} ]
    then
        mv ${{file1}} ${{file2}}
    else 
        echo >&2 There is already a file ${{file2}}.
    fi
fi
""".format(file1=fs_dir + '/temp-' + bids_id + '/morphometrics', 
           file2_chk=fs_dir + '/' + bids_id + '/morphometrics',
           file2=fs_dir + '/' + bids_id) 

cmds += [mv_cmd]
cmds += [' '.join(['mri_convert',fs_dir + '/' + bids_id + '/mri/T1.mgz', source_dir + '/anat/' + bids_id + '_T1w.nii.gz'])]

#WRITE COMMANDS OUT TO FILE
with open(outcmds, 'w') as ofile:
    for cmd in cmds:
        ofile.write(cmd + '\n')


