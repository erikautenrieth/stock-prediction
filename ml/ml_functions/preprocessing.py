import yfinance as yf
import talib as ta
from datetime import datetime
from sklearn.preprocessing import StandardScaler
def get_data(stock_wkn="^GSPC"):
    # Install TaLIb:      https://cloudstrata.io/install-ta-lib-on-ubuntu-server/
    sp500_data = yf.download(stock_wkn, start="1980-01-01", end=datetime.now().strftime('%Y-%m-%d'))
    inputs = sp500_data['Close']
    time_period = 10
    sp500_data['Target'] = (sp500_data['Close'].shift(-10) > sp500_data['Close']).astype(int)
    sp500_data['Rendite'] = sp500_data['Close'].pct_change()
    sp500_data = sp500_data.dropna()
    sp500_data[f"SMA {time_period}"]      = ta.SMA(inputs, timeperiod = time_period)
    sp500_data[f"EMA {time_period}"]      = ta.EMA(inputs, timeperiod = time_period)
    sp500_data[f"EMA {20}"]               = ta.EMA(inputs, timeperiod = 20)
    sp500_data[f"WMA {time_period}"]      = ta.WMA(inputs, timeperiod = time_period)
    sp500_data[f"Momentum {time_period}"] = ta.MOM(inputs, timeperiod = time_period)
    sp500_data["SAR"] = ta.SAR(sp500_data["High"], sp500_data["Low"], acceleration=0.02, maximum=0.2)
    sp500_data["RSI"] = ta.RSI(sp500_data["Close"], timeperiod = 14)
    sp500_data["ROC"] = ta.ROC(sp500_data["Close"], timeperiod = 10) # On-Balance-Volume
    sp500_data["%R"]  = ta.WILLR(sp500_data["High"], sp500_data["Low"], sp500_data["Close"], timeperiod = 14)
    sp500_data["OBV"] = ta.OBV(sp500_data["Close"], sp500_data["Volume"])
    sp500_data["MACD"], sp500_data["MACD_SIGNAL"], sp500_data["MACD_HIST"] = ta.MACD(sp500_data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    sp500_data["CCI"] = ta.CCI(sp500_data["High"], sp500_data["Low"], sp500_data["Close"], timeperiod = 14)
    sp500_data["ADOSC"] = ta.ADOSC(sp500_data["High"], sp500_data["Low"], sp500_data["Close"], sp500_data["Volume"], fastperiod=3, slowperiod=10)
    sp500_data["%K"] = (sp500_data['Close'] - sp500_data['Low']) * 100 / (sp500_data['High'] - sp500_data['Low'])
    sp500_data["%D"] =  sp500_data['%K'].rolling(3).mean()
    sp500_data = sp500_data.dropna() #print("Anzahl der Zeilen mit mindestens einem NaN-Wert:", sp500_data.isna().any(axis=1).sum())
    sp500_data.drop(["High", "Low", "Adj Close", "Open"], axis=1, inplace=True)

    # Scaling
    target_column = sp500_data.pop('Target')
    numeric_columns = sp500_data.select_dtypes(include=['float64', 'int64']).columns
    scaler = StandardScaler()
    sp500_data[numeric_columns] = scaler.fit_transform(sp500_data[numeric_columns])
    sp500_data['Target'] = target_column

    # Filter last day
    last_day_df = sp500_data.drop("Target", axis=1)
    last_day_df = last_day_df.tail(1)
    last_day = last_day_df.index[0].strftime('%Y-%m-%d')
    last_day_df.to_csv(f'./data/sp500_predict_{last_day}.csv', index=True)

    # Save last day to influx
    yesterday_data = last_day_df.iloc[0].to_dict()
    yesterday_data['Date'] = last_day_df.index[0].isoformat()
    #save_to_influx(data=yesterday_data)

    # Save trainings data
    sp500_data = sp500_data.iloc[:-10] # Drop last 10 days
    sp500_data.to_csv(f'./data/sp500_training_data_to_{last_day}.csv', index=False)

    return sp500_data, last_day_df