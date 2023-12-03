import quandl
def calc_new_feature(df):
    # https://www.alphavantage.co/


    quandl.ApiConfig.api_key = 'Wy8ZWQS9rkyJKyuiVu4G'
    quandl.get('MULTPL/SP500_DIV_YIELD_MONTH',start_date='undefined',end_date='undefined')



    return df