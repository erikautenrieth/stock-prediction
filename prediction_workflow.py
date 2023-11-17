from influxdb_manager import InfluxDBOperations
from model import model_prediction
from preprocessing import get_data

DEFAULT_MODEL = "runs:/5c036be77ea045228b58b4fa52821f65/model"

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