import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017')
db = client['stock_db']
collection = db['Items_Info']
result = collection.delete_many({'basDt' : '20231017'})

print("Deleted", result.deleted_count, "documents")
client.close()
