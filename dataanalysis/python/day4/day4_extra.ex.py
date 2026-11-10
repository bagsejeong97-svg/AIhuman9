#day4_extra

#이름 입력 여부 확인
# name = input('이름 : ')
# if name:             # name에 입력이 되있다면 True이기 때문에 '이름 입력 완료' 진행
#     print("이름 입력 완료")
# else:
#     print('이름없음')

# 회원등급 확인
grade = input("회원 등급 입력 : ")

result = "정상 등급" if grade == ["noraml" or "gold" or "vip"] else "입력 오류"
print(result)

grade = input("회원 등급 입력 : ")

result = "정상 등급" if grade == "noraml" or grade == "gold" or grade == "vip" else "입력 오류"
print(result)

# 홀수 / 짝수 판정
# num = int(input('입력 :'))
# result = "짝수" if num % 2 == 0 else "홀수"
# print(result)

# 오전 / 오후 판정
# time = int(input('시간 입력 : '))
# if time < 0 or time > 23:
#     print('입력 오류')
# elif time <= 12:
#     print('오전')
# else:
#     print('오후')

# 계절 판정
# num = int(input('입력 : '))
# if num < 1 or num > 12:
#     print('입력오류')
# elif num == 12 or num <= 2:
#     print('겨울')
# elif 3 <= num <= 5:
#     print('봄')
# elif 6 <= num <= 8:
#     print('여름')
# else:
#     print('가을')

# 배송비 판정
grade = input('등급 입력 : ')
price = int(input('주문금액 입력 :'))

if grade not in ["normal", "gold", "vip"]:
    print('입력 오류')

if price >= 50000:
    print('무료 배송')
elif price >= 30000:
    if grade == 'vip':
        print('무료배송')
    elif grade == 'gold':
        print('무료배송')
    else:
        print('배송비 3,000원')
else:
    print('배송비 3000원')

# 장학금 대상 판정
# average = int(input('평균점수 : '))
# attendance = int(input('출석률(%) :'))
#
# if average >= 95 and attendance >= 85:
#     result = "우수 장학금 대상"
# elif average >= 85 and attendance >= 90:
#     result = " 장학금 대상"
# else:
#     result = "대상아님"
# print(result)

# 직원 성과등급 판정

# score = int(input('성과 점수 :'))
# count = int(input('지각횟수 : '))
#
# if 0 > score or score > 100 or count < 0:
#     print('입력오류')
# else:
#     if score >= 90 and count == 0:
#         grade = 'S'
#     elif score >= 80 and count <= 2:
#         grade = 'A'
#     elif score >= 70 and count <= 4:
#         grade = 'B'
#     else:
#         grade = 'C'
#     print(grade)

# ATM 출금 검증
# coin = int(input('현재 잔액 :'))
# out_coin = int(input('출금 금액 : '))
# if out_coin <= 0:
#     print('잘못된 금액')
# else:
#     if out_coin % 10000 != 0:
#         print('만원단위로 입력')
#     elif out_coin >= coin:
#         print('잔액 부족')
#     else:
#         print(f'{coin-out_coin}원')



















