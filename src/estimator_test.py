# to test only py part
# 

from estimator import handle_request, load_all_models, DEFAULT_ERROR_KEYS
import json

values =  [[0.0, 
            0.0,
            10261888.000000002,
            657541352.0,
            271351808.0,
            8672664.0,
            657541352.0,
            315585868416.0,
            797468706528.0,
            21.008000000000003]]

full_metrics = ['curr_bytes_read',
            'curr_bytes_writes',
            'curr_cache_miss',
            'curr_cgroupfs_cpu_usage_us',
            'curr_cgroupfs_memory_usage_bytes',
            'curr_cgroupfs_system_cpu_usage_us',
            'curr_cgroupfs_user_cpu_usage_us',
            'curr_cpu_cycles',
            'curr_cpu_instr',
            'curr_cpu_time']

cgroup_metrics = ['curr_cgroupfs_cpu_usage_us',
            'curr_cgroupfs_memory_usage_bytes',
            'curr_cgroupfs_system_cpu_usage_us',
            'curr_cgroupfs_user_cpu_usage_us']

power_dict = {
    'core_power': [10],
    'dram_power': [1],
    'uncore_power': [0],
    'gpu_power': [5],
    'pkg_power': [15],
    }

model_names = [None, 'GradientBoostingRegressor_10', 'Linear Regression_10', 'Polynomial Regression_10', 'CorrRatio']

def generate_request(model_name, n=1, metrics=full_metrics, power_on=True):
    request_json = dict() 
    if model_name is not None:
        request_json['model_name'] = model_name
    request_json['metrics'] = metrics
    request_json['values'] = [values[0][0:len(metrics)]]*n
    if power_on:
        request_json.update(power_dict)
    return request_json

if __name__ == '__main__':
    model_df = load_all_models(DEFAULT_ERROR_KEYS)
    init_len = len(model_df)
    for request_json in [generate_request(model_name, 10) for model_name in model_names]:
        data = json.dumps(request_json)
        output = handle_request(model_df, data)
        assert len(output['powers']) > 0, "cannot get power {}".format(output['msg'])
    cgrouponly_request = generate_request(None, metrics=cgroup_metrics, power_on=False)
    data = json.dumps(cgrouponly_request)
    output = handle_request(model_df, data)
    assert len(output['powers']) > 0, "cannot get power {}".format(output['msg'])
    assert len(model_df) < init_len, "some invalid model must be removed {}".format(model_df)