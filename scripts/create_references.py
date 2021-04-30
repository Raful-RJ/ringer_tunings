#!/usr/bin/env python

# from saphyra import PandasJob, sp, PreProcChain_v1, Norm1, Summary, PileupFit, ReshapeToConv1D
from saphyra import sp, Summary
from Gaugi.messenger import LoggingLevel, Logger
from Gaugi import load
import argparse
import sys,os
import numpy as np

path = '/home/juan.marin/datasets/npz/mc16_13TeV/allTruth_mc16e/*.npz'


from Gaugi import expandFolders
fileList = expandFolders(path)


ref_target = [
              #('tight_v8'       , 'T0HLTElectronRingerTight_v8'     ),
              #('medium_v8'      , 'T0HLTElectronRingerMedium_v8'    ),
              #('loose_v8'       , 'T0HLTElectronRingerLoose_v8'     ),
              #('vloose_v8'      , 'T0HLTElectronRingerVeryLoose_v8' ),
              #('tight_v6'       , 'T0HLTElectronRingerTight_v6'     ),
              #('medium_v6'      , 'T0HLTElectronRingerMedium_v6'    ),
              #('loose_v6'       , 'T0HLTElectronRingerLoose_v6'     ),
              #('vloose_v6'      , 'T0HLTElectronRingerVeryLoose_v6' ),
              ('t2calo_tight_cutbased' , 'T0HLTPhotonT2CaloTight'        ),
              ('t2calo_medium_cutbased', 'T0HLTPhotonT2CaloMedium'       ),
              ('t2calo_loose_cutbased' , 'T0HLTPhotonT2CaloLoose'        ),
              ('hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
              ('hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
              ('hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
              ('rlx20_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
              ('rlx20_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
              ('rlx20_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
              ('rlx30_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
              ('rlx30_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
              ('rlx30_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
              ('rlx40_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
              ('rlx40_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
              ('rlx40_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
              ('rlx50_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
              ('rlx50_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
              ('rlx50_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),

              ]



from saphyra import Reference_v1

for f in fileList:

  ff = f.split('/')[-1].replace('.npz','')+'.ref'
  obj = Reference_v1()
  raw = load(f)
  data = raw['data']
  target = raw['target']
  features=raw['features']

  sgnData = data[target==1]
  bkgData = data[target!=1]

  featIndex = np.where(features=='mc_type')[0][0]
  s = []
  b = []
  for i in range(len(sgnData)):
    if sgnData[i,featIndex]==14 or sgnData[i,featIndex]==15 or sgnData[i,featIndex]==13:
      s.append(sgnData[i,:])

  for i in range(len(bkgData)):
    if bkgData[i,featIndex]!=14 and bkgData[i,featIndex]!=15 and bkgData[i,featIndex]!=13:
      b.append(bkgData[i,:])
  
  s = np.asarray(s)
  b = np.asarray(b)
  data = np.concatenate((s,b),axis=0)
  target = np.concatenate((np.ones(len(s)), np.zeros(len(b))))  
  print (ff )
  etBins = raw["etBins"] 
  etaBins = raw["etaBins"  ] 
  etBinIdx = raw["etBinIdx" ] 
  etaBinIdx =raw["etaBinIdx"] 

  key = 'et%d_eta%d'%(etBinIdx,etaBinIdx)
  obj.setEtBins( etBins ) 
  obj.setEtaBins( etaBins ) 
  obj.setEtBinIdx( etBinIdx ) 
  obj.setEtaBinIdx( etBinIdx ) 

  for ref in ref_target:
    d = data[:,np.where(raw['features'] == ref[1])[0][0]]
    d_s = d[target==1]
    d_b = d[target!=1]
    if 'rlx' in ref[0]:
      factor = ref[0].replace('rlx','')
      factor = int(factor[0:factor.find('_')])
      id = ref[0].replace('rlx'+str(factor)+'_hlt_','')
      passedT2Calo = obj.getSgnPassed('t2calo_'+id)
      passedHLT = obj.getSgnPassed('hlt_'+id)
      deltaPassed = int((passedT2Calo - passedHLT)*factor/100)
      obj.addSgn( ref[0], ref[1], sum(d_s) + deltaPassed, len(d_s) )
      obj.addBkg( ref[0], ref[1], sum(d_b), len(d_b) )
    else:
      obj.addSgn( ref[0], ref[1], sum(d_s), len(d_s) )
      obj.addBkg( ref[0], ref[1], sum(d_b), len(d_b) )
  
  obj.save(ff)
