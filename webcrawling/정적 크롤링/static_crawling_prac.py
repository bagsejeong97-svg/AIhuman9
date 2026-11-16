
# static_crawling_prac.py
# 명언 웹사이트의 모든 페이지에서 데이터를 수집하여 CSV로 저장

import csv
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from util.print_util import pp

ROOT = Path(__file__).resolve().parent
START_URL = 'https://quotes.toscrape.com/'
TARGET = ROOT / 'quotes_data.csv'


def main():
    url = START_URL
    page_number = 1
    rows = []
    failed = False

    while url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            pp(f'{page_number}페이지 요청 실패: {error}')
            failed = True
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.select('div.quote')

        if not quotes:
            pp(f'{page_number}페이지에서 명언을 찾지 못했습니다.')
            failed = True
            break

        collected_count = 0

        for quote in quotes:
            quote_text = quote.select_one('span.text')
            author_name = quote.select_one('small.author')
            author_link = quote.select_one('a[href*="/author/"]')
            tags = quote.select('div.tags a.tag')

            if quote_text is None or author_name is None or author_link is None:
                pp(f'{page_number}페이지에서 필요한 정보가 없는 명언을 발견했습니다.')
                failed = True
                continue

            rows.append({
                '페이지번호': page_number,
                '명언': quote_text.get_text(strip=True),
                '작가명': author_name.get_text(strip=True),
                '태그': ', '.join(tag.get_text(strip=True) for tag in tags),
                '작가상세URL': urljoin(url, author_link['href'])
            })
            collected_count += 1

        pp(f'{page_number}페이지 수집 완료: {collected_count}개')

        next_link = soup.select_one('li.next a')
        if next_link is None:
            break

        url = urljoin(url, next_link['href'])
        page_number += 1

    if not rows:
        pp('수집된 명언이 0개입니다. CSV 파일을 저장하지 않습니다.')
        return

    with TARGET.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=['페이지번호', '명언', '작가명', '태그', '작가상세URL']
        )
        writer.writeheader()
        writer.writerows(rows)

    authors = {row['작가명'] for row in rows}

    pp(f'CSV 저장 완료: {TARGET}')
    pp(f'총 명언 수: {len(rows)}개')
    pp(f'총 작가 수: {len(authors)}명')

    if failed:
        pp('일부 페이지 또는 명언의 수집에 실패했습니다. 저장된 CSV는 부분 결과입니다.')
    else:
        pp('모든 페이지 수집이 완료되었습니다.')


if __name__ == '__main__':
    main()
