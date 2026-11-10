# day24_basic.py
# 주제:

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from tensorflow import keras
from tensorflow.keras import layers
X, y = make_classification(
    n_samples=1500,
    n_features=10,
    random_state=42
)

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.2,
    random_state=42,
    stratify=y_train_full
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)


def build_model():
    model = keras.Sequential([
        layers.Input(shape=(10,)),
        layers.Dense(8, activation='relu'),
        layers.Dense(4, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])

    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss = 'binary_crossentropy', # 2진분류
        metrics=['accuracy'] # 평가지표 : 정확도
    )
    return model

a = build_model()
history1 = a.fit(
    X_train,
    y_train,
epochs=30, batch_size=16,
    validation_data=(X_val, y_val),
    verbose=0
)

b = build_model()
history2 = b.fit(
    X_train,
    y_train,
epochs=60, batch_size=64,
    validation_data=(X_val, y_val),
    verbose=0
)

acc_a = history1.history['val_accuracy'][-1]


acc_b = history2.history['val_accuracy'][-1]


pp(acc_a,len(history1.history['loss']))
pp(acc_b,len(history2.history['loss']))

if acc_a >= acc_b:
    model = a
    name = '설정a'
else:
    model = b
    name = '설정b'

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
pp(f'더 낳은 설정은[{name}]이고 로스는{test_loss:.4f},정확도는{test_acc:.4f}')





# day24_basic.py

# import os
# # 운영체제의 환경변수(Environment Variable) 를 설정
# # TF_CPP_MIN_LOG_LEVEL : TensorFlow 내부의 C++ 엔진이 출력할 로그의 최소 레벨을 지정
# # 0 : INFO, WARNING, ERROR 모두 출력
# # 1 : INFO 숨김 / WARNING, ERROR 출력
# # 2 : INFO, WARNING 숨김 / ERROR 출력
# # 3 : INFO, WARNING, ERROR 모두 숨김
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
#
# import time
# import numpy as np
# import tensorflow as tf
# from tensorflow import keras
# from sklearn.datasets import make_classification
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from util.print_util import pp, up
#
# np.random.seed(42)
#
# tf.random.set_seed(42)
#
# X, y = make_classification(
#     n_samples=1500,
#     n_features=10,
#     n_informative=7,
#     n_redundant=2,
#     class_sep=1.0,
#     random_state=42
# )
#
# X_train_full, X_test, y_train_full, y_test = train_test_split(
#     X,
#     y,
#     test_size=0.2,
#     stratify=y,
#     random_state=42
# )
#
# X_train, X_val, y_train, y_val = train_test_split(
#     X_train_full,
#     y_train_full,
#     test_size=0.2,
#     stratify=y_train_full,
#     random_state=42
# )
#
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_val = scaler.transform(X_val)
# X_test = scaler.transform(X_test)
#
# def build_model():
#     model = keras.Sequential([
#         keras.layers.Input(shape=(10,)),
#         keras.layers.Dense(48, activation='relu'),
#         keras.layers.Dense(24, activation='relu'),
#         keras.layers.Dense(1, activation='sigmoid'),
#     ])
#     model.compile(
#         optimizer=keras.optimizers.Adam(learning_rate=0.001),
#         loss='binary_crossentropy',
#         metrics=['accuracy']
#     )
#     return model
#
# def run_experiment(epochs, batch_size):
#     tf.keras.backend.clear_session() # 세션 초기화
#     tf.random.set_seed(42)
#     model = build_model()
#     started = time.perf_counter() # 시작시간
#     history = model.fit(
#         X_train,
#         y_train,
#         epochs=epochs,
#         batch_size=batch_size,
#         validation_data=(X_val, y_val),
#         verbose=0
#     )
#     elapsed = time.perf_counter() - started # 소요시간
#
#     val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
#
#     return model, history, elapsed, val_loss, val_acc
#
# model_a, history_a, time_a, loss_a, acc_a = run_experiment(30, 16)
# model_b, history_b, time_b, loss_b, acc_b = run_experiment(60, 64)
#
# pp('설정 A', {
#     'epochs': len(history_a.history['loss']),
#     'batch_size': 16,
#     'seconds': round(time_a, 3),
#     'val_accuracy': round(acc_a, 4)
# })
# pp('설정 B', {
#     'epochs': len(history_b.history['loss']),
#     'batch_size': 64,
#     'seconds': round(time_b, 3),
#     'val_accuracy': round(acc_b, 4)
# })
#
# best_model = model_a if acc_a >= acc_b else model_b
# best_name = 'A' if acc_a >= acc_b else 'B'
#
# test_loss, test_acc = best_model.evaluate(X_test, y_test, verbose=0)
#
# pp('선택 결과: ', {
#     'setting': best_name,
#     'test_accuracy': round(test_acc, 4)
# })
#
# up(5)























































