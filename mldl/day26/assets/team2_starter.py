# team2_starter.py
# 배송 소요시간 예측 - Dense 회귀 미니프로젝트

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from util.print_util import pp
from include.graph_config import set_graph
import time
# 난수 시드를 고정합니다.
keras.utils.set_random_seed(42)

# CSV 파일 경로를 지정합니다.
DATA_FILE = Path(__file__).resolve().parent / "team2_data.csv"

# CSV 데이터를 읽습니다.
df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

set_graph(10, 8, 13)

# TODO 1. 데이터 shape, 자료형, 결측치를 확인하세요.
pp('데이터 shape: \n',df.shape) #형태
pp('자료형: \n',df.dtypes) # type
pp('결측치 수: \n', df.isna().sum()) # 결측치 수

# TODO 2. 숫자형 결측치를 중앙값으로 처리하세요.
cols = ['배송거리_km', '주문상품수', '출고대기시간_분', '교통혼잡도', '비여부', '기사경력_년', '야간여부']
df[cols] = df[cols].fillna(df[cols].median())
 # 결측치 중앙값 대체
pp(df.isnull().sum()) # 결측치 여부 확인

# TODO 3. X와 y를 분리하세요.
Target = df['배송소요시간_분']
X = df.drop(columns=['배송소요시간_분'])
y = Target

# TODO 4. Train/Test를 75:25로 나누세요.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# TODO 5. StandardScaler를 Training Set 기준으로 적용하세요.
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train) # 학습용 데이터
X_test = scaler.transform(X_test)   # 평가용 데이터 스케일 변환

# TODO 6. Dense 회귀 모델을 생성하는 함수를 작성하세요.
# TODO 7. optimizer="adam", loss="mse"로 compile하세요.
# TODO 10. 두 실험에 같은 EarlyStopping 조건을 사용하세요.
# 예: Input → Dense(32, relu) → Dense(16, relu) → Dense(1)
def make_model():                       # 모델 생성 함수
    model = keras.Sequential([
        keras.layers.Input(shape=(X_train.shape[1],)),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(1)
    ])
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )

    return model

early_stopping = keras.callbacks.EarlyStopping(             # early stop용 값
    monitor="val_loss",
    patience=8,                               # epoch 사용수를 맞추기 위한 값 지정
    restore_best_weights=True,
    min_delta=3.0,
    mode="min",
)
# TODO 8. batch_size=16 실험을 수행하세요.
start_time_16 = time.time()
model_16= make_model()
history_16 = model_16.fit(
    X_train, y_train,
    epochs=300,
    batch_size=16,
    validation_split=0.2,
    callbacks=[early_stopping],
    verbose=1
)
time_16 = time.time() - start_time_16  # 모델 fit 소요시간 측정
epoch_16 = len(history_16.history['loss']) # 모델이 사용한 epoch수

# TODO 9. 동일 구조를 다시 만들고 batch_size=64 실험을 수행하세요.
start_time_64 = time.time()
model_64= make_model()
history_64 = model_64.fit(
X_train, y_train,
    epochs=300,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping],
    verbose=1
)
time_64 = time.time() - start_time_64 # 모델 fit 소요시간 측정
epoch_64 = len(history_64.history['loss']) # 모델이 사용한 epoch 수

# TODO 11. History의 validation loss를 비교하세요.
val_loss_16 = history_16.history['val_loss']             # val_loss는 컴파일시 MSE로 지정
val_loss_64 = history_64.history['val_loss']

# 비교 시각화
plt.figure(figsize = (10,10))
plt.plot(val_loss_16, label='val_loss_16')
plt.plot(val_loss_64, label='val_loss_64')
plt.title('batch_size별 val_loss 비교')
plt.xlabel('epoch')
plt.ylabel('val_loss')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('val_loss.png', dpi=300, bbox_inches='tight')
plt.show()

# batch_size16,64 비교시  epoch 약 50,83에서 early stop이 진행되고 안정화 값 또한 16이 더 낮은것을 볼 수 있다. 이를 통해
# batch_size 16을 최종모델로 선택



# TODO 12. MAE와 RMSE를 계산하세요.
mse_16, mae_16 = model_16.evaluate(X_test, y_test, verbose=0)  # 컴파일에서 지정된 MSE,MAE 지정
rmse_16 = np.sqrt(mse_16)      # 루트 씌움
mse_64, mae_64 = model_64.evaluate(X_test, y_test, verbose=0)   # 컴파일에서 지정된 MSE,MAE 지정
rmse_64 = np.sqrt(mse_64)       # 루트 씌움

# 비교 데이터 정리
pp(f"Batch Size 16,64 모델 비교")              # df형식으로 보기 쉽게 정리
df_m = pd.DataFrame({
    'matrix': ['MSE','MAE','RMSE','소요시간','수행 epoch수'],
    '16': [mse_16,mae_16,rmse_16,time_16,epoch_16],
    '64': [mse_64,mae_64,rmse_64,time_64,epoch_64]
})
pp(df_m)

# TODO 13. 실제값과 예측값 산점도를 그리세요.
#실제값 : a  / 예측값 : b
a = y_test
b = model_16.predict(X_test,verbose=0).flatten()   # 예측 모델 사용한 값

plt.figure(figsize=(10, 10))
plt.scatter(a,b, alpha=0.3, color='blue', label='예측값')
plt.title('실제 배송소요시간 vs 예측 배송소요시간')
plt.xlabel('실제 배송소요시간 (분)')
plt.ylabel('예측 배송소요시간 (분)')
plt.grid(alpha=0.3)
min_val = min(a.min(), b.min())
max_val = max(a.max(), b.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='기준선 (y=x)')
plt.legend()
plt.tight_layout()
plt.savefig('predict.png', dpi=300, bbox_inches='tight')
plt.show()






























