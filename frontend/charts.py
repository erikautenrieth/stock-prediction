from pygments.lexers import go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf


def line_chart(predictions, stock_symbol):
    months = 3

    end_date_linie = datetime.now()
    start_date_linie = end_date_linie - relativedelta(months=months)
    data_linie = yf.download(stock_symbol[0], start=start_date_linie.strftime('%Y-%m-%d'),
                             end=end_date_linie.strftime('%Y-%m-%d'))
    fig_linie = go.Figure(data=[go.Scatter(x=data_linie.index, y=data_linie['Close'], mode='lines')])
    for index, row in predictions.iterrows():
        date = row['Date']
        target = row['Target']
        if date in data_linie.index:
            fig_linie.add_annotation(
                x=date,
                y=data_linie.loc[date, 'Close'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if target == 1 else 'red'
            )
        fig_linie.update_layout(
            title=f'3-Month Line Chart for {stock_symbol[1]}',
            xaxis=dict(
                type='date'
            ),
            yaxis_title='Closing Price',
            xaxis_tickformat='%Y-%m-%d'
        )
    return fig_linie
