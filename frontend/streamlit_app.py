import streamlit as st
import yfinance as yf
import pandas as pd
import os
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

from charts import line_chart, candlestick_chart

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from ml.database.influxdb_manager import InfluxDBOperations

db = InfluxDBOperations()


## Test locally with:
# cd frontend
# streamlit run streamlit_app.py


def main():
    """
    Main function for the streamlit app.
    """
    st.set_page_config(
        page_title="Stock Price Trend Prediction",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("<h3 style='text-align: center; color: black;'>Stock Price (15-day-ahead) Trend Prediction</h3>",
                unsafe_allow_html=True)

    stock_symbol = ["^GSPC", "S&P500"]

    end_date = datetime.now()
    start_date = end_date - relativedelta(months=6)
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')
    data = yf.download(stock_symbol[0], start=start_date, end=end_date)

    if not data.empty:
        predictions = db.get_prediction_from_influx()
        predictions = predictions.dropna()
        predictions = predictions.drop_duplicates(subset=['Date'])

        candle_stick_plot = candlestick_chart(data, predictions, stock_symbol)
        line_chart_plot = line_chart(predictions, stock_symbol)

        # Plot the charts
        st.plotly_chart(candle_stick_plot)
        st.plotly_chart(line_chart_plot)

        # Table with model information
        model_info = predictions.drop("time", axis=1).drop_duplicates()
        model_info['Date'] = pd.to_datetime(model_info['Date']).dt.strftime('%Y-%m-%d')
        st.write("Model Information and Accuracy")
        st.table(model_info)

    else:
        st.write('No data available.')


if __name__ == '__main__':
    main()

# %%

# %%
