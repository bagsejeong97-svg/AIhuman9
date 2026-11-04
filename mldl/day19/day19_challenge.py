# day19_challenge.py
# 주제:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

from util.print_util import pp, up,pt
from include.graph_config import set_graph

set_graph(10, 8, 13)

rng = np.random.default_rng(42)
size = 1200
df = pd.DataFrame({
    'overtime': rng.integers(0, 2, size),                  # 0 또는 1 (야근 여부)
    'satisfaction': rng.uniform(1, 10, size),
    # 만족도 (1~10)
    'monthly_income': rng.uniform(250, 900, size),          # 월소득 (250~900)
    'years_company': rng.integers(0, 21, size),
    # 근속년수
    'projects': rng.integers(1, 9, size),
    # 프로젝트 수
    'commute_min': rng.uniform(10, 120, size)               # 통근시간 (10~120)
})

normal = rng.normal(0,0.9,size)

df['risk'] = df['overtime']*1.8 - df['satisfaction']*0.35 - df['monthly_income']*0.004 - df["years_company"]*0.08 + df['projects']*0.18 + df['commute_min']*0.015+normal

a = df['risk'].quantile(0.65)

df['risk'] = np.where(df['risk'] > a, 1, 0)


X = df.drop(columns = ['risk'])

y = df['risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 42,stratify = y)


tree1 = DecisionTreeClassifier(
    random_state = 42,
)

tree2 = DecisionTreeClassifier(
max_depth=5, min_samples_leaf=8, random_state=42
)

forest = RandomForestClassifier(
n_estimators=300, max_depth=8, min_samples_leaf=3, random_state=42, n_jobs=-1
)

tree1.fit(X_train, y_train)
tree2.fit(X_train, y_train)
forest.fit(X_train, y_train)
pred_tree1 = tree1.predict(X_test)
pred_tree2 = tree2.predict(X_test)
pred_forest = forest.predict(X_test)
a = tree1.predict(X_train)
b = tree2.predict(X_train)
c=forest.predict(X_train)

# 학습 정확도
train_tree1 = accuracy_score(y_train, a)
train_tree2 = accuracy_score(y_train, b)
train_forest = accuracy_score(y_train, c)

# 테스트 정확도
acc_tree1 = accuracy_score(y_test, pred_tree1)
acc_tree2 = accuracy_score(y_test, pred_tree2)
acc_forest = accuracy_score(y_test, pred_forest)


# gap 컬럼
gap_df = pd.DataFrame({
    '모델' : ['tree1','tree2','forest'],
    '학습정확도' :[train_tree1,train_tree2,train_forest],
    '테스트정확도':[acc_tree1,acc_tree2,acc_forest],
    'gap': [train_tree1-acc_tree1,train_tree2-acc_tree2,train_forest-acc_forest]
})

# 가장  gap이큰 모델과값
pp(gap_df)
big_gap = gap_df['gap'].max()
big_gap_name = gap_df.loc[gap_df['gap'].idxmax(),'모델']

pp(big_gap_name,big_gap)


# 가장
big_test = gap_df['테스트정확도'].max()
big_test_name = gap_df.loc[gap_df['테스트정확도'].idxmax(),'모델']

pp(big_test_name,big_test)



importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': forest.feature_importances_,
}).sort_values(by='importance', ascending=False).reset_index(drop=True)


importance_df.head(3).plot(
    x = 'feature',
    y = 'importance',
    kind = 'bar'
)

for i, val in enumerate(importance_df.head(3)['importance']):
    plt.text(i, val + 0.005, f'{val:.4f}', ha='center')
plt.title('특성 중요도 상위3')
plt.tight_layout()
plt.xticks(rotation=0)
plt.show()

new_employee = pd.DataFrame([{
    'overtime': 1,
    'satisfaction': 4.0,
    'monthly_income': 420,
    'years_company': 2,
    'projects': 6,
    'commute_min': 80
}])

pred = forest.predict(new_employee)[0] # 예측클래스
prob = forest.predict_proba(new_employee)[0] # 예측클래스 확률

# 이직 클래스 (1)의 위치
class_index = list(forest.classes_).index(1)

attrition_prob = prob[class_index]

pp('[신규 직원 예측]')
pp(new_employee)

pp(f'예측 이직 여부: {pred}')

pp(f'이직 확률: {attrition_prob:.4f}')

# 단일 깊은 트리는 특정 학습 샘플과 잡음에 민감하지만
# 랜덤포레스트는 서로 다른 여러 트리의 예측을 결합해 변동성을 줄일 수 있음

# feature_importances_는 모델 분기에 대한 상대적 기여도이므로
# 해당 특성이 실제 결과를 직접 유발한다는 인과관계를 의미하지는 않음

up(5)







