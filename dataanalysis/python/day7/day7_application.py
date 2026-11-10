#day7_application
import csv

from pathlib import Path
# students = [
#     ['name','score'],
#     ['김민수',88],
#     ['이서연',93],
#     ['박지훈',76],
#     ['최유진',85]
# ]
# 파일 , csv 생성
DATA_DIR = Path('day7_application_data')
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / 'student_scores.csv' # CSV파일 경로

# 파일에 쓰는 함수
def create_smaple_csv(path):
    rows = [ #csv에저장할 2차원 리스트
        ['name','score'],
        ['김민수', 88],
        ['이서연', 93],
        ['박지훈', 76],
        ['최유진', 85]
    ]
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)   #writer 획득
        writer.writerows(rows)  #csv파일에쓰기

# 파일을 읽어서 데이터 리스트를 반환하는 함수
def load_scores(path):
    result = []  # 정상 데이터 저장할 리스트
    try:
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file) #reader 획득
            header = next(reader)   # 헤더 라인 건너뜀
            print('CSV 헤더 :', header)    # 헤더 출력  /  데이터 제목 출력
            for row in reader:     # 데이터행 반복
                name = row[0].strip()    #공백 제거후 이름
                score = int(row[1])  # 점수를 정수로 변환
                # 추출한 이름과 점수를 튜플로 만들어 result 리스트에 추가
                result.append([name, score])
    except FileNotFoundError:  # path 파일이 없을떄
        print('성적 파일을 찾을 수 없습니다.')
    except ValueError:  # int로 정수 변환할때
        print('점수는 숫자로 입력되어야 합니다.')
    return result  # 리스트 반환
if not CSV_PATH.exists(): # csv 경로가 없다면
    create_smaple_csv(CSV_PATH)  # 생성

scores = load_scores(CSV_PATH)  # 리스트 반환

if len(scores) > 0:  # 데이터가 있다면
    print('\n[학생별 점수]') # 제목 출력
    for name, score in scores: # 리스트내의 튜플 수만큼 반복
        print(f'{name}: {score}점')
    total = sum(score for name, score in scores)  # 총점
    average = total / len(scores)  # 평균
    print(f'\n평균 점수 : {average:.2f}점')
else:
    print('계산할 데이터가 없습니다.')










