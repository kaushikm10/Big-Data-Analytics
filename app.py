from flask import Flask, jsonify, render_template, url_for, request
import os
import psycopg2
import requests
from  polygon import RESTClient
import pickle
from datetime import datetime, timedelta
import pandas as pd
import pickle
import numpy as np
import sklearn
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)

tickers = pickle.load(open("model/tickers.pkl", "rb"))


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
        last_date = datetime.strptime(end, '%Y-%m-%d')
        query = f"SELECT price FROM stock_data WHERE date_predicted = '{last_date}' AND stock_symbol = '{symbol}';"
        cursor.execute(query)
        results = cursor.fetchall()

        prediction = results[0][0]

        ema = list(pd.Series(close).ewm(span=10, adjust=False).mean().values)

        hidden = 0
    return render_template('home.html', ema=ema, close=close, open=open, low=low, high=high, date=date, data=data, hidden=hidden, symbol=symbol, tickers=tickers, prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)