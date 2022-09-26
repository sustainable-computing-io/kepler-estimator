import requests
import enum
import os
import sys
import shutil
import json
import codecs
util_path = os.path.join(os.path.dirname(__file__), 'util')
sys.path.append(util_path)
from util.config import getConfig

class ModelOutputType(enum.Enum):
    AbsPower = 1
    AbsModelWeight = 2
    AbsComponentPower = 3
    AbsComponentModelWeight = 4
    DynPower = 5
    DynModelWeight = 6
    DynComponentPower = 7
    DynComponentModelWeight = 8

def is_weight_output(output_type):
    if output_type == ModelOutputType.AbsModelWeight:
        return True
    if output_type == ModelOutputType.AbsComponentModelWeight:
        return True
    if output_type == ModelOutputType.DynModelWeight:
        return True
    if output_type == ModelOutputType.DynComponentModelWeight:
        return True
    return False

def is_comp_output(output_type):
    if output_type == ModelOutputType.AbsComponentPower:
        return True
    if output_type == ModelOutputType.DynComponentPower:
        return True
    return False

MODEL_SERVER_URL = "kepler-model-server.monitoring.cluster.local"
MODEL_SERVER_URL = getConfig('MODEL_SERVER_URL', MODEL_SERVER_URL)

MODEL_SERVER_PORT = 8100
MODEL_SERVER_PORT = getConfig('MODEL_SERVER_PORT', MODEL_SERVER_PORT)
MODEL_SERVER_PORT = int(MODEL_SERVER_PORT)

def make_model_request(power_request):
    return {"metrics": power_request.metrics + power_request.system_features, "output_type": power_request.output_type, "filter": power_request.filter, "model_name": power_request.model_name}

TMP_FILE = 'tmp.zip'
DOWNLOAD_FOLDER = 'download'

def get_output_path(output_type):
    return os.path.join(os.path.dirname(__file__), DOWNLOAD_FOLDER, output_type.name)

def make_request(power_request):
    model_request = make_model_request(power_request)
    output_type = ModelOutputType[power_request.output_type]
    output_path = get_output_path(output_type)
    response = requests.post('http://{}:{}/model'.format(MODEL_SERVER_URL, MODEL_SERVER_PORT), json=model_request)
    if response.status_code != 200:
        return None
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    with codecs.open(TMP_FILE, 'wb') as f:
        f.write(response.content)
    shutil.unpack_archive(TMP_FILE, output_path)
    os.remove(TMP_FILE)
    return output_path

def list_all_models():
    response = requests.get('http://{}:{}/best-models'.format(MODEL_SERVER_URL, MODEL_SERVER_PORT))
    if response.status_code != 200:
        return None
    model_names = json.loads(response.content.decode("utf-8"))
    return model_names