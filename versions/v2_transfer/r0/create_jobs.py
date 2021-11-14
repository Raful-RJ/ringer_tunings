from saphyra import *
import argparse as ap
import numpy as np

# tensorflow
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras import layers, Model
from tensorflow import keras
#from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, Flatten

# function to define the keras model
def get_model(neuron_min, neuron_max, model):
  modelCol = []
  model.trainable = False
  for n in range(neuron_min,neuron_max+1):

    base_inputs = model.layers[0].input
    base_outputs = model.layers[-2].output
    inter_layer = layers.Dense(n,activation = 'tanh', name = 'second_hidden_layer')(base_outputs)                     
    final_dense_layer = layers.Dense(1, activation = 'linear', name = 'final_Dense_Layer')(inter_layer)
    final_outputs = layers.Activation('tanh', name='output_for_training')(final_dense_layer)
    new_model = keras.Model(inputs=base_inputs, outputs=final_outputs)
    new_model.layers[-2].trainable, new_model.layers[-3].trainable = True, True
    #new_model.trainable = False
    #new_model.layers[-3].trainable = True
    
    modelCol.append(new_model)
  return modelCol

parser =  ap.ArgumentParser(description='Create Jobs parser control for zrad transfer')

##Creating arg to select folder in which the pretrained models are
parser.add_argument('--oldmodels', metavar = 'Old model files', nargs = '*', dest='list_old_models',
required = True, help = 'Old model directory path')

list_old_models = parser.parse_args().list_old_models
print(len(list_old_models))

et_min, et_max = 0,4
eta_min, eta_max = 0,3
n_min_neuron = 2
n_max_neuron = 10

for et in range(eta_min,et_max+1):
  for eta in range(eta_min,eta_max+1):
        phase = 'et' + str(et) + '_eta' + str(eta)
        
        #Selecting model regarding the current phase space among the others in the folder
        index = [ ( (phase in e) and ('.json' in e) ) for e in list_old_models ]
        array_old_models = np.array(list_old_models)
        #Opening model
        std_old_json_model_path = array_old_models[index][0]
        json_file = open(std_old_json_model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        old_model = model_from_json(loaded_model_json)
        #Loading weigths into model
        old_model.load_weights(std_old_json_model_path[:-5] + ".h5", 'r')

        create_jobs( 
                models       = get_model(neuron_min=n_min_neuron,
                                        neuron_max=n_max_neuron,
                                        model = old_model),
                nInits        = 10,
                nInitsPerJob  = 1,
                sortBounds    = 10,
                nSortsPerJob  = 1,
                nModelsPerJob = 1,
                outputFolder  = phase + '.' + 'job_config.Zrad_transfer_v1.n2to5.10sorts.10inits.r0',
                )
