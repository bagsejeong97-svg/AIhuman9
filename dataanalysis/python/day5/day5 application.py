#day 5 application

scores = [72, 88, 95, 61, 83, 90]
count = 0  # 합격자 수
# 최고점수 합격자수 점수합계 평균점수 전체 학생수
total = 0
people = len(scores)
max_score = scores[0]
for score in scores:
    total += score
    if score >= 80:
        count += 1
    if max_score < score:
        max_score = score

print(f'전체학생수 : {people}')
print(f'점수 합계 :{total}')
print(f'평균점수 : {total/people:.2f}')
print(f'합격자 수 :{count}')
print(f'최고점 : {max_score}')



































