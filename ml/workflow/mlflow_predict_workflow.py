import subprocess
import os
import time

from ml.ml_functions.serve.mlflow_model_serve import mlflow_model_prediction

working_directory = "/home/erik/DataspellProjects/stock-prediction/ml/ml_functions/"

#mlflow.server._run_server(host="0.0.0.0", port=5000)
command = "mlflow server --host 0.0.0.0 --port 5000"

#process = subprocess.Popen(command, shell=True, cwd=working_directory)

mlflow_model_prediction()

time.sleep(10)
#process.terminate()
#%%
