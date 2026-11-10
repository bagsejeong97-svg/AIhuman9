# day10_ex.py
# 주제:
# CSV파일 > 데이터프레임, 데이터프레임 구조 확인 , 기초 통계, 데이터 사전

import pandas as pd #데이터 분석 라이브러리
from pathlib import Path # 경로 처리 라이브러리

DATA_FILE = Path('students.csv') # 실습용 CSV파일 경로
REPORT_FILE  = Path('students_dd.csv') #데이터 사전 CSV 파일 경로

# 출력시 구분선과 함꼐 출력하는 함수
def pp(*obj):
    print(obj)
    print('=' * 50)

# 실습용CSV파일 생성 함수

def create_sample_csv():
    sample_df = {
            "학생ID": ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008"],
            "이름": ["김민지", "박준호", "이서연", "최도윤", "정하은", "윤지호", "한유진", "오민석"],
            "전공": ["컴퓨터공학", "경영학", "통계학", "전자공학", "경영학", "컴퓨터공학", "디자인", "전자공학"],
            "Python점수": [88, 76, 95, 82, 91, 69, 84, 90],
            "AI점수": [91, 80, 93, 85, 89, 74, 88, 92],
            "출석률": [98.0, 94.5, 100.0, 96.0, 99.0, 91.5, 97.0, 98.5],
    }
    sample_df = pd.DataFrame(sample_df)
    #데이터 프레임 > CSV파일
    #index=false : 데이터프레임 생성시 생성된 행번호(index)는 CSV파일에 포함시키지 않음
    #encoding = 'utf-8-sig'  : BOM이 포함된 utf-8-sig로 인코딩
    sample_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    print(f'[CSV파일 생성]{DATA_FILE.resolve()}')   # 생성된 파일 경로 출력

if not DATA_FILE.exists():
    create_sample_csv()

# CSV파일 > 데이터프레임
df = pd.read_csv(DATA_FILE,encoding='utf-8-sig')

# 1. 데이터프레임 정보 출력

pp(df)
pp(type(df))  #<class 'pandas.DataFrame'>
pp(df.head())  # 상위 5개행  ()미입력시 기본 5 설정됨  (0 ~ 4)
pp(df.tail())    # head와 반대로 아래 5개행 (-1 ~ -5)

pp('모양: ', df.shape)  #(8,6) 2차원 데이터
pp('행의수 :',df.shape[0]) # 8
pp('열의수 :',df.shape[1]) # 6

pp('차원의수 :', df.ndim) # 2
pp('전체 요소 수 :', df.size) #48
#('컬럼의 목록 :', ['학생ID', '이름', '전공', 'Python점수', 'AI점수', '출석률'])
pp('컬럼의 목록 :', list(df.columns))
# ('인덱스 :', RangeIndex(start=0, stop=8, step=1))
pp('인덱스 :', df.index)  # 0부터 7까지 1씩 증가

pp('컬럼의 데이터 타입',df.dtypes)


# 전체 데이터 구조 확인
# 데이터타입, 데이터 건수, 인덱스 범위 , 컬럼수, 컬럼명, 결측치수, 컬럼타입, 메모리 사용량
df.info() # print() 없이 사용해야함

# 기초통계값 : 수치데이터컬럼에 대해 기초통계
# count(null이 아닌 데이터 개수), mean(산술평균), std(표준 편차),
# min(최소값), 25%(1사분위수), 50%(중앙값), 75%(3사분위수), max(최대값)
pp(df.describe())

# 2. 컬럼 일부 추출

python_score = df['Python점수'] # Python 점수 컬럼만 추출
pp(type(python_score))  # 한 컬럼의 타입은 시리즈 <class 'pandas.Series'>

score_df = df[['이름', 'Python점수', 'AI점수'
]]
pp(type(score_df))  # 2개 이상 컬럼의 타입은 데이터프레임 <class 'pandas.DataFrame'>

# 3. 집계 함수 (aggregation function : 여러 데이터로 하나의 결과를 내는 함수)
pp('합계: ',python_score.sum()) #  , 675
pp('평균: ',python_score.mean()) #  , 84.375
pp('중앙값: ',python_score.median()) #  , 86.0
pp('최소값: ',python_score.min()) #   69
pp('최대값: ',python_score.max()) #  , 95
pp('개수: ',python_score.count()) #  , 8


# 4. 범주형 데이터

#['컴퓨터공학', '경영학', '통계학', '전자공학', '디자인'], 유일한 값들
pp('고유 전공: ', df['전공'].unique())

# 유일한 값들의 수
pp('고유 전공의 수: ', df['전공'].nunique()) #5

# 범주형 데이터의 빈도 수
pp(df['전공'].value_counts()) # 전공별 개수

# 5. usecols, nrows

# 전체CSV에서 3개 컬럼으로 구성된 데이터 프레임 생성
selected_df = pd.read_csv(
    DATA_FILE,
    encoding='utf-8-sig',
    usecols=['이름','Python점수','AI점수'] # 3개 컬럼만 사용
)

pp(selected_df)

# 전체  CSV에서 3개 행으로 구성된 데이터 프레임 생성
first_three_df = pd.read_csv(
    DATA_FILE,
    encoding='utf-8-sig',
    nrows=3   #3개 행만 사용
)

pp(first_three_df)

#6. 데이터 사전

# 컬럼별 점검 결과를 담을 리스트 생성
data_dictionary_rows = []

for column in df.columns:  # 컬럼 수만큼 반복
    example_value = df[column].iloc[0] # 시리즈 첫번째 값
    data_dictionary_rows.append({
        '컬럼명 ' : column,
        'dtype ' : str(df[column].dtype),
        '전체행수 ' : len(df[column]),
        'Non-Null개수 :': df[column].count(),
        '고유갑수:': df[column].nunique,
        '예시값:': example_value
    })

# 리스트 > 데이터 프레임
data_dictionary = pd.DataFrame(data_dictionary_rows)
pp(data_dictionary)

# 데이터 사전  CSV생성
data_dictionary.to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
pp(f'[데이터사전 파일저장 {REPORT_FILE.resolve()}]')



















































































