from flask import Flask, jsonify, render_template, url_for, request
import os
import psycopg2
import requests
from polygon import RESTClient
import datetime
import pickle
from datetime import datetime


app = Flask(__name__)


@app.route('/')
def home():
    closing = pickle.load(open("closing.pkl", "rb"))
    date = pickle.load(open("date.pkl", "rb")) 
    for i, d in enumerate(date): 
        temp = d.astype(object)
        temp = datetime.fromtimestamp(int(str(temp)[:10]))
        date[i] = f"{temp.year}-{temp.month}-{temp.day}"
    return render_template('home.html', closing=closing, date=date)


if __name__ == '__main__':
    app.run(debug=True)