#day8_ex1
# 클래스, 객체, 인스턴스, 속성(인스턴스 변수), 기능(메서드), 생성자

# 클래스 정의 = 사용자 정의 타입(UDT : User Defined Type) 생성
class Student:
    # 생성자 (Constructor)
    # 역할 : 객체가 가지는 인스턴스 변수의 값을 초기화
    # self.name, self.score : 인스턴스 변수
    # name, score : 생성자 파라미터
    def __init__(self,name,score):
        self.name = name
        self.score = score

    # 메소드 (method) : 객체로 접근하는 함수
    def grade(self):
        if self.score >= 80:
            return 'PASS'
        else:
            return 'RETRY'

    def show(self):
        print(f'이름: {self.name}, 점수 : {self.score}, 결과 : {self.grade()}')

# 객체 리스트를 받아서 전체학생들의  정보를 출력하는 함수
def show_all_students(students):
    print('\n[전체 학생]')
    for student in students:  # 학생 수만큼 반복
        student.show()

# 객체 리스트를 받아서 합격한 학생들의 정보를 출력하는 함수
def show_pass_students(students):
        print('\n[합격 학생]')
        for student in students:
            if student.grade() == 'PASS':
                student.show()
# 전체 한색들의 점수의 평균을 반환하는 함수
def get_average(students):
    total = 0
    for student in students:
        total += student.score
    return total/len(students)
# 학생 리슽와 파일명을 전달 받아 출력하고 레포트 저장하는 함수
def save_report(students, filename):
    try:
        with open(filename,'w', encoding = 'utf-8') as file:
            file.write('[학생 성적 결과]\n')
            for student in students:
                line = f'{student.name},{student.score},{student.grade()}\n'
                file.write(line)
            file.write(f'평균,{get_average(students):.1f}\n')
        print(f'\n결과가{filename}파일에 저장되었습니다.')
    except FileNotFoundError:
        print(f' 파일을 찾을 수 없습니다!')

# main실행 함수
def main():

    student1 = Student('김민수', 85)
    student2 = Student('이서연', 92)
    student3 = Student('박지훈', 76)
    student4 = Student('정하늘', 88)

    # 객체 4개로 된 리스트
    students = [student1,student2,student3,student4]

    show_all_students(students) # 모든 학생 정보 출력

    show_pass_students(students) # 합격 학생 정보 출력

    average = get_average(students)  # 평균

    print(f'\n전체 평균 : {average:.1f}')

    save_report(students, 'day8_result.txt')
# 현재 파일이 메인모듈이면 main() 함수를 실행
# __name__ : 현재 모듈명
if __name__ == '__main__':
    main()

























































































