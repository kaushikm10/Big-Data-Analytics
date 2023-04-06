import psycopg2
import pickle
conn = psycopg2.connect(
                host="localhost",
                database="stock_db",
                user="postgres",
                password="postgres")

cur = conn.cursor()
snp = pickle.load(open("snp500.pkl", "rb"))
try:
    cur.execute(f"DROP TABLE SNP;")
    conn.commit()
except:
    pass
for symbol in snp[1:]:
    try:
        cur.execute(f"DROP TABLE {symbol}_DB;")
        conn.commit()
    except:
        pass
cur.close()
conn.close()