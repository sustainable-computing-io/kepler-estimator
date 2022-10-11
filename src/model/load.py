import json
from common import load_metadata

from scikit_model import ScikitModel
from keras_model import KerasModel

# model wrapper
MODELCLASS = {
    'scikit': ScikitModel,
    'keras': KerasModel,
}

class Model():
    def __init__(self, model_class, model_name, output_type, model_file, features, fe_files=[],\
            mae=None, mse=None, mae_val=None, mse_val=None, \
            abs_model=None, abs_mae=None, abs_mae_val=None, abs_mse=None, abs_mse_val=None, abs_max_corr=None, \
            reconstructed_mae=None, reconstructed_mse=None, avg_mae=None):
        self.model_name = model_name
        self.dyn_model = MODELCLASS[model_class](model_name, output_type, model_file, features, fe_files)
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
        for attrb, val in filters.items():
            if attrb == 'features':
                if not self.feature_check(val):
                    return False
            else:
                if not hasattr(self, attrb) or getattr(self, attrb) is None:
                    print('{} has no {}'.format(self.model_name, attrb))
                else:
                    cmp_val = getattr(self, attrb)
                    val = float(val)
                    if attrb == 'abs_max_corr': # higher is better
                        valid = cmp_val >= val
                    else: # lower is better
                        valid = cmp_val <= val
                    if not valid:
                        return False
        return True

    def feature_check(self, features):
        invalid_features = [f for f in self.dyn_model.features if f not in features]
        return len(invalid_features) == 0


def load_model(output_type):
    metadata = load_metadata(output_type)
    if metadata is not None:
        metadata_str = json.dumps(metadata)
        try: 
            model = json.loads(metadata_str, object_hook = lambda d : Model(**d))
            return model
        except Exception as e:
            print("fail to load: ", e)
            return None
    print("no metadata")
    return None
