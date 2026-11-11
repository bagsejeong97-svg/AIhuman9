# static_crawling_prac.py
# 명언, 작가, 태그, 작가 소개 URL 크롤링 후 CSV 저장

import time
import random
import csv
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from util.print_util import pp, up

BASE_URL = "https://quotes.toscrape.com/"
OUTPUT = Path(__file__).resolve().parent / "quotes_data.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

COLUMNS = ["페이지번호", "명언", "작가명", "태그", "작가상세URL"]

MAX_PAGES = 10

# 지정된 URL에서 HTML 문서를 요청하는 함수
# url : 크롤링할 페이지의 절대 URL
# 반환값 : 서버가 반환한 HTML 문자열
def get_html(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()  # 4xx/5xx 응답이면 HTTPError 발생
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text  # 서버에서 받은 HTML 문자열 반환

# HTML에서 명언 카드 정보를 추출하는 함수
# html : 파싱할 HTML 원문 문자열
# page_number : CSV에 기록할 원본 페이지 번호
# 반환값 : 명언별 정보가 담긴 딕셔너리 리스트
def parse_quotes(html, page_number):

    soup = BeautifulSoup(html, "html.parser")

    rows = []  # 한 페이지에서 추출한 결과를 저장할 리스트

    cards = soup.select("div.quote")  # 동일 구조의 명언 카드 전체

    for card in cards:

        quote_tag = card.select_one("span.text")  # 명언 본문 요소
        author_tag = card.select_one("small.author")  # 작가 이름 요소
        detail_tag = card.select_one("a[href^='/author/']")

        if quote_tag is None or author_tag is None:
            continue  # 필수 정보가 없으면 해당 카드만 건너뜀

        quote = quote_tag.get_text(" ", strip=True)
        author = author_tag.get_text(strip=True)

        if not quote or not author:
            continue

        tags = card.select("div.tags a.tag")  # 다중 태그 수집
        tag_text = ", ".join(tag.get_text(strip=True) for tag in tags)
        href = detail_tag.get("href", "") if detail_tag else ""

        detail_url = urljoin(BASE_URL, href) if href else ""

        rows.append({
            "페이지번호": page_number,
            "명언": quote,
            "작가명": author,
            "태그": tag_text,
            "작가상세URL": detail_url,
        })

    return rows

# 수집한 명언 데이터를 CSV 파일로 저장하는 함수
# rows : 컬럼명이 COLUMNS와 일치하는 딕셔너리 리스트
# 반환값 : 저장된 CSV 파일의 Path 객체
def save_csv(rows):
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()  # 첫 번째 행에 컬럼명 작성
        writer.writerows(rows)  # 딕셔너리를 각 CSV 데이터 행으로 저장
    return OUTPUT

def main():

    all_rows = []  # 페이지별 수집 결과를 합칠 리스트

    try:

        for page_number in range(1, MAX_PAGES + 1):

            page_url = urljoin(BASE_URL, f"page/{page_number}/")

            html = get_html(page_url)

            rows = parse_quotes(html, page_number)

            pp(f"{page_number}페이지 수집: {len(rows)}건")

            if not rows:
                pp("명언 카드가 없어 수집을 종료합니다.")
                break

            all_rows.extend(rows)

        if not all_rows:
            pp("수집된 데이터가 없어 CSV 파일을 생성하지 않습니다.")
            return

        output_path = save_csv(all_rows)

        authors = {row["작가명"] for row in all_rows}

        for row in all_rows[:5]:
            pp(row)  # 결과 일부만 출력하여 실행 결과를 간단히 확인
        pp("총 명언 수:", len(all_rows))
        pp("고유 작가 수:", len(authors))
        pp("저장 파일:", output_path)

        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)

    except requests.RequestException as exc:
        pp("웹페이지 요청 오류:", exc)

    except OSError as exc:
        pp("CSV 파일 저장 오류:", exc)

if __name__ == "__main__":
    main()

up(5)


