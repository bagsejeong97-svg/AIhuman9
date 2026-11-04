# day48_application.py
# 여행 계획 문장 생성 : Top-k와 Top-p 비교

import time
from pathlib import Path
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from util.print_util import pp, up

MODEL_ID = 'HuggingFaceTB/SmolLM2-135M-Instruct'

ROOT = Path(__file__).resolve().parent

# 토크나이저와 모델 로딩, 장치 설치
def setup():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    model.to(device)
    model.eval()
    return tokenizer, model, device

# 프롬프트와 generate() 인자를 전달 받아 결과 텍스트, 길이, 시간 반환 함수
def infer(tokenizer, model, device, prompt, params, seed=2026):
    torch.manual_seed(seed)

    messages = [{'role': 'user', 'content': prompt}] # 사용자 프롬프트

    # 모델이 학습한 대화 형식으로 변환
    tokens = tokenizer.apply_chat_template(
        messages, # 사용자 프롬프트를 포함한 메세지
        add_generation_prompt=True, # 생성된 프롬프트 추가
        tokenize=True, # 토큰화
        return_dict=True, # 딕셔너리로 반환
        return_tensors='pt' # PyTorch텐서 반환
    )

    tokens = {key: val.to(device) for key, val in tokens.items()}
    start_len = tokens["input_ids"].shape[1]
    start = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **tokens, pad_token_id=tokenizer.eos_token_id, **params
        )
    elapsed = time.perf_counter() - start
    new_ids = output[0, start_len:]
    answer = tokenizer.decode(new_ids, skip_special_tokens=True)
    return answer.strip(), len(new_ids), round(elapsed, 3)

def main():

    tokenizer, model, device = setup()

    prompt = ("Recommend a one-day walking itinerary in Kyoto "
              "in three concise English sentences.")

    settings = [
        ('top_k_10', {'top_k': 10, 'top_p': 1.0}),
        ('top_k_50', {'top_k': 50, 'top_p': 1.0}),
        ('top_p_075', {'top_k': 0, 'top_p': 0.75}),
        ('top_p_095', {'top_k': 0, 'top_p': 0.95})
    ]

    records = []

    for name, filters in settings:
        params = {'do_sample': True, 'temperature': 0.8, 'max_new_tokens': 75, **filters}
        answer, count, seconds = infer(tokenizer, model, device, prompt, params)
        records.append({
            'setting': name,
            'response': answer,
            'new_tokens': count,
            'seconds': seconds
        })
        pp(name, answer)

    out = ROOT / 'travel_results.csv'
    pd.DataFrame(records).to_csv(out, index=False, encoding='utf-8-sig')
    pp(f'Saved: {out}')

if __name__ == '__main__':
    main()

up(5)











