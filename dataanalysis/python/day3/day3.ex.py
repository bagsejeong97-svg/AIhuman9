# day3.ex.py
# 연산자, 표준 입출력, 형변환

#1. 산술 연산자
 # a = 10
 # b = 3
 # print(f'더하기: {a+b}')
 # print(f'빼기: {a-b}')
 # print(f'곱하기: {a*b}')
 # print(f'나누기: {a/b}') # 나눗셈 결과는 float
 # print(f'몫: {a//b}') # 정수 나눗셈
 # print(f'나머지: {a%b}') # 배수 연산시 많이 활용
 # print(f'거듭제곱: {a**b}')

#2. 연산자 우선순위
#() 가 우선순위가 가장 높을을 이용해서
# 먼저 연산할 것들을 () 묶어줌
result1 = 2 + 3 * 4
result2 = (2 +3) * 4
print(result1,result2)

# 3. 비교 연산자 : 결과는 bool
print((f' 10>5: {10>5}'))
print((f' 10<5: {10<5}'))
print((f' 10>=5: {10>=5}'))
print((f' 10<=5: {10<=5}'))
print((f' 10==5: {10==5}'))
print((f' 10!=5: {10!=5}'))

# 4. 논리 연산자
age_ok = 23 >= 20 # True
scoore_ok = 85 >= 80 # True
print(f'and: {age_ok and scoore_ok}')
print(f'or: {age_ok or scoore_ok}')
print(f'not: {not age_ok }')
a = 5
b = 3
print(f'xor: {a ^ b}') # XOR연산 : 두 비트가 같으면 False (0), 다르면  True(1)
print(True ^ True)
print(True ^ False)
print(False ^ False)
print(False ^ True)

# 5. input() 표준 입력 함수
# name = input('이름을 입력하세요: ')
# print(f'입력한 이름: {name}')
# print(type(name)) #input() 의 결과는 str

# 6, input() 으로 입력 받은 숫자의 타입 확인
# age_text = input('나이를 입력하세여: ')
# print(f'age-text:{ age_text}, {type(age_text)}')
# age_int = int(age_text) #정수로 형변환
# print(f'age-int:{ age_int}, {type(age_int)}')

# 7. 형변환 실습
# in_int = int(input('정수 입력: '))
# in_float = float(input('실수 입력: '))
# in_bool = bool(input('불리언 입력(True/False): '))
# print(type(in_int),type(in_float),type(in_bool))
# str_bool = str(in_bool)  #bool >> str
# print(str_bool,type(str_bool))

# 8. 간단한 가격, 수량 계산
# price = int(input('상품 가격을 입력하세요: '))
# quanity = int(input('수량을 입력하세요: '))
# total = price * quanity
# print(f'총액: {total}')
# print(f'쉼표 포함 총약: {total:,}')

# 9. 할인율을 포함한 주문 계산
# product = input('상품명을 입력하세요: ')
# unit_price = int(input('단가를 입력하세요: '))
# qty = int(input('수량을 입력하세요: '))
# ciscount_rate = float(input('할인율(%)을 입력하세요: '))
# subtotal = unit_price * qty
# discount_amount = subtotal * ciscount_rate / 100
#
# final_amount = subtotal - discount_amount
#
# print('='*40)
# print(f'상품명: {product}')
# print(f'할인 전 합계: {subtotal:,.0f}')
# print(f'할인 금액: {discount_amount:,.0f}')
# print(f'최종 결제 금액: {final_amount:,.0f}')
# print('='*40)

# 10. 형변환 오류 확인
# tc_error1 = int('abc') #ValueError
tc_error2 = int(35.72)  # 소수점 이하 절삭
print(tc_error2)

tc_error3 = float(35)
print(tc_error3)
tc_error4 = bool(35)
print(tc_error4) # 숫자 0은 False 나머지는 True















