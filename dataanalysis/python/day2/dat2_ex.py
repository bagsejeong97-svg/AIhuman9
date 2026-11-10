# day2_ex.py
#Python 실행 흐름, 변수, 자료형, type()

#1. Python 코드 실행 흐름
print('실습 시작')
print('Python 코드는 기본적으로 코드의 위에서 아래로 읽어가면서 실행됨')

#2. 리터럴과 변수
name = '홍길동' # 홍길동이라는 문자열 타입의 값을 name변수가 가르킨다
age = 22 # 22라는 정수타입의 값을 age라는 변수가 가르킨다
score = 85.5 # 85.5라는 실수 타입의 값을 score 변수가 가르킨
is_job_seeker  = True # True 라는 불리언 타입의 값을 is_job_seeker 변수가 가르킨다.
portfolio_url = None #None 이라는   NoneType의 값을 portfolio_url  변수가 가르킴

# 3. 변수의 값과 타입을 확인
print(name, type(name))
print(age, type(age))
print(score, type(score))
print(is_job_seeker, type(is_job_seeker))
print(portfolio_url, type(portfolio_url))

# 4.  변수에 값 재할당
status = '준비중'
print(status)
status = '학습중'
print(status)

# 5. 동적 타이핑  (실행중 변수타입이 바뀜)
data = 100 # int
print(data,type(data))
data = '백'
print(data,type(data))
data = True
print(data,type(data))

# 6. 변수명은 의미 있게 만드는게 중요
student_name = '김AI'
student_age = 24
desired_job = '데이터 분석가'
python_experience_years = 0.5 #  길 더라도 의미있는 이름이 좋은 이름
is_major = False

# 7. f-string으로 개인 프로필 출력
# f-string : 문자열 앞에f를 사용, 변수의 값이나 연산결과를 포함
print('\n === 개인 프로필 ===') # \n : newline, 줄바꿈 문자
print(f'이름 : {student_name}')
print(f'나이 : {student_age}')
print(f'희망 직무 : {desired_job}')
print(f'파이썬 경력 년수 : {python_experience_years}')
print(f'전공 여부 : {is_major}')
print(f'10년 후 나이 : {student_age + 10}')

# 8. 변수와 값의 참조(가리킴)
# 기본겂의 경우는 값복사 (value copy)가 일어남
first_score = 90
second_score = first_score #first_score = 90 , second_score = 90
print(first_score)
print(second_score)
second_score = 50  # first_score = 90, second_scre = 50
print(first_score)
print(second_score)
first_score = 30
print(first_score)
print(second_score)

# 9. 흔한 오류
# 2name = '홍길동'  # SyntaxError: invalid decimal literal
# job = ai개발자 # NameError: name 'ai개발자' is not defined
# print(user_name)

# 10. 상수(constant)
# - 상수는 한번 값을 할당하면 할당된 값을 변경할 수 없는 변수
# - 상수는 대문자로 만드는 관례가 있음
PI = 3.141592
print(PI)
TOTAL_OF_STUDENT = 100
print(TOTAL_OF_STUDENT)

print('\n')
print('\n')


# 11. extra
oct_num = 0o10 # 8진 정수 10
print(oct_num, type(oct_num)) #8, int
hex_num = 0xff # 16진 정수 FF
print(hex_num, type(hex_num))# 255, int

# 진법, 진수 , 진법 변환
# 진법 : 수를 표현하는 방법
# 진수 : 진법에 의해서 사용되는 수
# 컴퓨터에서는 2, 8, 16 진법을 사용 , 일상 생활에서는 10 진법을 사용

# 진법 변환
# 1. 10진수를 다른진수로 바꿀때는 계속 잔법수로 나눠서 꺼꾸로 쓰기
# 2. 다른진수를 10 진수로 바꿀떄는 각 자리수에 진법수 제곱을 모두 더함




















