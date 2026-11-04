# day7_basic


from pathlib import Path
DATA_DIR = Path('day7_basic_data') # 경로생성
DATA_DIR.mkdir(exist_ok = True) # 경로가 없으면 생성 # 디렉토리 생성
MEMO_PATH = DATA_DIR / 'learning_log.txt' # 학습 기록 파일 경로

# 파일에 추가할 문장
first_text = '과정명 : AI휴먼\n학습주제 : 파일 입출력과 예외처리\n핵심 개념 : with open()은 파일을 자동으로 닫아준다\n'

#f로 별명 짖은 파일 생성해서 첫번째 학습기록 쓰기 write
with open(MEMO_PATH, 'w' , encoding = 'utf-8') as f: # 덮어쓰기
    f.write(first_text)

# f로 별명짖은 파일의 추가할 내용 입력 append
with open(MEMO_PATH, 'a', encoding = 'utf-8') as f: # 추가 생성
    f.write('다음에 복습할 내용 : try -except')

# f로 별명 짖은 파일의 내욜 읽기
with open(MEMO_PATH, 'r', encoding = 'utf-8') as f:
    content = f.read() # 전체 읽기

print('저장 파일:', MEMO_PATH.resolve())
print('\n[학습기록]')
print(content)






































