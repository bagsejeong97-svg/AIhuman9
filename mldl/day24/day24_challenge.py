
# day24_challenge.py
# 주제:
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

np.random.seed(42)

tf.random.set_seed(42)

X, y = make_regression(
    n_samples=2400,
    n_features=12,
    n_informative=9,
    noise=18.0, # noise는 현실적인 예측 오차를 모사하기 위해 추가
    random_state=42
)

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# 모델 생성 함수
def build_model(learning_rate):
    model = keras.Sequential([
        keras.layers.Input(shape=(12,)),
        keras.layers.Dense(96, activation="relu"),
        keras.layers.Dense(48, activation="relu"),
        keras.layers.Dense(24, activation="relu"),
        keras.layers.Dense(1)
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='mse',
        metrics=['mae']
    )
    return model

learning_rates = [0.0005,0.001,0.005]

results = []
histories={}
models={}

for learning_rate in learning_rates:
    tf.keras.backend.clear_session() # 세션 초기화
    tf.random.set_seed(42)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss', #검증 손실
        patience=15, # 15회 epoch
        min_delta=0.01, # val_loss가 최소 0.01 이상 개선되어야 개선으로 인정
        restore_best_weights=True # 최적 가중치로 복원
    )

    model = build_model(learning_rate)

    history = model.fit(
        X_train, y_train,
        batch_size=32,
        epochs=50,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping],
        verbose=0
    )

    # 검증 손실, 검증 MAE
    val_loss,val_mae = model.evaluate(X_val, y_val,verbose=0)

    # 최적의 epoch 수
    best_epoch = int(np.argmin(history.history['val_loss'])) + 1

    # 최적의 검증 손실
    best_val_loss = float(np.min(history.history['val_loss']))

    results.append({
        'learning_rate': learning_rate,
        'executed_epoch': len(history.history['loss']),
        'best_epoch': best_epoch,
        'best_val_loss': best_val_loss,
        'val_mae': float(val_mae)
    })

    # learning rate 마다의 history와 model을 각 딕셔너리에 저장
    histories[learning_rate] = history
    models[learning_rate] = model

# 결과 출력
for result in results:
    pp('Learning Rate 비교: ',{
        'learning_rate': result['learning_rate'],
        'executed_epoch': result['executed_epoch'],
        'best_epoch': result['best_epoch'],
        'best_val_loss': result['best_val_loss'],
        'val_mae': result['val_mae']
    })

for learning_rate,history in histories.items():
    plt.plot(history.history['val_loss'], label=f'lr={learning_rate}')

plt.xlabel('Epoch')
plt.ylabel('Validation Mse')
plt.title('Delivery Time : Learing Rate Comparison')
plt.legend()
plt.tight_layout()
plt.grid(alpha=0.3)
plt.show()

best_result = min(results, key=lambda item:item['val_mae'])
best_lr = best_result['learning_rate']
best_model = models[best_lr]

test_loss,test_mae = best_model.evaluate(X_test, y_test, verbose=0)

pp('최적 설정',{
    'learning_rate': best_lr,
    'best_epoch': best_result['best_epoch'],
    'best_mae': round(float(test_mae),3)
})

# 매우 큰 Learning Rate는 손실이 불안정하게 움직일 수 있고
# 너무작은 값은 안정적이어도 수렴에 더 많은  Epoch이 필요할 수 있음















































