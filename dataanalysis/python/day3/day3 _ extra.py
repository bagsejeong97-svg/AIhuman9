#day3 extra


#문자열 입력
company = input('회사명 :')
couse_name = input('교육과정명 :')
# 정수입력
people = int(input('참가인원 :'))
hours_rate = int(input('고객 청구 시간당 교육비(원): '))
instructor_rate = int(input('강사 지급 시간당 강사료(원): '))
textbook_rate = int(input('1인당 교재/실습비(원) : '))
place_cost = int(input('장소 및 장비 비용(원) : '))
# 실수 입력
total_hours = float(input('총교육 시간 : '))
discount = float(input('할인율 % : '))
#
# # [1] 교육 판매금액
sale_price = total_hours * hours_rate
# [2] 전체 교재/실습비
total_textbook_rate = people * textbook_rate
# [3] 할인 전 견적금액
before_discount_price = sale_price + total_textbook_rate + place_cost
# [4] 할인금액
discount_price = (before_discount_price * discount / 100)
# [5] 최종 계약 예상금액
final_contract_amount = before_discount_price - discount_price
# [6] 강사비
instructor_free = total_hours * instructor_rate
# [7] 총 원가
total_cost = instructor_free + total_textbook_rate + place_cost
# [8] 예상 이익
expected_profit = final_contract_amount - total_cost
# [9] 예상 이익률
expected_rate = (expected_profit / final_contract_amount * 100)


print('-'*40)
print('기업교육 견적 및 손익 리포트')
print('-'*40)
print(f'회사명              : {company}')
print(f'교육과정            : {couse_name}')
print(f'참가 인원           : {people}명')
print(f'총 교육시간          : {total_hours:.1f}시간')
print('\n')
print('[견적]')
print(f'교육 판매금액        : {sale_price:,.0f}원')
print(f'교재/실습비         : {total_textbook_rate:,}원')
print(f'장소/장비비         : {place_cost:,}원')
print(f'할인 전 견적금액     : {before_discount_price:,.0f}원')
print(f'할인율             : {discount:.1f}%')
print(f'할인금액             : {discount_price:,}원')
print(f'최종 계약 예상금액     : {final_contract_amount:,.0f}원')
print('\n')
print('[예상 원가 및 손익]')
print(f'강사비              : {instructor_free:,.0f}원')
print(f'총 원가             : {total_cost:,.0f}원')
print(f'예상 이익            : {expected_profit:,.0f}원')
print(f'예상 이익률          : {expected_rate:.2f}%')
print('\n')
print('[사업성 점검]')

# 1) is_profitable
#    예상 이익 > 0
print(f'이익 발생 여부  :{expected_profit > 0}')
# 2) is_participant_range_ok
#    참가 인원 >= 5 and 참가 인원 <= 30
print(f'권장 인원 충족 여부 : {people >= 5 and people <= 30}')
# 3) is_target_margin_ok
#    예상 이익률 >= 25
print(f'목표 이익률 충족 여부 : {expected_rate >= 25}')
# 4) can_proceed
#    is_profitable and is_participant_range_ok and is_target_margin_ok
print(f'사업  진행 기준 충족 : {expected_profit >0 and people >= 5 and people <= 30 and expected_rate >= 25 }')
print('-'*40)
print('\n')
print('\n')
print('='*40)
















