# day24_application.py
# 주제:

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
from include.graph_config import set_graph

set_graph(10, 8, 13)

X,y = make_classification(
    n_samples=2000,
    n_features=16,
    random_state=42,
)

X_train_full,X_test,y_train_full,y_test = train_test_split(
    X,y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

X_train,X_val,y_train,y_val = train_test_split(
    X_train_full,y_train_full,
    test_size=0.2,
    stratify=y_train_full,
    random_state=42
)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)


A = keras.Sequential([
        layers.Input(shape=(16,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])

a = keras.optimizers.Adam(learning_rate=0.001)
A.compile(optimizer=a,loss = 'binary_crossentropy',
        metrics=['accuracy'])

history_A = A.fit(X_train,y_train,
epochs=180, batch_size=32,validation_data=(X_val,y_val),verbose=0)



B = keras.Sequential([
        layers.Input(shape=(16,)),
        layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.4,seed=42),
        layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.2,seed=42),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')])

b = keras.optimizers.Adam(learning_rate=0.001)
B.compile(optimizer=b,loss = 'binary_crossentropy',
        metrics=['accuracy'])

history_B = B.fit(X_train,y_train,
     epochs=180, batch_size=32,
     validation_data=(X_val, y_val),
     verbose=0 )


train_acc_A = history_A.history['accuracy'][-1]
val_acc_A = history_A.history['val_accuracy'][-1]

train_acc_B = history_B.history['accuracy'][-1]
val_acc_B = history_B.history['val_accuracy'][-1]

gap_A =  abs(train_acc_A - val_acc_A)
gap_B =  abs(train_acc_B - val_acc_B)


plt.figure(figsize=(10,5))
plt.plot(history_A.history['val_loss'],label='model A')
plt.plot(history_B.history['val_loss'],label='model B')
plt.title('모델별 val_loss')
plt.ylabel('val_loss')
plt.xlabel('epoch')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

if val_acc_A <= val_acc_B or gap_B <= gap_A:
    name = 'model_B'
    model = B

else:
    name = 'model_A'
    model = A

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)

pp(f'더 나은 모델 이름:{name}\n loss:{test_loss}\n accuracy:{test_acc}')



# day24_application.py
#
# import os
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
# import numpy as np
# import matplotlib.pyplot as plt
# import tensorflow as tf
# from tensorflow import keras
# from sklearn.datasets import make_classification
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from util.print_util import pp, up
# from include.graph_config import set_graph
#
# set_graph(10, 8, 13)
#
# np.random.seed(42)
#
# tf.random.set_seed(42)
#
# X, y = make_classification(
#     n_samples=2000,
#     n_features=16,
#     n_informative=10,
#     n_redundant=4,
#     flip_y=0.04, # flip_y는 일부 라벨에 잡음을 추가
#     class_sep=0.9,
#     random_state=42
# )
#
# X_train_full, X_test, y_train_full, y_test = train_test_split(
#     X, y, test_size=0.2, stratify=y, random_state=42
# )
#
# X_train, X_val, y_train, y_val = train_test_split(
#     X_train_full,
#     y_train_full,
#     test_size=0.25,
#     stratify=y_train_full,
#     random_state=42
# )
#
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_val = scaler.transform(X_val)
# X_test = scaler.transform(X_test)
#
# def build_model(use_dropout):
#
#     layers = [
#         keras.layers.Input(shape=(16,)),
#         keras.layers.Dense(128, activation='relu'),
#     ]
#
#     if use_dropout:
#         layers.append(keras.layers.Dropout(0.4, seed=42))
#
#     layers.append(keras.layers.Dense(64, activation='relu'))
#
#     if use_dropout:
#         layers.append(keras.layers.Dropout(0.2, seed=42))
#
#     layers.extend([
#         keras.layers.Dense(32, activation='relu'),
#         keras.layers.Dense(1, activation='sigmoid')
#     ])
#
#     model = keras.Sequential(layers)
#
#     model.compile(
#         optimizer=keras.optimizers.Adam(0.001),
#         loss='binary_crossentropy',
#         metrics=['accuracy']
#     )
#
#     return model
#
# def train_model(use_dropout):
#
#     tf.keras.backend.clear_session()
#
#     tf.random.set_seed(42)
#
#     model = build_model(use_dropout)
#
#     history = model.fit(
#         X_train,
#         y_train,
#         epochs=180,
#         batch_size=32,
#         validation_data=(X_val, y_val),
#         verbose=0
#     )
#
#     train_acc = history.history['accuracy'][-1]
#     val_acc = history.history['val_accuracy'][-1]
#
#     gap = train_acc - val_acc
#
#     return model, history, train_acc, val_acc, gap
#
# model_a, history_a, train_a, val_a, gap_a = train_model(False)
# model_b, history_b, train_b, val_b, gap_b = train_model(True)
#
# pp('Dropout 없음', {
#     'train_accuracy': round(train_a, 4),
#     'val_accuracy': round(val_a, 4),
#     'gap': round(gap_a, 4)
# })
# pp('Dropout 있음', {
#     'train_accuracy': round(train_b, 4),
#     'val_accuracy': round(val_b, 4),
#     'gap': round(gap_b, 4)
# })
#
# plt.plot(history_a.history['val_loss'], label='No Dropout')
# plt.plot(history_b.history['val_loss'], label='Dropout')
# plt.xlabel('Epochs')
# plt.ylabel('Validation Loss')
# plt.title('Loan Risk: Dropout Validation Lose')
# plt.legend()
# plt.tight_layout()
# plt.show()
#
# # Validation Accuracy가 비슷하다면 Train - Validation Gap이 작은 모델을
# # 일반화 관점에서 우선시 함
# score_a = val_a - max(gap_a, 0) * 0.2
# score_b = val_b - max(gap_b, 0) * 0.2
#
# best_model = model_a if score_a >= score_b else model_b
# best_name = 'Dropout 없음' if score_a >= score_b else 'Dropout 적용'
#
# test_loss, test_acc = best_model.evaluate(X_test, y_test, verbose=0)
#
# pp('선택 결과', {
#     'model': best_name,
#     'test_accuracy': round(test_acc, 4)
# })
#
# up(5)




























