import plotly.graph_objs as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf


def candlestick_chart(data, predictions, stock_symbol):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])

    for index, row in predictions.iterrows():
        date = row['Date']
        target = row['Target']
        if date in data.index:
            fig.add_annotation(
                x=date,
                y=data.loc[date, 'Close'],
                text='↑' if target == 1 else '↓',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if target == 1 else 'red'
            )

    fig.update_layout(
        title=f'Stock Prediction for {stock_symbol[1]}',
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(step='all')
                ])
            ),
            type='date'
        ),
        xaxis_tickformat='%Y-%m-%d'
    )
    return fig


def line_chart(predictions, stock_symbol):
    months = 3
    end_date_linie = datetime.now()
    start_date_linie = end_date_linie - relativedelta(months=months)

    data_linie = yf.download(stock_symbol[0], start=start_date_linie.strftime('%Y-%m-%d'),
                             end=end_date_linie.strftime('%Y-%m-%d'))

    fig_linie = go.Figure(data=[go.Scatter(x=data_linie.index, y=data_linie['Close'], mode='lines')])

    arrow_count = 0  # Zählvariable für die Pfeile

    for index, row in predictions.iterrows():
        date = row['Date']
        target = row['Target']
        if date in data_linie.index:
            arrow_count += 1  # Pfeilnummer erhöhen
            # Pfeil hinzufügen mit Nummerierung
            fig_linie.add_annotation(
                x=date,
                y=data_linie.loc[date, 'Close'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='green' if target == 1 else 'red',
                text=str(arrow_count)  # Pfeilnummer als Text
            )
            date_str = date.split('T')[0]  # Trennt den String am 'T' und nimmt nur den Datumsanteil
            date = datetime.strptime(date_str, '%Y-%m-%d')
            # Datum 15 Tage in der Zukunft berechnen
            future_date = date + relativedelta(days=15)

            # Gestrichelte Linie hinzufügen
            if future_date in data_linie.index:
                closing_price_start = data_linie.loc[date, 'Close']
                closing_price_end = data_linie.loc[future_date, 'Close']
                price_diff = closing_price_end - closing_price_start

                line_color = 'green' if price_diff > 0 else 'red'
                price_diff_sign = '+' if price_diff > 0 else ''
                fig_linie.add_trace(go.Scatter(
                    x=[date, future_date],
                    y=[closing_price_start, closing_price_end],
                    mode='lines',
                    name=f'(Pfeil {arrow_count}) Diff: {price_diff_sign}{price_diff:.2f}',  # Nummerierung und Preisdifferenz
                    line=dict(color=line_color, dash='dot')
                ))

    fig_linie.update_layout(
        title=f'3-Month Chart for {stock_symbol[1]}',
        xaxis=dict(type='date'),
        yaxis_title='Closing Price',
        xaxis_tickformat='%Y-%m-%d'
    )

    return fig_linie