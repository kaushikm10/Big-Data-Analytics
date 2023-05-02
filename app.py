from flask import Flask, jsonify, render_template, url_for, request, session, redirect
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
app.secret_key = 'big-data-analytics'
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

@app.route('/stock/', methods=['GET', 'POST'])
def home():

    if session['logged_in'] is False:
        return redirect(url_for('index'))
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

        hidden = 0
    return render_template('try.html', ema=ema, close=close, open=open, low=low, high=high, date=date, data=data, hidden=hidden, symbol=symbol, tickers=tickers, prediction=prediction)


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

if __name__ == '__main__':
    app.run(debug=True)