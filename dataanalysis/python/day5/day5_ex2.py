#day 5_ex2.py
# 파이썬 데이터 타입 정리
#primitive type (scalar type) : 하나의 변수에 하나의 데이터를 저장
#                               정수, 시리수, 문자열, 불리언, None Type
#  complex type : 하나의 변수에 여러 데이터를 저장
#                 리스트, 튜플, 딕셔너리, 셋 ,클래스
# mutable type : 값을 변경할 수 있는 타입
#                   리스트 , 딕셔너리, 셋, 클래스
#immupable type :  값을 변경할 수 없는 타입, 딕셔너리 키는  immutable 해야 함
#                  정수, 실수, 문자열, 불리언, 튜플

# 정수
print(type(100))  # int

# 실수
print(type(3.14)) # float

# 문자열
print(type('hello')) # str

# bool
print(type(True))  #bool

#None
print(type(None)) #NoneType

#리스트(List,[])
# 1. 순서대로 요소를 저장
# 2. 어떤 타입의 요소도 저장 가능
# 3. mutable타입으로 값으 변경, 추가, 삭제 가능
# 4. 중복 요소 저장 가능
print((type([1,2,3])))  # List

#튜플 (tuple,())
# 1. 기본적으로 리스트의 특성을 가짐
# 2. immutable 타입으로 값의 변경, 추가 ,삭제 불가
print(type((1,2,3,))) # tuple


#딕셔너리 (dictionary, {})
# 1. 아이템(키:값) 순서가 없음
# 2. 키는 immutable 타입이어야 함, 값은 상관 없음
# 3. 키는 중복 불허  : 값을 구별할 방법이 없어짐 / 값은 중복 가능
print((type({'name': '홍길동', 'age' : 20}))) # dict

# 셋(set,{})
# 1. 요소의 순서가 없음
# 2. 중복데이터는 한번만 저장 : 리스트의 중복 요소 제거에 많이 사용
print(type(set()))   #set


#question : {}   -> empty dictionary


























































