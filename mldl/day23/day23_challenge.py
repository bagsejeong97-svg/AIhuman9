# day23_challenge.py
# 주제:
# day23_challenge.py

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from util.print_util import pp, up

keras.utils.set_random_seed(42)

X = np.array([
    [0.30, 0.20, 0.55, 0.45], [0.35, 0.25, 0.52, 0.48],
    [0.40, 0.28, 0.50, 0.50], [0.45, 0.35, 0.48, 0.55],
    [0.55, 0.48, 0.45, 0.62], [0.58, 0.52, 0.43, 0.65],
    [0.62, 0.58, 0.42, 0.68], [0.66, 0.62, 0.40, 0.70],
    [0.72, 0.75, 0.34, 0.78], [0.78, 0.82, 0.30, 0.82],
    [0.85, 0.90, 0.25, 0.88], [0.92, 0.96, 0.20, 0.94]
], dtype=np.float32)

y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2], dtype=np.int32)

class_names = np.array(["정상", "점검필요", "위험"])

# 모델 생성 함수
def build_model(hidden_units, activation):
    model = keras.Sequential([
        layers.Input(shape=(4,)), # 온도, 진동, 압력, 회전수 4개 특성
        layers.Dense(hidden_units, activation=activation, name='hidden1'),
        layers.Dense(6, activation='relu', name='hidden2'),
        layers.Dense(3, activation='softmax', name='state')
    ])
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

model_a = build_model(hidden_units=8, activation='relu')
model_b = build_model(hidden_units=2, activation='tanh')

history_a = model_a.fit(X, y, epochs=300, verbose=0)
history_b = model_b.fit(X, y, epochs=300, verbose=0)

results = [
    ['구조', '최종 Loss', '최종 accuracy', '파라미터 수'],
    ['A', history_a.history['loss'][-1], history_a.history['accuracy'][-1], \
        model_a.count_params()],
    ['B', history_b.history['loss'][-1], history_b.history['accuracy'][-1], \
     model_b.count_params()]
]

# 제목라인 출력
pp(f'{results[0][0]:<6}{results[0][1]:>14}{results[0][2]:>18}{results[0][3]:>14}')

# 각 행 출력
for row in results[1:]:
    pp(f'{row[0]:<6}{row[1]:>14.6f}{row[2]:>18.4f}{row[3]:>14}')

new_machines = np.array([
    [0.38, 0.24, 0.51, 0.49],
    [0.60, 0.56, 0.42, 0.67],
    [0.88, 0.92, 0.23, 0.91]
], dtype=np.float32)

for model_name, model in [('A', model_a), ('B', model_b)]:
    probabilites = model.predict(new_machines, verbose=0)
    predicted_classes = np.argmax(probabilites, axis=1)
    pp(f'구조 {model_name} 예측')
    for index, (prob, predicted_class) in \
        enumerate(zip(probabilites, predicted_classes), start=1):
        pp(f'설비 {index}: 확률={np.round(prob, 4)}, \
           합={prob.sum():.6f}, 예측={class_names[predicted_class]}')

# 구조 B는 첫 은닉층 뉴런 수가 12개로 구조 A의 8개보다 많음
# 그러므로 입력층>은닉층과 은닉층>다음층 연결 파라미터가 증가함

# 파라미터 수가 많으면 표현력은 커질 수 있지만 특성, 초기값, 학습 조건에 따라
# 성능이 달라지므로 구조가 크다고 항상 더 좋은 모델이라고 단정할 수는 없음

up(5)
























