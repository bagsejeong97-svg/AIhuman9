def pp(*obj): # 출력 할떄마다 구분선
    print(*obj)
    print('-'*80)

def up(n): #  위로 몇줄 출력 결과창 올리기 위함
    print('\n'*n)

def pt(*ages): # 타입과 구분선 과 함께 출력
    print(type(*ages))
    pl(80)


def pl(n): # 개수 만큼 구분선 출력
    print('-'*n)