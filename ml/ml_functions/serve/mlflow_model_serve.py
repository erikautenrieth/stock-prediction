from ml.database.influxdb_manager import InfluxDBOperations
import mlflow

def mlflow_model_prediction(model=None):
    # mlflow server --host 0.0.0.0 --port 5000

    db = InfluxDBOperations()
    df, prediction_df = db.get_data_from_influx()

    logged_model = "runs:/5a62984791c945a1bae69cd36a1a23fb/model"

    if model: logged_model = model

    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db.save_prediction_to_influx(prediction_df)

    return prediction_df