from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

app = Flask(__name__, template_folder = '/Users/c26/Desktop/mlops_project/templates')

# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client['stock_db']  # 여기에 사용할 데이터베이스 이름을 지정하세요
collection = db['Items_Info']  # 여기에 사용할 컬렉션 이름을 지정하세요

@app.route('/')
def stock_search():
    return render_template('search_stock.html')

@app.route('/search', methods=['POST'])
def search_stock():
    isinCd = request.form['isinCd']
    start_date_str = request.form['start_date']
    start_date_format = datetime.strptime(start_date_str, '%Y-%m-%d')
    start_date = datetime.strftime(start_date_format, '%Y%m%d')
    end_date_str = request.form['end_date']
    end_date_format = datetime.strptime(end_date_str, '%Y-%m-%d')
    end_date = datetime.strftime(end_date_format, '%Y%m%d')
    query = {'isinCd' : isinCd,
            'basDt' : {'$gte' : start_date, '$lte' : end_date}
            }
    result = collection.find(query).sort('basDt', -1)
    return render_template('stock_results.html', data = result, isinCd = isinCd, start_date = start_date, end_date = end_date)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
