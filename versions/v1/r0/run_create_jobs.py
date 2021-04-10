import argparse as ap
from create_jobs import *
from tensorflow.keras.models import model_from_json

parser =  ap.ArgumentParser(description='Create Jobs parser control for zrad transfer')

parser.add_argument('--oldmodels', metavar = 'Old model files', nargs = '*', dest='list_old_models',
required = True, help = 'Old model directory path')

list_old_models = parser.parse_args().list_old_models

et_min, et_max = 0,0
eta_min, eta_max = 0,0

for et in range(eta_min,et_max+1):
  for eta in range(eta_min,eta_max+1):
        phase = 'et' + str(et) + '_eta' + str(eta)

        index = [ ( (phase in e) and ('.json' in e) and ('Tight' in e) ) for e in list_old_models ]
        array_old_models = np.array(list_old_models)
        std_old_json_model_path = array_old_models[index][0]
        json_file = open(std_old_json_model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        #Loading weigths into model
        model.load_weights(std_old_json_model_path[:-5] + ".h5", 'r')

        
