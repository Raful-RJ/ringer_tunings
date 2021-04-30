#!/usr/bin/env python

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
  raw = load(path)
  data = raw['data']
  target = raw['target']
  target[target!=1]=-1
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
  target[target!=1]=-1

  data = norm1(data[:,1:101])
  
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

  targets = [   ('t2calo_tight_cutbased' , 'T0HLTPhotonT2CaloTight'  ),
                ('t2calo_medium_cutbased', 'T0HLTPhotonT2CaloMedium' ),
                ('t2calo_loose_cutbased' , 'T0HLTPhotonT2CaloLoose'  ),
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


  from saphyra.decorators import Summary, Reference
  decorators = [Summary(), Reference(args.refFile, targets)]

  from sklearn.model_selection import StratifiedKFold
  from saphyra.callbacks import sp
  from saphyra import BinaryClassificationJob
  from saphyra import PatternGenerator

  # Create the panda job

  def plot_nn_histograms( context ): 
    x_val, y_val = context.getHandler("valData") 
    model = context.getHandler( "model" ) 
    history = context.getHandler( "history" ) 
    threshold = history['reference']['rlx30_hlt_loose_cutbased']['threshold_val']
    y_pred_val = model.predict( x_val ) 
    sgn_pred_val =  y_pred_val[y_val==1] 
    bkg_pred_val =  y_pred_val[y_val==-1] 
    import matplotlib.pyplot as plt
    plt.hist(sgn_pred_val, color='blue', bins=50, alpha=0.5)
    plt.hist(bkg_pred_val, color='red', bins = 50,alpha=0.5)
    plt.xlabel(str(threshold))
    plt.yscale('log')
    plt.savefig('hist_tunning_medium.png')


  from tensorflow.keras.models import Sequential
  from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten

  # model = Sequential()
  # model.add(Dense(2, input_shape=(100,), activation='tanh'))
  # model.add(Dense(1, activation='linear'))
  # model.add(Activation('tanh'))
  # from tensorflow.keras import layers
  # import tensorflow as tf
  # input = layers.Input(shape=(100,), name = 'Input') # 0
  # input_reshape = layers.Reshape((100,1), name='Reshape_layer')(input)
  # conv = layers.Conv1D(4, kernel_size = 2, activation='relu', name = 'conv1d_layer_1')(input_reshape) # 1
  # conv = layers.Conv1D(8, kernel_size = 2, activation='relu', name = 'conv1d_layer_2')(conv) # 2
  # conv = layers.Flatten(name='flatten')(conv) # 3
  # dense = layers.Dense(16, activation='relu', name='dense_layer')(conv) # 4
  # dense = layers.Dense(1,activation='linear', name='output_for_inference')(dense) # 5
  # output = layers.Activation('sigmoid', name='output_for_training')(dense) # 6
  # model = tf.keras.Model(input, output, name = "model")

  job = BinaryClassificationJob(
                      PatternGenerator( args.dataFile, getPatterns ),
                      StratifiedKFold(n_splits=10, random_state=512, shuffle=True),
                      job               = args.configFile,
                      # sorts             = [0],
                      # inits             = 1,
                      loss              = 'mse',
                      metrics           = ['accuracy'],
                      epochs            = 5000,
                      callbacks         = [sp(patience=25, verbose=True, save_the_best=True)],
                      outputFile        = outputFile,                   
                      # class_weight      = True,
                      # plots             = [plot_nn_histograms],
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
