import pandas as pd
from influxdb_client_3 import InfluxDBClient3, Point
def save_to_influx(last_day_df, model_path):
    token = "nlg1Z5pTNYCdwYwK7jh1LV6lIoJAYnYdLpgZNNqBdLrnX4d8PnBNTJfBDNhtrc9_tzGiBLyJE4Zh4pEP5I45VQ=="
    org = "Dev Team"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    bucket = "data_to_predict"

    client = InfluxDBClient3(host=host,
                             token=token,
                             org=org)

    # os.environ['INFLUXDB_HOST']
    # os.environ['INFLUXDB_ORG']
    # os.environ['INFLUXDB_TOKEN']

    last_day_df['model'] = model_path
    last_day_df['Target'] = 999
    data = last_day_df.iloc[0].to_dict()
    data['Date'] = last_day_df.index[0].isoformat()

    point = Point("stock_data")
    for key, value in data.items():
        point = point.field(key, value)

    client.write(database=bucket, record=point)
    client.close()
    print("Complete. Return to the InfluxDB UI.")

def get_data_form_influx():
    from influxdb_client_3 import flight_client_options, InfluxDBClient3
    import certifi
    fh = open(certifi.where(), "r")
    cert = fh.read()
    fh.close()

    token = "nlg1Z5pTNYCdwYwK7jh1LV6lIoJAYnYdLpgZNNqBdLrnX4d8PnBNTJfBDNhtrc9_tzGiBLyJE4Zh4pEP5I45VQ=="
    org = "Dev Team"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    bucket = "data_to_predict"
    # os.environ['INFLUXDB_HOST']
    # os.environ['INFLUXDB_ORG']
    # os.environ['INFLUXDB_TOKEN']
    client = InfluxDBClient3(host=host,
                             token=token,
                             org=org,
                             flight_client_options=flight_client_options(tls_root_certs=cert),
                             database=bucket)

    query = """SELECT *
    FROM "stock_data"
    WHERE time > now() - 24h"""


    result = client.query(query=query, database=bucket, language="influxql")

    df = result.to_pandas().drop(["iox::measurement", "time"], axis=1)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    prediction_df = df[["Target", "model"]].copy()
    df.drop(["Target", "model"], axis=1, inplace=True)
    cols_list = ['Close', 'Volume', 'Rendite', 'SMA 10', 'EMA 10', 'EMA 20', 'WMA 10', 'Momentum 10', 'SAR', 'RSI', 'ROC', '%R', 'OBV', 'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'CCI', 'ADOSC', '%K', '%D']
    df = df[cols_list]

    return df.iloc[-1:], prediction_df.iloc[-1:]


def save_prediction_to_influx(prediction_df):
    token = "nlg1Z5pTNYCdwYwK7jh1LV6lIoJAYnYdLpgZNNqBdLrnX4d8PnBNTJfBDNhtrc9_tzGiBLyJE4Zh4pEP5I45VQ=="
    org = "Dev Team"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    bucket = "predictions"

    client = InfluxDBClient3(host=host,
                             token=token,
                             org=org)

    # os.environ['INFLUXDB_HOST']
    # os.environ['INFLUXDB_ORG']
    # os.environ['INFLUXDB_TOKEN']

    data = prediction_df.iloc[0].to_dict()
    data['Date'] = prediction_df.index[0].isoformat()
    point = Point("stock_predicts")
    for key, value in data.items():
        point = point.field(key, value)
    client.write(database=bucket, record=point)
    client.close()
    print("Complete. Return to the InfluxDB UI.")