# day50_ex2.py
# 실제 GPT-2 모델에 LoRA를 적용해 짧은 분류 정답을 추가 학습

# 설치 : python -m pip install peft

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
from peft import LoraConfig, TaskType, get_peft_model, PeftModel
from util.print_util import pp, up

ROOT = Path(__file__).resolve().parent
MODEL_ID = 'sshleifer/tiny-gpt2' # 구조 학습용 초소형 영어 GPT-2
ADAPTER_DIR = ROOT / 'day50_lora_adapter'
PROMPT = 'Customer: I want to cancel my payment.\nCategory:'
ANSWER = ' refund'
TRAIN_STEPS = 100 # CPU에서도 가능한 소규모 반복 학습
LEARNING_RATE = 0.01 # 학습률

# 질문과 정답을 토큰으로 바꾸고, 정답 부분만 손실 계산에 포함하는 함수
# 반환값: input_ids와 labels가 담긴 딕셔너리
def make_training_batch(tokenizer, prompt, answer):
    prefix_ids = tokenizer.encode(prompt, add_special_tokens=False) # 질문 토큰ID들
    answer_ids = tokenizer.encode(answer, add_special_tokens=False) # 정답 토큰ID들
    if not answer_ids:
        raise ValueError('정답이 토큰으로 변환되지 않았습니다.')
    input_ids = torch.tensor([prefix_ids + answer_ids]) # PyTorch Tensor 생성
    # -100 : 정답이 아닌 질문 부분은 손실 계산에서 제외
    # 텍스트 입력 뒤에 정답을 붙여서 정답이 나타날 확률을 높이도록 학습
    labels = torch.tensor([[-100] * len(prefix_ids) + answer_ids]) # 레이블들
    return {'input_ids': input_ids, 'labels': labels}

# 정답의 첫 토큰이 선택될 확률을 확인하는 함수
# 반환값 : 목표 정답 첫 토큰의 예측 확률
def answer_probability(model, tokenizer, prompt, answer, device):
    prompt_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    answer_ids = tokenizer.encode(answer, add_special_tokens=False)
    model.eval() # 드롭아웃 등을 끄고 비교 조건을 일정하게 설정
    with torch.no_grad(): # 평가 과정에서는 기울기를 계산하지 않음
        logits = model(input_ids=prompt_ids).logits[0, -1]
        probs = torch.softmax(logits, dim=-1)
    return probs[answer_ids[0]].item()

def main():

    torch.manual_seed(42)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    pp('사용 장치: ', device)
    pp('기본 모델 다운로드/로드: ', MODEL_ID)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    base_model = AutoModelForCausalLM.from_pretrained(MODEL_ID)

    # LoRA 설정
    # GPT-2의 c_attn은 Query/Key/Value를 계산하는 투영 모듈
    config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r = 4, # 저랭크 어댑터 크기
        lora_alpha = 8, # 어댑터 업데이트의 스케일 조절
        lora_dropout = 0.0, # 학습 전후 확률 비교를 단순화 하기 위해 dropout 하지 않음
        target_modules = ['c_attn'],
        bias = 'none' # bias 제외
    )

    # 기본 모델 + LoRA 설정
    model = get_peft_model(base_model, config).to(device)

    pp('[1] LoRA를 적용한 실제 모델의 학습 대상')
    model.print_trainable_parameters() # 파라미터 수 출력
    trainable = [p for p in model.parameters() if p.requires_grad]
    pp('실제 업데이트할 파라미터 텐서: ', len(trainable), '개')

    before = answer_probability(model, tokenizer, PROMPT, ANSWER, device)

    pp('[2] 학습 전 정답 첫 토큰 확률: ', round(before, 6))

    batch = make_training_batch(tokenizer, PROMPT, ANSWER)
    batch = {key: value.to(device) for key, value in batch.items()}

    optimizer = torch.optim.AdamW(trainable, lr=LEARNING_RATE) # 옵티마이져

    pp('[3] LoRA만 실제 학습 시작')
    for step in range(1, TRAIN_STEPS + 1):
        model.train() # LoRA 가중치를 업데이트할 수 있는 학습 모드
        optimizer.zero_grad() # 직전 반복의 기울기를 초기화
        loss = model(**batch).loss # 정답 토큰에 대한 예측 오차 계산
        loss.backward() # LoRA A/B행렬의 기울기 계산
        optimizer.step() # 기울기를 이용하여 LoRA 가중치 업데이트
        if step==1 or step%20==0:
            pp(f'학습 {step:3d}/{TRAIN_STEPS}, 손실: {loss.item():.4f}')

    after = answer_probability(model, tokenizer, PROMPT, ANSWER, device)

    pp('[4] 정답 첫 토큰 확률 비교')
    pp('학습 전: ', round(before, 6), ', 학습 후: ', round(after, 6))
    pp('질문: ', PROMPT.replace('\n', '/'))
    pp('목표 정답: ', ANSWER.strip())

    model.save_pretrained(str(ADAPTER_DIR)) # LoRA 어댑터를 저장
    tokenizer.save_pretrained(str(ADAPTER_DIR))

    pp('[5] 학습된 어댑터 저장: ', ADAPTER_DIR)

    # 저장한 어댑터를 새 기본 모델에 연결해 재사용 가능한지 확인
    del model # 현재 학습 모델에 대한 참조 해제
    restored_base = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    restored = PeftModel.from_pretrained(restored_base, str(ADAPTER_DIR))
    restored = restored.to(device)
    reloaded = answer_probability(restored, tokenizer, PROMPT, ANSWER, device)

    pp('[6] 어댑터 재로드 후 정답 확률: ', round(reloaded, 6))

if __name__ == '__main__':
    main()

up(5)
























