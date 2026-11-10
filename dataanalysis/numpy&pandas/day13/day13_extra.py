# # day13_extra
# # 정규 표현식 추가 실습
from util.print_util import pp

pp()

import re
#
# # 1.문자열에서 숫자만 추출



# 1. 문자열에서 숫자만 추출
# 다음 문자열에서 모든 숫자 덩어리를 찾아 리스트로 출력하세요.
text = '상품번호 A123, 가격 25000원'
pp(re.findall(r'\d+', text))




# 2. 문자열에서 한글만 추출
# 다음 문자열에서 한글로 이루어진 문자열만 찾아 출력하세요.
text = 'Python 파이썬 Java 자바 123'
pp(re.findall(r'[가-힣]+', text))


# 3. 영문 단어만 추출
# 다음 문자열에서 영문자로 이루어진 단어만 찾아 출력하세요.
text = 'Python 파이썬 Java 자바 AI 인공지능'
pp(re.findall(r'[a-zA-z]+', text))


# 4. 공백 제거
# 다음 문자열의 모든 공백을 제거하세요.
text = '파이썬 데이터 분석 수업'
pp(re.sub(r'\s','',text))


# 5. 숫자 제거
# 다음 문자열에서 모든 숫자를 제거하세요.
text = 'Python3 Java17 HTML5 CSS3'
pp(re.sub(r'\d+','',text))


# 6. 특정 단어 존재 여부 확인
# 다음 문자열에 'Python'이라는 단어가 존재하는지 확인하세요.
text = '오늘은 Python 정규표현식을 공부합니다.'
pp('있음' if re.search(r'Python', text) else '없음')


# 7. 특정 문자열로 시작하는지 확인
# 다음 문자열이 'Python'으로 시작하는지 정규표현식을 이용하여 검사하세요.
text = 'Python은 데이터 분석에 많이 사용됩니다.'
pp('시작함' if re.search(r'^Python', text) else 'X')
# [^a] : a 가 아닌 문자 하나


# 8. 특정 확장자로 끝나는지 확인
# 다음 파일명이 '.pdf'로 끝나는지 확인하세요.
filename = 'report.pdf'
pp('끝남' if re.search(r'\.pdf$', filename) else 'X')
# . : 특정 문자하나, \. : .문자 자체


# 9. 전화번호에서 숫자 추출
# 다음 문자열에서 전화번호의 각 숫자 영역을 추출하세요.
text = '연락처: 010-1234-5678'
pp(re.findall(r'\d+', text))


# 10. 여러 개의 연속된 공백을 하나로 변경
# 다음 문자열의 연속된 공백을 공백 하나로 변경하세요.
text = 'Python    Java   C++     AI'
pp(re.sub(r'\s+',' ',text))


# 11. 이메일 주소 찾기
# 다음 문자열에서 이메일 주소를 모두 추출하세요.
text = '문의: test@example.com 또는 admin@company.co.kr'
pp(re.findall(r'[\w.-]+@[\w.-]+\.[a-zA-z]+',text))


# 12. 휴대전화 번호 찾기
# 다음 문자열에서 010-0000-0000 형식의 휴대전화 번호만 추출하세요.
text = '''
홍길동 010-1234-5678
김철수 02-123-4567
이영희 010-9876-5432
'''
pp(re.findall(r'010-\d{4}-\d{4}', text))


# 13. 날짜 찾기
# 다음 문자열에서 YYYY-MM-DD 형식의 날짜를 모두 찾으세요
text = '회의일은 2026-09-15이고 다음 회의는 2026-10-03입니다.'
pp(re.findall(r'\d{4}-\d{2}-\d{2}', text))


# 14. 주민등록번호 일부 마스킹
# 다음 문자열에서 주민등록번호 뒤의 7자리를 '*' 문자 7개로 변경하세요.
text = '주민번호: 900101-1234567'
pp(re.sub(r'(\d{6})-\d{7}',r'\1-*******',text))


# 15. HTML 태그 제거
# 다음 문자열에서 HTML 태그를 모두 제거하여 텍스트만 남기세요.
text = '<h1>Python</h1><p>정규표현식 학습</p>'
pp(re.sub(r'<[^>]+>','',text))
# <[^>]+> : <문자가 나오고 >문자가 아닌 문자가 1개 이상 나오고 > 문자 나오는 패턴

# 16. 상품코드 검증
# 상품코드는 다음 규칙을 만족해야 합니다.
# - 영문 대문자 2자리
# - 숫자 4자리
# 다음 문자열들이 올바른 상품코드인지 검사하세요.
codes = ['AB1234', 'A1234', 'abc1234', 'XY9999']

for code in codes:
    if re.search(r'^[A-Z]{2}\d{4}$', code):
        pp(code,':정상')
    else:
        pp(code,':비정상')
# ^[A-Z]{2}\d{4}$ : 대문자 2개로 시작하고 숫자 4 개로 끝나는 패턴

# 17. 전화번호 그룹 분리
# 다음 전화번호를 정규표현식의 캡처 그룹 ()을 사용하여 3부분으로 분리하세요.
phone = '010-1234-5678'
match = re.search(r'(\d{3})-(\d{4})-(\d{4})', phone)
pp(type(match)) #<class 're.Match'>
if match:
    print('통신번호: ',match.group(1))
    print('중간번호: ',match.group(2))
    print('끝번호: ',match.group(3))

# 18. 날짜 형식 변경
#
# 다음 문자열의 날짜를 YYYY-MM-DD 형식에서
# YYYY년 MM월 DD일 형식으로 변경하세요.
text = '오늘 날짜는 2026-09-09입니다.'
pp(re.sub(r'(\d{4})-(\d{2})-(\d{2})',r'\1년-\2월-\3일',text))


# 19. 비밀번호 형식 검사
#
# 비밀번호는 다음 조건을 모두 만족해야 합니다.
# - 8자 이상
# - 영문 대문자 최소 1개
# - 영문 소문자 최소 1개
# - 숫자 최소 1개
# 다음 비밀번호들을 검사하세요.
passwords = [
    'Python123',
    'python123',
    'PYTHON123',
    'Py123',
    'Data2026AI'
]

for password in passwords:
    length_ok = len(password) >= 8   # 8자 이상
    upper_ok = re.search(r'[A-Z]', password)   # 대문자가 최소 1개이상
    lower_ok = re.search(r'[a-z]', password)  # 소문자가 최소 1개이상
    num_ok = re.search(r'[\d]', password)  # 숫자가 최소 1개 이상
    if length_ok and upper_ok and lower_ok and num_ok: # 3개지 조건 모두 만족
        pp(password,'정상')
    else:
        pp(password,'비정상')


# 20. 로그 데이터 분석
# 다음 로그 데이터가 있습니다.

# 1) 모든 날짜 2) 모든 시간 3) ERROR가 발생한 행 4) 모든 사용자 이름
logs = '''
2026-09-09 10:15:20 INFO user=kim login success
2026-09-09 10:16:32 ERROR user=lee database connection failed
2026-09-09 10:18:05 INFO user=park logout
2026-09-09 10:20:41 ERROR user=kim file not found
'''
# 정규표현식을 사용하여 다음 정보를 추출하세요.

pp(re.findall(r'\d{4}-\d{2}-\d{2}', logs))
pp(re.findall(r'\d{2}:\d{2}:\d{2}', logs))

pp(re.findall(r'^.*ERROR.*$', logs,
              flags=re.MULTILINE)) # .* : 문자 하나가 0 개 이상 반복

pp(re.findall(r'user=(\w+)', logs))  # user=(\w+) : user = 뒤에 나온 문자 캡춰



































