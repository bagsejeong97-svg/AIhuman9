# day25_application.py
# 배송량 시계열의 다음 날 물량 예측

import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from util.print_util import pp
from include.graph_config import set_graph

set_graph(10, 8, 13)

np.random.seed(240)
keras.utils.set_random_seed(240)

def make_delivery_series(day_count=840):
    days = np.arange(day_count, dtype="float32")
    trend = 180 + days * 0.09  # 장기적으로 조금씩 증가하는 배송량
    weekly = 28 * np.sin(2 * np.pi * days / 7)  # 7일 주기 반복 패턴
    noise = np.random.normal(0, 8, day_count).astype("float32")
    return (trend + weekly + noise).astype("float32")

def make_windows(series, window_size=14):
    X, y = [], []
    for end in range(window_size, len(series)):
        X.append(series[end - window_size:end])  # 최근 14일을 한 입력으로 구성
        y.append(series[end])  # 바로 다음 날 배송량
    X = np.array(X, dtype="float32")[..., np.newaxis]  # (samples, 14, 1)
    y = np.array(y, dtype="float32")
    return X, y

series = make_delivery_series()

X, y = make_windows(series, window_size=14)

split = int(len(X) * 0.8)

X_train, X_test = X[:split], X[split:]  # 시간 순서를 유지하여 분할

y_train, y_test = y[:split], y[split:]

mean = X_train.mean()  # 학습 구간에서만 정규화 기준 계산
std = X_train.std()

X_train_scaled = (X_train - mean) / std
X_test_scaled = (X_test - mean) / std
y_train_scaled = (y_train - mean) / std  # 출력도 같은 단위로 정규화
y_test_scaled = (y_test - mean) / std

pp("원본 시계열 길이", len(series))
pp("X/y shape", X.shape, y.shape)
pp("학습/평가 shape", X_train.shape, X_test.shape)
pp("입력 timesteps/features", X.shape[1], X.shape[2])

model = keras.Sequential([
    keras.Input(shape=(14, 1)),
    keras.layers.LSTM(32),  # 최근 14일의 순차 패턴을 하나의 상태 벡터로 압축
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(1)  # 회귀 출력이므로 별도 활성화 함수를 사용하지 않음
], name="delivery_lstm")

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

model.fit(
    X_train_scaled,
    y_train_scaled,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    shuffle=False,  # 시계열 내부 순서를 보존하도록 배치 섞기를 사용하지 않음
    verbose=0
)

pred_scaled = model.predict(X_test_scaled, verbose=0).reshape(-1)
pred = pred_scaled * std + mean  # 원래 배송량 단위로 복원
mae = np.mean(np.abs(y_test - pred))

pp("평가 MAE", round(float(mae), 3))
pp("실제 배송량 앞 10개", np.round(y_test[:10], 1))
pp("예측 배송량 앞 10개", np.round(pred[:10], 1))

plt.plot(y_test, label="실제 배송량")
plt.plot(pred, label="예측 배송량")
plt.xlabel("평가 구간 일자 인덱스")
plt.ylabel("배송량")
plt.title("LSTM 다음 날 배송량 예측")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

up(5)
