# day24_kerastuner.py
# KerasTuner를 이용한 하이퍼파라미터 튜닝 : 최적의 하이퍼파라미터 조합 찾기

# Alt + F12 : pip install keras_tuner

import keras
from keras import layers, Sequential
import keras_tuner as kt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up

# 유방암 이진분류 데이터셋
data = load_breast_cancer()

# X / y split
X = data.data # 입력 특성 데이터
y = data.target # 정답 데이터, 0 또는 1의 이진분류
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size = 0.2,
    random_state = 42,
    stratify = y
)

# 스케일링
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# KerasTuner가 사용할 모델 생성 함수
def build_model(hp):

    model = Sequential() # 시퀀셜 모델

    # 첫번째 은닉층, units를 16, 32, 48, 64 중에서 선택
    units1 = hp.Int(
        'units1', # 유닛명
        min_value = 16, # 최소값
        max_value = 64, # 최대값
        step = 16 # 스텝
    )
    # 시퀀셜 모델에 첫번째 은닉층 추가
    model.add(layers.Dense(units1, activation='relu'))

    # 두번째 은닉층, units를 8, 16, 24, 32 중에서 선택
    units2 = hp.Int(
        'units2', # 유닛명
        min_value = 8, # 최소값
        max_value = 32, # 최대값
        step = 8 # 스텝
    )
    # 시퀀셜 모델에 두번째 은닉층 추가
    model.add(layers.Dense(units2, activation='relu'))

    # 시퀀셜 모델에 출력층 추가
    model.add(layers.Dense(1, activation='sigmoid'))

    # 학습률 후보
    learning_rate = hp.Choice(
        'learning_rate',
        values = [0.01, 0.001, 0.0001]
    )

    # optimizer
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    # 모델 학습 설정
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model

# 여러 하이퍼파라미터 조합을 탐색
tuner = kt.RandomSearch(
    build_model,
    objective='val_accuracy', # 최적 모델 기준 지표
    max_trials=10, # 최대 10개의 조합을 실험
    directory='tuner_result', # 결과 저장 폴더
    project_name='dense_test' # 프로젝트 이름
)

# 하이퍼파라미터 탐색
tuner.search(
    X_train,
    y_train,
    epochs=30, # 각 모델을 최대 30 Epoch
    validation_split=0.2, # 학습 데이터의 20%를 검증 데이터로 사용
    verbose=1
)

# 가장 좋은 하이퍼파라미터 확인
best_hp = tuner.get_best_hyperparameters(
    num_trials=1 # 가장 좋은 조합 1개 가져옴
)[0]

pp('[최적 하이퍼파라미터]')
pp('첫번째 은닉층 뉴런: ', best_hp.get('units1'))
pp('두번째 은닉층 뉴런: ', best_hp.get('units2'))
pp('Learning Rate: ', best_hp.get('learning_rate'))

# 가장 좋은 모델 가져오기
best_model = tuner.get_best_models(num_models=1)[0]

# 테스트 데이터로 최종 평가
loss, accuracy = best_model.evaluate(
    X_test,
    y_test,
    verbose=0
)
pp('[테스트 결과]')
pp(f'Loss: {loss:.4f}')
pp(f'Accuracy: {accuracy:.4f}')

up(5)



































