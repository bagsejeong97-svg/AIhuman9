# day16_challenge.py

import pandas as pd
from sklearn.utils import check_X_y
from sklearn.utils.multiclass import type_of_target
from util.print_util import pp, up

TARGET = 'failure_next_7d' # TARGET

CANDIDATE_FEATURES = [ # FEATURE 후보 리스트
    'temperature_c',
    'vibration_mm_s',
    'operating_hours',
    'alarm_count_24h',
    'repair_completed_after_failure'
]

LEAKAGE_FEATURES =['repair_completed_after_failure'] # leakage
FEATURES = [col for col in CANDIDATE_FEATURES if col not in LEAKAGE_FEATURES] # leakage 제외

df = pd.DataFrame({
    "temperature_c": [61, 73, 68, 84, 59, 88, 76, 64, 91, 70],
    "vibration_mm_s": [2.1, 3.8, 2.9, 5.7, 1.9, 6.2, 4.4, 2.3, 6.8, 3.1],
    "operating_hours": [1200, 2800, 1900, 5100, 900, 6200, 3500, 1500, 7100, 2400],
    "alarm_count_24h": [0, 2, 1, 5, 0, 6, 3, 1, 7, 2],
    "repair_completed_after_failure": [0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    "failure_next_7d": [0, 0, 0, 1, 0, 1, 1, 0, 1, 0]
})

# X, y 구성 함수
def build_xy(dataframe, feature_cols, target_col):

    if target_col in feature_cols:
        raise ValueError('Target 컬럼은 Feature에 포함할 수 없습니다!')

    required_cols = feature_cols + [target_col]
    missing_cols = [col for col in required_cols if col not in dataframe.columns]

    if missing_cols:
        raise ValueError(f'존재하지 않는 컬럼: {missing_cols}')

    X = dataframe[feature_cols]
    y = dataframe[target_col]

    if X.isna().any().any() or y.isna().any():
        raise ValueError('X 또는 y에 결측치가 있습니다.')

    return X, y

X, y = build_xy(df, FEATURES, TARGET)

pp('Final Features: ', FEATURES)
pp('Excluded leakage features: ', LEAKAGE_FEATURES)
pp('X shape: ', X.shape)
pp('y shape: ', y.shape)
pp('Target type: ', type_of_target(y))

X_checked, y_checked = check_X_y(X, y, dtype='numeric')
pp('Validated X shape: ', X_checked.shape)
pp('Validated y shape: ', y_checked.shape)

new_X = pd.DataFrame([{
    "temperature_c": 79,
    "vibration_mm_s": 4.9,
    "operating_hours": 4200,
    "alarm_count_24h": 4
}])[FEATURES]

pp('New X shape: ', new_X.shape)
pp('Same feature order: ', new_X.columns.tolist() == X.columns.tolist())
pp(new_X)
pp('Leakage reason: repair_completed_after_failure는 고장이 발생한 뒤에야 확정되는 미래 정보임!')




















