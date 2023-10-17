import requests
import pandas as pd
import pymongo
from pymongo import MongoClient
import datetime
from datetime import date, datetime, timedelta


client = MongoClient('mongodb://localhost:27017')
db = client['stock_db']
collection = db['Items']
collection2 = db['Items_Info']

today = datetime.today()
yesterday_date =today - timedelta(days = 1)
base_date = yesterday_date.strftime('%Y%m%d')
    
    
headers = {'Content-Type': 'application/json', 'Accept': '*/*'}
key = "VxP6f0LmEQCDjpRdRaX8UbjxaubVl8qLovwcwJAv5Vht84mFQ8YekGmdKDChsGpoIFHlFs6jQJctpOdfEju6HA=="
url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
body = {
    "serviceKey":key,
    "numOfRows": 10000,
    "pageNo": 1,
    "basDt" : base_date,
    "resultType" : 'json'
    }

response = requests.get(url=url,params=body)
data = response.json()
table = pd.DataFrame(data['response']['body']['items']['item'])

Items = table[['srtnCd', 'isinCd', 'itmsNm']]
Items_Info = table.drop(['srtnCd', 'itmsNm'], axis = 1)
Items_Info['basDt'] =  pd.to_datetime(Items_Info['basDt'], format = '%Y%m%d')
Items_Info_List = Items_Info.to_dict(orient = 'records')
collection2.insert_many(Items_Info_List)
