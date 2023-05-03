import schedule
from kafka import KafkaProducer
import json
import yfinance as yf
import pickle
import datetime
import time

def my_task():
    # Code to be executed at the scheduled time

    tickers = pickle.load(open("model/tickers.pkl", "rb"))

    producer = KafkaProducer(
        bootstrap_servers=['localhost:29092'],
        value_serializer=lambda m: json.dumps(m).encode('ascii')
    )

    date_ = datetime.datetime.strftime((datetime.datetime.today() + datetime.timedelta(days=1)), "%Y-%m-%d")

    for ticker in tickers:
        print("PRODUCING FOR TICKER: ", ticker)
        obj = yf.Ticker(ticker)
        historical_data = obj.history(period='5mo')[['Close']][-60:]
        if len(historical_data) == 0:
            message = {
                'date': date_,
                'ticker': ticker,
                'data': []
            }
            producer.send('stock_producer', {'message': message})
            producer.flush()
        else:
            historical_data = historical_data.values
            close = []
            for data in historical_data:
                close.append(data[0])
            message = {
                'date': date_,
                'ticker': ticker,
                'data': close
            }
            producer.send('stock_producer', {'message': message})
            producer.flush()

# Example: Print a message every day at 10:30 AM
schedule.every().day.at("20:00").do(my_task)

while True:
    schedule.run_pending()
    time.sleep(1)
