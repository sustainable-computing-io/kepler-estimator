import pickle
import keras
from keras import backend as K
import json
import os

METADATA_FILENAME = 'metadata.json'
MODEL_FOLDER = os.path.join(os.path.dirname(__file__), '../download')

def transform_and_predict(model, request):
    msg = ""
    try:
        x_values = request.datapoint[model.features].values
        for fe in model.fe_list:
            if fe is None:
                continue
            x_values = fe.transform(x_values)
        y = model.model.predict(x_values).squeeze()
        y[y < 0] = 0
        y = y.tolist()
    except Exception as e:
        msg = '{}\n'.format(e)
        y = []
    return y, msg


###############################################
# load data

def _modelpath(output_type):
    return "{}/{}/".format(MODEL_FOLDER, output_type)

def load_metadata(output_type):
    metadata_file = _modelpath(output_type) + METADATA_FILENAME
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
    except Exception as e:
        print(e)
        return None
    return metadata

def load_model_by_pickle(output_type, model_filename):
    model_file = _modelpath(output_type) + model_filename
    print(model_file)
    try:
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print("cannot load by pickle: ", e)
        return None
    return model


def coeff_determination(y_true, y_pred):
    SS_res =  K.sum(K.square( y_true-y_pred )) 
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) ) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )

def load_model_by_keras(output_type, model_filename):
    model_file = _modelpath(output_type) + model_filename
    try:
        model = keras.models.load_model(model_file, custom_objects={'coeff_determination': coeff_determination})
    except Exception as e:
        print(e)
        return None
    return model

def load_model_by_json(output_type, model_filename):
    model_file = _modelpath(output_type) + model_filename
    try:
        with open(model_file) as f:
            model = json.load(f)
    except Exception as e:
        print(e)
        return None
    return model

###############################################

FILTER_ITEM_DELIMIT = ';'
VALUE_DELIMIT = ':'
ARRAY_DELIMIT = ','

def parse_filters(filter):
    filter_list = filter.split(FILTER_ITEM_DELIMIT)
    filters = dict()
    for filter_item in filter_list:
        splits = filter_item.split(VALUE_DELIMIT)
        if len(splits) != 2:
            continue
        key = splits[0]
        if key == 'features':
            value = splits[1].split(ARRAY_DELIMIT)
        else:
            value = splits[1]
        filters[key] = value
    return filters 