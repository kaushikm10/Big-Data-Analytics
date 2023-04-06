from flask import Flask, jsonify, render_template, url_for, request
import os
import psycopg2
import yfinance as yf
import requests
from polygon import RESTClient
import datetime
from datetime import datetime


api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():

    return render_template('home.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
    if request.method == 'POST':
        symbol = request.form['symbol']
        print(symbol)
        conn = psycopg2.connect(
                host="localhost",
                database="stock_db",
                user="postgres",
                password="postgres")
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {symbol} (date DATE, open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume INT);")
        conn.commit()
        cur.close()


        bars = client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_="1970-01-01", to="2023-04-04")
        cur = conn.cursor()
        data = []
        for bar in bars:
            cur.execute(f"INSERT INTO {symbol} (date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)", (datetime.fromtimestamp(int(str(bar.timestamp)[:10])), bar.open, bar.high, bar.low, bar.close, bar.volume))
            temp = []
            temp.append(bar.timestamp)
            temp.append(bar.open)
            temp.append(bar.high)
            temp.append(bar.low)
            temp.append(bar.high)    
            data.append(temp)        
            conn.commit()
        cur.close()
        conn.close()
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)