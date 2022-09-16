# to test only py part
# 
import os
import shutil
os.environ['MODEL_SERVER_URL'] = 'localhost'

from estimator import handle_request, get_output_path, loaded_model
from model_server_connector import ModelOutputType
import json

SYSTEM_FEATURES = ["cpu_architecture"]

COUNTER_FEAUTRES = ["cache_miss", "cpu_cycles", "cpu_instr"]
CGROUP_FEATURES = ["cgroupfs_cpu_usage_us", "cgroupfs_memory_usage_bytes", "cgroupfs_system_cpu_usage_us", "cgroupfs_user_cpu_usage_us"]
IO_FEATURES = ["bytes_read", "bytes_writes"]
BPF_FEATURES = ["cpu_time"]
KUBELET_FEATURES =['container_cpu_usage_seconds_total', 'container_memory_working_set_bytes']
WORKLOAD_FEATURES = COUNTER_FEAUTRES + CGROUP_FEATURES + IO_FEATURES + BPF_FEATURES + KUBELET_FEATURES

NODE_STAT_POWER_LABEL = ["energy_in_pkg_joule", "energy_in_core_joule", "energy_in_dram_joule", "energy_in_uncore_joule", "energy_in_gpu_joule", "energy_in_other_joule"]

CATEGORICAL_LABEL_TO_VOCAB = {
                    "cpu_architecture": ["Sandy Bridge", "Ivy Bridge", "Haswell", "Broadwell", "Sky Lake", "Cascade Lake", "Coffee Lake", "Alder Lake"] 
                    }

FULL_FEATURES = WORKLOAD_FEATURES + SYSTEM_FEATURES

def generate_request(model_name, n=1, metrics=WORKLOAD_FEATURES, system_features=SYSTEM_FEATURES, output_type=ModelOutputType.AbsPower.name):
    request_json = dict() 
    if model_name is not None:
        request_json['model_name'] = model_name
    request_json['metrics'] = metrics
    request_json['system_features'] = system_features
    request_json['system_values'] = []
    for m in system_features:
        request_json['system_values'] += [CATEGORICAL_LABEL_TO_VOCAB[m][0]]
    request_json['values'] = [[1.0] *len(metrics)]*n
    request_json['output_type'] = output_type
    return request_json

if __name__ == '__main__':
    output_types = [ModelOutputType.AbsPower, ModelOutputType.AbsComponentPower, ModelOutputType.DynPower]
    for output_type in output_types:
        request_json = generate_request(None, n=10, output_type=output_type.name)
        data = json.dumps(request_json)
        output = handle_request(data)
        print(output)
        assert len(output['powers']) > 0, "cannot get power {}\n {}".format(output['msg'], request_json)
    
    output_types = [ModelOutputType.DynPower]
    for output_type in output_types:
        output_path = get_output_path(output_type)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        del loaded_model[output_type.name]
        request_json = generate_request(None, n=10, metrics=CGROUP_FEATURES + IO_FEATURES, output_type=output_type.name)
        data = json.dumps(request_json)
        output = handle_request(data)
        print(output)
        assert len(output['powers']) > 0, "cannot get power {}\n {}".format(output['msg'], request_json)
