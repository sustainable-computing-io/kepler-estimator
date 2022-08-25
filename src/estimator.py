# predict.py <model name> <feature values>
# load model, scaler, and metadata from model folder ../data/model/<model name>
# apply scaler and model to metadata
import pandas as pd
import json
import os

import sys
import pandas as pd

fpath = os.path.join(os.path.dirname(__file__), 'model')
sys.path.append(fpath)
from model.load import load_all_models

SERVE_SOCKET = '/tmp/estimator.sock'

###############################################
# power request 

class PowerRequest():
    def __init__(self, metrics, values, model_name="", core_power=[], dram_power=[], uncore_power=[], pkg_power=[], gpu_power=[], filter=""):
        self.model_name = model_name
        self.datapoint = pd.DataFrame(values, columns=metrics)
        self.core_power = core_power
        self.dram_power = dram_power
        self.uncore_power = uncore_power
        self.pkg_power = pkg_power
        self.gpu_power = gpu_power
        self.filter = filter

###############################################
# serve

import sys
import socket
import signal

DEFAULT_ERROR_KEYS = ['avg_mae', 'mae']

def select_valid_model(model_df, features, filters):
    for index, row in model_df.iterrows():
        model = row['model']
        if model.is_valid_model(filters):
            if model.feature_check(features):
                return model
        model_df.drop(index, inplace=True)
    return None

def handle_request(model_df, data):
    try:
        power_request = json.loads(data, object_hook = lambda d : PowerRequest(**d))
    except Exception as e:
        msg = 'fail to handle request: {}'.format(e)
        return {"powers": [], "msg": msg}

    best_available_model = select_valid_model(model_df, power_request.datapoint.columns, power_request.filter)
    if power_request.model_name == "":
        model = best_available_model
    else:
        selected = model_df[model_df['name']==power_request.model_name]
        if len(selected) == 0:
            print('cannnot find model: {}, use best available model'.format(power_request.model_name))
            model = best_available_model
        else:
            model = selected.iloc[0]['model']
    if model is not None:
        print('Estimator model: ', model.model_name)
        powers, msg = model.get_power(power_request)
        return {"powers": powers, "msg": msg}
    else:
        return {"powers": [], "msg": "no model to apply"}

class EstimatorServer:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.model_df = load_all_models(DEFAULT_ERROR_KEYS)
    
    def start(self):
        s = self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(self.socket_path)
        s.listen(1)
        try:
            while True:
                connection, address = s.accept()
                self.accepted(connection, address)
        finally:
            try:
                os.remove(self.socket_path)
                sys.stdout.write("close socket\n")
            except:
                pass

    def accepted(self, connection, address):
        data = b''
        while True:
            shunk = connection.recv(1024).strip()
            data += shunk
            if shunk is None or shunk.decode()[-1] == '}':
                break
        decoded_data = data.decode()
        y = handle_request(self.model_df, decoded_data)
        response = json.dumps(y)
        connection.send(response.encode())

def clean_socket():
    print("clean socket")
    if os.path.exists(SERVE_SOCKET):
        os.unlink(SERVE_SOCKET)

def sig_handler(signum, frame) -> None:
    clean_socket()
    sys.exit(1)

import argparse

if __name__ == '__main__':
    clean_socket()
    signal.signal(signal.SIGTERM, sig_handler)
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--err',
                            required=False,
                            type=str,
                            default='mae', 
                            metavar="<error metric>",
                            help="Error metric for determining the model with minimum error value" )
        args = parser.parse_args()
        DEFAULT_ERROR_KEYS = args.err.split(',')
        server = EstimatorServer(SERVE_SOCKET)
        server.start()
    finally:
        clean_socket()