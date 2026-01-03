import mlflow

from src.database.influxdb_manager import InfluxDBOperations
from src.ml_functions.registry.model_registry import load_model_path, _set_mlflow_tracking


def mlflow_model_prediction(model=None):
    _set_mlflow_tracking()
    
    db = InfluxDBOperations()
    df, prediction_df = db.get_data_from_influx()

    model_uri = model if model else load_model_path()
    if not model_uri:
        raise RuntimeError("No model URI found. Train and register a model first.")

    loaded_model = mlflow.pyfunc.load_model(model_uri)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db.save_prediction_to_influx(prediction_df)
    print("Vorhersage wurde erstellt:", prediction)

    return prediction_df