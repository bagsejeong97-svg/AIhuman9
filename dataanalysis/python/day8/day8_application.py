# day8_application



class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    def grade(self):
        if self.score >= 80:
            return  'PASS'
        else:
            return  'RETRY'

    def show(self):
        print(f'이름: {self.name},점수: {self.score},결과: {self.grade()}')


student1 = Student('김민수',85)
student2 = Student('이서연',92)
student3 = Student('박지훈',76)
student4 = Student('정하늘',88)

students = [student1, student2, student3, student4]

for student in students:
    student.show()





























