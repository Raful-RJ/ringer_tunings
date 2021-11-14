import os
import glob

from itertools import product

# define the paths into the container
data_path    = '/home/rafael.vianna/dataset/npz/offline_medium/merge/mc16_13TeV.sgn.ph_medium.gammajet.bkg.vetoph_loose.dijet_et%i_eta%i.npz'
ref_path     = '/home/rafael.vianna/tunings/versions/v2/referenceFiles/mc16_13TeV.sgn.ph_medium.gammajet.bkg.vetoph_loose.dijet_et%i_eta%i.ref.pic.gz'
config_path  = '/home/rafael.vianna/tunings/versions/v2/configFiles/et%i_eta%i.job_config.Zrad_transfer_v1.n2to5.10sorts.10inits.r0/*'
output_path  = '/home/rafael.vianna/tunings/versions/v2/output/mc16_13TeV.sgn.ph_medium.gammajet.bkg.vetoph_loose.dijet_et%i_eta%i'

# create a list of config files
#config_list  = glob.glob(config_path)
#print(config_list)

# loop over the bins
#list(product(range(3,5), range(0,4)))
for iet, ieta in [(0,0)]:
    print('Processing -> et: %i | eta: %i' %(iet, ieta))
    # format the names
    data_file = data_path %(iet, ieta)
    print('Data: ' + data_file)
    ref_file  = ref_path  %(iet, ieta)
    print('Ref: ' + ref_file)
    config_list = glob.glob(config_path %(iet, ieta))
    print('Config: ' + str(config_list))
    out_name  = output_path%(iet, ieta)
    print('Out: ' + out_name)

    # loop over the config files
    for iconfig in config_list:
        m_command = """python3 job_tuning.py -c {CONFIG} \\
                       -d {DATAIN} \\
                       -v {OUT} \\
                       -r {REF}""".format(CONFIG=iconfig, DATAIN=data_file, OUT=out_name, REF=ref_file)

        print(m_command)
        # execute the tuning
        
        os.system(m_command)