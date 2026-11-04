# day3 challenger.ex.py

product = input('상품명 : ')
price = int(input('단가 : '))
quantity = int(input('수량 :'))
discount_rate = float(input('할인율(%) : '))
vat_rate = float(input('부가세율(%) : '))

total_price = price * quantity
discount_price = int(total_price * discount_rate / 100)
after_discount_price = total_price - discount_price
vat_price = int(after_discount_price * vat_rate / 100)
total_amount = after_discount_price + vat_price

print(f'상품명 : {product}')
print(f'주문금액 : {total_price:,}')
print(f' 할인율 : {discount_rate:.1f}%')
print(f'할인금액 : {discount_price:,}')
print(f'할인 후 금액: {after_discount_price:,}')
print(f'부가세율: {vat_rate:.1f}%')
print(f'부가세: {vat_price:,}')
print(f'최종 결제금액: {total_amount:,}')

#과제 2
#value error
#str은 과 int 연산을 할수 없기 때문에
# 중간 중간에 type() 확인을 하여야 한다
# 코드를 작성하지 않아도 자료형을 알수 있는 단축키 가 있음 편할것 같다












