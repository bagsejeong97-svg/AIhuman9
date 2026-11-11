# dynamic_crawling.py
# Sellenium을 활용한 동적 크롤링

# OrangeHRM 공개 데모 웹사이트 > 로그인 > PIM 메뉴 클릭 > Employee List 획득 > Excel 저장

# 설치: python -m pip install selenium openpyxl

import time
import os
from pathlib import Path
import pandas as pd
from selenium import webdriver # 웹브라우져 드라이버
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException, WebDriverException
)
from selenium.webdriver.chrome.options import Options # 드라이버 옵션
from selenium.webdriver.common.by import By # 셀렉터
from selenium.webdriver.support import expected_conditions as EC # 대기 조건
from selenium.webdriver.support.ui import WebDriverWait # 대기
from util.print_util import pp, up

# OrangeHRM 동적 크롤링 실습용 오픈소스 웹페이지 (오픈소스 인사관리시스템)
LOGIN_URL = 'https://opensource-demo.orangehrmlive.com/web/index.php/auth/login'

# 로그인 계정명 / 비밀번호
USERNAME = os.getenv('ORANGEHRM_USERNAME', 'Admin')
PASSWORD = os.getenv('ORANGEHRM_PASSWORD', 'admin123')

HEADLESS = False # True: 브라우져를 화면에 표시하지 않음

MAX_PAGES = 3 # 최대 수집할 페이지 수, 0이면 마지막 페이지까지

WAIT_SECONDS = 20 # DOM 요소의 최대 대기 시간 (초)

ROOT = Path(__file__).resolve().parent
SAVE_PATH = ROOT / 'orangehrm_employee_list.xlsx'

COLUMNS = ['사원번호', '이름',  '직책', '고용상태', '부서', '상급자']

# Chrome을 실행하고 브라우져 제어 객체를 돌려주는 함수
# 반환값: webdriver.Chrome
def create_browser():
    options = Options() # Chrome 실행 옵션
    options.add_argument('--window-size=1500,950') # 창의 크기
    if HEADLESS:
        options.add_argument('--headless=new') # 브라우져 표시하지 않음
    browser = webdriver.Chrome(options=options) # 브라우져 제어 객체 생성
    browser.set_page_load_timeout(45) # 페이지 로딩 최대 시간 (초)
    return browser

# 로그인 폼에 계정 정보를 입력하고 대시보드 화면이 나타날 때까지 기다리는 함수
# browser: webdriver.Chrome, 현재 실행 중인 브라우져
# wait: WebDriverWait, 동적으로 나타나는 요소를 기다림
def login(browser, wait):

    # 로그인 페이지를 GET 방식으로 요청해서 열기
    browser.get(LOGIN_URL)

    # name속성의 값이 username인 요소가 화면에 보여질때까지 대기
    name = wait.until(EC.visibility_of_element_located((By.NAME, 'username')))

    # 계정명 입력
    name.send_keys(USERNAME)

    # name속성의 값이 password인 요소를 찾아서 비밀번호 입력
    browser.find_element(By.NAME, 'password').send_keys(PASSWORD)

    # 로그인 버튼 클릭
    # CSS 셀렉터 방식으로 type속성의 값이 submit인 button요소가 클릭 가능할때까지 기다렸다가 클릭
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, 'button[type="submit"]'
    ))).click()

    # 로그인 버튼 클릭 후 좌측 메뉴가 나타날때까지 대기
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'ul.oxd-main-menu')
    ))

    pp('[로그인 성공] 대시보드 접속')


# 좌측 PIM 메뉴를 누른 뒤 상단 Employee List 메뉴를 선택하는 함수
def open_employee_list(browser, wait):

    # class 속성의 값이 oxd-main-menu-item인 a 요소 중 href 속성의 값이 /pim 문자열을 포함하는
    # 요소가 클릭 가능할 때까지 대기
    pim = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, 'a.oxd-main-menu-item[href*="/pim"]'
    )))

    pim.click()

    # 상단 탭 메뉴들
    menus = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, 'a.oxd-topbar-body-nav-tab-item'
    )))

    # 상단 탭 메뉴 중 Employee List메뉴 클릭
    for menu in menus:
        if menu.text.strip() == 'Employee List':
            wait.until(EC.element_to_be_clickable(menu)).click()
        break

    # 테이블 보일 때까지 대기
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-table'
    )))

    pp('[메뉴 이동] PIM > Employee List')

# 현재 페이지 행을 읽는 함수
# page_number: int, Excel에 기록할 페이지 번호
# 반환값: list[dict], 직원별 사원번호, 이름, 직책 등의 목록
def collect_page(browser, wait, page_number):

    # 테이블 헤더 보일 때까지 대기
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-table-header'
    )))



    records = []

    # 데이터 행들
    cards = browser.find_elements(By.CSS_SELECTOR, '.oxd-table-body .oxd-table-card')

    for card in cards:

        cells = card.find_elements(By.CSS_SELECTOR, '.oxd-table-cell') # 셀들

        values = [cell.text.strip() for cell in cells] # 셀 값들

        # pp(values) # 확인용

        datarow = {
            '사원번호': values[1],
            '이름': values[2] + ' ' + values[3],
            '직무': values[4],
            '고용상태': values[5],
            '부서': values[6],
            '상급자': values[7]
        }

        # pp(datarow) # 확인용
        records.append(datarow)
    return records

# 현재 페이지의 다음 버튼을 찾아 클릭하는 함수
# 반환값 : bool, 다음 페이지로 이동하면 True, 마지막이면 False
def click_next(browser, wait):

    # 다음 버튼
    # class 속성의 값이 .oxd-pagination-page-item인 button
    # 하위에 class 속성의 값이 bi-chevron-right인 i 요소들
    button = browser.find_element(
        By.CSS_SELECTOR, '.oxd-pagination-page-item:has(i.bi-chevron-right)'
    )

    if not button: # 다음 버튼이 없다면 마지막 페이지
        return False
    wait.until(EC.element_to_be_clickable(button)).click() # 다음 버튼 클릭
    return False
# 수집한 직원 데이터를 Excel 파일로 저장하는 함수
# records: list[dict], 여러 페이지에서 수집한 직원 목록
# 반환값: Path, 저장된 Excel 파일의 절대 경로

def save_excel(records):

    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(records, columns=COLUMNS)

    with pd.ExcelWriter(SAVE_PATH, engine="openpyxl") as writer:

        frame.to_excel(writer, sheet_name="직원명단", index=False)
        sheet = writer.sheets["직원명단"]
        sheet.freeze_panes = "A2"  # 첫 번째 제목 행을 고정
        sheet.auto_filter.ref = sheet.dimensions  # 제목에 필터 적용

        widths = [16, 44, 30, 25, 25, 25]

        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[
                sheet.cell(row=1, column=index).column_letter
            ].width = width

        for cell in sheet["A"][1:]:
            cell.number_format = "@"  # 사원번호는 텍스트 서식 사용

    return SAVE_PATH


def main():

    browser = None

    records = []

    try:

        browser = create_browser()

        wait = WebDriverWait(browser, WAIT_SECONDS) # 20초 대기

        login(browser, wait)

        open_employee_list(browser, wait)

        records=collect_page(browser, wait, 1)

        page_number = 1

        while True:

            current = collect_page(browser, wait, page_number)
            pp(f'[수집] {page_number}페이지: {len(current)}명')

            if MAX_PAGES > 0 and page_number >= MAX_PAGES:
                break

            if not click_next(browser, wait):
                break
            page_number += 1

        if records:
            frame = pd.DataFrame(records, columns=COLUMNS)
            pp(frame.to_string(index=False))
            path = save_excel(records)
            pp(f'[완료] {len(records)}행 수집 / Excel 저장: {path}')
        else:
            pp('직원 목록이 없어서 Excel 저장하지 않음')

    except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
        pp(e)

    finally:

        time.sleep(10)

        if browser is not None:
            browser.quit() # 예외 발생해도 브라우져 자원 해제

if __name__ == '__main__':
    main()

# 뉴스 기사 모음 => 뉴스기사 웹크롤링 => ai api 요약 => 정리 csv 저장
























