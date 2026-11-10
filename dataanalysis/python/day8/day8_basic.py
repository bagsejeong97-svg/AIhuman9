# basic
class Student:
    def __init__(self,name,score):
        self.name = name
        self.score = int(score)

student1 = Student("김민수", 85)
student2 = Student("이서연", 92)
print(f'{student1.name},{student1.score}점')
print(f'{student2.name},{student2.score}점')
























