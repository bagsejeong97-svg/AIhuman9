# day25_rnn.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, GRU, Bidirectional
from tensorflow.keras.optimizers import SGD
from tensorflow.random import set_seed
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

# 시드
set_seed(455)
np.random.seed(455)

# 데이터셋
dataset = pd.read_csv(
    "assets/Mastercard_stock_history.csv", index_col="Date", parse_dates=["Date"]
).drop(["Dividends", "Stock Splits"], axis=1)
pp(dataset.head())
pp(dataset.describe())

# 널값 확인
dataset.isna().sum()

# 테스트 시작/종료년도
tstart = 2016
tend = 2020

# 마스터카드 주가 그래프
def train_test_plot(dataset, tstart, tend):
    dataset.loc[f"{tstart}":f"{tend}", "High"].plot(figsize=(16, 4), legend=True)
    dataset.loc[f"{tend+1}":, "High"].plot(figsize=(16, 4), legend=True)
    plt.legend([f"Train (Before {tend+1})", f"Test ({tend+1} and beyond)"])
    plt.title("MasterCard stock price")
    plt.show()
train_test_plot(dataset,tstart,tend)

# 데이터 처리
def train_test_split(dataset, tstart, tend):
    train = dataset.loc[f"{tstart}":f"{tend}", "High"].values
    test = dataset.loc[f"{tend+1}":, "High"].values
    return train, test

# train/test 분리
training_set, test_set = train_test_split(dataset, tstart, tend)

# 스케일링
sc = MinMaxScaler(feature_range=(0, 1))
training_set = training_set.reshape(-1, 1)
training_set_scaled = sc.fit_transform(training_set)

# 시퀀스 분리 함수
def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        end_ix = i + n_steps
        if end_ix > len(sequence) - 1:
            break
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


# 리쉐이프
n_steps = 60
features = 1
X_train, y_train = split_sequence(training_set_scaled, n_steps)
X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],features)

# LSTM 모델
model_lstm = Sequential()
model_lstm.add(LSTM(units=125, activation="tanh", input_shape=(n_steps, features)))
model_lstm.add(Dense(units=1))
model_lstm.compile(optimizer="RMSprop", loss="mse")

# 모델 확인
model_lstm.summary()

# 모델 훈련
model_lstm.fit(X_train, y_train, epochs=50, batch_size=32)

# 리쉐이프
dataset_total = dataset.loc[:,"High"]
inputs = dataset_total[len(dataset_total) - len(test_set) - n_steps :].values
inputs = inputs.reshape(-1, 1)

# 스케일링
inputs = sc.transform(inputs)

# test 분리
X_test, y_test = split_sequence(inputs, n_steps)

# 리쉐이프
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], features)

# 예측
predicted_stock_price = model_lstm.predict(X_test)

# 역변환
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

# 에측 그래프 함수
def plot_predictions(test, predicted):
    plt.plot(test, color="gray", label="Real")
    plt.plot(predicted, color="red", label="Predicted")
    plt.title("MasterCard Stock Price Prediction")
    plt.xlabel("Time")
    plt.ylabel("MasterCard Stock Price")
    plt.legend()
    plt.show()

# rmse 리턴 함수
def return_rmse(test, predicted):
    rmse = np.sqrt(mean_squared_error(test, predicted))
    print("The root mean squared error is {:.2f}.".format(rmse))

plot_predictions(test_set,predicted_stock_price)

return_rmse(test_set,predicted_stock_price)

up(5)




