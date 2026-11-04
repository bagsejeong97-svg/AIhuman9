#day7_ex2
# 인코딩/ 디코딩 정리, 파일에 bytes 읽고 쓰기

# 1. 인코딩과 디코딩 기본 개념
# 컴퓨터의 파일이나 메모리나 네트워크에는 문자가 그대로 저장되는 것이 아니라
# 최종적으로 byte(바이트) 형태의 데이터가 저장/전송 되는 것
# 인코딩(encoding) : 문자(str) > bytes
# 디코딩(decoding) : bytes > 문자(str)

# 2. ASCII 코드
# 영문자, 숫자, 특수기호를 표현한 문자집합(charset)
#  부호가 없는 1byte로 문자를 표현, 1byte는 128개 표현 가능
# - A > 65, a > 97 , 0 > 48 처럼 각 문자에 번호가 부여되어 있음 (0~127)
print('A의 문자 코드 :', ord('A'))
print('65코드에 해당하는 문자 :', chr(65))

# 3. Unicode, Code Point
# Unicode는 전 세계의 문자를 하나의 문자 체계로 정리한 문자셋
# 각 Unicode 문자에 부여한 고유 숫자를 Code Point라 함
# A > U+0041, 가 > U+AC00, 😀 > U+1F600 처럼 유니코드 문자와 코드포인트가 매핑되어 있음
# - Unicode는 인코딩 방식이 여러개 존재함, utf-8도 유니코드 인코딩 방식 중 하나
# utf-8 : Unicode 문자를 실제 byte로 어떻게 표현할 것인가를 정의한 인코딩 방식
# 인코딩 방식에 따라서 같은 문자라도 실제 byte수가 다를 수 있음
# 데이터를 보내는 쪽에서 인코딩한 방식으로 디코딩해야 글자가 깨지지 않음
print('A :', hex(ord('A')))
print('가 :', hex(ord('가')))
print('😀 :', hex(ord('😀')))

# 4. utf-8
#   utf-8은 가변 길이 인코딩을 사용
#   영문 : 1bytes, 한글 : 3bytes, 이모지: 4bytes
for ch in ['A','가','😀']:
    data = ch.encode('utf-8')
    print(f'문자: {ch}, byte : {data}, 크기 : {len(data)}')

# 5. str과 bytes : 파이썬에서 문자열과 바이트는 서로 다른 자료형
# str : 사람이 읽을 수 있는 문자의 나열(문자열)
# bytes : 파일 저장이냐 네트워크 전송에 사용하는 바이트 데이터(010101010101...)
text = '안녕하세요'
print('문자열: ', text)
print('자료형: ', type(text)) #str


byte_data = text.encode('utf-8')   # 문자열 > 바이트
print('인코딩 결과: ', byte_data)
print('자료형: ', type(byte_data))  #<class 'bytes'>

decoded_text = byte_data.decode('utf-8') # 디코딩 : 바이트 > 문자열
print('디코딩 결과: ', decoded_text)
print('자료형: ', type(decoded_text))

# 6. 대표적인 인코딩 방식
# 1) utf-8
#   현재 웹, API, 파일, 네트워크 등에서 가장 널리 사용되는 인코딩 방식
#   Unicode 기반 인코딩 / 디코딩에 사용
#   1~4 바이트 가변길이 인코딩 / 디코딩
# 2) utf-8-sig
#   - utf-8 + BOM(Byte Order Mark)
#   BOM : 파일 시작에 EF BB BF 인 3바이트가 추가됨 ( 바이트 순서에 대한 표시)
#   windows Excel 처리시
# 3) EUC-KR  : 과거에 한글을 처리하기 위한 인코딩 방식
# 4) CP949
#   - 마이크소프트에서 만든 EUC-KR을 확장한 한국어 인코딩 방식
#   - 오래된 윈도우의 문서들, 공공데이터포털의 이전 데이터들에서 가끔 보임

# 7. BOM(Byte Order Mark)
# 파일의 맨 앞에 들어가는 특별한 byte,바이트의 순서를 기록
# utf-8 BOM : EF BB BF
# python에서
# encoding = 'utf-8' : 일반 UTF-8
# encoding = 'utf-8-sig' : BOM을 처리하는 UTF-8
#   utf-8-sig로 읽기 : BOM이 추가되어 있으면 자동으로 제거
#   utf-8-sig로 쓰기 : 파일 맨 앞에 BOM을 추가

# 8. 한글이 깨지는 대표적인이유
# 파일을 저장할때 사용한 인코딩 방식과 파일을 읽을때 사용한 인코딩 방식이 다를때
# 네트워크로 전송할때 사용한 인코딩 방식과 네트워크에서 데이터를 읽을때 사용한 인코딩 방식이 다를 떄
# 아뭏든... 인코딩 방식을 확인해서 같은 방식을 디코딩 해야함

# 9. 파이썬 파일 처리모드
# 1) 텍스트 모드 (w,r) : str 데이터를 사용, encoding 파라미터 필요
# 2) 바이너리 모드 (wb,rb) : bytes 데이터를 사용, encoding 파라미터 불필요

# 10. 파일에 byte 쓰기
# 문자열 인코딩
message = '안녕하세요! python 바이트 파일 실습입니다.'
message_bytes = message.encode('utf-8') # 문자열 > bytes utf-8 인코딩
# 파일에 바이트 쓰기
with open('day7_data/message.bin', 'wb') as f:
    f.write(message_bytes)

# 11. 파일의 byte 읽기
with open('day7_data/message.bin', 'rb') as f:
    read_data = f.read()
print('읽은 데이터: ', read_data)
print('자료형: ', type(read_data))
print('byte 크기: ', len(read_data))




















