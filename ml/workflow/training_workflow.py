import ray

from ml.features.preprocessing import get_data
from ml.functions.influxdb_manager import InfluxDBOperations
from ml.ml_functions.ml_model_extra_tree import train_and_tune_extra_tree_model, log_to_mlflow


ray.init()
## ray.init("ray://localhost:10001") ## VM
#print(ray.cluster_resources())


stock_data, last_day_df = get_data()

best_model, accuracy = ray.get(train_and_tune_extra_tree_model.remote(stock_data))

model_path = log_to_mlflow(best_model, accuracy)


## AWS Container
# mlflow sagemaker build-and-push-container --build --push -c for-sagemaker-deployment

## Deploy Model
# mlflow sagemaker deploy --app-name xformer -m runs:/7-16420961991120000000062/model
# --execution-role-arn arn:aws:iam::612652722220:role/role-for-mlflow-sagemaker-deploy
# --bucket jaganes-sagemaker
# --image-url 612652722220.dkr.ecr.us-east-1.amazonaws.com/for-sagemaker-deployment:1.22.0
# --region-name us-east-1
# --mode create
# --instance-type ml.m5.large
# --instance-count 1
# --flavor python_function


#prediction_df = model_prediction()
#print("Workflow erfolgreich durchgelaufen")