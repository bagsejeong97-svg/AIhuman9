# day25_challenge.py
# 주제:
# day25_challenge.py
# 긴 시퀀스의 첫 신호 기억하기

import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras

from include.graph_config import set_graph
from util.print_util import pp
set_graph()


np.random.seed(2400)
keras.utils.set_random_seed(2400)

def make_memory_data(sample_count=2000, timesteps=40):
    y = np.random.randint(0, 2, sample_count).astype("float32")
    X = np.random.normal(0.0, 0.35, (sample_count, timesteps, 1)).astype("float32")
    signal_strength = np.random.uniform(1.0, 1.5, sample_count).astype("float32")
    X[:, 0, 0] = np.where(y == 1, signal_strength, -signal_strength)  # 첫 시점에 정답 신호 배치
    order = np.random.permutation(sample_count)
    return X[order], y[order]

def make_model(layer_type, units=24, timesteps=40):
    if layer_type == "rnn":
        recurrent = keras.layers.SimpleRNN(units)  # 비교를 위해 units를 LSTM과 동일하게 설정
        name = "memory_simple_rnn"
    else:
        recurrent = keras.layers.LSTM(units)  # gate와 cell state를 가진 구조
        name = "memory_lstm"
    return keras.Sequential([
        keras.Input(shape=(timesteps, 1)),
        recurrent,
        keras.layers.Dense(1, activation="sigmoid")
    ], name=name)

X, y = make_memory_data()

split = int(len(X) * 0.8)

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

pp("데이터 shape", X.shape, y.shape)
pp("학습/평가 shape", X_train.shape, X_test.shape)

rnn = make_model("rnn", units=24, timesteps=X.shape[1])
lstm = make_model("lstm", units=24, timesteps=X.shape[1])

for model in (rnn, lstm):
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

common_fit = {
    "epochs": 12,
    "batch_size": 32,
    "validation_split": 0.2,
    "verbose": 0
}

rnn_history = rnn.fit(X_train, y_train, **common_fit)
lstm_history = lstm.fit(X_train, y_train, **common_fit)

rnn_loss, rnn_acc = rnn.evaluate(X_test, y_test, verbose=0)
lstm_loss, lstm_acc = lstm.evaluate(X_test, y_test, verbose=0)

pp("SimpleRNN 파라미터 수", rnn.count_params())
pp("LSTM 파라미터 수", lstm.count_params())
pp("SimpleRNN 평가 accuracy", round(float(rnn_acc), 4))
pp("LSTM 평가 accuracy", round(float(lstm_acc), 4))

if lstm_acc > rnn_acc:
    pp("측정 결과", "현재 실행에서는 LSTM의 평가 정확도가 더 높습니다.")
elif lstm_acc < rnn_acc:
    pp("측정 결과", "현재 실행에서는 SimpleRNN의 평가 정확도가 더 높습니다.")
else:
    pp("측정 결과", "현재 실행에서는 두 모델의 평가 정확도가 같습니다.")

plt.plot(rnn_history.history["val_accuracy"], label="SimpleRNN val_accuracy")
plt.plot(lstm_history.history["val_accuracy"], label="LSTM val_accuracy")
plt.xlabel("Epoch")
plt.ylabel("Validation Accuracy")
plt.title("장기 기억 문제: SimpleRNN과 LSTM 비교")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

pp(
    "해석 포인트",
    "LSTM은 입력·망각·출력 gate와 cell state를 사용하므로 같은 units에서도 SimpleRNN보다 파라미터 수가 많습니다.",
    "시퀀스 길이를 10, 20, 40으로 바꿔 동일 조건에서 평가하면 장기 의존성 길이에 따른 차이를 관찰할 수 있습니다."
)
