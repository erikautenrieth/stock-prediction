import ray

from ml.features.preprocessing import get_data
from ml.ml_functions.model_train_extra_tree import train_and_tune_extra_tree_model
from ml.ml_functions.model_registry import log_to_mlflow

ray.init()
## ray.init("ray://localhost:10001") ## VM
#print(ray.cluster_resources())


stock_data, last_day_df = get_data()

best_model, accuracy = ray.get(train_and_tune_extra_tree_model.remote(stock_data))

model_path = log_to_mlflow(best_model, accuracy)





#prediction_df = model_prediction()
#print("Workflow erfolgreich durchgelaufen")