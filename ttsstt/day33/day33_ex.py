# day33_ex.py
# 주제:
# 텍스트 전처리, TF_IDF, 코사인 유사도, WAV 파형

# alt +f12 _> pip install librosa

import re
from collections import Counter
from pathlib import Path
import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from util.print_util import pp
from include.graph_config import set_graph

set_graph(10,8,13)

BASE_DIR = Path(__file__).resolve().parent

DOCS = [
    'AI 음성 인식 모델은 말을 텍스트로 변환합니다!',
    '음성 합성 모델은 텍스트를 말소리로 바꿉니다.',
    '텍스트 분석에는 AI 모델과 전처리가 중요합니다.',
    '음성 인식과 텍스트 분석은 입력 데이터가 다릅니다.'
]

# 텍스트 정규화 함수
def normalize(text):
    # 한글, 영문대소문자, 숫자, 공백문자가 아닌 것은 ' '로 변환
    text = re.sub(r'[^가-힣A-Za-z0-9\s]',' ',text)
    # 공백문자가 1개 이상이면 ' '로 변환 후 앞뒤 공백 제거후 소문자로 변환후 리턴
    return re.sub(r'\s+',' ',text).strip().lower()

# 문서 토큰화 반환 함수
def inspect_documents(documents):

    cleaned = [normalize(doc) for doc in documents] # 문서들 정규화한 리스트

    pp('문서 전처리와 토큰화')

    for index, doc in enumerate(cleaned,1):
        tokens = doc.split() # 문서를 공백문자 기준으로 토큰화
        pp(f'문서 {index}:{doc}')
        pp(f'토큰:{tokens}')

    counts = Counter(' '.join(cleaned).split())  # 빈도 카운트
    pp('전체 토큰 빈도 TOP7: ',counts.most_common(7))
    return  cleaned

# 어휘집과 BoW / TF_IDF 특성 행렬 확인 함수
def inspect_vectors(documents):

    token_patten = r'(?u)\b\w+\b'
    count_vec = CountVectorizer(token_pattern=token_patten)

    # fit_transform() : 어휘집 학습 후 문서를 카운트 행렬로 변환
    bow = count_vec.fit_transform(documents)
    pp('BoW(단어 빈도)')
    pp('어휘집: ',count_vec.get_feature_names_out().tolist())
    pp('행렬 shape:', bow.shape) # (문서 수, 어휘 수)
    pp(bow.toarray()) # 변환된 배열

    # TF-IDF 벡터화
    tfidf_vec = TfidfVectorizer(
        token_pattern=token_patten,
        norm='l2',
        smooth_idf=True
    )
    matrix = tfidf_vec.fit_transform(documents)
    pp('TF-IDF와 문서 유사도')
    pp('TF-IDF 행렬 shape:', matrix.shape)

    # 어휘와 학습한 idf값들을 반복 출력
    pp('어휘별 IDF: ')
    for term,value in zip(tfidf_vec.get_feature_names_out(),tfidf_vec.idf_):
        pp(f'{term}: {value:.3f}')

    scores = cosine_similarity(matrix) # 코사인 유사도
    pp('문서별 코사인 유사도:\n', np.round(scores, 3))

    new_doc = normalize('음성 인식과 텍스트 변환')# 새로운 문서

    # 기존 어휘와 IDF를 사용해서 변환
    vector = tfidf_vec.transform([new_doc])
    pp('새로운 문서 벡터 shape:', vector.shape)
    pp('새로운 문서와 기존 문서 유사도: \n')
    pp(np.round(cosine_similarity(vector,matrix), 3))

# 직접 생성한 가상 음성 신호를 WAV로 저장하고 읽는 함수
def inspect_audio():

    pp('오디오 파형, 샘플 수, 샘플링레이트')

    sr = 16000
    seconds = 1.5
    time = np.arange(int(sr*seconds)) / sr

    # 220 Hz 및 440 Hz 합성 : 실습용 신호
    # 진폭 * np.sin(2*np.pi*주파수*시간)
    samples = 0.35 * np.sin(2 * np.pi * 220 * time)
    samples += 0.15 * np.sin(2 * np.pi * 440 * time)

    # 실습용 신호를 WAV 파일로 생성
    path = BASE_DIR / 'sample.wav'
    sf.write(path, samples, sr)

    # 신호, 샘플링 비율
    signal, loaded_sr = librosa.load(
        path, # WAV 파일 경로
        sr = None, # 원래의 샘플링 비율을 사용
        mono = True # 1 채널 (모노)
    )

    duration = len(signal) / loaded_sr # 재셍시간(초)

    pp('파일 : ', path.name)
    pp('자료형 및 배열 크기 :', signal.dtype,signal.shape)
    pp('샘플링레이트(hz):', loaded_sr)
    pp('샘플 수: ', len(signal))
    pp(f'길이(초): {duration:.3f}')

    # X축은 샘플인덱스를 Hz로 나눈시간 (초)
    x = np.arange(len(signal)) / loaded_sr

    fig, ax = plt.subplots()
    ax.plot(x, signal,linewidth=8)
    ax.set(xlabel='Time (s)', ylabel='Amplitude',title = 'Audio Waveform')
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(BASE_DIR / 'waveform.png',dpi=130)
    plt.show()


if __name__ == '__main__':
    cleaned_docs = inspect_documents(DOCS)
    inspect_vectors(cleaned_docs)
    inspect_audio()









































































