# CSV 파일 처리를 위해 표준 라이브러리 csv 모듈을 가져옵니다.
import csv


# 테스트용 CSV 파일을 저장하는 함수를 정의합니다.
def save_sample_csv(path):
    # 헤더와 샘플 학생 데이터를 준비합니다.
    rows = [
        ["name", "score"],
        ["김민수", 88],
        ["이서연", 93],
        ["박지훈", 76],
        ["최유진", 85],
        ["오류데이터", "점수없음"],
        ["한지민", 91],
    ]

    # 전달받은 경로의 CSV 파일을 쓰기 모드로 엽니다.
    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        # CSV writer 객체를 만듭니다.
        writer = csv.writer(file)

        # 준비한 모든 행을 CSV 파일에 저장합니다.
        writer.writerows(rows)


# CSV 파일을 안전하게 읽는 함수를 정의합니다.
def load_score_csv(path):
    # 정상적으로 읽은 학생 데이터를 저장할 리스트를 만듭니다.
    result = []

    # 파일을 찾지 못할 가능성이 있으므로 try 블록을 사용합니다.
    try:
        # 전달받은 CSV 파일을 읽기 모드로 엽니다.
        with open(path, "r", encoding="utf-8-sig") as file:
            # CSV reader 객체를 만듭니다.
            reader = csv.reader(file)

            # 첫 번째 행을 헤더로 읽습니다.
            next(reader, None)

            # 실제 CSV 행 번호에 맞게 2부터 시작합니다.
            for row_number, row in enumerate(reader, start=2):
                # 필요한 열이 2개보다 적으면 잘못된 행으로 판단합니다.
                if len(row) < 2:
                    # 열 부족 오류를 안내합니다.
                    print(f"{row_number}행은 열 개수가 부족하므로 건너뜁니다.")

                    # 다음 행으로 이동합니다.
                    continue

                # 첫 번째 열의 이름을 앞뒤 공백 없이 가져옵니다.
                name = row[0].strip()

                # 두 번째 열의 점수 문자열을 가져옵니다.
                score_text = row[1].strip()

                # 각 행의 점수 변환 오류를 독립적으로 처리합니다.
                try:
                    # 점수 문자열을 정수로 변환합니다.
                    score = int(score_text)

                # 현재 행의 점수가 숫자가 아닐 때 처리합니다.
                except ValueError:
                    # 잘못된 행과 값을 구체적으로 안내합니다.
                    print(
                        f"{row_number}행의 점수 '{score_text}'은 숫자가 아니므로 건너뜁니다."
                    )

                    # 현재 행만 건너뛰고 다음 행으로 이동합니다.
                    continue

                # 이름 또는 점수가 정상적이면 결과 리스트에 추가합니다.
                result.append((name, score))

    # 파일 자체가 존재하지 않을 때 처리합니다.
    except FileNotFoundError:
        # 사용자가 확인해야 할 파일 경로를 함께 출력합니다.
        print(f"파일을 찾을 수 없습니다: {path}")

    # 파일 내용의 문자 인코딩을 해석할 수 없을 때 처리합니다.
    except UnicodeDecodeError:
        # 인코딩을 확인하라는 메시지를 출력합니다.
        print("CSV 파일의 문자 인코딩을 확인해 주세요.")

    # 정상적으로 수집한 학생 데이터 리스트를 반환합니다.
    return result