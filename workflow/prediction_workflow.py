from ml_functions.influxdb_manager import InfluxDBOperations
from ml_functions.model import model_prediction
from ml_functions.preprocessing import get_data

DEFAULT_MODEL = "runs:/c413fe91b94f4a8db7492ffa6657a0f6/model"

def model_prediction(db_operations):
    import mlflow

    df, prediction_df = db_operations.get_data_from_influx()
    logged_model = prediction_df["model"].iloc[0]
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db_operations.save_prediction_to_influx(prediction_df)

    return  prediction_df


db_operations = InfluxDBOperations()
sp500_data, last_day_df = get_data()
db_operations.save_to_influx(last_day_df=last_day_df, model_path=DEFAULT_MODEL)

prediction_df = model_prediction(db_operations)

print("Prediction wurde estellt. \n")
print(prediction_df)