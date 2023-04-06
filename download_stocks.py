import psycopg2
from polygon import RESTClient
import pickle
import time
from datetime import datetime

api_key = "Xljq9nB1MP3h8PhC5ZIPjp9QyjI1t11N"
client = RESTClient(api_key=api_key)
snp = pickle.load(open("snp500.pkl", "rb"))
print(snp)

conn = psycopg2.connect(
                host="localhost",
                database="stock_db",
                user="postgres",
                password="postgres")

cur = conn.cursor()

cur.execute(f"CREATE TABLE IF NOT EXISTS SNP (FROM_DATE DATE, TO_DATE DATE, SYMBOL VARCHAR);")
conn.commit()


for i, symbol in enumerate(snp[1:]):
    print("CURRENT: ", i, symbol)

    cur.execute(f"CREATE TABLE IF NOT EXISTS {symbol}_DB (date DATE, open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume INT);")
    conn.commit()
    try:
        bars = client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_="1970-01-01", to="2023-04-05") 
        from_date = datetime.fromtimestamp(int(str(bars[0].timestamp)[:10]))
        to_date = datetime.fromtimestamp(int(str(bars[-1].timestamp)[:10]))
        print(from_date, to_date)
        cur.execute(f"INSERT INTO SNP (FROM_DATE, TO_DATE, SYMBOL) VALUES (%s, %s, %s)", (from_date, to_date, symbol))
        conn.commit()
        for bar in bars:
            cur.execute(f"INSERT INTO {symbol}_DB (date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)", (datetime.fromtimestamp(int(str(bar.timestamp)[:10])), bar.open, bar.high, bar.low, bar.close, bar.volume))
            conn.commit()
        if i % 5 == 0:
            time.sleep(61)
    except:
        print("ERROR: ", symbol)
        continue

cur.close()
conn.close()