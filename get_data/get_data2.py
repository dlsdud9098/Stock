import requests
import json
import pandas as pd

def format_time(time_string):
    return f"{time_string[:2]}:{time_string[2:4]}:{time_string[4:]}"

# 거래원순간거래량요청
def fn_ka10052(token, data, cont_yn='N', next_key=''):
    # 1. 요청할 API URL
    # host = 'https://mockapi.kiwoom.com' # 모의투자
    host = 'https://api.kiwoom.com' # 실전투자
    endpoint = '/api/dostk/stkinfo'
    url =  host + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
        'authorization': f'Bearer {token}', # 접근토큰
        'cont-yn': cont_yn, # 연속조회여부
        'next-key': next_key, # 연속조회키
        'api-id': 'ka10052', # TR명
    }

    # 3. http POST 요청
    response = requests.post(url, headers=headers, json=data)
          
    # print(response.json())

    if response.status_code == 200:
        # print(response.json())
        data = response.json()['trde_ori_mont_trde_qty']
        df = pd.DataFrame(data)
        df = df[~df['stk_nm'].str.contains('선물', case=False, na=False)]
        df = df[~df['stk_nm'].str.contains('KODEX', case=False, na=False)]
        df = df[['tm','stk_cd', 'stk_nm','trde_ori_nm','tp','mont_trde_qty','cur_prc','acc_netprps', 'pred_pre','flu_rt']]
        df.columns = ['시간','종목코드', '종목명', '거래원명', '구분', '순간거래량', '현재가', '누적순매수', '전일대비','등락률']
        df['시간'] = df['시간'].apply(format_time)
        df['종목코드'] = df['종목코드'].map(lambda x: x.replace('_AL', ''))

        idx = df.groupby(by='종목명')['누적순매수'].idxmax()
        df2 = df.loc[idx]
        df2['누적순매수'] = pd.to_numeric(df2['누적순매수'], errors='coerce')
        
        df2 = df2.sort_values(by='누적순매수', ascending=False)
        df2 = df2.reset_index(drop=True)
        df2 = df2.head(10)

        # print(df2.head())
        
        df = df.reset_index(drop=True)
        return df2, df

    else:
        print(f'Error: {response.status_code}, {response.text}')

def get_data2_main(token):
    # 2. 요청 데이터
    params = {
        'mmcm_cd': '888', # 회원사코드 회원사 코드는 ka10102 조회
        'stk_cd': '', # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
        'mrkt_tp': '0', # 시장구분 0:전체, 1:코스피, 2:코스닥, 3:종목
        'qty_tp': '0', # 수량구분  0:전체, 1:1000주, 2:2000주, 3:, 5:, 10:10000주, 30: 30000주, 50: 50000주, 100: 100000주
        'pric_tp': '0', # 가격구분 0:전체, 1:1천원 미만, 8:1천원 이상, 2:1천원 ~ 2천원, 3:2천원 ~ 5천원, 4:5천원 ~ 1만원, 5:1만원 이상
        'stex_tp': '3', # 거래소구분 1:KRX, 2:NXT 3.통합
    }

    # print(token)
    # 3. API 실행
    df2, df = fn_ka10052(token=token, data=params)
    return df2, df

# 실행 구간
if __name__ == '__main__':
    # with open('fake/fake_keys.json', 'r', encoding='utf-8') as f:
    #     key_data = json.load(f)
    with open('keys/real_keys.json', 'r', encoding='utf-8') as f:
        key_data = json.load(f)
    
    MY_ACCESS_TOKEN = key_data.get('token', '')
    # 1. 토큰 설정
    # MY_ACCESS_TOKEN = '사용자 AccessToken' # 접근토큰

    # 2. 요청 데이터
    params = {
        'mmcm_cd': '888', # 회원사코드 회원사 코드는 ka10102 조회
        'stk_cd': '', # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
        'mrkt_tp': '0', # 시장구분 0:전체, 1:코스피, 2:코스닥, 3:종목
        'qty_tp': '0', # 수량구분  0:전체, 1:1000주, 2:2000주, 3:, 5:, 10:10000주, 30: 30000주, 50: 50000주, 100: 100000주
        'pric_tp': '0', # 가격구분 0:전체, 1:1천원 미만, 8:1천원 이상, 2:1천원 ~ 2천원, 3:2천원 ~ 5천원, 4:5천원 ~ 1만원, 5:1만원 이상
        'stex_tp': '3', # 거래소구분 1:KRX, 2:NXT 3.통합
    }

    # 3. API 실행
    df2, df = fn_ka10052(token=MY_ACCESS_TOKEN, data=params)
    print(df.head())

	# next-key, cont-yn 값이 있을 경우
	# fn_ka10052(token=MY_ACCESS_TOKEN, data=params, cont_yn='Y', next_key='nextkey..')