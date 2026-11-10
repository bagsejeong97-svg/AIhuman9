from pathlib import Path
import day7_challenge_utils as cutils

DATA_DIR = Path('day7_challenge_data')
DATA_DIR.mkdir( exist_ok=True)
CSV_PATH = DATA_DIR / 'challenge_score.csv'

if not CSV_PATH.exists():
    cutils.save_sample_csv(CSV_PATH)

students = cutils.load_score_csv(CSV_PATH)

if len(students) > 0:
    #리스,트 컴프리헨션
    # 리스트 생성시 반복문과 조건문 사용하는 파이썬다운 문법
    # students의 name, score에서 score들로 리스트를 구성
    scores = [score for name, score in students] # 점수 리스트
    student_count = len(scores) # 학생수
    total_score = sum(scores)
    average_score = total_score / student_count
    max_score = max(scores)
    min_score = min(scores)
    print(f'정상 학생수 : {student_count}명')
    print(f'평균 : {average_score:.2f}점')
    print(f'최고점 : {max_score}')
    print(f'최저점: {min_score}')

    print('\n[PASS 학생]')
    for name,score in students:
        if score >= 80:
            print(f'{name},{score}')
else:
    print('학생 데이터가 없어 통계를 계산하지 않습니다.')



















