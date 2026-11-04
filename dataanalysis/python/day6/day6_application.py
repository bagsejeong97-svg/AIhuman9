#day6_application


students = {
    '김민수' : 87,
    '이서연' : 95,
    '박준호' : 73,
    '최지우' : 61,
    '정하늘' : 55
}
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


for name,score in students.items():
    grade = get_grade(score)
    print(f'{name} | {score}점 | {grade}등급')




























