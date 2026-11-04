# day48_ex.py
# 주제: LLaMA 계열 모델 추론 및 생성 파라미터 비교

# 섶이 : python -m pip install torch

import time
from pathlib import Path
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from util.print_util import pp

MODEL_ID = 'HuggingFaceTB/SmolLM2-135M-Instruct'

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / 'generation_result.csv'

PROMPT = 'Explain why testing matters in software in two short sentences.'

MAX_NEW_TOKENS = 60 # 생성할 최대 토큰 수

SEED = 42

'''
[LLaMA 계열 모델과 생성 파라미터]

[개념]
- 앞에 나온 토큰들을 이용해 다음 토큰을 차례대로 예측
- 동일한 입력이어도 토큰 선택 방식에 따라 결과각 달라질 수 있음

[용어]
- LLaMA(Large Language Model Meta AI): Meta 사의 언어 모델
- Decoder-only: 앞쪽 토큰을 참고해서 다음 토큰을 생성하는 구조
- Autoregressive(자기회귀): 직전까지 생성한 토큰도 다음 예측에 사용
- SmolL2: LLaMA 아키텍쳐를 사용하는 공개된 소형 모델, Meta의 공식 LLaMa의 축소 버젼

[수식]
- P(x1,x2,x3) = p(x1) * P(x2|x1) * P(x3|x1, x2)
- x1이 나오고 x2가 나오고 x3가 나올 확률 = x1이 나올 확률 * x1이 나왔는데 x2가 나올 확률
  * x1이 나오고 x2가 나왔는데 x3가 나올 확률
[수식 예시]
- 0.5 * 0.4 * 0.3 = 0.06, 특정 세개의 토큰이 순서대로 나올 확률 6%
'''
# 학습된 모델과 토크나이저를 불러와 연산 장치를 설정하는 함수
# 반환값: (tokenizer, model, device) 튜플
def load_model():
    # GPU 사용가능하면 GPU에서 연산, 그렇지 않으면 cpu
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    pp(f'모델 로딩: {MODEL_ID}, 장치: {device}')
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID) # 학습된 토크나이저
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID) # 학습된 모델
    model.to(device) # 모델 가중치 계산을 gpu나 cpu 에서 수행
    model.eval() # 평가 모드로 변경
    return tokenizer, model, device

# 동일 모델을 다시 다운로드하지 않도록 필요한 시점에만 로드하는 함수
# state: 모델과 실험 결과 등을 저장하는 딕셔너리
# 반환값 : (tokenizer, model, device) 튜플
def ensure_model(state):
    if 'bundle' not in state:
        state['bundle'] = load_model()
    return state['bundle']

# 하나의 프롬프트에서 세 토큰을 생성하고 생성 속도를 계산하는 함수
# prompt: 모델에 전달할 입력 텍스트
# params: generate()에 전달할 생성 옵션 딕셔너리
# 반환값: answer, tokens, seconds, tokens_per_sec 등을 담은 딕셔너리
def generate_text(tokenizer, model, device, prompt, params, seed=SEED):
    torch.manual_seed(seed) # 샘플링의 난수 초기 상태 수동 설정
    messages = [{'role':'user','content':prompt}] # 사용자 프롬프트 (프롬프트 종류는 3종류 있다)
    # inputs = tokenizer(prompt, return_tensors='pt') # PyTorch Tensor
    # 모델이 학습한 대화 형식으로 변환
    inputs = tokenizer.apply_chat_template(
        messages, # 사용자 프롬프트를 포함한 메세지
        add_generation_prompt=True, # 생성된 프롬프트 추가
        tokenize=True, # 토큰화
        return_dict=True, # 딕셔너리로 반환
        return_tensors='pt' # PyTorch텐서 반환
    )
    inputs = {key: value.to(device) for key, value in inputs.items()} # 딕셔너리
    input_len = inputs['input_ids'].shape[1] # 배치 차원 뒤 토큰 수 (B L 에서 L)
    begin = time.perf_counter()
    with torch.inference_mode(): # 추론 문맥 사용
        output = model.generate(
            **inputs, # input_ids와 attention_mask 등을 펼쳐서 전달
            pad_token_id = tokenizer.eos_token_id, # eos_token_id 모델이 추가한 시퀀스 종료토큰ID
            **params # do_sample, temperature, top_k 등의 옵션 파라미터들
        )
    seconds = time.perf_counter() - begin # 소요 시간
    new_ids = output[0,input_len:] # 전체 출력에서 프롬프트 제거한 토큰들의 ID
# 추가
    pp(f'생성 토큰 ID:{new_ids.tolist()}') # 생성한 토큰의 ID들
    # 특수 토큰을 제거하지 않는 원본 출력
    pp('원본 출력', repr(
        tokenizer.decode(new_ids, skip_special_tokens=False)
    ))

    # 토큰 ID를 문자열로 디코딩
    answer = tokenizer.decode(new_ids,skip_special_tokens=True)
    tokens = len(new_ids) # 새로 생성된 토큰 수
    speed = tokens / seconds if seconds > 0 else 0.0 # 초 당 생성된 토큰
    return {
        'answer': answer.strip(),
        'tokens': tokens,
        'seconds': round(seconds,3),
        'tokens_per_sec': round(speed,3)
    }

# 단일 실험 조건을 실행하여 메모리 결과 목록에 기록하는 함수
# state: 모델 캐시와 records 목록이 들어 있는 딕셔너리
# name: 실험 조건 식별 문자열, 예) 'greedy'
# params: generate()용 생성 옵션 딕셔너리
# 반환값 : 생성 텍스트와 시간 등이 기록된 딕셔너리
def run_case(state, name, params):
    tokenizer, model, device = ensure_model(state)
    options = {'max_new_tokens': MAX_NEW_TOKENS, **params}
    result = generate_text(tokenizer, model, device, PROMPT, options)
    record = {'setting': name, **result}
    state['records']=[
        row for row in state['records'] if row['setting'] != name
    ]
    state['records'].append(record)
    pp(f"[{name}] {result['answer']}")
    pp(f"생성토큰: {result['tokens']}개")
    pp(f"생성시간: {result['seconds']}초")
    pp(f"처리량: {result['tokens_per_sec']} tokens/s")

'''
[1단계, 모델 로딩과 연산 장치 확인]

[개념]
- Checkpoint에 저장된 가중치와 설정을 읽어 추론용 모델 준비
- 같은 모델을 반복 다운로드하지 않고 state에 저장한 객체를 재사용

[용어]
- Checkpoint: 학습된 가중치와 모델 설정을 저장한 파일 묶음
- Causal LM(Causal Language Model): 이전 토큰으로 당므 토큰을 예측하는 모델
- CUDA : NVIDIA GPU 연산 실행 환경

[예시]
- 모델 파라미터 1억 3,500만개를 4바이트를 저장하면 약 540MB
- 실제 메모리는 설정, 임시 텐서 등에 따라 이보다 더 필요
'''

# 1단계, 모델 및 토크나이저를 로드하고 기본 정보를 확인하는 함수
def step_1(state):
    pp('[1단계] 모델 로딩과 연산 장치를 확인')
    tokenizer, model, device = ensure_model(state)
    pp(f'장치:{device}')
    pp(f'토크나이저:{type(tokenizer).__name__}')
    pp(f'모델:{type(model).__name__}')

'''
[2단계, 토큰화와 Tensor 확인]

[개념]
- 사람이 읽는 문장을 정수형 토큰 ID로 변환해 모델에 입력
- 모델 입력에는 토큰 ID와 유효 입력 위치를 나타내는 마스크(Attention Mask) 사용

[예시]
- input_ids.shape = (1, 8) 이면 문장 1개(B), 입력토큰 8개(L)
- attention_mask = [1,1,1,0]이면 마지막 위치는 패딩
- 토큰ID [101, 205]는 설명용 가상? 

[수식]
- 문자 수 = inputs['input_ids'].shape[0]
- 입력 토큰 수 = inputs['input_ids'].shape[1]
'''

# 2단계, 프롬프트를 토큰ID로 인코딩 하고 역변환(텍스트로 변환) 하는 함수
def step_2(state):
    pp('[2단계] 토큰화, Tensor, 입력길이')
    tokenizer,_,_ = ensure_model(state) # 토크나이저만
    inputs = tokenizer(PROMPT, return_tensors='pt')  # PyTorch 텐서 변환
    pp(f'input_ids: {inputs["input_ids"].tolist()}')
    pp(f'shape:{tuple(inputs["input_ids"].shape)}')
    pp(f'입력 토큰 수:{inputs["input_ids"].shape[1]}')
    if 'attention_mask' in inputs:
        pp(f'attention_mask: {inputs["attention_mask"].tolist()}')
    pp(f'역변환:{tokenizer.decode(inputs["input_ids"][0])}')

'''
[3단계, 첫 생성과 Greedy Decoding]

[개념]
- Decoder-only모델은 입력 토큰 뒤에 신규 토큰을 붙여 문장 생성
- Greedy는 매 단계 가장 높은 점수의 토큰을 선택하는 방식
- 생성된 전체 토큰에서 입력 구간을 제외한 신규 토큰만 디코딩

[용어]
- Inference(추론): 학습된 가중치를 변경하지 않고 예측 수행
- Generation(생성): 다음 토큰 예측과 선택을 반복해 문장 확장
- Logits: 확률로 변환하기 전 후보 투큰의 원시 점수
- EOS(End of Sequence): 시퀀스(순서대로 나열된 토큰들) 종료를 알리는 특수 토큰

[예시]
- 후보 확률 A=0.6, B=0.3, C=0.1 Greedy는 A를 선택
- 입력 8개, 신규 5개면 출력 13개, output[0, 8:]로 신규 5개 선택
'''

# 3단계, Greedy 방식의 첫 문장 생성을 실행하는 함수
def step_3(state):
    pp('[3단계] 첫 생성과 Greedy Decoding')
    run_case(state, 'greedy', {'do_sample': False})


'''
[4단계, Sampling과 Temperature]

[개념]
- Sampling은 확률에 따라 다음 토큰을 무작위로 선택하는 방식
- Temperature는 확률 분포의 집중도를 조정하는 양수 값
- 비교 시 모델, 프롬프트, 최대 생성 토큰 수를 동일하게 유지

[용어]
- Sampling: 확률 분포를 이용한 토큰 추출
- Temperature(T): Logits를 나눠서 후보 확률의 차이를 조절

[API]
- do_sample=True: 확률적 샘플링 활성화
- temperature=0.3: 높은 점수 토큰애 확률이 크게 집중
- temperature=1.0: 기본값
- temperature=1.2: 상대적으로 다양한 후보 선택 가능성 증대

[수식]
- P(i) = exp(z_i / T) / Σ_j exp(z_j / T)
- z_i 는 i번째 토큰 로짓, T는 Temperature, exp는 자연 지수 함수

[수식 예시]     티 원~~일떄 제제야
- 로짓 [2,1], T=1 이면 확률 [0.731, 0.269]
- 로짓 [2,1], T=0.5 이면 확률 [0.881, 0.119]
- 로짓 [2,1], T=2 이면 확률 [0.662, 0.378] 
'''
# 4단계, Temperature만 달리하는 샘플링 실험 함수
def step_4(state):
    pp('[4단계] Sampling 과 Temperature')
    common = {'do_sample': True, 'top_k': 50, 'top_p':1.0}
    for name, temp in [('temperature_low',0.3), ('temperature_high',1.2)]:
        run_case(state,name, {**common, 'temperature':temp})


'''
[5단계, Top-k 후보 개수 제한]
[개념]
- 다음 토큰 확률이 높은 상위 k개 후보만 남겨 샘플링
- 나머지 후보 확률을 0으로 만든 후 남은 확률을 재정규화

[용어]
- Top-k Sampling: 확률 순위에 따라 후보 수를 제한하는 방식
- Candidate: 다음 토큰으로 선택될 수 있는 후보
- Renormalization(재정규화): 후보 수 제한으로 선택된 후보들의 확률 합을 다시 1로 맞추는 과정

[수식]
- 재정규화 확률 = 남은 후보의 기존 확률 / 남은 후보들의 확률의 합

[수식 예시]
- 원래 확률 [0.05,0.30,0.15,0.05], k=2
- 남은 확률[0.50,0.30], 합계 0.80
- 재정규화 후 최종 확률 [0.50/0.80, 0.30 / 0.80] = [0.625, 0.175]
'''

# 5단계, Top-k 필터의 의미와 실제 출력을 확인하는 함수
def step_5(state):
    pp('[5단계] Top-k 후보 개수 제한')
    run_case(state, 'top_k_10', {
        'do_sample': True , 'temperature':0.8, 'top_k':10,'top_p':1.0
    })


'''
[6단계, Top-p와 Nucleus Sampling]

[개념]
- 확률이 높은 토큰부터 확률들을 더해서 누적 확률이 p 이상인 최소 집합 선택
- Top-k와 달리 선택되는 후보 수가 확률 분포마다 달라짐

[용어]
- Top-p Sampling: 누적 확률을 기준으로 후보를 제한하는 방식
- Nucleus Sampling: Top-p Sampling의 다른 이름
- Cumulative Probability(누적 확률): 후보 확률을 상위에서 부터 차례대로 더한 값

[수식]
- p 이상을 처음 만족하는 후보 수 n 선택
- P1 + P2 + ... + Pn, >= p

[수식 예시]
- 후보 확률 [0.50, 0.25, 0.15, 0.10], p=0.8
- 2개 누적 0.75 부족, 3개 누적 0.90이므로 3개 유지
- 재정규화 [0.50/0,90, 0.25/0.90, 0.15/0.90]
- 최종 확률 [0.556,0.278,0.167], 합은 1.0
'''

# 6단계, Top-p 후보 누적 확률을 확인하는 함수
def step_6(state):
    pp('[6단계] Top-p Sampling')
    run_case(state, 'top_p_08', {
        'do_sample': True , 'temperature':0.8, 'top_k':0,'top_p':0.8
    })

'''
[7단계, Repetition Penalty와 재현성]

[개념]
- 반복 억제 계수를 적용해 이미 등장한 토크의 재선택 경향 조정 => 반복이 안되게
- 같은 생성 조건에서 패널티를 적용하기 위해 전후 응답 비교

[용어]
- Repetition Penalty(반복 패널티): 기존 등장한 토큰의 로짓 조정 계수
- Baseline(기준선): 변경한 설정의 효과를 비교할 기본 실험
- Reproducibility(재현가능성): 같은 조건에서 결과를 반복 확인하는 성질

[API]
- repetition_penalty = 1.0 : 반복 패널티 미적용
- repetition_penalty = 1.2 : 이미 나온 토큰에 반복 패널티 적용

[수식]
- 이미 나온 토큰의 로짓 z가 양수이면 z` = z / penalty
- 이미 나온 토큰의 로짓 z가 음수이면 z` = z * penalty

[수식 예시]
- z=2.4, penalty=1.2이면 저정된 점수 z` = 2.4/ 1.2 = 2.0
- z=-1.0, penalty=1.2이면 저정된 점수 z` = -1.0 / 1.2 = -1.2

'''
# 7단계, 이미 등장한 토큰에 대한 반복 억제를 확인하는 함수
def step_7(state):
    pp('[7단계] Repetition Penalty와 재현성')
    common = {
        'do_sample': True , 'temperature':0.8, 'top_k':50,'top_p':1.0
    }
    run_case(state, 'repetition_baseline', common)
    run_case(state, 'repetition_control', {
        **common, 'repetition_penalty':1.2,
    })

'''
[8단계, 생성 성능 지표와 CSV저장]

[개념]
- 각 설정의 생성 텍스트, 토큰 수, 소요시간, 처리량을 표로 비교
- CSV 파일로 결과를 보존하고 엑셀이나 pandas에서 후속 분석

[용어]
- Latency(지연시간): 모델 생성 호출에 소요된 시간
- Generate Tokens(생성 토큰 수): 입력을 제외하고 새로 나온 토큰 수
- Throughput(처리량): 초당 생성된 신규 토큰 수

[수식]
- 처리량(tokens/s) = 신규 생성 토큰 수 / 생성 소요 시간

[수식 예시]
- 60토큰 생성에 3초 소요되었다면 60/3 = 20 tokems/s
- 45토큰 생성에 2.5초 소요되었다면 45/2.5 = 18 tokems/s
'''

# 8단계, 현재까지 실행한 실험의 성능을 비교하고 CSV로 저장하는 함수
def step_8(state):
    pp('[8단계] 성능 지표 비교와 CSV 결과 저장')
    if not state['records']:
        pp('저장할 결과가 없음')
        return
    frame = pd.DataFrame(state['records'])
    cols = ['setting', 'tokens', 'seconds', 'tokens_per_sec']
    pp(frame[cols].to_string(index=False))
    frame.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
    pp((f'CSV 저장 완료 : {OUT_FILE}'))


def main():
    # pp(load_model()) # 학습된 모델과 토크나이저를 불러와 연산 장치를 설정하는 함수
    state = {'records': []} # 모델 캐시와 생성 결과를 공유할 상태 딕셔너리
    step_1(state) # 모델과 토크나이저 준비
    step_2(state) # 입력 문장 토큰화 및 텐서 확인
    step_3(state) # Greedy 방식으로 첫 문장 생성
    step_4(state) # Temperature 샘플링
    step_5(state) # Top-k 샘플링
    step_6(state) # Top-p 샘플링
    step_7(state) # repetition_penalty
    step_8(state) # 전체 생성결과를 CSV 저장
if __name__ == '__main__':
    main()
































