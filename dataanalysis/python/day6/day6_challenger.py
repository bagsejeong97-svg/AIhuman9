#day6_ challenger

students = [
    {"name": "김민수", "scores": [85, 90, 78]},
    {"name": "이서연", "scores": [95, 92, 92]},
    {"name": "박준호", "scores": [70, 68, 68]},
    {"name": "최지우", "scores": [82, 88, 91]}
]

# 성적리시트를 받아서 합계 구하고 평균 반환하는 함수
def get_average(scores):
    total = 0
    for score in scores:
        total += score
    return total/len(scores)

# 등급 반환
def get_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

# 학생 한명의 출력용 리포트 문자열을 만드는 함수
def make_report(students):
    average = get_average(student['scores'])  #평균
    grade = get_grade(average)  # 등급
    return f'{student['name']} | 평균 : {average:.1f} | 등급: {grade}'

# 전체 학생 평균울 계산하는 함수
def get_class_average(student_list):
    total_average = 0 # 학생별 평균의 합
    for student in student_list:
        average = get_average(student['scores'])   # 학생 한명의 평균
        total_average += average  # 평균의 전체 합
    return total_average/len(student_list) # 전체 학생 평균

# 레포트 출력

for student in students:
    print(make_report(student))
# 전체 학생 평균
print(f' 전체 학생 평균 : {get_class_average(students):.1f}')




































