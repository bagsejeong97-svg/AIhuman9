# day5_challenger

students = {'민수' : 72,
            '지연' : 88,
            '준호' : 95,
            '서연' : 61,
            '하늘' : 84
            }
total = -1
count = 0
high_score = 0
high_name = ''

for name, score in students.items():
    total += score
    if score >= 80:
        count += 1
    if score > high_score:
        high_score = score
        high_name = name
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    else:
        grade = 'D'
    if score >= 80:      # result = 'PASS' if score >= 80 else 'RETRY'
        result = 'PASS'
    else:
        result = 'RETRY'
    print(f'{name}|{score}|{grade}|{result}')

averge = total/len(students)
print(f'평균 : {averge}')
print(f'합격자 수 : {count}')
print(f'최고점 : {high_name}|{high_score}')




























