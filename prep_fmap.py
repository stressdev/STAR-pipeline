import pandas as pd
import os, sys
import json
import glob as glob

sdl_path = '/net/holynfs01/srv/export/mclaughlin/share_root/stressdevlab'
star_dir = sdl_path + '/STAR'

direction_opp = {'ap': 'pa', 'pa': 'ap'}
cmds = []


subject = str(sys.argv[1])
subject_dir =  star_dir + '/' + str(subject)
fmap_dir = subject_dir + '/fmap'
if not os.path.exists(fmap_dir):
    os.makedirs(fmap_dir)

for func_image in glob.glob(subject_dir + '/func/*bold.nii.gz'):
    print(func_image)
    direction = func_image.split('/')[-1].split('_dir-')[1].split('_')[0]
    opp_func_image = func_image.replace(direction, direction_opp[direction])
    if os.path.exists(opp_func_image):
        #Make epi image
        epi_image = func_image.replace('bold', 'epi').replace('func','fmap')
        epi_json = epi_image.replace('.nii.gz', '.json')
        cmds += [[' '.join(['fslroi', func_image, epi_image, '0', '10'])]]
        
        
        #Get direction
        with open(func_image.replace('.nii.gz','.json')) as json_file:
            phase_encoding_dir = json.load(json_file)['PhaseEncodingDirection']
        
        #Write phase encoding direction and intendedfor to json
        epi_metadata = {}
        epi_metadata['IntendedFor'] = 'func/' + opp_func_image.split('/')[-1]
        epi_metadata['PhaseEncodingDirection'] = phase_encoding_dir
        json_object = json.dumps(epi_metadata)
        with open(epi_json, 'w') as outfile:
            outfile.write(json_object) 

#Save cmds to txt
pd.DataFrame.from_records(cmds).to_csv(subject_dir + '/fmap_cmds.txt', index = False, header = False)
        
