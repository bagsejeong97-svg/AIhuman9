# day19_ex.py
# 의사결정트리. 랜덤포레스트

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

RANDOM_STATE = 42

# wine 데이터셋
wine = load_wine(as_frame=True)
X = wine.data
y = wine.target
target_names = list(wine.target_names)
pp(X.shape)
pp('클래스명:',target_names)

# X / y split
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.25,random_state=RANDOM_STATE,stratify=y)

# decision tree classifier
tree = DecisionTreeClassifier(
    criterion='gini', # 분기 품질을 평가할 분순도 기준
    splitter='best', # 가능한 후보중 가장 좋은 분기를 선택
    max_depth=4, #트리가 성정할 수 있는 최대 깊이
    min_samples_split=4, #내부 노드를 다시 분할하기 위한 최소 샘플 수
    min_samples_leaf=2, # 하나의 리프 노드가 가져야 할 최소 샘플수
    max_leaf_nodes=12, #생성할 수 있는 리프 노드 최대 수
    ccp_alpha=0.0, # 비용복잡도가지치기의 강도, 클수록 트리가 단순화됨
    random_state=RANDOM_STATE
)

# 학습
tree.fit(X_train, y_train)

# 예측
tree_pred = tree.predict(X_test)

# 정확도
pp('DecisionTreeClassifier 정확도:',accuracy_score(y_test,tree_pred))

#  predict_proba 클래스에 속할 확률
pp('DecisionTreeClassifier 정확도 확률(predict_proba):',tree.predict_proba(X_test.iloc[:3]))

# 특성 중요도 : 각 Feature가 불순도 감소에 기여한 상대적 비율, 합 = 1
pp('특성 중요도: ',tree.feature_importances_)

# 학습한후 tree_를 통해 트리의 속성을 확인
pp(tree.tree_.max_depth)
pp(tree.tree_.node_count) # 총 노드 수

# 제한 없는 트리와 제한된 트리 train/test 성능 비교
deep_tree = DecisionTreeClassifier(random_state=RANDOM_STATE)
deep_tree.fit(X_train, y_train)
pp('제한 없는 트리 Train:', deep_tree.score(X_train, y_train))
pp('제한 없는 트리 Test:', deep_tree.score(X_test, y_test))
pp('제한된 트리 Train:', tree.score(X_train, y_train))
pp('제한된 트리 Train:', tree.score(X_test, y_test))

# plot_tree : 학습된 트리의 분기 규칙을 시각화
# plt.figure(figsize=(18,8))
# plot_tree(
#     tree,
#     feature_names=X.columns, # 분기 노드에 표시할 feature 이름
#     class_names=target_names, # 리프와 노드에 표시할 클래스 이름
#     filled=True, # 클래스 분포에 따라 노드 색상을 채움
#     max_depth=15, # 시각화 할 최대 깊이
#     fontsize=8 # 노드내의 글자 크기
# )
#
# plt.show()


# export_text() : 트리 규칙을 텍스트 형태로 변환
rules = export_text(
    tree,
    feature_names = list(X.columns),
    max_depth = 3
)
pp(rules)

#RandomForestClassifier
forest = RandomForestClassifier(
    n_estimators=100, # 생성할 트리 계수
    criterion='gini',  # 각 트리에서 사용할 분기 기준
    max_depth= 8, # 개별트리의 최대 깊이
    min_samples_leaf=2, # 개별 트리의 리프 최소 샘플 수
    max_features='sqrt', # 각 분기에서 전체 Feature의 제곱근 정도만 후보로 사용
    bootstrap=True, # 각 트리를 위한 복원 추출 샘플 사용
    n_jobs=-1,  # 가능한 CPU코어를 모두 사용해 병렬 처리
    random_state=RANDOM_STATE
)

# 학습 예측
forest.fit(X_train, y_train)

forest_pred = forest.predict(X_test)

# 정확도
pp('Forest accuracy:',accuracy_score(y_test,forest_pred))

# predict_proba
pp('predict_proba: ',forest.predict_proba(X_test.iloc[:3]))

# estimators_ : 학습 후에 학습이 완료된 트리 목록
pp('트리 개수:', len(forest.estimators_))
pp('첫번째 트리 깊이: ',forest.estimators_[0].tree_.max_depth)


# feature_importance_ : 전체 Forest의 평균적인 Feature 중요도
importance = pd.Series(forest.feature_importances_, index=X.columns).sort_values(ascending=False)

pp(importance.head())
pp('importance 합: ',importance.sum())

# confusion matrix
cm = confusion_matrix(y_test,forest_pred)
pp(cm)

# 두 모델을 동일한 test 데이터에서 비교
pp('tree: ',accuracy_score(y_test,tree_pred))
pp('forest: ',accuracy_score(y_test,forest_pred))

# Freature 중요도를 정렬해서 막대그래프로 시각화
importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': forest.feature_importances_,
}).sort_values(by='importance', ascending=False)

importance_df.head(10).plot(
    x = 'feature',
    y = 'importance',
    kind = 'bar', #막대그래프
    legend = False # 범례표시안함
)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()






























































