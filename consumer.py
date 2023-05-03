import psycopg2
import pickle
from tensorflow.keras.models import load_model
import sklearn
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'stock_producer',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    group_id=None
)

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

for message in consumer:
    print(message)
    date = message.value['message']['date']
    ticker = message.value['message']['ticker']
    close = message.value['message']['data']
    print("Consuming: ", ticker)
    if len(close) == 0:
        prediction = 0.0
    else:
        pred_data = np.expand_dims(close, 0)
        scaler = scalers[ticker]
        prediction = scaler.inverse_transform(model.predict(pred_data)[tickers_map[ticker]])[0][0]
    query = "INSERT INTO stock_data (date_predicted, stock_symbol, price) VALUES (%s, %s, %s)"
    values = (date, ticker, float(prediction))
    cursor.execute(query, values)
    conn.commit()
