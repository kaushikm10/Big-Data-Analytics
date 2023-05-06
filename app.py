import os
import pickle
from datetime import datetime, timedelta
import ta
import numpy as np
import pandas as pd
import psycopg2
import requests
import sklearn
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from polygon import RESTClient
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
app.secret_key = 'big-data-analytics'
api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)

tickers = pickle.load(open("model/tickers.pkl", "rb"))



conn = psycopg2.connect(
    user="postgres",
    password="postgres",
    host="127.0.0.1",
    port="5432",
    database="stock_data"
)
cursor = conn.cursor()
if conn:
    print("Connected")
else:
    print("Not Connected")

@app.route('/stock/', methods=['GET', 'POST'])
def home():

    if session['logged_in'] is False:
        return redirect(url_for('index'))
    date = []
    close = []
    hidden = 1
    data = []
    high = []
    low = []
    open = []
    ema = []
    rsi = []
    bb = []
    upper_bb = []
    lower_bb = []
    so = []
    k = []
    d = []
    symbol = "STOCK"
    ema_pred = None
    rsi_pred = None
    bb_pred = None
    so_pred = None

    prediction = None
    if request.method == "POST":
        symbol = request.form['stock']
        start = (datetime.today() - timedelta(days=2*365)).strftime('%Y-%m-%d')
        end = datetime.today().strftime('%Y-%m-%d')
        bars = client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_=start, to=end) 
        for i, bar in enumerate(bars): 
            temp = datetime.fromtimestamp(int(str(bar.timestamp)[:10]))
            d = "{}-{}-{}".format(temp.year, temp.month, temp.day)
            date.append(d)
            close.append(bar.close)
            high.append(bar.high)
            low.append(bar.low)
            open.append(bar.open)
            data.append([bar.timestamp, bar.open, bar.high, bar.low, bar.close])
        last_date = datetime.strftime((datetime.today() + timedelta(days=1)), "%Y-%m-%d")
        query = "SELECT price FROM stock_data WHERE date_predicted = '{}' AND stock_symbol = '{}';".format(last_date, symbol)
        cursor.execute(query)
        results = cursor.fetchall()
        print(results)
        prediction = results[0][0]
        

        ema = list(pd.Series(close).ewm(span=10, adjust=False).mean().values)
        rsi = ta.momentum.RSIIndicator(pd.Series(close)).rsi()
        rsi.dropna(inplace=True)
        bb = ta.volatility.BollingerBands(pd.Series(close)).bollinger_mavg()
        bb.dropna(inplace=True)
        upper_bb = ta.volatility.BollingerBands(pd.Series(close)).bollinger_hband()
        upper_bb.dropna(inplace=True)
        lower_bb = ta.volatility.BollingerBands(pd.Series(close)).bollinger_lband()
        lower_bb.dropna(inplace=True)
        so = ta.momentum.StochasticOscillator(pd.Series(high), pd.Series(low), pd.Series(close))
        k = pd.Series(so.stoch())
        k.dropna(inplace=True)
        d = pd.Series(k).rolling(window=3).mean()
        d.dropna(inplace=True)
        hidden = 0
        rsi = list(rsi.values)
        bb = list(bb.values)
        upper_bb = list(upper_bb.values)
        lower_bb = list(lower_bb.values)
        k = list(k.values)
        d = list(d.values)


        if close[-1] > ema[-1]:
            ema_pred = "BUY"
        else:
            ema_pred = "SELL"

        if rsi[-1] < 30:
            rsi_pred = "BUY"
        elif rsi[-1] > 70:
            rsi_pred = "SELL"
        else:
            rsi_pred = "HOLD"
        
        
        if close[-1] < lower_bb[-1]:
            bb_pred = "BUY"
        elif close[-1] > upper_bb[-1]:
            bb_pred = "SELL"
        else:
            bb_pred = "HOLD"

        if k[-1] < 20:
            so_pred = "BUY"
        elif k[-1] > 80:
            so_pred = "SELL"
        else:
            so_pred = "HOLD"

    return render_template('try.html', ema=ema, close=close, date=date, data=data, hidden=hidden, symbol=symbol, tickers=tickers, prediction=prediction, rsi=rsi, bb=bb, upper_bb=upper_bb, lower_bb=lower_bb, k=k, d=d, ema_pred=ema_pred, so_pred=so_pred, rsi_pred=rsi_pred, bb_pred=bb_pred)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            print(username, password, email)
            query = "SELECT * FROM USERS WHERE USERNAME_='{}';".format(username)
            cursor.execute(query)
            res = cursor.fetchall()
            print(res)
            if len(res) != 0:
                return redirect(url_for('index'))                
            else:
                query = "INSERT INTO USERS (USERNAME_, PASSWORD_, EMAIL_) VALUES (%s, %s, %s)"
                values = (username, password, email)
                cursor.execute(query, values)
                conn.commit()
                return redirect(url_for('login'))
        except Exception as e:
            print(e)
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        query = "SELECT * FROM USERS WHERE USERNAME_='{}';".format(u)
        cursor.execute(query)
        res = cursor.fetchone()
        if res:
            session['logged_in'] = True
            return redirect(url_for('home'))
        return render_template('index.html', message="Incorrect Details")


@app.route("/", methods=['GET', 'POST'])
def index():
    session['logged_in'] = False
    if request.method=='POST':
        req_type = request.form['type']
        if req_type == 'login':
            return render_template('login.html')
        else:
            
            return render_template('register.html')
    return render_template("register.html")

@app.route("/logout/",methods=['GET', 'POST'])
def logout():
    session['logged_in']=False
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
