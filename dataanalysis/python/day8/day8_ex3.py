# day8 ex3
# 상속, 오버라이딩


# 상위 클래스 : 추상적, 설계의 개념, 공통의 개념
class Animal:
    def __init__(self,name):
        self.name = name
    def sound(self):
        print('동물소리???')

# Animal 을 상속 받은 하위 클래스 Dog
# 하위 클래스 : 구체적, 구현의 개념, 개별의 개념
# Animal에 있는 name과  sound를 정희하지 않아도 사용 가능
class Dog(Animal):
    type = '강아지'
    # 메소드 오버라이딩 : 상위클래스의 메소드를 재구현해서 다른 기능을 정의
    def sound(self):
        print(f'{self.name}은 {Dog.type}이며 멍멍 소리를 냅니다.')


class Cat(Animal):
    type = '고양이'

    # 메소드 오버라이딩 : 상위클래스의 메소드를 재구현해서 다른 기능을 정의
    def sound(self):
        print(f'{self.name}은 {Cat.type}이며 야옹 소리를 냅니다.')


# Animal을 상속 받은 타입들의 리스트
animals = [Dog('초코'),
           Cat('나비'),
           Dog('뽀미'),
           Cat('푸딩')
        ]

# 다른 타입일지라도  Animal을 상속받은 타입은 sound 메소드로 각자의 소리를 낼수 있음
#오버라이딩의 목적이자 존재 이유
for animal in animals:
    animal.sound()






class Student:
    def grade(self):
        if self.score >= 80:
            return "PASS"
        return "RETRY"

student = Student()
student.score = 75
print(student.grade())


























