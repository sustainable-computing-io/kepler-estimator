import pickle
import keras
import json
import os

METADATA_FILENAME = 'metadata.json'
MODEL_FOLDER = os.path.join(os.path.dirname(__file__), 'init')
SCALER_FILENAME = 'scaler.pkl'

def transform_and_predict(model, request):
    msg = ""
    try:
        x_values = request.datapoint[model.features].values
        normalized_x = model.scaler.transform(x_values)
        for fe in model.fe_list:
            if fe is None:
                continue
            normalized_x = fe.transform(normalized_x)
        y = model.model.predict(normalized_x)
        y[y < 0] = 0
        y = list(y)
    except Exception as e:
        msg = '{}\n'.format(e)
        y = []
    return y, msg


###############################################
# load data

def _modelpath(model_name):
    return "{}/{}/".format(MODEL_FOLDER, model_name)

def load_metadata(model_name):
    metadata_file = _modelpath(model_name) + METADATA_FILENAME
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
    except Exception as e:
        print(e)
        return None
    return metadata

def load_model_by_pickle(model_name, model_filename):
    model_file = _modelpath(model_name) + model_filename
    try:
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print(e)
        return None
    return model

def load_model_by_keras(model_name, model_filename):
    model_file = _modelpath(model_name) + model_filename
    try:
        model = keras.models.load_model(model_file)
    except Exception as e:
        print(e)
        return None
    return model

def load_model_by_json(model_name, model_filename):
    model_file = _modelpath(model_name) + model_filename
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