from ml.database.influxdb_manager import InfluxDBOperations

from ml.ml_functions.registry.model_registry import load_model_path

import mlflow
import os
def mlflow_model_prediction(model=None):
    # mlflow server --host 0.0.0.0 --port 5001
    print(os.getcwd())
    db = InfluxDBOperations()
    df, prediction_df = db.get_data_from_influx()

    run_id = load_model_path().split("/")[1] # "4df9743095004dd1ad96955ee05b9a34"

    logged_model = f"ml/models/mlartifacts/932838311827738885/{run_id}/artifacts/model"

    if model: logged_model = model

    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db.save_prediction_to_influx(prediction_df)
    print("Vorhersage wurde erstellt:", prediction)

    return prediction_df