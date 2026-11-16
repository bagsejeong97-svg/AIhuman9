# dynamic_crawling_prac.py
# SauceDemo 로그인 > 메뉴 클릭 > 상품 정렬 > Excel 저장

# 공개 테스트 사이트: https://www.saucedemo.com/

import os
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from util.print_util import pp, up

URL = "https://www.saucedemo.com/"

USERNAME = os.getenv("SAUCEDEMO_USERNAME", "standard_user")
PASSWORD = os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce")

HEADLESS = False  # True: Chrome 창을 표시하지 않음
WAIT_SECONDS = 20  # JavaScript 콘텐츠의 최대 대기 시간(초)

SORT_VALUE = "lohi"  # az: 이름 오름차순, lohi: 가격 오름차순

ROOT = Path(__file__).resolve().parent
SAVE_PATH = ROOT / "saucedemo_products.xlsx"

COLUMNS = ["상품명", "설명", "가격(USD)", "정렬방식"]

# Chrome 브라우저를 실행하는 함수
# 반환값: webdriver.Chrome, 웹사이트 탐색에 사용할 브라우저
def create_browser():
    options = Options()  # Chrome 실행 옵션
    options.add_argument("--window-size=1400,900")
    if HEADLESS:
        options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(45)  # 네트워크 로딩 제한
    return browser

# 공개 데모 사이트에 로그인하는 함수
# browser: webdriver.Chrome, 실행 중인 브라우저
# wait: WebDriverWait, 화면 요소가 나타날 때까지 기다리는 객체
def login(browser, wait):
    browser.get(URL)  # 로그인 주소로 이동
    user = wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, "#user-name"
    )))  # 아이디 입력창이 표시될 때까지 대기
    user.send_keys(USERNAME)  # 아이디 입력
    browser.find_element(By.CSS_SELECTOR, "#password").send_keys(PASSWORD)
    browser.find_element(By.CSS_SELECTOR, "#login-button").click()
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, ".inventory_list"
    )))  # 로그인 완료 시 상품 리스트 표시
    pp("[로그인] SauceDemo 상품 화면 접속 성공")

# 햄버거 메뉴를 열어 All Items를 클릭하는 함수
# browser: webdriver.Chrome, 브라우저 제어 객체
# wait: WebDriverWait, 메뉴가 클릭 가능해질 때까지 대기
def open_all_items(browser, wait):
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#react-burger-menu-btn"
    ))).click()  # 좌측 메뉴 열기
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#inventory_sidebar_link"
    ))).click()  # All Items 선택
    wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, ".inventory_list"
    )))
    pp("[메뉴] All Items 클릭 완료")

# 상품 정렬 메뉴에서 지정한 정렬 방식을 선택하는 함수
# browser: webdriver.Chrome, 현재 상품 목록이 열린 브라우저
# wait: WebDriverWait, 드롭다운이 표시될 때까지 대기
# sort_value: str, az/za/lohi/hilo 중 하나
def sort_products(browser, wait, sort_value):
    allowed = {"az", "za", "lohi", "hilo"}
    if sort_value not in allowed:
        raise ValueError(f"지원하지 않는 정렬 방식: {sort_value}")
    dropdown = wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, "select.product_sort_container"
    )))
    Select(dropdown).select_by_value(sort_value)  # value 속성으로 선택
    wait.until(lambda d: Select(d.find_element(
        By.CSS_SELECTOR, "select.product_sort_container"
    )).first_selected_option.get_attribute("value") == sort_value)
    pp(f"[정렬] 적용한 정렬 방식: {sort_value}")

# 표시된 상품 목록에서 이름·설명·가격을 추출하는 함수
# browser: webdriver.Chrome, 상품 목록이 열린 브라우저
# wait: WebDriverWait, 상품 카드 렌더링을 기다리는 객체
# 반환값 : list[dict], 각 상품 정보를 저장한 사전들의 목록
def collect_products(browser, wait):
    wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, ".inventory_item"
    )))  # JavaScript로 생성된 상품 카드 대기
    cards = browser.find_elements(By.CSS_SELECTOR, ".inventory_item")
    records = []
    for card in cards:
        name = card.find_element(
            By.CSS_SELECTOR, ".inventory_item_name"
        ).text.strip()  # 상품명
        description = card.find_element(
            By.CSS_SELECTOR, ".inventory_item_desc"
        ).text.strip()  # 설명
        price_text = card.find_element(
            By.CSS_SELECTOR, ".inventory_item_price"
        ).text.strip()  # 예: $29.99
        price = float(price_text.replace("$", "").replace(",", ""))
        records.append({
            "상품명": name, "설명": description,
            "가격(USD)": price, "정렬방식": SORT_VALUE,
        })
    return records

# 추출한 상품 목록을 Excel로 저장하는 함수
# records: list[dict], 상품명·설명·가격이 포함된 목록
# 반환값: Path, 생성한 Excel 파일 경로
def save_excel(records):
    frame = pd.DataFrame(records, columns=COLUMNS)
    with pd.ExcelWriter(SAVE_PATH, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="상품목록", index=False)
        sheet = writer.sheets["상품목록"]
        sheet.freeze_panes = "A2"  # 첫 번째 행 고정
        sheet.auto_filter.ref = sheet.dimensions  # 필터 활성화
        for column, width in zip("ABCD", [35, 70, 18, 18]):
            sheet.column_dimensions[column].width = width
        for cell in sheet["C"][1:]:
            cell.number_format = '#,##0.00'  # 달러 가격 소수점 2자리
    return SAVE_PATH

def main():

    browser = None

    try:

        browser = create_browser()

        wait = WebDriverWait(browser, WAIT_SECONDS)

        login(browser, wait)

        open_all_items(browser, wait)

        sort_products(browser, wait, SORT_VALUE)

        records = collect_products(browser, wait)

        if not records:
            pp("[안내] 수집된 상품이 없습니다.")
            return

        frame = pd.DataFrame(records, columns=COLUMNS)
        pp(frame.to_string(index=False))  # 상품 전체를 콘솔에 출력

        saved = save_excel(records)
        pp(f"[완료] 상품 {len(records)}개, 저장 경로: {saved}")

    except (TimeoutException, WebDriverException, ValueError) as exc:

        pp(f"[오류] 실습 실행 실패: {exc}")

        if browser is not None:
            error_file = ROOT / "saucedemo_error.png"
            browser.save_screenshot(str(error_file))  # 문제 화면 저장
            pp(f"[오류 화면] {error_file}")
        raise
    finally:
        if browser is not None:
            browser.quit()  # 작업 종료 시 Chrome 정리

if __name__ == "__main__":
    main()

up(5)














