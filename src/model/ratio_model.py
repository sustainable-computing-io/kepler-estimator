import numpy as np
import pandas as pd

from common import load_model_by_json

class RatioModel():
    def __init__(self, model_name, model_file, features, fe_files):
        self.name = model_name
        self.features = features
        self.model = load_model_by_json(model_name, model_file)
        self.power_components = ['gpu', 'pkg'] # omit core, dram, uncore
    
    def get_power(self, request):
        msg = ""
        try:
            df = request.datapoint[self.features]
            if len(df) == 1:
                total_power = 0
                for component in self.power_components:
                    total_power += np.sum(getattr(request, '{}_power'.format(component)))
                return [total_power], msg
            sum_wl_stat = pd.DataFrame([df.sum().values], columns=df.columns, index=df.index)
            ratio_df = df.join(sum_wl_stat, rsuffix='_sum')
            output_df = pd.DataFrame()
            for component in self.power_components:
                for metric in self.features:
                    score_key = '{}_score'.format(component)
                    if metric not in self.model[score_key]:
                        continue
                    ratio_df[metric +'_{}_ratio'.format(component)] = ratio_df[metric]/ratio_df[metric+'_sum']*self.model[score_key][metric]
                sum_ratio_df = ratio_df[[col for col in ratio_df if '{}_ratio'.format(component) in col]].sum(axis=1)
                total_power = getattr(request, '{}_power'.format(component))
                output_df[component] = sum_ratio_df*total_power
            y = list(output_df.sum(axis=1).values.squeeze())
        except Exception as e:
            msg = '{}\n'.format(e)
            print(e)
            y = []
        return y, msg
