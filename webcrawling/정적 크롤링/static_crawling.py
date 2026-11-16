# static_crawling.py
# 웹페이지 정적 크롤링 - 네이버 랭킹뉴스 웹페이지의 언론사명, 순위, 제목, URL 크롤링

# 설치 : python -m pip install requests, bs4

import csv
import time
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin # URL 접합
import requests
from bs4 import BeautifulSoup # 응답으로 받은 HTML 코드 파싱 라이브러리
from util.print_util import pp

# 네이버 언론사별 랭킹뉴스 URL
URL = 'https://news.naver.com/main/ranking/popularDay.naver'

OUTPUT = Path(__file__).resolve().parent / 'naver_rankingnews.csv'

# 서버에 전달할 HTTP 요청 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0', # 웹브라우져/버젼(파이썬 요청이 아니라 웹브라우져 요청이라고 서버를 속임)
    'Accept-Language': 'ko-KR,ko;q=0.9', # 웹브라우져 해석 언어 설정
}

COLUMNS =['언론사명','순위','기사제목','상세URL'] # CSV 컬럼명

# 네이버 랭킹뉴스 웹페이지 HTML 코드를 요청하는 함수
# 반환값: HTML 코드 문자열
def get_html():
    response = requests.get( # GET 요청을 보내 응답 획득
        URL, # 요청 URL
        headers=HEADERS, # 요청 Header
        timeout=15 # 요청 타임아웃(응답 대기 최대 시간)
    )
    # 웹서버에서 보내는 응답 상태코드(status code)가 200(ok)이 아닌 경우
    response.raise_for_status()
    return response.text # HTML 코드 문자열 반환

# HTML에서 언론사별 랭킹 기사를 추출하는 함수
# html: requests로 가져온 HTML 문자열
# 반환값: 기사 정보를 담은 딕셔너리들의 리스트 (딕셔너리 1개 = 기사 1건)
def parse_news(html):

    soup = BeautifulSoup(html, 'html.parser') # HTML Parser 생성

    results = [] # 결과 저장할 리스트

    # 언론사별 랭킹뉴스 영역 검색
    # select : 여러개 획득
    # div.rankingnews_box : div 요소 중에서 class 속성 값이 rankingnews_box 인 div (CSS selector)
    boxes = soup.select('div.rankingnews_box')
    pp('검색된 언론사 영역 수:', len(boxes))

    for box in boxes:

        # 언론사명 추출
        # select_one : 한개 획득
        press_tag = box.select_one('strong.rankingnews_name')
        if press_tag is None:
            continue
        press = press_tag.get_text(strip=True) # 앞뒤 공백 제거한 언론사명 텍스트

        # 해당 언론사의 기사 목록 추출
        # class 속성의 값이 rankingnews_list 인 ul요소 자식 요소 중 li요소들
        articles = box.select('ul.rankingnews_list > li')

        for index, article in enumerate(articles, start=1):

            # 기사 순위 추출
            rank_tag = article.select_one('em.list_ranking_num')

            rank = rank_tag.get_text(strip=True) if rank_tag else str(index)

            # 기사 제목과 URL이 들어 있는 a 태그 추출
            title_tag = article.select_one('a.list_title')
            if title_tag is None:
                continue

            # 기사 제목에서 불필요한 공백 제거
            title = title_tag.get_text(strip=True)

            # href 속성에서 기사 URL 추출
            # a태그의 href속성 값을 가져옴, 없으면 ""
            href = title_tag.get('href', "")

            if not title or not href:
                continue

            # 상대경로 URL을 절대경로 URL로 변환
            detail_url = urljoin(URL, href)

            # 기사 정보를 딕셔너리로 저장
            results.append({
                '언론사명': press,
                '순위': rank,
                '기사제목': title,
                '상세URL': detail_url
            })

    # 0.1 ~ 0.5 랜덤 실수
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay) # 하나 처리하고 랜덤시간 잠깐 멈춤

    return results

# 추출한 기사 정보를 CSV 파일로 저장하는 함수
# news: 기사 정보 딕셔너리 리스트
# 반환값: 저장된 Path 객체
def save_csv(news):
    with OUTPUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, COLUMNS)
        writer.writeheader()
        writer.writerows(news)
    return OUTPUT

def main():
    try:

        html = get_html()

        news = parse_news(html)

        if not news:
            pp('추출된 기사가 없습니다.')
            return

        filepath = save_csv(news)

        # 추출된 데이터 일부 출력
        for item in news[:10]:
            pp(item)

        pp('총 기사 수:', len(news))
        pp('언론사 수:', len(set(item['언론사명'] for item in news)))
        pp('저장 파일:', filepath)

    except requests.RequestException as e:
        pp('네트워크 요청 오류',e)
    except (OSError, ValueError) as e:
        pp('처리오류:',e)

if __name__ == '__main__':
    main()
