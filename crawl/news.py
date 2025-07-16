import requests
from lxml import html
import parmap
from datetime import datetime, timedelta
import time
import random
import re

import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fake_useragent import UserAgent
from tqdm import tqdm

# UserAgent 객체 생성
ua = UserAgent(platforms='desktop')


url = 'https://finance.naver.com/news/news_list.naver?mode=RANK&page=1'

url = 'https://finance.naver.com/news/market_notice.naver?&page=1'

def create_session():
    """재시도 로직과 User-Agent가 포함된 requests 세션을 생성합니다."""
    session = requests.Session()
    
    # User-Agent 설정
    session.headers.update({
        'User-Agent': ua.random,
        # 'refer'
        })
    
    # 재시도 전략 설정
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def get_page_links(start_date_str, end_date_str):
    """지정된 기간 동안 크롤링할 기본 URL 리스트를 생성합니다."""
    urls = []
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    current_date = start_date
    total_days = (end_date - start_date).days + 1
    
    print("Generating URLs...")
    for _ in tqdm(range(total_days), total=total_days):
        date_str = current_date.strftime("%Y%m%d")
        
        # LSS2D: 증권/증시
        urls.append(f'https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={date_str}&page=')
        
        # LSS3D: 시황, 투자정보, 해외증시 등
        for section_id3 in ['401', '402', '403', '404', '406', '429']:
            urls.append(f'https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3={section_id3}&date={date_str}&page=')
        
        # LSTD: 주요뉴스
        urls.append(f'https://finance.naver.com/news/news_list.naver?mode=LSTD&section_id=101&section_id2=258&type=1&date={date_str}&page=')

        # 포토뉴스
        urls.append(f'https://finance.naver.com/news/news_list.naver?mode=LSTD&section_id=101&section_id2=258&type=1&date={date_str}&page=')
        # tv뉴스
        urls.append(f'https://finance.naver.com/news/news_list.naver?mode=STOCK&section_id=tv&date={date_str}&page=')
        
        current_date += timedelta(days=1)

    return urls

def get_links_from_page(base_url):
    """하나의 기본 URL(특정 섹션/날짜)에 대해 모든 페이지를 순회하며 기사 링크를 수집합니다."""
    all_links = []
    session = create_session()
    page = 1


    cookies = {
        'NSCS': '1',
        'NNB': 'GNK3QJKHLA6WQ',
        'nstore_session': '14XTjLV2Eka6qx/38Ua/lCKp',
        'nstore_pagesession': 'jv1hgsqWlt3cAssM+Q4-263385',
        'NAC': 'kI9vBoQpeSNBB',
        'BUC': 'SuKBj-g9-5Rv4H58vbUVAcsTaNINf_SoeU6L3RoKAR8=',
        'nid_inf': '1796069924',
        'NACT': '1',
        'VISIT_LOG_CLEAN': '1',
        'N_SES': '8b429e1c-53cb-4788-b4dd-74695593101b',
    }

    while True:
        current_url = base_url + str(page)
        try:
            response = session.get(current_url, cookies=cookies)
            response.raise_for_status() # 오류가 있는 경우 예외 발생
            response.encoding='euc-kr'
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            break

        tree = html.fromstring(response.text)

        # 여러 XPath를 시도하여 링크를 찾음
        xpaths = [
            '//*[@id="contentarea_left"]/ul/li/dl/dd/a'
            '//ul[@class="newsList"]/li/dl/dd/a', # 뉴스 리스트 형식 1
            '//div[@class="newsList"]/ul/li/dl/dd/a', # 뉴스 리스트 형식 2
            '//div[@id="contentarea_left"]/ul/li/dl/dd/a' # 다른 구조
        ]

        links_found_on_page = []
        for xpath in xpaths:
            tags = tree.xpath(xpath)
            if tags:
                for tag in tags:
                    href = tag.get('href')
                    if href:
                        # 이미 전체 URL인 경우와 상대 경로인 경우를 모두 처리
                        if href.startswith('http'):
                            links_found_on_page.append(href)
                        else:
                            links_found_on_page.append('https://finance.naver.com' + href)
                break # 하나의 XPath에서 링크를 찾았으면 더 이상 다른 XPath를 시도하지 않음

        if not links_found_on_page:
            # 현재 페이지에서 링크를 하나도 찾지 못했다면 마지막 페이지이므로 종료
            break
        
        all_links.extend(links_found_on_page)
        page += 1
        time.sleep(random.uniform(0.1, 0.3)) # 서버 부하를 줄이기 위한 지연

    time.sleep(2)
    return all_links

def get_data(url):
    try:
        session = create_session()

        response = session.get(url)
        response.encoding = 'euc-kr'

        # tree = html.fromstring(response.text)

        # 2. JS 리디렉션 확인 및 처리
        if "top.location.href" in response.text:
            # 정규표현식을 사용해 리디렉션 URL을 정확히 추출
            match = re.search(r"top\.location\.href\s*=\s*['\"](.*?)['\"]", response.text)
            if match:
                redirect_url = match.group(1)
                # 3. 실제 뉴스 페이지로 다시 요청
                response = session.get(redirect_url)
                response.raise_for_status()
                # n.news.naver.com 페이지는 대부분 utf-8을 사용합니다.
                response.encoding = 'utf-8' 
            else:
                # 리디렉션 코드는 있는데 URL 추출에 실패한 경우
                return None

        tree = html.fromstring(response.text)
        # print(len(tree.xpath('//*[@id="title_area"]')))
        title = tree.xpath('//*[@id="title_area"]')[0].text_content()
        date = tree.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div/span')[0].text_content()
        content = tree.xpath('//*[@id="dic_area"]')[0].text_content()

        xpaths = [
            '//*[@id="contents"]/div[2]/p/span',
            '//*[@id="contents"]/div[4]/p/span'
        ]
        for xpath in xpaths:
            tags = tree.xpath(xpath)
            if tags:
                writer = tags[0].text_content()
                break
            else:
                writer = ''
                            
        data = {
            "title": title,
            "writer": writer,
            "date": date,
            "content": content
        }

        return data
        # print(response.text)
    except:
        import traceback
        print(traceback.print_exc())

        print(url)

if __name__ == '__main__':
    # 시작일과 종료일 설정 (YYYYMMDD 형식)
    start_date = '20240101'
    end_date = '20240105' # 테스트를 위해 짧은 기간으로 설정

    # 크롤링할 기본 URL 리스트 생성
    base_urls = get_page_links(start_date, end_date)
    base_urls = base_urls[:5]    
    print(f"\n총 url 개수{len(base_urls)}")
    
    # parmap을 사용하여 병렬로 링크 수집
    # get_links_from_page 함수를 base_urls 리스트의 각 항목에 대해 실행
    results_list_of_lists = parmap.map(get_links_from_page, base_urls, pm_pbar=True, pm_processes=5)

    # 2차원 리스트를 1차원 리스트로 변환 (Flattening)
    final_links = [link for sublist in results_list_of_lists for link in sublist]

    # 중복 제거
    unique_links = sorted(list(set(final_links)))
    
    print(f"\n크롤링 종료")
    print(f"크롤링한 뉴스 개수: {len(unique_links)}")

    # 뉴스 데이터 크롤링하기
    data_results = parmap.map(get_data, unique_links, pm_pbar=True, pm_processes=5)

    # unique_datas = sorted(list(set(final_datas)))
    print(data_results)
    print(f'크롤링한 뉴스 데이터 개수: {len(data_results)}')
    df = pd.DataFrame(data_results)
    df.to_csv('asdf.csv', encoding='utf-8', index=False)