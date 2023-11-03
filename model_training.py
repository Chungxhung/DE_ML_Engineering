import pandas as pd
import pymongo
from pymongo import MongoClient
import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import tensorflow
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import joblib
import numpy as np
import os


client = MongoClient('mongodb://localhost:27017')
db = client['stock_db']
collection = db['Items_Info']

query = {}
result1 = pd.DataFrame(collection.find(query, {'basDt' : 1, 'clpr': 1, '_id' : 0, 'hipr' : 1, 'lopr' : 1, 'mkp': 1, 'vs': 1, 'isinCd' : 1}).sort('basDt', 1))
result1.set_index('basDt', inplace = True)

result1['labeled_isinCd'] = pd.Categorical(result1['isinCd'])
result1['labeled_isinCd'] = result1['labeled_isinCd'].cat.codes

unique_isinCd = result1['isinCd'].unique()
scaler = MinMaxScaler()

for isinCd in unique_isinCd:
    try:
        subset = result1[result1['isinCd'] == isinCd]
        train = subset[['mkp', 'hipr', 'lopr', 'vs', 'clpr', 'labeled_isinCd']]
        dfx = pd.DataFrame(scaler.fit_transform(train.values), columns = train.columns, index = train.index)
        dfy = dfx[['clpr']]
        dfx = dfx[['mkp', 'hipr', 'lopr', 'vs', 'labeled_isinCd']]
        y = dfy.values.tolist()
        X = dfx.values.tolist()
        window_size = 30
        data_X = []
        data_y = []
        for i in range(len(y) - window_size):
            _X = X[i : i + window_size]
            _y = y[i + window_size]
            data_X.append(_X)
            data_y.append(_y)
        train_size = int(len(data_y) * 0.7)
        train_X = np.array(data_X[0 : train_size])
        train_y = np.array(data_y[0 : train_size])

        test_size = len(data_y) - train_size
        test_X = np.array(data_X[train_size : len(data_X)])
        test_y = np.array(data_y[train_size : len(data_y)])
        model = Sequential()
        model.add(LSTM(units=25, activation='relu', return_sequences=True, input_shape=(30, 5)))
        model.add(Dropout(0.01))
        model.add(LSTM(units=25, activation='relu'))
        model.add(Dropout(0.01))
        model.add(Dense(units=1))
        model.summary()
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(train_X, train_y, epochs=80, batch_size=20)

        pred_y = model.predict(test_X)
        plt.figure()
        plt.plot(test_y, color='red', label='real stock price')
        plt.plot(pred_y, color='blue', label='predicted stock price')
        plt.title(f'{isinCd} stock price prediction')
        plt.xlabel('date')
        plt.ylabel('stock price')
        plt.legend()
        plt.show()

        today_price = int(train.clpr[-1]) * pred_y[-1] / dfy.clpr[-1]

        print(f"오늘 {isinCd} 주가 :", today_price, 'KRW')

        today_date = datetime.now().strftime('%Y-%m-%d')

        predictions = pd.DataFrame(columns=['basDt', 'isinCd', 'predicted_clpr'])
        predictions['basDt'] = [today_date]
        predictions['isinCd'] = [isinCd]
        predictions['predicted_clpr'] = today_price

        collection = db['predictions']
        predictions_dict = predictions.to_dict(orient='records')
        collection.insert_many(predictions_dict)


        model_dir = '/Users/c26/Desktop/mlops_project/models/'
        model_file = f'{isinCd}_model.pkl'
        model.save(os.path.join(model_dir, model_file))
    except Exceptions as e:
        print("데이터가 없습니다.")
        continue
    
client.close()
