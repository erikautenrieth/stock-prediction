import yfinance as yf
from ml.features.preprocessing import calc_target, calc_indicators, scale_data


def setup_module():
    global sample_data
    sample_data = yf.download("AAPL", start="2019-01-01", end="2020-01-10")

def test_calc_target():
    df = calc_target(sample_data.copy())
    assert 'Target' in df.columns

def test_calc_indicators():
    df = calc_indicators(sample_data.copy())
    assert 'SMA 10' in df.columns
def test_scaling():
    df = calc_target(sample_data.copy())
    df = calc_indicators(df)
    original = df.copy()
    df_scaled = scale_data(df)
    assert original['Close'].mean() != df_scaled['Close'].mean()

def test_get_data():
    pass
