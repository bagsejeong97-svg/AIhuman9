# dynamic_crawling.py
# Selenium을 활용한 동적 크롤링
# OrangeHRM > 로그인 > PIM > Employee List > 전체 목록 > Excel 저장
# 설치: python -m pip install selenium pandas openpyxl
import time
import os
from pathlib import Path
import pandas as pd
from selenium import webdriver  # 웹브라우저 드라이버
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException, WebDriverException
)
from selenium.webdriver.chrome.options import Options  # 드라이버 옵션
from selenium.webdriver.common.by import By  # 셀렉터
from selenium.webdriver.support import expected_conditions as EC  # 대기 조건
from selenium.webdriver.support.ui import WebDriverWait  # 대기
from util.print_util import pp, up

# OrangeHRM 공개 데모 사이트
LOGIN_URL = 'https://opensource-demo.orangehrmlive.com/web/index.php/auth/login'
USERNAME = os.getenv('ORANGEHRM_USERNAME', 'Admin')
PASSWORD = os.getenv('ORANGEHRM_PASSWORD', 'admin123')
HEADLESS = False  # True: 브라우저 숨김
MAX_PAGES = 0  # 0이면 마지막 페이지까지
WAIT_SECONDS = 20  # 동적 화면 최대 대기 시간(초)
ROOT = Path(__file__).resolve().parent
SAVE_PATH = ROOT / 'orangehrm_employee_list.xlsx'
COLUMNS = ['사원번호', '이름', '직책', '고용상태', '부서', '상급자']

# Chrome 브라우저를 실행하는 함수
# 반환값 : webdriver.Chrome, Selenium 브라우저 제어 객체
def create_browser():
    options = Options()  # Chrome 옵션
    options.add_argument('--window-size=1500,950')
    if HEADLESS:
        options.add_argument('--headless=new')
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(45)
    return browser

# OrangeHRM 데모 계정으로 로그인하는 함수
# browser : webdriver.Chrome, 실행 중인 브라우저
# wait : WebDriverWait, 요소 표시를 기다리는 객체
# 반환값 : 없음
def login(browser, wait):
    browser.get(LOGIN_URL)
    name = wait.until(EC.visibility_of_element_located(
        (By.NAME, 'username')
    ))
    name.send_keys(USERNAME)
    browser.find_element(By.NAME, 'password').send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, 'button[type="submit"]'
    ))).click()
    wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'ul.oxd-main-menu'
    )))
    pp('[로그인 성공] 대시보드 접속')

# PIM 메뉴와 Employee List 메뉴를 차례로 클릭하는 함수
# browser : webdriver.Chrome, 실행 중인 브라우저
# wait : WebDriverWait, 클릭 가능한 시점을 기다리는 객체
# 반환값 : 없음
def open_employee_list(browser, wait):
    pim = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, 'a.oxd-main-menu-item[href*="/pim"]'
    )))
    pim.click()
    menus = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, 'a.oxd-topbar-body-nav-tab-item'
    )))
    for menu in menus:
        if menu.text.strip() == 'Employee List':
            wait.until(EC.element_to_be_clickable(menu)).click()
            break  # 일치하는 메뉴를 클릭했을 때만 반복 종료
        # break  # 이전 코드: if 밖이어서 첫 번째 메뉴에서 항상 종료
    else:
        raise TimeoutException('Employee List 메뉴를 찾지 못했습니다.')
    # wait.until(EC.visibility_of_element_located((
    #     By.CSS_SELECTOR, '.oxd-table'
    # )))
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-table-header'
    )))
    pp('[메뉴 이동] PIM > Employee List')

# 현재 페이지의 직원 행을 수집하는 함수
# browser : webdriver.Chrome, 직원 목록 화면
# wait : WebDriverWait, 화면 표시를 기다리는 객체
# page_number : int, 로그에 표시할 페이지 번호
# 반환값 : list[dict], 현재 페이지 직원 정보
def collect_page(browser, wait, page_number):
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-table-header'
    )))
    wait.until(EC.invisibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-loading-spinner'
    )))
    records = []
    cards = browser.find_elements(
        By.CSS_SELECTOR, '.oxd-table-body .oxd-table-card'
    )
    for card in cards:
        cells = card.find_elements(By.CSS_SELECTOR, '.oxd-table-cell')
        values = [cell.text.strip() for cell in cells]
        if len(values) < 8:  # 테이블이 아직 로딩되지 않았거나 빈 행
            continue
        datarow = {
            '사원번호': values[1],
            '이름': values[2] + ' ' + values[3],
            # '직무': values[4],  # 이전 코드: COLUMNS에는 '직책'이 있음
            '직책': values[4],
            '고용상태': values[5],
            '부서': values[6],
            '상급자': values[7]
        }
        # records.append(datarow)  # 이전 코드: 빈 행도 추가
        if datarow['사원번호'] or datarow['이름'].strip():
            records.append(datarow)
    return records

# 다음 페이지 버튼 클릭 후 실제 목록 변경까지 대기하는 함수
# browser : webdriver.Chrome, 현재 직원 목록 화면
# wait : WebDriverWait, 페이지 변경을 기다리는 객체
# 반환값 : bool, 이동 성공 True / 마지막 페이지 False
def click_next(browser, wait):
    # button = browser.find_element(
    #     By.CSS_SELECTOR,
    #     'button.oxd-pagination-page-item:has(i.bi-chevron-right)'
    # )  # 이전 코드: 마지막 페이지에 버튼이 없으면 예외 발생
    buttons = browser.find_elements(
        By.CSS_SELECTOR,
        'button.oxd-pagination-page-item:has(i.bi-chevron-right)'
    )
    # if not button:  # 이전 코드: find_element가 먼저 예외를 내므로 실행되지 않음
    #     return False
    if not buttons:
        return False
    button = buttons[-1]
    classes = button.get_attribute('class') or ''
    if not button.is_enabled() or '--disabled' in classes:
        return False
    old_cards = browser.find_elements(
        By.CSS_SELECTOR, '.oxd-table-body .oxd-table-card'
    )
    old_first = old_cards[0] if old_cards else None
    browser.execute_script(
        'arguments[0].scrollIntoView({block: "center"});', button
    )
    wait.until(EC.element_to_be_clickable(button)).click()
    if old_first is not None:
        wait.until(EC.staleness_of(old_first))
    wait.until(EC.invisibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-loading-spinner'
    )))
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '.oxd-table-header'
    )))
    return True

# 수집한 직원 목록을 Excel로 저장하는 함수
# records : list[dict], 여러 페이지의 직원 정보
# 반환값 : Path, 저장한 파일 경로
def save_excel(records):
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(records, columns=COLUMNS)
    pp(f'[저장 직전] {len(frame)}행 / '
       f'고유 사원번호 {frame["사원번호"].nunique()}건')
    with pd.ExcelWriter(SAVE_PATH, engine='openpyxl') as writer:
        frame.to_excel(writer, sheet_name='직원명단', index=False)
        sheet = writer.sheets['직원명단']
        sheet.freeze_panes = 'A2'
        sheet.auto_filter.ref = sheet.dimensions
        widths = [16, 44, 30, 25, 25, 25]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[
                sheet.cell(row=1, column=index).column_letter
            ].width = width
        for cell in sheet['A'][1:]:
            cell.number_format = '@'
    saved_count = len(pd.read_excel(SAVE_PATH, dtype={'사원번호': str}))
    pp(f'[저장 검증] Excel 데이터 {saved_count}행')
    if saved_count != len(frame):
        raise ValueError('Excel 저장 전후 행 수가 일치하지 않습니다.')
    return SAVE_PATH

# 로그인부터 전체 페이지 수집과 Excel 저장까지 실행하는 함수
# 반환값 : 없음
def main():
    browser = None
    records = []
    try:
        browser = create_browser()
        wait = WebDriverWait(browser, WAIT_SECONDS)
        login(browser, wait)
        open_employee_list(browser, wait)
        page_number = 1
        while True:
            current = collect_page(browser, wait, page_number)
            records.extend(current)
            # pp(f'[수집 {page_number} 페이지:{len(current)}명]')  # 이전 코드
            pp(f'[수집] {page_number}페이지: {len(current)}명 / '
               f'누적 {len(records)}명')
            if MAX_PAGES > 0 and page_number >= MAX_PAGES:
                break
            if not click_next(browser, wait):
                break
            page_number += 1
        if records:
            frame = pd.DataFrame(records, columns=COLUMNS)
            pp(frame.to_string(index=False))
            path = save_excel(records)
            # pp(f'[완료] {len(records)}행 수집 / Excel 저장:{path}')  # 이전 코드
            pp(f'[완료] {len(records)}행 / Excel 저장: {path}')
        else:
            pp('직원 목록이 없어서 Excel 저장하지 않음')
    # except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
    #     pp(e)  # 이전 코드: 오류 출력 후 정상 종료 처리
    except (TimeoutException, StaleElementReferenceException,
            WebDriverException) as e:
        pp(f'[브라우저 오류] {type(e).__name__}: {e}')
        raise
    finally:
        time.sleep(10)
        if browser is not None:
            # browser.quit()  # 이전 코드: 종료 자체에서 오류가 나면 원래 오류를 가림
            try:
                browser.quit()
            except WebDriverException:
                pass

if __name__ == '__main__':
    main()

up(5)
