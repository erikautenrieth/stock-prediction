import yfinance as yf
import talib as ta

from datetime import datetime
from sklearn.preprocessing import StandardScaler
from ml.functions.influxdb_manager import InfluxDBOperations
from ml.features.new_features import calc_new_feature

def get_data(stock_wkn="^GSPC", start_year="1980-01-01", save_data=False):
    # Add Stock
    stock_data = yf.download(stock_wkn, start=start_year, end=datetime.now().strftime('%Y-%m-%d'))

    # Add Target
    stock_data = calc_target(df=stock_data)

    # Add Indicators
    stock_data = calc_indicators(df=stock_data)

    # ADD NEW FEATURES
    #stock_data = calc_new_feature(df=stock_data)

    # Add Scaling
    stock_data = scaling(df=stock_data)

    # Filter Last Day
    last_day_df = stock_data.drop("Target", axis=1)
    last_day_df = last_day_df.tail(1)

    # Trainings Data
    stock_data = stock_data.iloc[:-10] # Drop last 10 days

    if save_data:
        db = InfluxDBOperations()
        db.save_to_influx(last_day_df=last_day_df, model_path="Extra-Tree")

        #last_day = last_day_df.index[0].strftime('%Y-%m-%d')
        #last_day_df.to_csv(f'../data/sp500_predict_{last_day}.csv', index=True)
        #stock_data.to_csv(f'../data/sp500_training_data_to_{last_day}.csv', index=False)
        print("Saved Data to Influx and CSV")

    return stock_data, last_day_df

def calc_target(df):
    df['Target'] = (df['Close'].shift(-10) > df['Close']).astype(int)
    return df

def calc_indicators(df):
    inputs = df['Close']
    time_period = 10
    df['Rendite'] = df['Close'].pct_change()
    df = df.dropna()
    df[f"SMA {time_period}"] = ta.SMA(inputs, timeperiod=time_period)
    df[f"EMA {time_period}"] = ta.EMA(inputs, timeperiod=time_period)
    df[f"EMA {20}"] = ta.EMA(inputs, timeperiod=20)
    df[f"WMA {time_period}"] = ta.WMA(inputs, timeperiod=time_period)
    df[f"Momentum {time_period}"] = ta.MOM(inputs, timeperiod=time_period)
    df["SAR"] = ta.SAR(df["High"], df["Low"], acceleration=0.02, maximum=0.2)
    df["RSI"] = ta.RSI(df["Close"], timeperiod=14)
    df["ROC"] = ta.ROC(df["Close"], timeperiod=10)
    df["%R"] = ta.WILLR(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["OBV"] = ta.OBV(df["Close"], df["Volume"])
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = ta.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    df["CCI"] = ta.CCI(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["ADOSC"] = ta.ADOSC(df["High"], df["Low"], df["Close"], df["Volume"], fastperiod=3, slowperiod=10)
    df["%K"] = (df['Close'] - df['Low']) * 100 / (df['High'] - df['Low'])
    df["%D"] = df['%K'].rolling(3).mean()
    #df['Bollinger_hband'] = ta.volatility.bollinger_hband(df['Close'])
    #df['Bollinger_lband'] = ta.volatility.bollinger_lband(df['Close'])


    df.dropna(inplace=True)
    df.drop(["High", "Low", "Adj Close", "Open"], axis=1, inplace=True)
    return df

def scaling(df):
    target_column = df.pop('Target')
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    scaler = StandardScaler()
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
    df['Target'] = target_column
    return df



