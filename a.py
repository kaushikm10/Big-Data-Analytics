import psycopg2


from datetime import datetime
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
end= datetime.today().strftime('%Y-%m-%d')
last_date = datetime.strptime(end, '%Y-%m-%d')
symbol = 'AAPL'
query = f"SELECT price FROM stock_data WHERE date_predicted = '{last_date}' AND stock_symbol = '{symbol}';"
cursor.execute(query)
results = cursor.fetchall()
print(results[0][0])