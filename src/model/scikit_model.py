from common import transform_and_predict, load_model_by_pickle

class ScikitModel():
    def __init__(self, model_name, output_type, model_file, features, fe_files):
        self.name = model_name
        self.features = features
        self.output_type = output_type
        self.model = load_model_by_pickle(output_type, model_file)
        self.fe_list = []
        for fe_filename in fe_files:
            self.fe_list += [load_model_by_pickle(output_type, fe_filename)]

    def get_power(self, request):
        return transform_and_predict(self, request)