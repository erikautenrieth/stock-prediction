import streamlit as st
import yfinance as yf
import plotly.express as px

def main():
    st.title('Aktienkursvorhersage')

    symbol = "^GSPC"

    data = yf.download(symbol, start='2020-01-01', end='2023-01-01')
    if not data.empty:
        fig = px.line(data, x=data.index, y='Close', title=f'Aktienkurse für {symbol}')
        st.plotly_chart(fig)
    else:
        st.write('Keine Daten verfügbar.')

if __name__ == '__main__':
    main()
