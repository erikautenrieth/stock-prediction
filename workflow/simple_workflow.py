import pandas as pd
import mlflow

df = pd.read_csv("../data/sp500_predict_2023-11-15.csv")
df.set_index('Date', inplace=True)

DEFAULT_MODEL = "runs:/c413fe91b94f4a8db7492ffa6657a0f6/model"
loaded_model = mlflow.pyfunc.load_model(DEFAULT_MODEL)
prediction = loaded_model.predict(df)

print(prediction)