import requests
import json
import os

# 접근토큰 발급
def fn_au10001(data):
    host = 'https://api.kiwoom.com'  # 실전투자
    # host = 'https://mockapi.kiwoom.com'
    endpoint = '/oauth2/token'
    url = host + endpoint

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',  # 컨텐츠타입
    }

    response = requests.post(url, headers=headers, json=data)
    # print(response.json())
    data = response.json()['token']
    
    return data

# def get_token():
def get_token(appkey, secretkey):
    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': appkey,  # 앱키
        'secretkey': secretkey,  # 시크릿키
    }

    token = fn_au10001(data=params)

    # print(token)
    return token

if __name__ == '__main__':
    path = 'keys/real_keys.json'
    # path = 'data/real_keys.json'
    with open(path, 'r', encoding='utf-8') as f:
        keys = json.load(f)

    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': keys['appkey'],  # 앱키
        'secretkey': keys['secretkey'],  # 시크릿키
    }

    token = fn_au10001(data=params)

    with open(path, 'w' ,encoding='utf-8') as f:
        json.dump({
            'appkey': keys['appkey'],
            'secretkey': keys['secretkey'],
            'token': keys['token']
        }, f)
        
    # print(body['token'])