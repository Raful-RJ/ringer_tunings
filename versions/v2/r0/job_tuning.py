#!/usr/bin/env python

import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1" #(or "1" or "2")

try:
  from tensorflow.compat.v1 import ConfigProto
  from tensorflow.compat.v1 import InteractiveSession
  config = ConfigProto()
  config.gpu_options.allow_growth = True
  session = InteractiveSession(config=config)
except Exception as e:
  print(e)
  print("Not possible to set gpu allow growth")


def getPatterns( path, cv, sort):

  def norm1( data ):
      norms = np.abs( data.sum(axis=1) )
      norms[norms==0] = 1
      return data/norms[:,None]

  from Gaugi import load
  d = load(path)
  data = norm1(d['data'][:,1:101])
  target = d['target']
  target[target!=1]=-1
  splits = [(train_index, val_index) for train_index, val_index in cv.split(data,target)]

  x_train = data [ splits[sort][0]]
  y_train = target [ splits[sort][0] ]
  x_val = data [ splits[sort][1]]
  y_val = target [ splits[sort][1] ]

  return x_train, x_val, y_train, y_val, splits, []




def getPileup( path ):
  from Gaugi import load
  return load(path)['data'][:,0]


def getJobConfigId( path ):
  from Gaugi import load
  return dict(load(path))['id']


from Gaugi.messenger import LoggingLevel, Logger
from Gaugi import load
import numpy as np
import argparse
import sys,os


mainLogger = Logger.getModuleLogger("job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-c','--configFile', action='store',
        dest='configFile', required = True,
            help = "The job config file that will be used to configure the job (sort and init).")

parser.add_argument('-v','--volume', action='store',
        dest='volume', required = False, default = None,
            help = "The volume output.")


parser.add_argument('-d','--dataFile', action='store',
        dest='dataFile', required = False, default = None,
            help = "The data/target file used to train the model.")

parser.add_argument('-r','--refFile', action='store',
        dest='refFile', required = False, default = None,
            help = "The reference file.")


if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


try:

  job_id = getJobConfigId( args.configFile )

  outputFile = args.volume+'/tunedDiscr.jobID_%s'%str(job_id).zfill(4) if args.volume else 'test.jobId_%s'%str(job_id).zfill(4)

  targets = [
                ('tight_cutbased' , 'T0HLTPhotonT2CaloTight'  ),
                ('medium_cutbased', 'T0HLTPhotonT2CaloMedium' ),
                ('loose_cutbased' , 'T0HLTPhotonT2CaloLoose'  ),
                ('rlx75_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
                ('rlx75_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
                ('rlx75_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
                ('rlx80_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
                ('rlx80_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
                ('rlx80_hlt_loose_cutbased' , 'trig_EF_ph_loose'        ),
                ('rlx85_hlt_tight_cutbased' , 'trig_EF_ph_tight'        ),
                ('rlx85_hlt_medium_cutbased', 'trig_EF_ph_medium'       ),
                ('rlx85_hlt_loose_cutbased' , 'trig_EF_ph_loose'        )
                ]


  from saphyra.decorators import Summary, Reference
  decorators = [Summary(), Reference(args.refFile, targets)]

  from sklearn.model_selection import StratifiedKFold
  from saphyra.callbacks import sp
  from saphyra import BinaryClassificationJob
  from saphyra import PatternGenerator

  # Create the panda job
  job = BinaryClassificationJob(
                    PatternGenerator( args.dataFile, getPatterns ),
                    StratifiedKFold(n_splits=10, random_state=512, shuffle=True),
                    job               = args.configFile,
                    loss              = 'mean_squared_error',
                    metrics           = ['accuracy'],
                    epochs            = 5000,
                    callbacks         = [sp(patience=25, verbose=True, save_the_best=True)],
                    outputFile        = outputFile
                    )

  job.decorators += decorators
  # Run it!
  job.run()

  # necessary to work on orchestra
  from saphyra import lock_as_completed_job
  lock_as_completed_job(args.volume if args.volume else '.')
  sys.exit(0)

except  Exception as e:
  print(e)

  # necessary to work on orchestra
  from saphyra import lock_as_failed_job
  lock_as_failed_job(args.volume if args.volume else '.')

  sys.exit(1)
