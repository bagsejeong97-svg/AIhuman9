# day33_note.py
# 자연어(Natural Language) 처리, 음성 신호 기초 개념

# Alt + F12 > python -m pip install soundfile

import math
from pathlib import Path
import numpy as np
import soundfile as sf # 사운드 파일 처리 라이브러리
from pyarrow import duration
from sklearn.feature_extraction.text import TfidfVectorizer # TF-IDF 벡터화 라이브러리
from sklearn.metrics.pairwise import cosine_similarity # 코사인 유사도 라이브러리
from sklearn.preprocessing import normalize # 정규화 라이브러리( L1,L2 정규화)
from util.print_util import pp

# 1. TF_IDF (Term Frequency - Inverse Document Frequency)

# [개념]
# - TF : 특정 문서에서 어떤 단어가 등장한 회수
# - DF : 특정 단어가 등장한 문서의 수
# - IDF : 전체 문서에서 단어가 드물게 등장하는 정도
# - TF-IDF : 특정 문서에서 자주 등장하지만 다른 문서들에서는 드물게 등장하는 단어에 높은 가중치를 부여하기 위한 수치
#           - 문서들을 구별하기 위해서 필요한 수치

# [수식]
# - N : 전체 문서 수, t : 단어, d: 문서
# - 순수 IDF(t) = ln(N / DF(t))
# - 순수 TF-IDF(t,d) = TF(t,d) * IDF(t)

# [실습 코드]
# 문서별 단어 빈도와 순수 TF-IDF를 계산하는 함수
def note_tfid():
    pp('1. TF_IDF: 빈도와 문서 간 희소성')
    docs = [ # 문서 리스트
        'AI 음성 음성 인식', # 문서 A
        'AI 이미지 이미지 분류', # 문서B
        'AI 데이터 데이터 분석', #문서 C
    ]
    # 모든 문서를 토큰화
    tokens_by_doc = [doc.lower().split() for doc in docs]
    pp(tokens_by_doc)
#[['ai', '음성', '음성', '인식'], ['ai', '이미지', '이미지', '분류'], ['ai', '데이터', '데이터', '분석']]
    n_docs = len(docs) # 문서 수

    for term in ('ai','음성','인식'):
        pp(term)
        tf = tokens_by_doc[0].count(term)
        pp(tf) # 문서내의 term 빈도 수
        df = sum(term in words for words in tokens_by_doc)
        pp(df) # term이 있는 문서의 수
        idf = math.log(n_docs / df)
        pp(idf)
        pp(f'TF_IDF: {tf * idf:.3f}')
# 의미와는 상관없이 특정 빈도수만 가지고 계산한값이므로 의미라고 생각하면 안된다.

# 2. IDF 평활화(Smoothing)
# [개념]
# - scikit-learn은 기본적으로 IDF를 평활화하여 계산함
# - IDF 계산시에 분자와 분모에 각각 1을 더해서 희소성 가중치를 완만하게 조정
#       1을 더하는 이유 - 더큰 값으로 나눠서 더값을 작게 만들려고 / 분모가 0인 상황 예방을 위해
# - 로그함수 밖에 +1 을 해서 IDF값이 0이 되는 것을 방지

# [수식]
# - sklearn 평활화 IDF = ln(N + 1 / DF(t) +1) + 1
# - sklearn 비평활화 IDF = ln(N / DF(t)) + 1
# - sklearn 파라미터 기본값 : smooth_idf = True, norm='l2'

# [실습 코드]
# 직접 계산과 sklearn의 평활화/비평활화 IDF 비교하는 함수
def note_smoothing():

    pp('2.IDF 평활화: 계산 방식 비교')

    n_docs = 10 # 문서수
    for df in (1,5,10): # term이 나온 문서의 수를 1,5,10 으로 반복
        raw = math.log(n_docs / df) #순수 IDF
        smooth = math.log((n_docs +1) / (df+1)) # sklearn의 평활화 IDF
        plain = raw + 1 # sklearn 비평활화 IDF
        pp(
            f'DF={df:.2f}, 순수={raw:.3f}, 평활화 = {smooth:.3f},비평활화 = {plain:.3f}'
        )
    docs = ['AI 음성 음성','AI 음성 이미지','AI 분석']

    # Tokenizing : 토큰화, 문서나 문장을 분석 가능한 작은 단위로 쪼갬
    # Vectorizing : 백터화, 문서나 문자를 수치화
    v_smooth = TfidfVectorizer(
        # (?u): 유니코드 문자, \b :워드의 경계, \w: 원드문자(영문대소문자,숫자,_) 히니
        token_pattern=r'(?u)\b\w+\b', # 토크나이징 정규표현식 패턴
        smooth_idf=True, # 평활하
        norm=None # 정규화 사용 안함
    )
    v_plain = TfidfVectorizer(
        token_pattern= r'(?u)\b\w+\b',
        smooth_idf= False, # 비평활화
        norm= None
    )

    v_smooth.fit(docs) # 문서들을 학습
    v_plain.fit(docs)

    # term들을 추출해서 반복
    for idx, word in enumerate(v_smooth.get_feature_names_out()):
        # 학 습 후 획득한 idf들을 출력
        pp(
            f'{word}: 평활화={v_smooth.idf_[idx]:.3f}'
            f', 비평활화={v_plain.idf_[idx]:.3f}'
        )

# 3. L1 / L2 정규화 (Normalization)

# [개념]
# - 정규화 : 벡터를 일정한 기준의 크기로 조정
# - L1 정구화 : 벡터 원소의 절대값의 합이 1이 되도록 나눔
# - L2 정규화 : 벡터의 유클리드 길이의 합이 1이 되도록 나눔

# [수식]
# - ||x||_1 = sum(|x_i|) #벡터 원소의 절대값의 합
# - ||x||_2 = sqrt(sum(x_i **2)) # 벡터의 유클리드 길이(두 점사이의 거리)
# - x_L1 = x / ||x||_1 # 절대값의 합으로 나눔
# - x_L2 = x / ||x||_2 # 유클리드 길이로 나눔
# - 예) [3 4]
#       L1 정규화 => [3/7 4/7] # 각 요소의 절대값의 합으로 나눔
#       L2 정규화 => [3/5 4/5] # 각 요소의 제곱후 합의 값에 루트로 나온 값으로 나눔
# - scikit-learn 의 TfidfVectorizer의 기본 정규화는 L2
# 정규화 하는 이유는 벡터의 크기를 줄이기 위해

# [실습 코드]
# 하나의 벡터에 L1,L2 정규화를 적용하고 결과를 검증하는 함수
def note_normalization():
    pp('3. L1,L2 정규화: [3 4] 비교')
    x = np.array([[3.0,4.0]]) # [3.0 4.0] 넘파이 다차원 배열
    L1 = normalize(x, norm='l1') # L1 정규화
    L2 = normalize(x, norm='l2') # L2 정규화
    pp(f'원본: {x.tolist()}')
    pp(f'L1: {np.abs(x).sum():.3f}')
    pp(f'L2: {np.linalg.norm(x):.3f}')
    pp(f'L1 정규화 결과: {L1.round(3).tolist()}')
    pp(f'L2 정규화 결과: {L2.round(3).tolist()}')
    pp(f'L1 검증(절대값 합): {np.abs(L1).sum():.3f}')
    pp(f'L2 검증(백터 길이): {np.linalg.norm(L2):.3f}')

# 4. 코사인 유사도(Cosine Similarity)

# [개념]
# - 두 백터의 크기보다는 방향이 얼마나 같은지를 나타내는 지표
# - 방향이 같으면 1, 직교하면 0, 방향이 반대면 -1
# TF-IDF는 0이상의 값이므로 코사인 유사도 범위는 0 ~ 1
# - L2 정규화된 두 벡터는 두 벡터의 내적이 코사인유사도와 같음
# [수식]
# - A·B = sum(A_i * B_i) => 두 벡터의 내적은 각 위치 원소 곱들의 합
# - cosine(A,B) = (A·B) / (||A||_2 * ||B||_2) = > 코사인 유사도는 내적 나누기 길이
# - 예) A=[3 4], B=[4 3] 이라면 내적=24, 길이=각각5, 코사인 유사도 = 24/5*5 = 24/25 = 0.96

# [실습코드]
# 내적과 벡터 길이로 코사인유사도를 계산하고 문서끼리 비교하는 함수
def note_cosine():
    pp('4. 코사인유사도: 내적과 벡터 방향')

    a = np.array([3.0, 4.0]) # a 벡터
    b = np.array([4.0, 3.0]) # b 벡터

    dot = np.dot(a,b) # 내적(dot product) : 같은 위치끼리 곲한 값의 합

    length_a = np.linalg.norm(a) # a 벡터 길이
    length_b = np.linalg.norm(b) # b 벡터 길이

    cosine = dot / (length_a * length_b) # 코사인 유사도 = 내적 / a 벡터길이 * b 벡터길이

    pp(f'내적: {dot:.3f}, a벡터길이: {length_a:.3f}, b벡터길이: {length_b:.3f}')
    pp(f' 직접 계산한 코사인유사도: {cosine:.3f}')
    pp(f'sklearn계산 코사인유사도: {cosine_similarity([a],[b])[0,0]:.3f}')

    docs = [
        'AI 음성 인식 모델',
        'AI 음성 인식 기술',
        '축구 경기 결과'
    ]

    vectorizer = TfidfVectorizer(
        token_pattern=r'(?u)\b\w+\b',
        norm='l2'
    )

    matrix = vectorizer.fit_transform(docs) # 문서별 TF-IDF 벡터
    scores = cosine_similarity(matrix) # 코사인 유사도

    pp('문서별 유사도 행렬')
    pp(np.round(scores, 3))
    pp(f'행렬 모양:{scores.shape}(문서수 X 문서수)')
    pp(f' 대칭 행렬 여부:{np.allclose(scores,scores.T)}')

# 5. 오디오 파형(WaveForm)과 샘플링레이트(Sample Rate)

# [개념]
# - 음성 파일은 시간에 따라 변하는 소리의 파형을 숫자로 저장함
# - 파형 (WaveForm) : 시간 순으로 나열한 샘플의 형태
# - 샘플링(Sampling) : 아날로그 신호를 특정 시간 간격으로 디지털 신호로 변환
# - 샘플링 비율(Sampling Rate) : 1초 동안 샘플링한 샘플의 계수
# - y : 시간 순으로 나열된 파형 값(샘플)의 배열
# - sr : 1초 동안 사용하는 샘플 개수, 단위는 Hz
# - 예) sr=4라면 1초에 4개의 샘플링, 2초에는 8개의 샘플링
# - soundfile 라이브러리의 sf.write(파일명,y,sr) : 샘플링 비율에 맞춰 파형을 WAV 파일로 저장
# - soundfile 라이브러리의 sf.read(파일명) : WAV파일을 파형과 sr로 읽음

# [수식]
# - 재생 시간(초) = 전체 샘플 수 / sr
# - 예) 샘플 수가 8개 이고 sr이 4Hz라면 재생 시간은 2초

#[실습코드]
# 짧음 파형 배열을 직접 만든 후 저장하고 읽기
def note_audio():

    pp('5. WAV파일: y와 sr이해하기')

    sr = 4 # 1초의 4개 샘플링
    y = np.array([0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5])
    duration = len(y) / sr #재생 시간

    pp(f'파형 데이터(y) : {y.tolist()}')
    pp(f' 샘플 수:{len(y)}개, 샘플링 레이트: {sr}Hz')
    pp(f'재생 시간: {duration:.1f}초')

    # WAV 파일 저장 결로
    output = Path(__file__).resolve().parent / 'day33_sample.wav'
    sf.write(output,y,sr) # WAV 파일로 저장

    # WAV 파일을 읽어서 y,sr 추출
    loaded_y,loaded_sr = sf.read(output)
    pp(f'읽은 샘플 수 : {len(loaded_y)}개')
    pp(f'읽은 sr 수 : {loaded_sr}Hz')

    # 샘플링 레이트 : 1초에 16000개 샘플
    sr = 16000

    # 2초 동안의 시간 배열
    t = np.arange(0, 2, 1 / sr)

    # 각 음의 주파수
    do = 0.5 * np.sin(2 * np.pi * 261.63 * t)  # 도(C4)
    mi = 0.3 * np.sin(2 * np.pi * 329.63 * t)  # 미(E4)
    sol = 0.2 * np.sin(2 * np.pi * 392.00 * t) # 솔(G4)

    # 세 음을 합성
    y = do + mi + sol

    # WAV 파일로 저장
    sf.write("music_sample.wav", y, sr)


sr = 22050
bpm = 112
beat = 60 / bpm
notes = [
    ("C4", 0.5), ("E4", 0.5), ("G4", 0.5), ("E4", 0.5),
    ("F4", 0.5), ("A4", 0.5), ("G4", 1.0),
    ("E4", 0.5), ("G4", 0.5), ("C5", 0.5), ("B4", 0.5),
    ("A4", 0.5), ("G4", 0.5), ("C5", 1.0),
]
freqs = {"C4":261.63,"E4":329.63,"F4":349.23,"G4":392.0,"A4":440.0,"B4":493.88,"C5":523.25}
rng = np.random.default_rng(42)

def play_note(freq, duration):
    n = int(sr * duration)
    t = np.arange(n) / sr
    # 악기 음색: 기본 주파수와 고조파
    tone = (np.sin(2*np.pi*freq*t) +
            0.32*np.sin(2*np.pi*2*freq*t) +
            0.12*np.sin(2*np.pi*3*freq*t))
    attack = np.minimum(1, t / 0.012)
    decay = np.exp(-1.7 * t / max(duration, 0.01))
    release = np.minimum(1, (duration-t) / 0.075)
    envelope = attack * decay * np.maximum(release, 0)
    return tone * envelope

y = np.concatenate([play_note(freqs[n], d*beat) for n,d in notes])
# 부드러운 잔향
delay = int(0.17 * sr)
reverb = np.zeros_like(y)
reverb[delay:] = 0.19*y[:-delay]
y = y + reverb
y = (0.85 / np.max(np.abs(y)) * y).astype(np.float32)
path = Path("short_melody.wav")
sf.write(path, y, sr, subtype="PCM_16")
print(f"파일: {path}, 재생시간: {len(y)/sr:.2f}초")
print("처음 20개 샘플:", np.round(y[:20], 4))

# 실행 코드
# note_tfid()
# note_smoothing()
# note_normalization()
# note_cosine()
# note_audio()

# 6. 진폭, 주파수, 강도

# [개념]
# - 진폭 (Amplitude) : 파형이 위아래로 움직이는 폭
# - 주파수 (Frequency) : 파형이 1초에 반복되는 회수(Hz)
# - 감도 (Intensity): 실제 소리가 전달하는 에너지의 세기

# [실습 코드]
# 간단한 사인파를 만들고 진폭, 주파수의` 차이를 숫자로 확인
'''
* 사인파의 기본 공식 : y(t) = A * sin(2 * pi * f * t)
- A : 진폭, f: 주파수, t:시간
- 2*pi*f*t는 각도
    : 시간이 흐르면서 사인파가 원 위에서 얼마나 회전헀는지를 나타냄
        사인함수는 각도가 2*pi 만큼 진행하면 한번 반복됨
'''
def note_af():

    pp('6.진폭과 주파수:파형 비교')

    sr = 100
    t = np.arange(sr) / sr # 0.00초 부터 0.99초까지의 시간

    small = 0.3 * np.sin(2 * np.pi * 2 * t )#  진폭 0.3, 주파수 2Hz
    large = 0.8 * np.sin(2 * np.pi * 2 * t )#  진폭 0.8, 주파수 2Hz
    fast = 0.3 * np.sin(2 * np.pi * 5 * t )#  진폭 0.3, 주파수 5Hz

    pp(f'작은 진폭의 최대값: {np.max(small):.1f}')
    pp(f'큰 진폭의 최대값: {np.max(large):.1f}')
    pp(f'2Hz:1초에 2번 진동, 5Hz : 1초에 5번 진동')
    pp(f'파형 세 종류의 샘플 수:{len(small)}개')
    pp(f'빠른 파형의 앞 5개 값:{fast[:5].round(3)}')

# note_af()













































































