from datetime import datetime
import yfinance as yf
import pandas as pd
import talib as ta

def calc_indicators(df):
    # convert relevant columns to numpy arrays to satisfy TA-Lib API
    time_period = 10
    close = df['Close'].astype(float).to_numpy()
    high = df['High'].astype(float).to_numpy()
    low = df['Low'].astype(float).to_numpy()
    volume = df['Volume'].astype(float).to_numpy()

    # compute indicators (results are numpy arrays, assign back to dataframe)
    df[f"SMA {time_period}"] = ta.SMA(close, timeperiod=time_period)
    df[f"EMA {time_period}"] = ta.EMA(close, timeperiod=time_period)
    df[f"EMA {20}"] = ta.EMA(close, timeperiod=20)
    df[f"WMA {time_period}"] = ta.WMA(close, timeperiod=time_period)
    df[f"Momentum {time_period}"] = ta.MOM(close, timeperiod=time_period)
    df["SAR"] = ta.SAR(high, low, acceleration=0.02, maximum=0.2)
    df["RSI"] = ta.RSI(close, timeperiod=14)
    df["ROC"] = ta.ROC(close, timeperiod=10)
    df["%R"] = ta.WILLR(high, low, close, timeperiod=14)
    df["OBV"] = ta.OBV(close, volume)
    macd, macd_sig, macd_hist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    df["MACD"] = macd
    df["MACD_SIGNAL"] = macd_sig
    df["MACD_HIST"] = macd_hist
    df["CCI"] = ta.CCI(high, low, close, timeperiod=14)
    df["ADOSC"] = ta.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
    # simple percent K/D
    df["%K"] = (df['Close'] - df['Low']) * 100 / (df['High'] - df['Low'])
    df["%D"] = df['%K'].rolling(3).mean()


    df['+DMI'] = ta.PLUS_DI(high, low, close, timeperiod=14)
    df['-DMI'] = ta.MINUS_DI(high, low, close, timeperiod=14)
    df['ADX'] = ta.ADX(high, low, close, timeperiod=14)
    up_band, mid_band, low_band = ta.BBANDS(close, timeperiod=20)
    df['up_band'] = up_band
    df['mid_band'] = mid_band
    df['low_band'] = low_band

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