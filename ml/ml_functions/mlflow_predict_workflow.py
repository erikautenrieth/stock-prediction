import subprocess
import time
from ml.ml_functions.serve.mlflow_model_serve import mlflow_model_prediction

server_process = subprocess.Popen(["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"])
time.sleep(5)
mlflow_model_prediction()
time.sleep(10)
server_process.terminate()





# import mlflow.cli#working_directory = "/home/erik/DataspellProjects/stock-prediction/ml/ml_functions/"
# command = "mlflow server --host 0.0.0.0 --port 5000"
#process = subprocess.Popen(command, shell=True)  #, cwd=working_directory
#time.sleep(10)
#process.terminate()
# mlflow.cli.server(["--port", "5000"])
# mlflow_model_prediction()
# time.sleep(10)
