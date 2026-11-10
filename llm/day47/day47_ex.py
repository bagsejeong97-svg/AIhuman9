# day47_ex.py
# LLM, Transformer, Tokenization, Self-Attention

# 설치 : python -m pip install transformers

# 실제 Hugging Face 토크나이저를 사용을 위해서는 환경변수에 RUN_HF_TOKENIZER=1 설정 해야 함

import csv
import os
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use('Agg')  # 그래프를 화면에 띄우지 않고 PNG 파일로 저장
import matplotlib.pyplot as plt
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

ROOT = Path(__file__).resolve().parent  # 현재 파일 경로
OUT = ROOT / 'outputs'  # 저장 경로
OUT.mkdir(parents=True, exist_ok=True)


# 점수 배열을 합계가 1인 가중치로 변환하는 softmax 함수
# scores : 마지막 축을 따라 정규화할 점수 배열
# 반환값 : 마지막 축의 합이 1인 넘파이 가중치 배열
def softmax(scores):
    scores = np.asarray(scores, dtype=float)  # 실수 배열로 변환
    # 마지막 축의 최대값을 빼서 exp계산시 값이 지나치게 커지는 현상을 방지
    shifted = scores - np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(shifted)  # 마지막 축의 지수값, 음의 무한대는 exp(-inf)=0
    return exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)


# 제목 출력 함수
def heading(title):
    pp('[' + title + ']')


'''
[LLM과 다음 토큰 예측]

[개념]
- LLM(Large Language Model, 대규모 언어 모델)은 이전 문맥을 참고하여 다음 토큰의
확률을 계산하고, 선택한 토큰을 이어 붙이는 과정을 반복
- Transformer는 Attention 매커니즘을 중심으로 토큰의 관계를 계산하는 신경망 구조

[예시]
입력 : '오늘 날씨가'
다음 토큰의 가상 확률 : '좋다':0.6, '춥다':0.3, '맑다':0.1
확률 합계 : 1.0, Greedy Decoding(최적의 확률 선택)에서는 '좋다'를 선택함

[용어]
- Token : 모델이 처리하는 텍스트 단위 (단어, 단어 일부, 문장 부호 등등...)
- Sequence : 순서대로 나열된 토큰들의 묶음
- Probability Distribution(확률 분포) : 후보별 확률을 나타낸 것으로 합계가 1임
- Conditional Probability(조건부 확률) : 어떤 조건이 주어졌을 때 그 조건 하에서 사건이 발생할 확률
- Greedy Decoding : 후보 중 가장 높은 확률의 토큰을 선택하는 방식

[조건부 확률 수식]
P(A|B) = P(A_and_B) / P(B), 단 P(B)>0 # A_and_B => A 교집합 B
P(x_t | x_1, x_2, ... ,x_(t-1)) : 이전 토큰들을 조건으로 다음 토큰 x_t 예측 확률
'''


# 다음 토큰 후보 확률과 Greedy 선택, 조건부 확률을 확인하는 함수
def example_probability():
    heading('다음 토큰 후보 확률과 Greedy 선택, 조건부 확률을 확인')
    candidates = {'좋다': 0.6, '춥다': 0.3, '맑다': 0.1}  # 후보 확률 딕셔너리
    pp('입력 문맥: ', '오늘 날씨가')
    pp('다음 토큰 후보 확률: ', candidates)
    pp('전체 확률의 합: ', sum(candidates.values()))
    pp('Greedy 선택: ', max(candidates, key=candidates.get))
    p_b, p_a_and_b = 0.5, 0.3  # 임의 설정
    pp('P(A|B) = P(A_and_B) / P(B) = ', p_a_and_b / p_b)


'''
[단어 수와 토큰 수의 차이]

[개념]
- Tokenization은 텍스트를 모델이 처리할 토큰들로 나누는 과정
- 공백 기준 단어 수와 실제 모델의 토큰수는 다를 수 있음

[예시]
- 'Transformer는'이라는 문장은 공백 기준 1개지만 서브워드(subword, 단어의 일부)로는
여러 토큰으로 분리될 수 있음
- '나는 사과를 먹는다' > ['나는', '사과를', '먹는다']는 공백 기준으로 이해를 돕기위한 토큰화일 뿐
  ['나', '는', '사과', '를', '먹', '는다'] 이런식의 토큰화도 가능함 (토크나이저에 따라서)

[용어]
- Tokenization : 입력 문자열을 토큰으로 분리하는 과정
- Subword : 단어의 일부에 해당하는 토큰
- Special Token : 모델이 시작, 종료, 구분 등에 사용하는 입력 문자열외의 특수한 토큰
- add_special_tokens=False : 특수 토큰 자동 추가를 끄는 옵션

[코드]
- 공백 단어 수 = len(text.split())
- 실제 모델 토큰 수 = len(tokenizer.encode(text, add_special_tokens=False))
'''


# 공백 기준 단어 분리가 실제 모델 토큰화와 다름은 보여주는 함수
def example_whitespace():
    heading('단어 수와 토큰 수의 차이')
    texts = ['AI Human', 'Transformer는 토큰 관계를 계산합니다.']
    for text in texts:
        words = text.split()
        pp('원문: ', text)
        pp('공백 단위: ', words, '개수: ', len(words))


'''
[Hugging Face 토크나이저 API]

[개념]
모델별로 저장된 토큰화 규칙을 불러와서 문장을 토큰ID(정수값)로 변환하고
다시 복원하는데 사용되는 Hugging Face의 API

[용어]
- AutoTokenizer : 모델에 맞는 토크나이저를 로드하는 클래스
- from_pretrained() : 공개된 모델의 토크나이저 설정을 읽는 메소드
- encode() : 텍스트를 정수 Token ID 목록으로 변환
- convert_ids_to_tokens() : Token ID를 토큰 문자열(모델이 분리한 조각)로 표시
- decode() : Token ID를 원본 텍스트로 복원
- return_tensors='np' : 결과를 넘파이 배열로 반환
- input_ids : 토큰 ID 배열
- attention_mask : 모델이 처리해야 할 실제 토큰과 길이를 맞추기 위해 추가한
                   가짜 토큰(padding)을 구분하는 배열
'''


# Hugging Face 토크나이저로 문장을 인코딩/디코딩 하는 함수
def example_huggingface():
    heading('Transformers 토크나이저 API')

    if os.environ.get('RUN_HF_TOKENIZER') != '1':
        pp('RUN_HF_TOKENIZER 환경변수를 설정해 주세요.')
        return

    try:

        from transformers import AutoTokenizer

        # 토크나이저 생성
        tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')

        text = 'AI휴먼은 문맥을 이해합니다.'

        # 특수 토큰은 포함하지 않고 텍스트를 인코딩해서 Token ID(정수값)들을 생성
        ids = tokenizer.encode(text, add_special_tokens=False)

        pp('원문: ', text)
        pp('특수 토큰 제외 Token ID: ', ids)
        pp('토큰 문자열: ', tokenizer.convert_ids_to_tokens(ids))
        pp('복원: ', tokenizer.decode(ids, skip_special_tokens=True))
        # 입력문자열을 토큰화하고 input_ids, attention_mask 등을 넘파이 배열로 반환
        encoded = tokenizer(text, return_tensors='np')
        pp('input_ids Shape: ', encoded['input_ids'].shape)
        pp('attention_mask: ', encoded['attention_mask'])

    except (ImportError, OSError, ValueError) as e:
        pp('토크나이저 실행 불가: ', e)


# 세 문장의 공백 토큰 수와 모델 토큰 수를 CSV 파일로 저장하는 함수
def save_token_report():
    sentences = [
        'AI휴먼은 문맥을 이해합니다.',
        'Transformer는 토큰 관계를 계산합니다.',
        'AI Human understands context.'
    ]

    tokenizer = None  # 모델 토크나이저 미사용
    if os.environ.get('RUN_HF_TOKENIZER') == '1':
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        except (ImportError, OSError, ValueError) as e:
            pp('모델 토크나이저 사용 불가, 공백 분석만 저장: ', e)

    rows = []  # CSV에 기록할 문장별 결과 저장 리스트
    for sentence in sentences:
        words = sentence.split()
        # 토크나이저 미사용시 행
        row = {
            'text': sentence,
            'space_tokens': len(words),
            'model_tokens': '',
            'model_ids': ''
        }
        # 토크나이저 사용시 행
        if tokenizer is not None:
            ids = tokenizer.encode(sentence, add_special_tokens=False)
            row['model_tokens'] = len(ids)  # 모델이 분리한 토큰 수
            row['model_ids'] = ' '.join(map(str, ids))  # Token ID를 문자열로 저장

        rows.append(row)
    path = OUT / 'token_report.csv'
    with path.open('w',newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f,fieldnames = rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    pp('토크 분석 CSV 저장: ',path.resolve())

'''
[다음 토큰 예측 과정과 Embedding]

[개념]
선택된 토큰을 문맥에 추가하고 예측을 반복함

[예측 과정]
입력 문장 > Tokenization > Token ID > Embedding > Positional Information > Transformer Block > Logits > Softmax > 다음 토큰 선택

[용어]
- Token ID : 토큰에 할당한 정수 식별자
- Embedding : 각 토큰 ID에 대응하는 실수 백터 
- Positional Information : 토큰의 순서 정보를 모델이 반영하는 방식/정보
- Transformer Block : Attention과 FFN 등을 이용하여 토큰의 정보를 가공하는 신경망의 기본 처리 단위
- FFN(Feed Forward Network) : Attention으로 문맥을 반영한 토큰 벡터를 추가로 변환하는 신경망
                              Attention은 토큰 정보를 섞고, FFN은 섞인 정보를 각 토큰별로 반환
- Logits : 출력 Softmax 적용 전 LLM이 다음 토큰 후보마다 계산한 최종 점수, 확률로 변환하기 전 값        
'''

# 가상의 Token ID, Embedding, Logits로 다음 토큰 예측 흐름을 보여주는 함수
def example_pipeline():
    heading('다음 토큰 예측 과정')
    tokens = ['AI','모델'] # 가상 토큰
    token_ids = [17,52] # 가상 토큰 ID
    rng = np.random.default_rng(47) # 난수 생성기
    table = rng.normal(0,0.3,size=(100,8)) # 가상 어휘 100개, 차원 8
    embeddings = table[token_ids] # 두 가상 토큰의 가상 임베딩 벡터
    positions = np.arange(len(tokens)) # 0부터 시작하는 토큰 위치 번호를 넘파이 배열로
    pp('토큰: ', tokens, '토큰ID: ', token_ids)
    pp('임베딩 Shape: ', embeddings.shape)
    pp('첫 토큰의 임베딩: ', np.round(embeddings[0],2))
    pp('위치 번호: ', positions)
    # Softmax 결과가 0.6, 0.3, 0.1이 퇴도록 가상 Logits를 역으로 구성
    logits = np.log(np.array([0.6,0.3,0.1]))
    pp('가상 Logits: ', np.round(logits,3))
    pp('Softmax 확률: ', np.round(softmax(logits),3))
    # np.argmax를 사용해 가장 높은 점수의 위치를 찾아 후보 토큰 선택
    pp('최대 확률 토큰: ', ['학습','개발','활용'][np.argmax(logits)])
    pp('다음 토큰 선택 후에는 그 토큰을 문맥에 추가하고 과정을 계속 반복')

'''
[입력 Shape의 의미]

[개념]
Shape는 배열의 차원별 원소 수

[용어]
- Tensor : 다차원 숫자 배열
- B(Batch Size) : 한번에 처리하는 문장 수
- L(Sequence Length) : 문장마다 처리하는 토큰 수
- D(Embedding Dimension) : 토큰 벡터의 실수의 개수

[수식]
Token ID Shape = (B, L)
Embedding Shape = (B, L, D)

[수식 예시]
B=2, L=4, D=8이면 Token ID Shape = (2, 4), Embedding Shape = (2, 4, 8)
그러므로 Token ID는 8개의 정수, Embedding은 64개의 실수
'''

# 배치 크기, 토큰 길이, 임베딩 차원에 따른 배열 Shape를 확인하는 함수
def example_shapes():
    heading('입력 Shape의 의미')
    b, l, d = 2, 4, 8
    # 0~7정수 8개를 2행 4열의 가상 Token ID 배열로
    input_ids = np.arange(b*l).reshape(b, l)
    # 문쟁 2개, 토큰 4개 , 벡터 차원 8의 3차원 실수 배열
    embeddings = np.zeros((b, l, d))
    # 패딩이 없다고 가정하여 입력 위치를 모두 1로 표시
    attention_mask = np.ones((b,l),dtype=int)
    pp('input_ids: ', input_ids)
    pp('input_ids Shape: ', input_ids.shape)
    pp( 'Mask Shape: ', attention_mask.shape)
    pp('Embedding Shape: ', embeddings.shape)
    pp('전체 실수 개수: ',embeddings.size)


'''
[Self-Attention의 Q, K, V와 문맥 벡터]

[개념]
Self-Attention은 같은 시퀀스의 토큰들에서 Q, K,V를 만들고 다른 토큰의 정보를 얼마나 반영할지 계산함
현재 토큰의 Q와 각 토큰의 K를 비교해 가중치를 정하고, V를 가중합하여 문맥 벤터(Context Vector)를 만듬

[용어]
- Q(Query): 현재 토큰이 찾으려는 정보를 나타내는 벡터, 예) 검색어
- K(Key) : 각 토큰이 비교에 제공하는 특징 벡터, 예) 각 웹페이지의 키워드
- V(Value) : 실제로 가중합할 정보 벡터, 예) 각 웹페이지가 가진 정보
            모델이 학습 과정에서 조정한 가중치 행렬 (Weight Matrix)와 임베딩의 곱
- Dot Product(내적) : 대응하는 원소끼리 곱한 값을 더하는 연산
                     Attention Score 연산에 내적을 사용
                     비슷한 정보는 비슷한 방향에 있다!
- Attention Score(Q@K.T) : Q와 K으 내적에 기반한 비교 점수 (내적 점수)                     
- Scaling : Attention Score를 np.sqrt(d_K)로 나누어 크기를 조절하는 과정
            차원이 너무 높은 것에 치중하지 않게 하려고 K벡터의 차원을 축소
- Attention Weight : Scaling 후 Softmax로 얻는 참고 비율, 한 Query에 대해 합계가 1
- Context Vector : 각 Value에 가중치를 곱하고 더한 결과

[수식]
Attention ( Q, K, V) = Softmax( (Q@K.T) / np.sqrt(d_K) ) @ V
K.T : Key 행렬을 전치
    Q와 여러 K의 내적을 행렬곱 한번으로 계산하기 위해 여러 K벡터를 하나의 행렬로 모은 다음 전치
d_k : Key 벡터의 차원수 (벡터 배열의 원소 수)
np.sqrt(d_k) : Key 벡터의 차원수를 루트 연산해서 Scaling

[수식 예시]
'은행'의 Q=[1,0], '은행'의 K1=[1,0], K2=[0,1]
Attention Score : Q@K1 = 1, Q@K2 = 0, Score = [1,0]
Attention Score Scaling : np.sqrt(2)로 나눈 점수 = [0.707, 0]
Attention Weight : Softmax Weight = 약 [0.670, 0.330]
Context Vector : V1=[1,2], V2=[3,4] 라고 하면 
                0.670@V1 + 0.330@V@ = [1.660, 2.660]      
'''

# 하나의 Query와 여러 Key, Value로 Attention 가중치와 묵맥 벡터를 계산하는 함수
def one_query_attention(q,k,v):
    q = np.asarray(q,dtype=float)
    k = np.asarray(k,dtype=float)
    v = np.asarray(v,dtype=float)

    # assert : 검사, 실패하면 AssertionError 발생
    assert q.ndim == 1 and k.ndim == 2 and v.ndim == 2 # Q가 1차원, K와 V가 2차원인지 검사
    assert k.shape[1] == q.shape[0] # Q와 K차원 일치여부 검사
    assert k.shape[0] == v.shape[0] # K와 V의 토큰 수 일치 여부 검사

    # K 행렬을 전치한 후 행렬곱 한번으로 모든 K와의 내적 점수 계산
    dot_scores = q @ k.T

    # 내적 점수를 K벡터의 차원 수의 제곱근으로 나눔
    scaled_scores = dot_scores / np.sqrt(k.shape[1])

    # 비교 점수를 합계 1인 상대적 Attention Weight으로 변환
    weights = softmax(scaled_scores)

    # 각 V를 Attention Weight만큼 반영한 문맥 벡터(Context Vector) 계산
    context = weights @ v
    pp('Q@K.T(내적): ', dot_scores)
    pp('np.sqrt(d_k)로 나눈 점수 : ', np.round(scaled_scores,3))
    pp('Softmax 가중치: ', np.round(weights,3))
    pp('가중치 합계: ', weights.sum())
    pp('Context Vector: ', np.round(context,3))

    return weights, context

def example_attention():
    heading('Causal Mask 없는 일반  Attention')
    q = np.array([1.,0.]) # '은행'의 Query
    k = np.array([[1.,0.],[0.,1.]]) # '은행', '돈'의 key
    v = np.array([[1.,2.],[3.,4.]]) # '은행', '돈'의 value
    one_query_attention(q,k,v)


'''
[Causal Mask의 역할]

[개념]
- Decoder-only 생성형 LLM에서 현재 토큰이 미래 위치의 토큰 정보를 보지 못하도록 차단함
- Decoder-inly LLM은 Encoder 없이 Decoder Block만으로 입력 문맥을 처리하고
다음 토큰을 새엇ㅇ하는 모델 ex) Chat GPT ...

[용어]
- Causal Mask : 미래 토큰 참조를 막는 마스크
- Padding Mask : 길이를 맞추기 위해 추가된 패딩 위치를 제외하는 마스크
- np.triu() : 주대각선 위쪽 영역만 남기는 넘파이 함수
- K=1 : 주대각선 바로 윗칸부터 선택 옵션

[예시]
3개 토큰의 미래 위치 : 
[
    [F, T, T], 
    [F, F, T],
    [F, F, F]
    ]
첫번째 토큰 점수 => [1, -inf, -inf] => softmax [1,0,0] (미래 토큰 확률은 0)
두번째 토큰 점수 => [1, 1, -inf] => softmax [1,1,0] (미래 토큰 확률은 0)
'''
# 여러 Query의 Attention을 행렬곱으로 계산하며 Causal Mask도 지원하는 함수
def matrix_attention(q,k,v,causal=False):
    q = np.asarray(q, dtype=float)  # Query를 실수형 넘파이 배열로 통일하여 벡터 계산 준비
    k = np.asarray(k, dtype=float)  # Key를 실수형 넘파이 배열로 통일
    v = np.asarray(v, dtype=float)  # Value를 실수형 넘파이 배열로 통일
    assert q.ndim == k.ndim == v.ndim == 2  # 여러 토큰의 Q, K, V가 모두 2차원 행렬인지 확인
    assert q.shape[1] == k.shape[1]  # Query와 Key의 벡터 차원이 같아야 내적이 가능
    assert k.shape[0] == v.shape[0]  # Key마다 대응하는 Value가 하나씩 있어야 함
    scores = (q @ k.T) / np.sqrt(k.shape[1])  # 모든 Query와 Key 내적을 구하고 Key 차원 제곱근으로 Scaling
    if causal:  # 미래 토큰 참조를 차단하는 Causal Mask 옵션이 켜진 경우
        assert q.shape[0] == k.shape[0]  # 이 실습의 미래 위치 마스크는 Query, Key 토큰 수가 같다고 가정
        future = np.triu(np.ones(scores.shape, dtype=bool), k=1)  # 주대각선 위쪽의 미래 토큰 위치만 True인 마스크 생성
        scores[future] = -np.inf  # 미래 위치 점수를 음의 무한대로 바꾸어 Softmax 후 가중치 0으로 처리
    weights = softmax(scores)  # 각 Query 행별로 Key 가중치를 정규화
    context = weights @ v  # 행렬곱으로 Query별 Value 가중합을 계산
    return weights, context  # 전체 Query의 Attention 가중치와 문맥 벡터를 반환

# 미래 토큰 차단 전후의 Attention 가중치와 문맥 벡터를 비교하는 함수
# 반환값 : (Causal Mask 적용 가중치 행렬, 문맥 행렬)
def example_causal_mask():
    heading("Causal Mask의 역할")
    q = np.array([[1., 0.], [0., 1.], [1., 1.]])
    k = q.copy()  # 실습용으로 Q 값을 복사하되 별도 배열을 생성
    v = np.array([[1., 2.], [3., 4.], [5., 6.]])
    # 3개 토큰 중 미래 위치를 표시하는 3×3 불리언 마스크 생성
    future = np.triu(np.ones((3, 3), dtype=bool), k=1)
    pp("미래 토큰 위치(True는 참조 금지):\n", future)
    # 미래 토큰을 볼 수 있는 마스크 미적용 가중치 계산
    weights_before, _ = matrix_attention(q, k, v, causal=False)
    # 미래 토큰을 차단한 가중치와 문맥 벡터 계산
    weights_after, context = matrix_attention(q, k, v, causal=True)
    pp("마스크 미적용:\n", np.round(weights_before, 3))
    pp("마스크 적용:\n", np.round(weights_after, 3))
    # Query마다 Key 가중치의 합이 1인지 행 기준으로 확인
    pp("행 합계:", weights_after.sum(axis=1))
    pp("문맥 벡터:\n", np.round(context, 3))
    return weights_after, context







# Attention 가중치를 색으로 표현하여 PNG 이미지로 저장하는 함수
# weights : (Query 수, Key 수) Attention 가중치 행렬
def example_heatmap(weights):
    heading("Attention Heatmap")
    fig, ax = plt.subplots()
    # 0~1 가중치를 파란색 농도로 표현하는 히트맵 생성
    image = ax.imshow(weights, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(weights.shape[1]))  # 가로축에 Key 토큰의 열 번호를 표시
    ax.set_yticks(range(weights.shape[0]))  # 세로축에 Query 토큰의 행 번호를 표시
    ax.set_xlabel("Key token")
    ax.set_ylabel("Query token")
    ax.set_title("Causal Self-Attention")
    # 색 농도가 어떤 가중치 값에 해당하는지 범례 추가
    fig.colorbar(image, ax=ax, label="Weight")
    fig.tight_layout()
    filename = OUT / "attention_heatmap.png"
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    pp("저장:", filename)
    return filename

# 토큰 간 Attention 가중치 행렬을 CSV 파일로 저장하는 함수
# weights : 3행 3열 Attention 가중치 행렬
def save_attention_weights_csv(weights):
    tokens = ['input', 'context', 'output']
    # 가중치 행렬의 행, 열 수가 토큰 수와 같은지 검사
    if weights.shape != (len(tokens), len(tokens)):
        raise ValueError('토큰 수와 Attention 행렬 크기가 일치해야 함.')
    path = OUT / 'attention_weights.csv'
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['query/key'] + tokens)
        for token, row in zip(tokens, weights):
            writer.writerow([token] + [round(float(x), 4) for x in row])
    pp('Attention 가중치 CSV 저장:', path.resolve())


def main():
    # example_probability()
    # example_whitespace()
    # example_huggingface()
    # save_token_report()
    # example_pipeline()
    # example_shapes()
    # example_attention()
    weights, _ = example_causal_mask()
    # pp(weights)
    # example_heatmap(weights)
    save_attention_weights_csv(weights)

if __name__ == '__main__':
    main()

up(5)
































