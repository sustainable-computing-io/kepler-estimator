from common import transform_and_predict, load_model_by_pickle
from common import SCALER_FILENAME

class ScikitModel():
    def __init__(self, model_name, model_file, features, fe_files):
        self.name = model_name
        self.features = features
        self.scaler = load_model_by_pickle(model_name, SCALER_FILENAME)
        self.model = load_model_by_pickle(model_name, model_file)
        self.fe_list = []
        for fe_filename in fe_files:
            self.fe_list += [load_model_by_pickle(model_name, fe_filename)]

    def get_power(self, request):
        return transform_and_predict(self, request)