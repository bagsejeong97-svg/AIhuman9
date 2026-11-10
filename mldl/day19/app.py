import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

rng = np.random.default_rng(42)

size = 800

df = pd.DataFrame({
    "visits": rng.integers(1, 31, size), # 정수 난수
    "avg_view_min": rng.uniform(0.5, 15.0, size),
    "cart_items": rng.integers(0, 11, size),
    "coupon_used": rng.integers(0, 2, size),
    "review_count": rng.integers(0, 21, size)
})

# 구매 행동 특성과 무작위 잡음을 조합해 연속형 구매 점수를 생성
score = (
    df['visits'] * 0.08
    + df['avg_view_min'] * 0.25
    + df['cart_items'] * 0.5
    + df['coupon_used'] * 1.2
    + df['review_count'] * 0.05
    + rng.normal(0, 1.2, size)
)
pp(score)

# 중앙값보다 큰지의 여부를 정수 변환
df['purchase'] = (score > np.median(score)).astype(int)
pp(df['purchase'])

X = df.drop(columns='purchase')
y = df['purchase']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

tree = DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

forest = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1
)

tree.fit(X_train, y_train)
forest.fit(X_train, y_train)

tree_pred = tree.predict(X_test)
forest_pred = forest.predict(X_test)

tree_acc = accuracy_score(y_test, tree_pred)
pp(f'tree 테스트 정확도: {tree_acc:.4f}')

forest_acc = accuracy_score(y_test, forest_pred)
pp(f'forest 테스트 정확도: {forest_acc:.4f}')

better = 'Random Forest' if forest_acc > tree_acc \
    else 'Decision Tree' if tree_acc > forest_acc else '같음'
pp(f'더 높은 정확도의 모델: {better}')

# 혼동행렬
pp(confusion_matrix(y_test, forest_pred))

importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': forest.feature_importances_
}).sort_values(by='importance', ascending=False).reset_index(drop=True)

pp('[특성 중요도]')
pp(importance_df)

# 특성 중요도 top3
top3 = importance_df.head(3)
pp(top3)

# 시각화
plt.barh(top3['feature'], top3['importance'])
plt.xlabel('특성 중요도')
plt.ylabel('특성')
plt.title('온라인 쇼핑 구매 예측 - 중요 특성 상위 3개')
plt.tight_layout()
plt.show()

up(5)









