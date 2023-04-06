from flask import Flask, jsonify, render_template, url_for, request
import os
import psycopg2
import requests
from polygon import RESTClient
import datetime
import pickle
from datetime import datetime


app = Flask(__name__)

api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)

@app.route('/', methods=['GET', 'POST'])
def home():
    date = []
    close = []
    hidden = 1
    if request.method == "POST":
        symbol = request.form['stock']
        bars = client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_="1970-01-01", to="2023-04-05") 
        for i, bar in enumerate(bars): 
            temp = datetime.fromtimestamp(int(str(bar.timestamp)[:10]))
            date.append(f"{temp.year}-{temp.month}-{temp.day}")
            close.append(bar.close)
        hidden = 0
        print(date, close)
    return render_template('home.html', close=close, date=date, hidden=hidden)


if __name__ == '__main__':
    app.run(debug=True)