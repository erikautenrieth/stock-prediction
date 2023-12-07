import yfinance as yf
from datetime import datetime
from ml.database.influxdb_manager import InfluxDBOperations
from ml.features.new_features import extract_yahoo_data, calc_indicators

def get_data(stock_wkn="^GSPC", start_year="2000-08-01", save_data=False, new_model=None):
    # Add Stock
    stock_data = yf.download(stock_wkn, start=start_year, end=datetime.now().strftime('%Y-%m-%d'))

    # Add Target
    stock_data = calc_target(df=stock_data)

    # Add Indicators
    stock_data = calc_indicators(df=stock_data)

    # ADD NEW FEATURES
    stock_data = extract_yahoo_data(df=stock_data)

    stock_data['Volume'] = stock_data['Volume'].astype(float)

    # Filter Last Day
    last_day_df = stock_data.drop("Target", axis=1)
    last_day_df = last_day_df.tail(1)

    # Trainings Data
    stock_data = stock_data.iloc[:-10] # Drop last 10 days

    if save_data:
        db = InfluxDBOperations()
        db.save_to_influx(last_day_df=last_day_df, new_model=new_model)

        last_day = last_day_df.index[0].strftime('%Y-%m-%d')
        #last_day_df.to_csv(f'../data/training_data/sp500_predict_{last_day}.csv', index=True)
        #stock_data.to_csv(f'../data/training_data/sp500_training_data_to_{last_day}.csv', index=False)
        print("Saved Data to Influx and CSV")

    return stock_data, last_day_df

def calc_target(df):
    df['Target'] = (df['Close'].shift(-15) > df['Close']).astype(int)
    return df



def scale_data(train_x, test_x):
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    train_x = scaler.fit_transform(train_x)
    test_x = scaler.transform(test_x)
    return train_x, test_x