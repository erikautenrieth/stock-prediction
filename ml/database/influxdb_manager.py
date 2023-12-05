import certifi
import os
import pandas as pd
from influxdb_client_3 import InfluxDBClient3, Point, flight_client_options
from dotenv import load_dotenv
load_dotenv()

class InfluxDBOperations:
    def __init__(self):
        fh = open(certifi.where(), "r")
        cert = fh.read()
        fh.close()

        self.host = os.getenv('INFLUXDB_HOST')
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.org = os.getenv('INFLUXDB_ORG')
        self.bucket = "data_to_predict"
        self.client = InfluxDBClient3(host=self.host, token=self.token, org=self.org,
                                      flight_client_options=flight_client_options(tls_root_certs=cert))

    def save_to_influx(self, last_day_df, new_model=None):
        if new_model:
            last_day_df['model'] = new_model[0]
            last_day_df['accuracy'] = new_model[1]
        else:
            last_day_df['model'] = "ExtraTreesClassifier"
            last_day_df['accuracy'] = 0.8477341389728097

        last_day_df['Volume'] = last_day_df['Volume'].astype(float)
        last_day_df['Target'] = 999
        data = last_day_df.iloc[0].to_dict()
        data['Date'] = last_day_df.index[0].isoformat()

        point = Point("stock_data")
        for key, value in data.items():
            point = point.field(key, value)

        self.client.write(database=self.bucket, record=point)
        print("Complete. Return to the InfluxDB UI.")


    def save_prediction_to_influx(self, prediction_df):
        data = prediction_df.iloc[0].to_dict()
        data['Date'] = prediction_df.index[0].isoformat()
        point = Point("stock_predicts")
        for key, value in data.items():
            point = point.field(key, value)
        self.client.write(database="predictions", record=point)
        print("Complete. Return to the InfluxDB UI.")


    def get_data_from_influx(self):
        # client = InfluxDBClient3(host=self.host,
        #                          token=self.token,
        #                          org=self.org,
        #                          flight_client_options=flight_client_options(tls_root_certs=cert),
        #                          database=self.bucket)

        query = """SELECT *
        FROM "stock_data"
        WHERE time >= now() - 30d"""

        result = self.client.query(query=query, database=self.bucket, language="influxql")

        df = result.to_pandas().drop(["iox::measurement", "time"], axis=1)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        prediction_df = df[["Target", "model", "accuracy"]].copy()
        df.drop(["Target", "model"], axis=1, inplace=True)
        ## TODO schould be generic!!!!!
        #stock_data, last_day_df = get_data(save_data=False)
        #stock_data.drop(['Target'], axis=1).columns.to_list()
        cols_list = ['Close', 'Volume', 'SMA 10', 'EMA 10', 'EMA 20', 'WMA 10',
                     'Momentum 10', 'SAR', 'RSI', 'ROC', '%R', 'OBV', 'MACD', 'MACD_SIGNAL',
                     'MACD_HIST', 'CCI', 'ADOSC', '%K', '%D', '+DMI', '-DMI', 'ADX',
                     'up_band', 'mid_band', 'low_band', 'GC=F Close', 'CL=F Close',
                     'EURUSD=X Close', 'GBPUSD=X Close', 'JPY=X Close', 'CNY=X Close',
                     '^IXIC Close', '^DJI Close', '^RUT Close', '^FTSE Close',
                     '^GDAXI Close', '^FCHI Close', '^N225 Close', '^HSI Close',
                     '^BSESN Close', '^MXX Close', '^AXJO Close', '^IBEX Close',
                     'SI=F Close', 'HG=F Close', 'NG=F Close', '^TNX Close', '^IRX Close',
                     '^FVX Close', '^TYX Close', 'SPY Close', 'EFA Close']
        df = df[cols_list]

        return df.iloc[-1:], prediction_df.iloc[-1:]


    def get_prediction_from_influx(self):
        query = """SELECT *
        FROM "stock_predicts"
        WHERE time >= now() - 30d"""

        result = self.client.query(query=query, database="predictions", language="influxql")

        df = result.to_pandas().drop(["iox::measurement"], axis=1)
        return df
    def __del__(self):
        self.client.close()
