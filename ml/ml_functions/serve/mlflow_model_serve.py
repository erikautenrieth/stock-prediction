from ml.database.influxdb_manager import InfluxDBOperations
import mlflow
import os
def mlflow_model_prediction(model=None):
    # mlflow server --host 0.0.0.0 --port 5001
    print(os.getcwd())
    db = InfluxDBOperations()
    df, prediction_df = db.get_data_from_influx()

    logged_model =  "runs:/50a4b51fd5614a9198c39e64e71b61b0/model"
    #logged_model = "/mlruns/372474618639634686/50a4b51fd5614a9198c39e64e71b61b0/artifacts/model"

    if model: logged_model = model

    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df)
    prediction_df["Target"] = prediction
    db.save_prediction_to_influx(prediction_df)
    print("Vorhersage wurde erstellt")

    return prediction_df