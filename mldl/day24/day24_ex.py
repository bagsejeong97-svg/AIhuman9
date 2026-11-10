# day24_ex.py
# 주제:
# day24_ex.py
# 딥러닝 학습 제어 : Epoch, Batch Size, Optimizer, Dropout, EarlyStopping

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

RANDOM_STATE = 42

np.random.seed(RANDOM_STATE) # NumPy 난수 재현

tf.random.set_seed(RANDOM_STATE) # TensorFlow 난수 재현

# 비선형 이진 분류 데이터
X, y = make_moons(
    n_samples=1200, # 전체 샘플 수
    noise=0.25, # 두 반달 모양에 추가할 잡음 크기
    random_state=RANDOM_STATE
)
pp(X.shape) # (1200, 2)
pp(y.shape) # (1200)

# train / test split
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y
)

# train / validation split
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y_train_full
)

# StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train) # 학습에만 fit, transform
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# 주요 Optimizer
sgd = keras.optimizers.SGD(
    learning_rate=0.01 # 한 번의 가중치 갱신 크기
)
sgd_momentum = keras.optimizers.SGD(
    learning_rate=0.01,
    momentum=0.9 # 이전 갱신 방향을 일부 반영해 진동을 줄이는 비율
)
rmsprop = keras.optimizers.RMSprop(
    learning_rate=0.001 # 최근 Gradient 크기를 반영해 파라미터별 학습률 조절
)
adam = keras.optimizers.Adam(
    learning_rate=0.001 # Momentum과 적응적 학습률 개념을 결합
)
# 설정정보 출력
pp('SGD: ', sgd.get_config())
pp('SGD Momentum: ', sgd_momentum.get_config())
pp('RMSProp: ', rmsprop.get_config())
pp('Adam: ', adam.get_config())

# Dropout(rate, seed, name) : 학습 중 지정 비율의 출력을 임시로 0으로 만들어 과적합 완화
model = keras.models.Sequential([
    keras.layers.Input(shape=(2,)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(
        rate=0.3, # 학습 중 약 30%의 출력을 제거
        seed=RANDOM_STATE,
        name='dropout_hidden'
    ),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

# compile : 모델의 Optimizer, Lose, Metric 설정
model.compile(
    optimizer=adam,
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# 모델의 요약정보 출력
model.summary(print_fn=lambda line: pp(line))

# EarlyStopping : 검증 지표가 일정 기간 개선되지 않으면 학습을 중단
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss', # 감시할 검증 지표
    patience=8, # 개선 없이 허용할 Epoch 수
    min_delta=0.001, # 이 값 이상 검증손실값이 좋아져야 개선으로 인정
    mode='min', # val_loss는 값이 작을수록 좋으므로 min 방향으로 설정
    restore_best_weights=True, # 최적의 가중치로 복원
    verbose=1 # 조기 종료 정보를 출력
)

# ModelCheckpoint : 가장 좋았던 모델을 파일로 저장
checkpoint = keras.callbacks.ModelCheckpoint(
    filepath='./model/day24_best.keras',
    monitor='val_loss',
    save_best_only=True # val_loss가 개선될때만 저장
)

# ReduceLROnPlateau : Learning Rate 감소
redulc_lr = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5, # 정체 시 Learning Rate을 절반으로 감소
    patience=4, # 4 Epoch 동안 개선이 없다면 감소
    min_lr = 1e-6 # Learning Rate이 이 값보다 작아지지 않도록 제한
)

# 학습
history = model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=32,
    validation_data = (X_val, y_val),
    callbacks=[early_stopping, checkpoint, redulc_lr], # 학습과정에 개입할 Callback
    verbose=0
)
pp('History keys: ', history.history.keys())
train_loss = history.history['loss'] # 학습 손실
val_loss = history.history['val_loss'] # 검증 손실
train_acc = history.history['accuracy'] # 학습 정확도
val_acc = history.history['val_accuracy'] # 검증 정확도
pp('실제 수행 Epoch: ', len(train_loss))
pp('마지막 train_loss: ', train_loss[-1])
pp('마지막 val_loss: ', val_loss[-1])

# evaluate : 별도 평가 데이터에서 Loss와 Metric을 계산
test_result = model.evaluate(X_test, y_test, verbose=0)
pp(test_result)

# predict : 새 데이터의 클래스 1 확률을 반환
prob = model.predict(X_test[:5], verbose=0)
pp('예측 확률: ')
pp(prob)

# 0.5를 임계값으로 확률을 최종 클래스 반환
pred = (prob[:, 0] >= 0.5).astype(int)
pp('예측 클래스: ')
pp(pred)

# 학습곡선 시각화

# 학습손실 / 검증손실
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='validation loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# 학습정확도 / 검증정확도
plt.plot(history.history['accuracy'], label='train accuracy')
plt.plot(history.history['val_accuracy'], label='validation accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()























































