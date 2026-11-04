# day23_application.py
# 주제:
# day23_application.py

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from util.print_util import pp, up

keras.utils.set_random_seed(42)

X = np.array([
    [0.95, 0.80, 0.05], [0.88, 0.70, 0.10], [0.82, 0.65, 0.08],
    [0.75, 0.55, 0.15], [0.68, 0.50, 0.18], [0.60, 0.42, 0.20],
    [0.48, 0.35, 0.35], [0.40, 0.30, 0.42], [0.32, 0.25, 0.50],
    [0.25, 0.18, 0.58], [0.18, 0.12, 0.68], [0.10, 0.08, 0.80]
], dtype=np.float32)

y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], dtype=np.float32)

model = keras.Sequential([
    layers.Input(shape=(3,)), # 로그인, 구매, 문의비율 3개 특성을 입력
    layers.Dense(8, activation='relu', name='hidden1'),
    layers.Dense(4, activation='relu', name='hidden2'),
    layers.Dense(1, activation='sigmoid', name='churn')
], name='churn_model')

model.summary(print_fn=lambda line: pp(line))

manual_params = (3*8 + 8) + (8*4 + 4) + (4*1 + 1)
pp('직접 계산한 파라미터 수: ', manual_params)
pp('Keras 파라미터 수: ', model.count_params())

# 모델 설정
model.compile(
    optimizer='adam',
    loss='binary_crossentropy', # 이진 분류 손실
    metrics=['accuracy']
)

# 학습
history = model.fit(
    X,
    y,
    epochs=250,
    verbose=0
)

pp(f'최종 Loss: {history.history["loss"][-1]:.6f}')
pp(f'최종 Accuracy: {history.history["accuracy"][-1]:.4f}')

new_users = np.array([
    [0.90, 0.72, 0.08],
    [0.45, 0.28, 0.45],
    [0.16, 0.10, 0.74]
], dtype=np.float32)

# 클래스에 속할 확률
probabilites = model.predict(new_users, verbose=0).reshape(-1)

# 클래스
classes = (probabilites >= 0.5).astype(int)

for index, (probability, predicted_class) in \
    enumerate(zip(probabilites, classes), start=1):
    staus = '이탈' if predicted_class==1 else '유지'
    pp(f'회원 {index}: 이탈확률={probability:.4f}, \
        예측={predicted_class}({staus})')

up(5)










