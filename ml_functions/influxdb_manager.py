import pandas as pd
from influxdb_client_3 import InfluxDBClient3, Point, flight_client_options
import certifi

class InfluxDBOperations:
    def __init__(self):
        self.host = "https://us-east-1-1.aws.cloud2.influxdata.com" # os.environ['INFLUXDB_HOST']
        self.token = "nlg1Z5pTNYCdwYwK7jh1LV6lIoJAYnYdLpgZNNqBdLrnX4d8PnBNTJfBDNhtrc9_tzGiBLyJE4Zh4pEP5I45VQ==" # os.environ['INFLUXDB_TOKEN']
        self.org = "Dev Team" # os.environ['INFLUXDB_ORG']
        self.bucket = "data_to_predict"
        self.client = InfluxDBClient3(host=self.host, token=self.token, org=self.org)

    def save_to_influx(self, last_day_df, model_path):
        last_day_df['model'] = model_path
        last_day_df['Target'] = 999
        data = last_day_df.iloc[0].to_dict()
        data['Date'] = last_day_df.index[0].isoformat()

        point = Point("stock_data")
        for key, value in data.items():
            point = point.field(key, value)

        self.client.write(database=self.bucket, record=point)
        print("Complete. Return to the InfluxDB UI.")


    def get_data_from_influx(self):
        fh = open(certifi.where(), "r")
        cert = fh.read()
        fh.close()

        client = InfluxDBClient3(host=self.host,
                                 token=self.token,
                                 org=self.org,
                                 flight_client_options=flight_client_options(tls_root_certs=cert),
                                 database=self.bucket)

        query = """SELECT *
        FROM "stock_data"
        WHERE time > now() - 24h"""

        result = client.query(query=query, database=self.bucket, language="influxql")

        df = result.to_pandas().drop(["iox::measurement", "time"], axis=1)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        prediction_df = df[["Target", "model"]].copy()
        df.drop(["Target", "model"], axis=1, inplace=True)
        cols_list = ['Close', 'Volume', 'Rendite', 'SMA 10', 'EMA 10', 'EMA 20', 'WMA 10', 'Momentum 10', 'SAR', 'RSI', 'ROC', '%R', 'OBV', 'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'CCI', 'ADOSC', '%K', '%D']
        df = df[cols_list]

        return df.iloc[-1:], prediction_df.iloc[-1:]

    def save_prediction_to_influx(self, prediction_df):
        data = prediction_df.iloc[0].to_dict()
        data['Date'] = prediction_df.index[0].isoformat()
        point = Point("stock_predicts")
        for key, value in data.items():
            point = point.field(key, value)
        self.client.write(database="predictions", record=point)
        print("Complete. Return to the InfluxDB UI.")


    def __del__(self):
        self.client.close()
