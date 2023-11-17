from influxdb_manager import InfluxDBOperations
from model import model_prediction
from preprocessing import get_data

DEFAULT_MODEL = "runs:/5c036be77ea045228b58b4fa52821f65/model"

db_operations = InfluxDBOperations()
sp500_data, last_day_df = get_data()
db_operations.save_to_influx(last_day_df=last_day_df, model_path=DEFAULT_MODEL)

prediction_df = model_prediction(db_operations)

print("Prediction wurde estellt. \n")
print(prediction_df)