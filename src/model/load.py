import json
import pandas as pd
import os
from common import load_metadata, MODEL_FOLDER, SCALER_FILENAME

from scikit_model import ScikitModel
from keras_model import KerasModel
from ratio_model import RatioModel

# model wrapper
MODELCLASS = {
    'scikit': ScikitModel,
    'keras': KerasModel,
    'ratio': RatioModel
}

class Model():
    def __init__(self, model_class, model_name, model_file, features, fe_files=[],\
            mae=None, mse=None, mae_val=None, mse_val=None, \
            abs_model=None, abs_mae=None, abs_mae_val=None, abs_mse=None, abs_mse_val=None, abs_max_corr=None, \
            reconstructed_mae=None, reconstructed_mse=None, avg_mae=None):
        self.model_name = model_name
        self.dyn_model = MODELCLASS[model_class](model_name, model_file, features, fe_files)
        self.mae = mae
        self.mae_val = mae_val
        self.mse = mse
        self.mse_val = mse_val
        self.abs_model = abs_model
        self.abs_mae = abs_mae
        self.abs_mae_val = abs_mae_val
        self.abs_mse = abs_mse
        self.abs_mse_val = abs_mse_val
        self.abs_max_corr = abs_max_corr
        self.reconstructed_mae = reconstructed_mae
        self.reconstructed_mse = reconstructed_mse
        self.avg_mae = avg_mae

    def get_power(self, request):
        return self.dyn_model.get_power(request)

    def is_valid_model(self, filters):
        for filter in filters:
            attrb = filter['attr'] 
            val = filter['val']
            if attrb == 'features':
                if not self.feature_check(val):
                    return False
            else:
                try:
                    cmp_val = getattr(self, attrb)
                    if attrb == 'abs_max_corr': # higher is better
                        valid = cmp_val >= val
                    else: # lower is better
                        valid = cmp_val <= val
                    if not valid:
                        return False
                except:
                    continue
        return True

    def feature_check(self, features):
        invalid_features = [f for f in self.dyn_model.features if f not in features]
        return len(invalid_features) == 0


def init_model(model_name):
    metadata = load_metadata(model_name)
    if metadata is not None:
        metadata_str = json.dumps(metadata)
        try: 
            model = json.loads(metadata_str, object_hook = lambda d : Model(**d))
            return model
        except Exception as e:
            print(e)
            return None
    return None

def load_all_models(error_key):
    model_names = [f for f in os.listdir(MODEL_FOLDER) if not os.path.isfile(os.path.join(MODEL_FOLDER,f))]
    print("Load models:", model_names)
    items = []
    for model_name in model_names:
        model = init_model(model_name)
        if model is not None:
            item = model.__dict__
            item['name'] = model.model_name
            item['model'] = model
            items += [item]
    model_df = pd.DataFrame(items)
    available_err = [err for err in error_key if err in model_df.columns]
    model_df = model_df.sort_values(available_err)
    return model_df
