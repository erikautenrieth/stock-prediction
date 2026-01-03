import os
import boto3
import json

from dotenv import load_dotenv
from src.database.influxdb_manager import InfluxDBOperations

load_dotenv()
class SageMakerHandler:
    def __init__(self):
        self.app_name = os.getenv('SAGEMAKER_APP_NAME')
        self.region = os.getenv('SAGEMAKER_REGION')
        self.influxDB = InfluxDBOperations()
        boto3.setup_default_session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region
        )

    def query_endpoint(self, input_json):
        client = boto3.session.Session().client('sagemaker-runtime', self.region)
        response = client.invoke_endpoint(
            EndpointName=self.app_name,
            Body=input_json,
            ContentType='application/json'
        )
        preds = response['Body'].read().decode('ascii')
        preds = json.loads(preds)
        print('Received response: {}'.format(preds))
        return preds

    def get_data_and_predict(self):
        input_df, predict_df = self.influxDB.get_data_from_influx()

        # Bereitet die Daten für die SageMaker-Anfrage vor
        input_df.reset_index(drop=True, inplace=True)
        query_input = input_df.to_dict(orient='split')
        data = {"dataframe_split": query_input}
        byte_data = json.dumps(data).encode('utf-8')

        # Ruft den SageMaker-Endpoint auf und erhält Vorhersagen
        prediction = self.query_endpoint(byte_data)

        predict_df["Target"] = prediction["predictions"][0]
        self.influxDB.save_prediction_to_influx(predict_df)



