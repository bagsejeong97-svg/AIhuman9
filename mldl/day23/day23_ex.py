# day23_ex.py
# 딥러닝, 신경망, 활성화함수, 손실함수, Tensorflow, Keras

import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

# 난수 재현성 확보
keras.utils.set_random_seed(42)

# 1. 머신러닝/딥러닝, 신경망 구조
'''
개념 :  머신러닝은 데이터에서 규칙을 학습하며, 딥러닝은 여러 층의 신경망을 이용함
       입력층은 특성을 입력 받고, 은닉층은 특성을 조합하고, 출력층은 예측 결과를 만듬
예시 : 공부시간/출석률 2개 입력 > 은닉 뉴런 8개 > 예상 시험점수 1개
'''
student = np.array([[0.8, 0.9]], dtype=np.float32) # 입력 1건, 특성 2개
pp(f'입력 shape={student.shape}, 층별 크기={[2, 8, 1]}') # 2:Input, 8:Hidden, 1:Output

# 2. 뉴런/가중치/편향 (Neuron/Weight/Bias)
'''
개념 : 뉴런은 입력값과 가중치를 곱해 합산(가중합)하고 편향을 더한 z에 활성화 함수 f를 적용함
      z = x1w1 + x2w2 + ... + xnwn + b
      a = f(z)
예시 : 0.8 * 07 + 0.6 * -0.2 = 0.44, 편향 0.1을 더하면 z=0.54
'''
x_neuron = np.array([0.8, 0.6], dtype=np.float32)
w_neuron = np.array([0.7, -0.2], dtype=np.float32)
b_neuron = 0.1
contribution = x_neuron * w_neuron
z_neuron = np.dot(x_neuron, w_neuron) + b_neuron # 가중합 + 편향
pp(f'입력별 기여도={contribution}, z={z_neuron}')

# 3. 활성화 함수가 필요한 이유
'''
개념 : 활성화 함수는 가중합 z를 다음 층에 전달할 값으로 변환하는 기능
      모든 층이 Linear라면 층을 여러개 쌓아도 하나의 변환으로 합쳐질 수 있음
      ReLU 같은 비선형 함수를 사용하면 복잡한 입력/출력 관계를 표현할 수 있음
예시 : 음수 입력 -1.5는 ReLU에서는 0, Linear에서는 -1.5
'''
pp(f'Linear(-1.5)={-1.5}, ReLU(-1.5)={max(0, -1.5)}')

# 4. ReLU(Rectified Linear Unit)
'''
개념 : f(x) = max(0, x) 음수나 0은 0, 양수는 그대로 출력, 은닉층에 주로 사용
예시 : [-2, -0.5, 0, 1, 3] > [0., 0., 0., 1., 3.]
'''
relu_x = np.array([-2.0, -0.5, 0.0, 1.0, 3.0])
pp(f'ReLU 결과 = {np.maximum(0, relu_x)}')

# 5. Sigmoid
'''
개념 : f(x) = 1 / (1+e^(-x)), 결과는 0과 1사이이므로 이진 분류 출력층에 사용
예시 : 입력 0의 출력은 0.5이며, 값이 클수록 결과는 1에 가까워짐
'''
sigmoid_x = np.array([-2.0, 0.0, 2.0])
sigmoid_y = 1 / (1 + np.exp(-sigmoid_x))
pp(f'Sigmoid 결과 = {np.round(sigmoid_y, 4)}')

# 6. Linear, Softmax
'''
개념 : Linear는 f(x)=x, 입력을 바꾸지 않아 회귀 출력에 사용
      Softmax는 여러 값을 각 클래스의 확률로 변환, 확률의 합은 1, 다중 분류 출력에 사용
예시 : 회귀 출력층 Dense(1)은 기본적으로 Linear이고
      3개 클래스면 Dense(3, activation='softmax')
'''
linear_layer = layers.Dense(1) # 기본 활성화 함수 : linear
pp(f'Dense(1)의 활성화 = {linear_layer.activation.__name__}') # 활성화 함수 이름

logits = np.array([1.0, 2.0, 3.0])
softmax_y = logits / logits.sum()
pp(f'Softmax={np.round(softmax_y, 4)}, 합={softmax_y.sum():.4f}')

# 7. 활성화 함수 비교와 출력층 선택
'''
개념 : ReLU는 은닉층(0 이상), Sigmoid는 이진 분류(0~1), Linear는 회귀(값 범위 제한 없음),
      Softmax는 다중 분류(클래스별 0~1, 합 1)에 주로 사용
예시 : 같은 Dense라도 activation과 출력 뉴런 수에 따라 해결할 문제 유형이 달라짐
'''
activation_example = {
    '은닉층': 'Dense(8, activation="relu")',
    '회귀': 'Dense(1, activation="linear")',
    '이진분류': 'Dense(1, activation="sigmoid")',
    '다중분류': 'Dense(3, activation="softmax")'
}
for purpose, code in activation_example.items():
    pp(f'{purpose}: {code}')

# 8. 손실 함수와 평균제곱오차 (Loss Fuction, MSE)
'''
개념 : 손실 함수는 정답과 예측값의 차이를 수치화하여 가중치/편향 갱신의 기준이 됨
      MSE = 평균((정답-예측)^2), 회귀에 많이 사용
예시 : 실제 [80, 90, 70], 예측 [78, 85, 74]의 제곱오차 평균을 구함
'''
y_true = np.array([80.0, 90.0, 70.0])
y_pred = np.array([78.0, 85.0, 74.0])
mse = np.mean((y_true - y_pred) ** 2)
pp(f'MSE = {mse:.4f}')

# 9. 이진 교차엔트로피 (Binary Crossentropy)
'''
개념 : 정답이 0 또는 1일때 예측 확률과 정답의 차이를 평가하는 대표적인 분류 손실
      정답 1에 대한 확률이 0에 가까워질수록 손실이 커짐
예시 : 정답이 1인 경우 예측 확률 0.9와 0.1의 손실을 비교
'''
for predicted_probability in [0.9, 0.1]:
    p = np.clip(predicted_probability, 1e-7, 1 - 1e-7) # log(0) 방지
    bce = -np.log(p) # 정답이 1일 때 Binary Crossentropy
    pp(f'정답=1, 확률={p:.1f}, BCE={bce:.4f}')

# 10. 문제 유형별 출력층과 손실 함수
'''
개념 : 회귀는 Linear + MSE, 이진 분류는 Sigmoid + Binary Crossentropy,
      다중 문류는 Softmax + Sparce Categorical Crossentropy
예시 : 출력층의 활성화 함수와 정답 형태에 맞는 손실 함수를 짝지어야 함
'''
task_settings = {
    '회귀': ('linear', 'mse'),
    '이진분류': ('sigmoid', 'binary_crossentropy'),
    '다중분류': ('softmax', 'sparse_categorical_crossentropy')
}
for task, (activation, loss) in task_settings.items():
    pp(f'{task}: 출력에 대한 활성화함수={activation}, 손실함수={loss}')

# 11. Tensorflow / Keras / Sequential
'''
개념 : Tensorflow는 머신러닝 프레임워크이며 Keras는 신경망 모델 구성/학습용 API
      Sequential은 입력층 > 은닉층 > 출력층을 순서대로 연결
예시 : Input(2) > Dense(8, ReLU) > Dense(1, Linear)로 점수 회귀 모델을 생성
'''
model = keras.Sequential([
    layers.Input(shape=(2,), name='input'),
    layers.Dense(8, activation='relu', name='hidden'),
    layers.Dense(1, name='output')
], name='score_model') # 모델명
pp(f'모델명={model.name}, 층 이름={[layer.name for layer in model.layers]}')

# 12. Input의 shape와 Dense의 주요 인자
'''
개념 : shape=(2,)는 한 건의 특성 수 2개를 의미, 데이터 건수는 넣지 않음
      Dense의 units는 뉴런 수, activation은 활성화 함수, name은 레이어 이름
예시 : 100건 * 2특성 입력의 shape=(100,2), 예측 출력은 (100,1)
'''
batch = np.zeros((100,2), dtype=np.float32) # 100행 2열, 0.0
hidden = model.get_layer(name='hidden')
pp(f'입력데이터={batch.shape}, 모델 입력={model.input_shape}, 출력={model.output_shape}')
pp(f'은닉층:units={hidden.units}') # 은닉층 뉴런 수
pp(f'은닉층:activation={hidden.activation.__name__}') # 은닉층 활성화함수명
pp(f'은닉층:name={hidden.name}') # 은닉층 명

# 13. Dense 파라미터 수 계산
'''
개념 : Dense 파라미터 수 = (이전 층 출력 수 * 현재 층 뉴런 수) + 현재 층 뉴런 수
예시 : 2 > 8: 16 + 8 = 24, 8 > 1: 8 + 1 = 9 그러므로 총 33개
'''
hidden_params = 2 * 8 + 8
output_params = 8 * 1 + 1
pp(f'수동계산={hidden_params+output_params}, Keras계산={model.count_params()}')

# 14. model.summary(), get_weights()
'''
개념 : summary()는 층별 출력 shape/파라미터수, get_weights()는 Weight/Bias 배열
      print_fn은 summary()의 각 줄을 전달받아 출력할 함수를 지정
예시 : 특성 2개, 은닉 뉴런 8개일때 Weight shape=(2, 8), Bias shape=(8,)
'''
model.summary(print_fn=lambda line:pp(line))
weights, biases = hidden.get_weights() # 가중치들, 편향들
pp(f'Weights shape={weights.shape}, Bias shape={biases.shape}')

# 15. Numpy로 Dense 계산 재현
'''
개념 : Dense는 행렬곱(입력 @ Weight)에 Bias를 더하고 활성화 함수를 적용합니다.
예시 : Numpy 계산과 실제 Keras 은닉층의 출력을 같은 입력값으로 비교
'''
hidden_z = student @ weights + biases # (1,2) @ (2,8) + (8,) > (1, 8)
hidden_a = np.maximum(0, hidden_z) # 은닉층에 ReLU 활성화 함수 적용
hidden_probe = keras.Model( # 은닉층의 출력만 확인하는 모델 생성
    inputs=model.inputs,
    outputs=hidden.output
)
keras_hidden_a = hidden_probe.predict(student, verbose=0) # verbose=0 : 진행 로그 미출력
pp(f'Numpy와 Keras 결과 일치: {np.allclose(hidden_a, keras_hidden_a)}')

# 16. 활성화 함수 그래프
'''
개념 : ReLU는 음수 구간에서 0, Sigmoid는 0~1, Linear는 입력 그대로
예시 : -5 ~ 5 범위의 세 함수의 곡선을 하나의 그래프로 비교
'''
# axis_x = np.linspace(-5, 5, 200) # -5 ~ 5 사이의 점 200개
# plt.plot(axis_x, np.maximum(0, axis_x), label='ReLU')
# plt.plot(axis_x, 1 / (1 + np.exp(-axis_x)), label='Sigmoid')
# plt.plot(axis_x, axis_x, label='Linear')
# plt.axhline(0, linewidth=0.8) # 수평선
# plt.axvline(0, linewidth=0.8) # 수직선
# plt.xlabel('Input')
# plt.ylabel('Output')
# plt.title('활성화 함수 그래프')
# plt.grid(alpha=0.25)
# plt.legend()
# plt.tight_layout()
# plt.show()

# 17. compile(), fit()
'''
개념 : compile()은 가중치 갱신 알고리즘(optimizer)와 손실 함수(loss)를 설정
      fit(x, y, epochs, vervose)는 입력/정답으로 학습, epochs는 전체 데이터 반복 횟수
예시 : 가상 점수 비율 데이터로 학습
'''
X = np.array([
    [0.20, 0.55], [0.30, 0.60], [0.35, 0.70], [0.45, 0.68],
    [0.50, 0.75], [0.55, 0.80], [0.60, 0.78], [0.65, 0.85],
    [0.70, 0.88], [0.75, 0.90], [0.82, 0.92], [0.90, 0.96]
], dtype=np.float32)
y = np.array([
    0.48, 0.53, 0.60, 0.62, 0.67, 0.72,
    0.73, 0.78, 0.82, 0.86, 0.91, 0.95
], dtype=np.float32)

model.compile(
    optimizer='adam', # 활성화 함수
    loss='mse' # 손실 함수
)
before_weights = hidden.get_weights()[0].copy() # 학습 전 Weight 별도 저장
history = model.fit(X, y, epochs=200, verbose=0) # X:입력, y:정답
after_weights = hidden.get_weights()[0] # 학습 후 Weight
pp(f'첫 Loss={history.history['loss'][0]:.6f}')
pp(f'마지막 Loss={history.history['loss'][-1]:.6f}')
pp(f'Weight 평균 변화량={np.abs(after_weights - before_weights).mean():.6f}')

# 18. predict()로 새 입력 예측
'''
개념 : predict()은 학습된 모델에 새 입력을 넣어 예측
예시 : 공부시간 비율 0.72, 출석률 0.90의 예상 점수 비율을 100점 척도로 환산
'''
new_student = np.array([[0.72, 0.90]], dtype=np.float32)
score_ratio = model.predict(new_student, verbose=0)
pp(f'예측 shape={score_ratio.shape}, 예상 점수={score_ratio[0, 0] * 100:.1f}점')

# 19. 이진 분류와 다중 분류 Keras 출력층
'''
개념 : 이진 분류는 Sigmoid 출력 뉴런 1개와 Binary Crossentropy를 사용
      다중 분류는 Softmax 출력 뉴런 3개와 Sparse Categorical Crossentropy를 사용
예시 : 데이터를 학습시키지 않고 두 모델의 출력 구조만 비교
'''

binary_model = keras.Sequential([
    layers.Input(shape=(3,)), # 특성 3개
    layers.Dense(6, activation='relu'),
    layers.Dense(1, activation='sigmoid') # 클래스 1의 예측 확률 출력
])
binary_model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

multi_model = keras.Sequential([
    layers.Input(shape=(4,)), # 특성 4개
    layers.Dense(8, activation='relu'),
    layers.Dense(3, activation='softmax') # 3개 클래스 확률 출력
])
multi_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

pp(f'이진분류 출력={binary_model.output_shape}') # (None, 1)
pp(f'다중분류 출력={multi_model.output_shape}') # (None, 3)

# 20. Softmax 확률의 합 확인
'''
개념 : Softmax는 클래스별 확률을 반환하므로 입력 한 건에서 출력 확률의 합은 1
예시 : 4개 특성의 가상 입력으로 3개 클래스 확률을 출력
'''
classs_probabilities = multi_model.predict(
    np.array([[0.2, 0.5, 0.7, 0.4]], dtype=np.float32),
    verbose=0
)
pp(f'클래스 확률={np.round(classs_probabilities, 4)}')
pp(f'합={classs_probabilities.sum():.6f}')












































