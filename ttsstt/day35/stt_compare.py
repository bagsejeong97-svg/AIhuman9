# day35_stt_compare.py
# 동일한 WAV 파일로 두 STT 모델(WhisperModel, Kresnik) 비교

# Alt + F12 > python -m pip install transformers torch

import time
import librosa # WAV 파일 읽기
import torch # pytorch 딥러닝 모델
from faster_whisper import WhisperModel  # Whisper 모델
from transformers import AutoProcessor, AutoModelForCTC
from jiwer import wer, cer # 단어/문자 오류율

# WAV 파일명
WAV_FILE = "myvoice30s.wav"

# 정답 텍스트
with open("reference.txt", "r", encoding="utf-8") as f:
    REFERENCE = f.read().strip()

# 1. 음성 파일 읽기
y, sr = librosa.load(WAV_FILE, sr=16000, mono=True)  # 모노, 16kHz 변환
duration = len(y) / sr # 음성 길이(초)
device = "cuda" if torch.cuda.is_available() else "cpu"  # GPU/CPU 선택

# 2. faster-whisper 음성인식
whisper = WhisperModel(
    "medium", # 모델 크기
    device=device, # 실행 장치
    compute_type="float16" if device == "cuda" else "int8"
)

start = time.perf_counter() # 시작 시간
segments, info = whisper.transcribe(
    y, language="ko", beam_size=1 # 한국어, 빔 탐색 크기 1
)
# 전사 조각 합치기
whisper_text = " ".join(
    seg.text.strip() for seg in segments
).strip()
whisper_time = time.perf_counter() - start # 처리 시간

# 3. Kresnik 한국어 모델 음성인식
model_id = "kresnik/wav2vec2-large-xlsr-korean" # 모델 ID
processor = AutoProcessor.from_pretrained(model_id) # 입력 처리기
model = AutoModelForCTC.from_pretrained(model_id).to(device) # 모델 로드
model.eval() # 평가 모드

start = time.perf_counter() # 시작 시간
# 파형을 텐서로 변환
inputs = processor(
    y, sampling_rate=sr, return_tensors="pt", padding=True
)
input_values = inputs.input_values.to(device) # 실행 장치로 이동

with torch.inference_mode():
    logits = model(input_values).logits # 토큰별 예측 점수

ids = torch.argmax(logits, dim=-1) # 최고 점수 토큰 선택

kresnik_text = processor.batch_decode(ids)[0].strip() # 문장 변환

if device == "cuda":
    torch.cuda.synchronize() # GPU 연산 완료까지 대기
kresnik_time = time.perf_counter() - start  # 처리 시간

# 4. 성능 비교 결과 출력
print(f"\n음성 길이: {duration:.2f}초 / 장치: {device}")
print(f"정답: {REFERENCE}")

for name, prediction, seconds in [
    ("faster-whisper", whisper_text, whisper_time),
    ("Kresnik", kresnik_text, kresnik_time),
]:
    print(f"\n[{name}]") # 모델명
    print(f"전사: {prediction}") # 전사
    print(f"WER: {wer(REFERENCE, prediction):.2%}") # 단어 오류율
    print(f"CER: {cer(REFERENCE, prediction):.2%}") # 문자 오류율
    print(f"추론 시간: {seconds:.2f}초") # 추론 시간
    print(f"RTF: {seconds / duration:.3f}") # 실시간 처리 비율
