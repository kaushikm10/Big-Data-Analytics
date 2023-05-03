import psycopg2
import yfinance as yf
import pickle
from tensorflow.keras.models import load_model
import sklearn
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import datetime


date_ = datetime.datetime.strftime((datetime.datetime.today() + datetime.timedelta(days=1)), "%Y-%m-%d")

tickers = pickle.load(open("model/tickers.pkl", "rb"))
tickers_map = {ticker: i for i, ticker in enumerate(tickers)}
model = load_model("model/prediction_model.h5")
scalers = pickle.load(open("model/scalers.pkl", "rb"))

try:
    conn = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432",
        database="stock_data"
    )
    cursor = conn.cursor()

    print("Connected")
except:
    print("Not Connected")


tickers_map = {ticker: i for i, ticker in enumerate(tickers)}
for ticker in tickers:
    print("PRODUCING FOR TICKER: ", ticker)
    obj = yf.Ticker(ticker)

    historical_data = obj.history(period='5mo')[['Close']][-60:]
    try:
        last_date = date_ 

        
    except:
        query = "INSERT INTO stock_data (date_predicted, stock_symbol, price) VALUES (%s, %s, %s)"
        values = (date_, ticker, float(0))
        cursor.execute(query, values)
        conn.commit()
        continue
    historical_data = historical_data.values
    close = []
    for data in historical_data:
        close.append(data[0])
    pred_data = np.expand_dims(close, 0)
    scaler = scalers[ticker]
    prediction = scaler.inverse_transform(model.predict(pred_data)[tickers_map[ticker]])[0][0]
    query = "INSERT INTO stock_data (date_predicted, stock_symbol, price) VALUES (%s, %s, %s)"
    values = (date_, ticker, float(prediction))
    cursor.execute(query, values)
    conn.commit()
