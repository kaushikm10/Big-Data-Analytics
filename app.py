from flask import Flask, jsonify, render_template, url_for, request
import os
import psycopg2
import requests
from polygon import RESTClient
import pickle
from datetime import datetime, timedelta
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
import numpy as np
import sklearn
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)

tickers = pickle.load(open("model/tickers.pkl", "rb"))
tickers_map = {ticker: i for i, ticker in enumerate(tickers)}
model = load_model("model/prediction_model.h5")
scalers = pickle.load(open("model/scalers.pkl", "rb"))

@app.route('/', methods=['GET', 'POST'])
def home():
    date = []
    close = []
    high = []
    low = []
    open = []
    hidden = 1
    data = []
    ema = []
    symbol = "STOCK"
    prediction = None
    if request.method == "POST":
        symbol = request.form['stock']
        start = (datetime.today() - timedelta(days=2*365)).strftime('%Y-%m-%d')
        end= datetime.today().strftime('%Y-%m-%d')
        bars = client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_=start, to=end) 
        for i, bar in enumerate(bars): 
            temp = datetime.fromtimestamp(int(str(bar.timestamp)[:10]))
            date.append(f"{temp.year}-{temp.month}-{temp.day}")
            close.append(bar.close)
            high.append(bar.high)
            low.append(bar.low)
            open.append(bar.open)
            data.append([bar.timestamp, bar.open, bar.high, bar.low, bar.close])
        pred_data = np.expand_dims(np.array(close[-60:]), 0)
        scaler = scalers[symbol]
        prediction = scaler.inverse_transform(model.predict(pred_data)[tickers_map[symbol]])[0][0]
        print(prediction)

        ema = list(pd.Series(close).ewm(span=10, adjust=False).mean().values)

        hidden = 0
    return render_template('home.html', ema=ema, close=close, open=open, low=low, high=high, date=date, data=data, hidden=hidden, symbol=symbol, tickers=tickers, prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)