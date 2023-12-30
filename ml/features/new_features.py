from datetime import datetime
import yfinance as yf
import pandas as pd
import talib as ta

def calc_indicators(df):
    inputs = df['Close']
    time_period = 10
    #df['Rendite'] = df['Close'].pct_change()
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


    df['+DMI'] = ta.PLUS_DI(df['High'],df['Low'],df['Close'],timeperiod=14)
    df['-DMI'] = ta.MINUS_DI(df['High'],df['Low'],df['Close'],timeperiod=14)
    df['ADX'] = ta.ADX(df['High'],df['Low'],df['Close'],timeperiod=14)
    df['up_band'], df['mid_band'], df['low_band'] = ta.BBANDS(df['Close'], timeperiod =20)

    df.dropna(inplace=True)
    df.drop(["High", "Low", "Adj Close", "Open"], axis=1, inplace=True)
    return df


def extract_yahoo_data(df):
    # https://www.alphavantage.co/

    combined_data = pd.DataFrame()

    tickers = ["GC=F", "CL=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "CNY=X", "^IXIC", "^DJI", "^RUT", "^FTSE", "^GDAXI",
               "^FCHI", "^N225", "^HSI", "^BSESN", "^MXX", "^AXJO", "^IBEX", "SI=F", "HG=F",  "CL=F", "NG=F","^TNX",
               "^IRX", "^FVX", "^TYX", "SPY", "EFA"]

    for ticker in tickers:
        data = yf.download(ticker, start="2000-08-01", end=datetime.now().strftime('%Y-%m-%d'))
        combined_data[f"{ticker} Close"] = data["Close"]

    combined_data.interpolate(method='polynomial', order=3, inplace=True, axis=0)
    combined_data.fillna(method='bfill', inplace=True)

    combined_data = df.merge(combined_data, left_index=True, right_index=True, how='left')
    combined_data.interpolate(method='polynomial', order=3, inplace=True, axis=0)
    combined_data.fillna(method='bfill', inplace=True)

    return combined_data



def get_quandl_data(df):
    import quandl
    quandl.ApiConfig.api_key = '' # load your api key from .env
    quandl.get('MULTPL/SP500_DIV_YIELD_MONTH',start_date='undefined',end_date='undefined')