#day6_extra

# numbers = [17, 5, 23, 9, 11]

# def find_min_max(numbers):
#     max1 = numbers[0]
#     min1 = numbers[0]
#     for i in numbers:
#         if i > max1:
#             max1 = i
#         if i < min1:
#             min1 = i
#     return max1, min1
# print(find_min_max(numbers))


# scores = [45, 72, 88, 59, 60, 91]
#
# def get_pass_scores(scores):
#     result = []
#     for score in scores:
#         if score >= 60:
#             result.append(score)
#     return result
# print(get_pass_scores(scores))

#
# def analyzetext(text):
#     str1 = len(text)
#     int1 = 0
#     null1 = 0
#     for text_date in text:
#         if text_date == ' ':
#             null1 += 1
#         if '0' <= text_date <= '9':
#             int1 += 1
#     null2 = str1 - null1
#     return {'전체문자수': str1,
#              '공백제외문자수' : null2,
#             '숫자개수': int1
#             }
#
# text = "Python 3 Function 2026"
# print(analyzetext(text))
#4
students = {
    "김철수": [80, 90, 70],
    "이영희": [95, 88, 92],
    "박민수": [60, 75, 68]
}
def calculate_student(name, scores):
    total = 0
    for score in scores:
         total += score       # 합계
    average = total / len(scores)      # 평균
    return  {
            '이름': name,
            '총점' : total,
            '평균' : average
        }

for name, scores in students.items():
    print(calculate_student(name, scores))

#5
def sum_all(*args):
    total = 0
    for number in args:
        total += number
    return total

print(sum_all(3, 4, 5, 6))
print(sum_all(1,2,3, 4, 5, 6))

# 6
# bonus_rate 파라미터에 인수가 전달되면 인수사용 아니면 0.1 사용
def calculare_salary(base_salary, bonus_rate: float= 0.1):
    final_salary = base_salary  + (base_salary * bonus_rate)
    return final_salary
# 숫자 세자리마다 _ 사용 가능
print(calculare_salary(3_000_000))
print(calculare_salary(3_000_000,0.2))

# 7
students = {
    "김철수": 85,
    "이영희": 92,
    "박민수": 76,
    "최지우": 64
}

def get_grade(socre):
    if socre >= 90:
        return "A"
    elif socre >= 80:
        return "B"
    elif socre >= 70:
        return "C"
    elif socre >= 60:
        return "D"
    else:
        return "F"

def make_report(students):
    report = []  # 결과 저장할 리스트
    for name, score in students.items():
        grade = get_grade(score)
        line = f"{name} : {score}점 / {grade}"
        report.append(line)
    return report
rsult = make_report(students)

for line in rsult:
    print(line)

# 8
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

# 고차함수 : 두인수와 콜백함수를 파라미터로
def calculate(a, b, operation):
    return operation(a, b)  # 콜백 함수에 두 인수를 전달해 처리한 결과를 리턴

print(calculate(10, 5, add))
print(calculate(10, 5, subtract))
print(calculate(10, 5, multiply))


# 9
def payment_complete(order_name):
    print(f'[{order_name}] 결제가 완료되엇습니다')

def send_message(order_name):
    print(f'[{order_name}] 주문 완료 메세지를 전송했습니다')

def process_order(order_name, callback):
    print(f'[{order_name}] 주문을 처리합니다')
    callback(order_name)

process_order('노트북', payment_complete)
process_order('키보드', send_message)

# 10.
scores = [55, 72, 88, 91, 67, 100, 83]

def is_pass(score):
    return score >= 60

def is_excellent(score):
    return score >= 90

# 고차 함수 : 점수리스트와 콜백함수를 파라미터로
def filter_scores(scores, condition):
    result = []
    for score in scores:
        if condition(score): # 콜백함수에 점수를 전달하고 받은 리턴값으로 분기
            result.append(score) # 조건 만족시 리스트에 추가
    return result


# 제목과 결과 출력 함수
def print_result(title,result):
    print(f"{title} : {result}")

# 고차함수 : 점수리스트, 점수판정콜백함수, 콜백함수, 제목 파라미터로
def process_scores(scores, condition, callback, title):
    filtered_scores = filter_scores(scores, condition) # 조건 만족 점수리스트
    callback(title, filtered_scores)# 콜백함수에 제목과 조건 만족 점수리스트를 인수로 호출
    return filtered_scores

process_scores(scores,is_pass, print_result,'합격자 점수')
process_scores(scores,is_excellent, print_result,'우수자 점수')




















