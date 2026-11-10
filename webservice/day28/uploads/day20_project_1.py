from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, f1_score, recall_score, confusion_matrix,ConfusionMatrixDisplay

from include.graph_config import set_graph
from util.print_util import pp, pt, up

set_graph(10, 8, 13)

# 1. 데이터 로드
DATA_FILE = Path(__file__).resolve().parent / 'assets' / 'team1_data.csv'
df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')


# 2.

pp(df.isna().sum()) # 결측치 개수
pp(df.shape) # 데이터의 행/열 개수
pp(df.columns) # 컬럼명
pp(df.dtypes) # 자료형
pp(df.describe()) # 기초 통계량

# 3. 중앙값 대체(연속형 자료)
median_cols = ['가입개월', '월이용금액', '최근로그인경과일', '만족도']
for col in median_cols:
    df[col] = df[col].fillna(df[col].median())

# 0으로 대체
zero_cols = ['고객센터문의수', '쿠폰사용수', '서비스장애횟수']
for col in zero_cols:
    df[col] = df[col].fillna(0)

# 최빈값 대체(이진 변수)
df['자동이체여부'] = df['자동이체여부'].fillna(df['자동이체여부'].mode()[0])
pp(df.columns)

target = df['이탈여부']

# 4. X, y 분리
X = df.drop(columns=['이탈여부'])
y = target

# 5. 학습용 / 테스트용 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y # 학습과 테스트 비율 동일 설정
)

# 6. 회귀 모델 객체 생성
l_model = LogisticRegression(
max_iter=1500, # 최적화 알고리즘 최대 1000번 반복
    solver='lbfgs', # 계수 최적화
    random_state=42
)
d_model = DecisionTreeClassifier(
    max_depth=4, #최대 깊이 4
    random_state=42)
f_model = RandomForestClassifier(
    n_jobs=-1, # 가능한 CPu전체사용
    random_state=42)

# 학습
l_model.fit(X_train, y_train)
d_model.fit(X_train, y_train)
f_model.fit(X_train, y_train)

# 예상 데이터 출력
l_pred = l_model.predict(X_test)
d_pred = d_model.predict(X_test)
f_pred = f_model.predict(X_test)



# 7. 성능표
models = [
        ('LogisticRegression', l_model, l_pred),
        ('DecisionTree', d_model, d_pred),
        ('RandomForest', f_model, f_pred)]

data = []
for name, model, pred in models:
    acc = model.score(X_test, y_test)
    precision = precision_score(y_test, pred)
    recall = recall_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    TN, FP, FN, TP = confusion_matrix(y_test, pred).ravel()   # 값을 나눠서 대입 해줌

    data.append({ #딕셔너리 키와 값 형태로 data 리스트에 추가
        '모델명': name,
        '정확도': round(acc, 4),
        '정밀도': round(precision, 4),
        '재현율': round(recall, 4),
        'f1-score': round(f1, 4),
        'TN': TN,
        'FP': FP,
        'FN': FN,
        'TP': TP
    })

model_names = ['LogisticRegression','DecisionTree','RandomForest']
# 인덱스 0번 1번 2번에 이름으로 바꿔줌
score_df = pd.DataFrame(data,index=model_names)
pp(score_df)

# 8.
# 모델별 F1-score 비교 그래프
plt.figure(figsize=(8, 5))
f1_bars = plt.bar(model_names, score_df['f1-score'])
plt.title('모델별 F1-score 비교')
plt.ylabel('F1 Score')
plt.ylim(0, 1)
plt.savefig('assets/f1.png', dpi=300, bbox_inches='tight')
plt.show()
#
# # 모델별 재현율 비교 그래프
plt.figure(figsize=(8, 5))
recall_bars = plt.bar(model_names, score_df['재현율'])
plt.title('모델별 재현율 비교')
plt.ylabel('재현율')
plt.ylim(0, 1)
plt.savefig('assets/recall.png', dpi=300, bbox_inches='tight')
plt.show()
#
# 모델별 정밀도 비교 그래프
plt.figure(figsize=(8, 5))
precision_bars = plt.bar(model_names, score_df['정밀도'])
plt.title('모델별 정밀도 비교')
plt.ylabel('정밀도')
plt.ylim(0, 1)
plt.savefig('assets/precision.png', dpi=300, bbox_inches='tight')
plt.show()
#
# 모델별 정확도 비교 그래프
plt.figure(figsize=(8, 5))
acc_bars = plt.bar(model_names, score_df['정확도'])
plt.title('모델별 정확도 비교')
plt.ylabel('정확도')
plt.ylim(0, 1)
plt.savefig('assets/acc.png', dpi=300, bbox_inches='tight')
plt.show()
#
# 최종 모델의 혼동행렬
l_cm = confusion_matrix(y_test, l_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=l_cm, display_labels=[0, 1])
# 0은 x축 : 유지 / 1은 y축 :이탈
disp.plot(cmap='Blues') # 숫자가 클수록 더 파란색
plt.title('최종 모델 혼동행렬 (Logistic Regression)')
plt.savefig('Matrix.png', dpi=300, bbox_inches='tight')
plt.show()


# 랜덤 포레스트 특성 중요도 그래프

importance_df = pd.DataFrame({
    'feature' : X.columns,
    'importance' : f_model.feature_importances_,
}).sort_values(by='importance', ascending=False).reset_index(drop=True)

plt.figure(figsize=(15,8))
plt.bar(importance_df['feature'], importance_df['importance'])
plt.xlabel('feature')
plt.ylabel('importance')
plt.title('포레스트 모델 특성별 중요도')
plt.tight_layout()
plt.savefig('assets/rf_feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

















































