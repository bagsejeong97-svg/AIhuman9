# day3 application.ex.py

product = input('상품명 :')
price = int(input('단가 :'))
quantity = int(input('수량 :'))
discount_rate = float(input('할인율(%): '))

total_price = price * quantity
discount_price = int(price * discount_rate / 100) #나누기 계산시 float이므로 int로 형변환 해준다.
total_amount = total_price - discount_price

print(f'상품명 : {product}')
print(f'주문금액 : {total_price:,}원')
print(f'할인율 : {discount_rate:.1f}%')
print(f'할인금액 : {discount_price:,}원')
print(f'최종 결제금액: {total_amount:,}원')

# 할인율의 %는 백분위를 나타내는 기호이기 때문에 할인율을 100으로 나눠 계산한다









