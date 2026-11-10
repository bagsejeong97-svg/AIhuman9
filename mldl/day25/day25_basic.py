# day25_basic.py
# 주제:
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from util.print_util import pp  # 과제 요구사항: pp 사용
from tensorflow import keras

RANDOM_SEED = 42
keras.utils.set_random_seed(RANDOM_SEED)

def make_parking_images(sample_count=600, image_size=20):
    X = np.random.normal(0.08, 0.05, (sample_count, image_size, image_size, 1)).astype("float32")
    y = np.random.randint(0, 2, sample_count).astype("float32")
    for i, label in enumerate(y):
        X[i, 2:-2, 2, 0] += 0.25  # 주차선 왼쪽
        X[i, 2:-2, -3, 0] += 0.25  # 주차선 오른쪽
        X[i, 2, 2:-2, 0] += 0.25  # 주차선 위쪽
        X[i, -3, 2:-2, 0] += 0.25  # 주차선 아래쪽
        if label == 1:
            row_shift = np.random.randint(-1, 2)  # 차량 위치를 조금 변화시킴
            col_shift = np.random.randint(-1, 2)
            r1, r2 = 6 + row_shift, 15 + row_shift
            c1, c2 = 7 + col_shift, 14 + col_shift
            X[i, r1:r2, c1:c2, 0] += 0.75  # 중앙 차량 패턴
    X = np.clip(X, 0.0, 1.0)
    order = np.random.permutation(sample_count)
    return X[order], y[order]

X, y = make_parking_images()

X_train, X_test, y_train, y_test = train_test_split(X,y,
    test_size=0.2,
    random_state=RANDOM_SEED,
    stratify=y,
)


model = keras.Sequential([
keras.Input(shape=(20, 20, 1)),
keras.layers.Conv2D(16, 3, padding="same", activation="relu"),
keras.layers.MaxPooling2D(2),
keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
keras.layers.MaxPooling2D(2),
keras.layers.Flatten(),
keras.layers.Dense(32, activation="relu"),
keras.layers.Dense(1, activation="sigmoid")
])

model.summary(
    print_fn=lambda line: pp(line)
)

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    X_train, y_train,
    epochs=8,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)

test_loss, test_acc = model.evaluate(X_test, y_test,verbose=0)

# 예측 모델
predict_proba = model.predict(X_test[:5], verbose=0).flatten()

# 실제 a / 예측 b
for i in range(5):
    a = int(y_test[i])
    b = int(predict_proba[i]>0.5)
    pp(a,b)
pp(test_acc)





