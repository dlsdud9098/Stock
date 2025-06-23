from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS
from get_data.get_data2 import get_data2_main
from get_data.get_token import get_token
import json

# Flask 앱 생성
app = Flask(__name__)
# CORS 설정 (모든 도메인에서의 요청을 허용)
CORS(app)

def get_keys():
    path = 'keys/real_keys.json'
    with open(path, 'r', encoding='utf-8') as f:
        keys = json.load(f)
    
    appkey = keys.get('appkey', '')
    secretkey = keys.get('secretkey', '')
    token = keys.get('token', '')

    if not token:
        token = get_token(appkey, secretkey)
        with open(path, 'w', encoding='utf-8') as f:
            keys = json.dump({'appkey': appkey, 'secretkey': secretkey, 'token': token},f)

    return appkey, secretkey, token

# API 엔드포인트 정의
@app.route('/api/market_data')
def get_data():
    # DataFrame을 JSON 형태로 변환하여 응답
    # orient='records'는 [{column: value}, {column: value}, ...] 형태의 배열로 만듭니다.
    appkey, secretkey, token = get_keys()
    df2, df = get_data2_main(token)


    # print(df.head())
    # return jsonify(df.to_dict(orient='records'))
    return jsonify({
        'df1': df.to_dict(orient='records'),
        'df2': df2.to_dict(orient='records'),
    })

# 서버 실행
if __name__ == '__main__':
    # host='0.0.0.0'은 외부에서도 접속 가능하게 합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)
