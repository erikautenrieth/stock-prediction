import ray

from preprocessing import get_data
from influxdb_manager import InfluxDBOperations
from model import train_and_tune_extra_tree_model, log_to_mlflow, model_prediction


#ray.init()
ray.init("ray://localhost:10001") ## VM
#print(ray.cluster_resources())

db_operations = InfluxDBOperations()

sp500_data, last_day_df = get_data()

best_model, accuracy = ray.get(train_and_tune_extra_tree_model.remote(sp500_data))

model_path = log_to_mlflow(best_model, accuracy)

db_operations.save_to_influx(last_day_df=last_day_df, model_path=model_path)

prediction_df = model_prediction(db_operations)

print("Workflow erfolgreich durchgelaufen")