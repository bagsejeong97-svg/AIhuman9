# day8_challenge

class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def show(self):
        print(f'{self.name},{self.score},{self.grade()}')


    def grade(self):
        if self.score >= 80:
            return  'PASS'
        else:
            return  'RETRY'


# # 전체 학생 정보
# def show_all_students(students):
#     for student in students:
#         student.show()

# PASS한 학생수
def show_pass_students(students):
    count = 0
    for student in students:
        if student.grade() == 'PASS':
            count += 1
    return count
# pass한 학생정보
def show_score_pass_students(students):
    for student in students:
        if student.grade() == 'PASS':
            student.show()

#  평균
def show_average(students):
    total = 0
    for student in students:
        total += student.score
    return total/len(students)





def save_report(students,filename):
    try:
        with open(filename,'w',encoding = 'utf-8') as file:
            file.write('[합격 학생]\n')
            for student in students:
                line = f'{student.name},{student.score},{student.grade()}\n'
                file.write(line)
            file.write(f'평균: {show_average(students):.1f}\n')
    except FileNotFoundError:
        print('파일을 찾을수 없습니다!')

# 메인 실행 함수
def main():
    student1 = Student('김민수', 85)
    student2 = Student('이서연', 92)
    student3 = Student('박지훈', 76)
    student4 = Student('정하늘', 88)
    student5 = Student('오세진', 69)

    students = [student1, student2, student3, student4, student5]
    save_report(students, 'day8_challenge_result.txt')

    with open('day8_challenge_result.txt', 'r', encoding ='utf-8') as file:
        line = file.readlines()
        print(line[0].strip())

    show_score_pass_students(students)
    pass_student = show_pass_students(students)
    average = show_average(students)
    print(f'전체 평균:{average:.1f}')
    print(f'합격한 학생수:{pass_student}')

main()

























