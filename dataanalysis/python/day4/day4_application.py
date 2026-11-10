#day_application

score = int(input('점수를 입력하시오 :'))

if score < 0 or score > 100:
    print(f'점수: {score}')
    print('입력 오류')
else:
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    elif score >= 60:
        grade = 'D'
    else:
        grade = 'F'
    print(f'점수 : {score}')
    print(f'등급 : {grade}')
















