#day3 ex.py

product = input('상품명을 입력 : ')  #str
price = int(input('상품 단가를 입력 : '))  #int
quantity = int(input('구매 수량을 입력 : ')) #int

total_price = price * quantity   #합계금액

print(f'상품명 : {product}')
print(f'단가 : {price:,}') #쉼표 추가
print(f'수량 : {quantity}개')
print(f'주문 금액 : {total_price:,}') #쉼표 추가

# 단가와 수량을 연산하여야 하므로 int변환을 해야한다.




















