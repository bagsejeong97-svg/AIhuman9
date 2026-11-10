# day5 ex_3
# 리스트, 딕셔너리, 셋 주요 메소드

# 1. list의 주요 메소드

fruits = ['apple', 'banana', 'orange']
print(fruits)

fruits.append('grape')   # 요소를 맨뒤에 추가
print(fruits)

fruits.extend(['kiwi', ' melon'])  # 리스트의 요소를 꺼내서 추가
print(fruits)

fruits.insert(1, 'mango') # 인덱스에 요소 추가
print(fruits)

fruits.remove('banana') # 요소제거
print(fruits)

removed = fruits.pop(1) # 인덱스의 요소 제거하고 제거된 요소를 반환
print(fruits, removed)

print(fruits.index('orange')) #요소의 인덱스
# print(fruits.index('watermelon')) #요소의 없는 인덱스 ValueError

numbers = [1,2,2,3,2,4]
print(numbers.count(2))# 2라는 요소의 개수

# list.sort() : 리스트 자체를 정렬함, 정렬한 후에 원래 리스트를 알 수 없음
# sorted() 함수 : 원본 리스트 보존하고 새로 정렬된 리스트를 만듬
scores = [75,90,65,100,85]
scores.sort()  # 요소들을 오름차순 정렬
print(scores)
scores.sort(reverse=True)  # 요소들을 내림차순 정렬
print(scores)

scores.reverse() #요소의 순서를 180도 뒤집음
print(scores)

# 깊은 복사 (deep copy) : 메모리를 복사 , 메모리에 원본 2개, 변수 2개
# 얕은 복사 (shallow copy) : 참조만 복사 메모리에 원본 1개, 변수 2개
scores_copy = scores.copy() #리스트 복사(얕은 복사)
print(f'원본리스트 : {scores}')
print(f'복사리스트 : {scores_copy}')

temp = [1,2,3]
temp.clear() # 모든 요소 제거
print(temp) # empty list : 요소가 없는 리스트

# 2. dictionary 주요 메소드

students = {
    'name' : '홍길동',
    'age' : 25,
    'score' : 90
}
print(students)

print(students.keys())
print(type(students.keys())) #dict_keys'
print(list(students.keys()))

print(students.values())
print(type(students.values())) #dict_values
print(list(students.values()))


print(students.items())
print(type(students.items())) #dict_items
print(list(students.items())) #[('name', '홍길동'), ('age', 25), ('score', 90)]

print(students.get('name')) # 키에 매칭된 값 획득
print(students.get('address')) # 없는 키 입력시 None
print(students.get('hobby','축구')) # 키가 없으면 뒤의 기본값 획득


# 키가 있으면 값을 수정, 키가 없으면 아이템 생성
students.update({
    'score' : 95,  # 키가 있으니 값을 수정
    'grade' : 'A'  # 키가 없으니 아이템 생성
})
print(students)

students.setdefault('city', '서울')  # 키가 없으면 기본값을 추가
print(students)
students.setdefault('score',0) # 키가 있으면 값 변경 불가
print(students)

# 키에 해당하는 아아팀을 제거하고 값을 반환
removed_value = students.pop('age')
print(students, removed_value)

#마지막 아이템 제거후 튜플로 변환
last_item = students.popitem()
print(students, last_item)


students_copy = students.copy()  # 옅은 복사
print(students ,students_copy)

temp_dict = {'a' : 1 , 'b' : 2}
temp_dict.clear() #모든 아이템 제거
print(temp_dict) # 아이템이 없는 딕셔너리 (empty dictionary)

# 3. set 주요 메소드

numbers = {1,2,3,4}
print(numbers)

numbers.add(5) #요소 추가
print(numbers)

numbers.update([6,7,8])# 여러 요소 추가
print(numbers)

numbers.remove(3) # 요소 삭제
print(numbers)

numbers.discard(100) # 요소가 있으면 삭제 없어도 error 미발생

remove_value = numbers.pop()  # 임의의 요소를 삭제하고 삭제되니 요소 반환
print(numbers, remove_value)

numers_copy = numbers.copy()
print(numbers ,numers_copy)

temp_set = {1,2,3}
temp_set.clear()   # 모든 요소 제거
print(temp_set) # set() : 요소가 없는 empty  set

python_students = {'철수', '영희', ' 민수', '지수'}
ai_students = {'영희', '민수', '준호'}

print(f'합집합 : {python_students.union(ai_students)}')
print(f'합집합 : {python_students | ai_students}')

print(f'교집합 : {python_students.intersection(ai_students)}')
print(f'교집합 : {python_students & ai_students}')

print(f'차집합 : {python_students.difference(ai_students)}')
print(f'차집합 : {python_students - ai_students}')

print(f'대칭차집합 : {python_students.symmetric_difference (ai_students)}')
print(f'대칭차집합 : {python_students ^ ai_students}')

a = {1,2}
b = {1,2,3,4}
c = {5,6}

print(a.issubset(b)) # a 가 b의 부분집합인지
print(b.issuperset(a)) # b 가 a의 상위집합인지

#  문자열과 리스트 슬라이싱

str = 'Hello There'
print(str[0]) # 인덱스 0 문자
print(str[:3]) # 인덱스 0~2 문자
print(str[3:])  # 인덱스 3부터 끝까지 문자
print(str[3:5]) #인덱스 3부터 4까지
print(str[::2])  # 첨부터 끝까지 step2씩 건너서


even = [2,4,6,8]
odd = [1,3,5,7]
print(even[0])
print(even[2:0])
print(even[:3])
print(even[1:4])
print(even[::2])
print(even[-1])

#문자열 , 리스트 뵹헙 / 반복

str1 = 'Hello'
str2 = ' Python'
print(str1 + str2)
print(str1 * 3)

list1 = [1,2]
list2 = [3,4,5]
print(list1 + list2)
print(list1 *3)



























