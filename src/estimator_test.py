#########################
# estimator_test.py
# 
# This file covers the following cases.
# - kepler-model-server is connected
#   - list all available models with its corresponding available feature groups and make a dummy PowerRequest
# - kepler-model-server is not connected, but some achived models can be download via URL.
#   - set sample model and make a dummy valid PowerRequest and another invalid PowerRequest
#
#########################

import os
import shutil
import enum

os.environ['MODEL_SERVER_URL'] = 'localhost'

from estimator import handle_request, get_output_path, loaded_model, PowerRequest
from model_server_connector import ModelOutputType, list_all_models
from archived_model import get_achived_model
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

class FeatureGroup(enum.Enum):
   Full = 1
   WorkloadOnly = 2
   CounterOnly = 3
   CgroupOnly = 4
   BPFOnly = 5
   KubeletOnly = 6
   Unknown = 99

def sort_features(features):
    sorted_features = features.copy()
    sorted_features.sort()
    return sorted_features

FeatureGroups = {
    FeatureGroup.Full: sort_features(WORKLOAD_FEATURES + SYSTEM_FEATURES),
    FeatureGroup.WorkloadOnly: sort_features(WORKLOAD_FEATURES),
    FeatureGroup.CounterOnly: sort_features(COUNTER_FEAUTRES),
    FeatureGroup.CgroupOnly: sort_features(CGROUP_FEATURES + IO_FEATURES),
    FeatureGroup.BPFOnly: sort_features(BPF_FEATURES),
    FeatureGroup.KubeletOnly: sort_features(KUBELET_FEATURES)
}

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
    # test getting model from server
    available_models = list_all_models()
    for output_type_name, valid_fgs in available_models.items():
        if 'Weight' in output_type_name:
            continue
        output_type = ModelOutputType[output_type_name]
        output_path = get_output_path(output_type)
        for fg_name, best_model in valid_fgs.items():
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            if output_type.name in loaded_model:
                del loaded_model[output_type.name]
            metrics = FeatureGroups[FeatureGroup[fg_name]]
            request_json = generate_request(None, n=10, metrics=metrics, output_type=output_type_name)
            data = json.dumps(request_json)
            output = handle_request(data)
            assert len(output['powers']) > 0, "cannot get power {}\n {}".format(output['msg'], request_json)

    # test getting model from archived
    if len(available_models) == 0:
        output_type_name = 'DynPower'
        output_type = ModelOutputType[output_type_name]
        output_path = get_output_path(output_type)
        if output_type_name in loaded_model:
            del loaded_model[output_type_name]
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        # valid model
        os.environ[output_type_name] = "https://raw.githubusercontent.com/sustainable-computing-io/kepler-estimator/main/models/DynPower/CgroupOnly/ScikitMixed.zip"
        request_json = generate_request(None, n=10, metrics=FeatureGroups[FeatureGroup.CgroupOnly], output_type=output_type_name)
        data = json.dumps(request_json)
        output = handle_request(data)
        assert len(output['powers']) > 0, "cannot get power {}\n {}".format(output['msg'], request_json)
        del loaded_model[output_type_name]
        # invalid model
        os.environ[output_type_name] = "https://raw.githubusercontent.com/sustainable-computing-io/kepler-estimator/main/models/DynPower/Full/ScikitMixed.zip"
        request_json = generate_request(None, n=10, metrics=FeatureGroups[FeatureGroup.CgroupOnly], output_type=output_type_name)
        data = json.dumps(request_json)
        power_request = json.loads(data, object_hook = lambda d : PowerRequest(**d))
        output_path = get_achived_model(power_request)
        assert output_path is None, "model should be invalid\n {}".format(output_path)