# day4 challenger

score = int(input('score (0~100) : '))
attendance = int(input('attendance (0~100) : '))

if (score < 0 or score > 100) and (attendance < 0 or attendance > 100):
    print('점수 입력 오류')
    print('출석률 입력 오류')
elif score < 0 or score > 100:
    print('점수 입력 오류')
elif attendance < 0 or attendance > 100:
    print('출석률 입력 오류')
else :
    if score >= 90 and attendance >= 95:
        result = '우수합격'
    elif score >= 70 and attendance >= 80:
        result = '합격'
    elif attendance < 80:
        result = ' 불합격 - 출석률 미달'
    else:
        result = '불합격 - 점수미달'
    print(f'점수 : {score}')
    print(f'출석률 : {attendance}')
    print(f'최종판정 : {result}')


















