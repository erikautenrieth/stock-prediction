from ml.features.preprocessing import get_data

DEFAULT_MODEL = "runs:/c413fe91b94f4a8db7492ffa6657a0f6/model"

sp500_data, last_day_df = get_data(save_data=True)