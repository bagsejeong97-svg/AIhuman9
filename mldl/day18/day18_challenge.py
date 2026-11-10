# day18_challenge.py
# 주제:

from include.graph_config import set_graph
from sklearn.datasets import load_digits
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from util.print_util import pp, up, pt

set_graph(10,8,13)
digits = load_digits(as_frame=True)


X = digits.data
y = digits.target

# 클래스별 데이터 개수
pp(y.value_counts().sort_index())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42,stratify=y)

#LogisticRegression 모델 생성
logistic = LogisticRegression(max_iter=3000)

logistic.fit(X_train, y_train) #학습

# 예측
logistic_pred = logistic.predict(X_test)
logistic_acc = accuracy_score(y_test, logistic_pred)

#KNN 모델
knn = KNeighborsClassifier(n_neighbors=3)

# 학습 출력, 정확도
knn.fit(X_train, y_train)
knn_pred = knn.predict(X_test)
knn_acc = accuracy_score(y_test, knn_pred)

# 정확도뿐 아니라 맞힌 개수와 틀린 개수도
comparison = pd.DataFrame({
    '모델' : ['LogisticRegression', 'KNN'],
    '정확도' : [logistic_acc, knn_acc],
    '정답수' : [
        (logistic_pred == y_test.to_numpy()).sum(),
        (knn_pred == y_test.to_numpy()).sum()
    ],
    '오답수' : [
        (logistic_pred != y_test.to_numpy()).sum(),
        (knn_pred != y_test.to_numpy()).sum()
    ]
})

comparison['정확도'] = comparison['정확도'].round(4)

pp(comparison)

# 정확도가 높은 모델의 이름와 예측 결과를 선택
if logistic_acc > knn_acc:
    best_name = 'LogisticRegression'
    best_pred = logistic_pred
elif logistic_acc < knn_acc:
    best_name = 'KNN'
    best_pred = knn_pred
else:
    best_name = '두모델의 정확도가 같음'
    best_pred = knn_pred
pp('정확도가 높은 모델:',best_name)
pp('모델의 정확도:',best_pred)


error_df = pd.DataFrame({
    '실제값': y_test.to_numpy(),
    '예측값': best_pred
},index = y_test.index)

error_df = error_df[error_df['실제값'] != error_df['예측값']]
pp(error_df.head(10))

# 어떤 실제 숫자에서 오분류가 많이 발생했는지 빈도를 집계
error_count = error_df['실제값'].value_counts().sort_index()
pp(error_count)


# 두 모델의 정확도를 막대 그래프로 비교
plt.bar(comparison['모델'],comparison['정확도'])
plt.ylim(0,1)
plt.ylabel('정확도')
plt.title('손글씨 숫자 분류 모델 정확도 비교')
for i, value in enumerate(comparison['정확도']):
    # 그래프에 텍스트 출력, ha:horizontal alignment(수평정렬)
    plt.text(i,value+0.01,f'{value:.4f}',ha='center')
plt.tight_layout()
plt.show()






