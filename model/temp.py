import pickle 

trains = pickle.load(open('X_trains.pkl', 'rb'))

pickle.dump(list(trains.keys()), open("tickers.pkl", 'wb'))