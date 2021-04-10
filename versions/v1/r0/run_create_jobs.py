import argparse as ap
import numpy as np
from saphyra import *
from tensorflow.keras.models import Sequential, model_from_json

parser =  ap.ArgumentParser(description='Create Jobs parser control for zrad transfer')

parser.add_argument('--oldmodels', metavar = 'Old model files', nargs = '*', dest='list_old_models',
required = True, help = 'Old model directory path')

array_old_models = np.array([parser.parse_args().list_old_models])

et_min, et_max = 0,4
eta_min, eta_max = 0,3

for et in range(eta_min,et_max+1):
  for eta in range(eta_min,eta_max+1):
      phase = 'et_' + str(et) + '_eta' + str(eta)

      std_old_json_model_path = [(phase in e) and ('.json' in e) for e in array_old_models][0]

      json_file = open(std_old_json_model_path, 'r')
      loaded_model_json = json_file.read()
      json_file.close()
      model = model_from_json(loaded_model_json)
      #Loading weigths into model
      model.load_weights(std_old_json_model_path[:-5] + ".h5", 'r')

      print(model.summary())
