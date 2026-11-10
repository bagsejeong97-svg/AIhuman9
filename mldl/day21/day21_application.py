# day21_application.py
# 주제:


import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate, train_test_split
from sklearn.pipeline import Pipeline,make_pipeline
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

X_array, y = make_classification(
    n_samples=1000,       # 고객 수
    n_features=8,         # 고객 행동/거래 특성 수
    n_informative=6,      # 실제 분류에 정보를 주는 특성 수
    n_redundant=1,        # 다른 특성 조합으로 표현되는 중복 특성 수
    weights=[0.7, 0.3],   # 유지 70%, 이탈 30%의 불균형을 가정
    class_sep=1.0,
    random_state=20
)
columns = ["이용기간", "월사용량", "문의횟수", "평균결제액", "할인율", "접속일수", "콘텐츠수", "만족도"]
X = pd.DataFrame(X_array, columns=columns)
X["평균결제액"] = X["평균결제액"] * 50000 + 80000  # 원 단위 결제액처럼 큰 스케일을 구성
X["할인율"] = X["할인율"] * 0.05 + 0.1            # 비율 데이터처럼 작은 스케일을 구성
pp("데이터 크기", X.shape)
pp("이탈 비율", pd.Series(y).value_counts(normalize=True).sort_index().round(3))



X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=20,
    stratify=y
)

pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=3000)
)


cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20)


cv_acc = cross_val_score(pipe, X, y, cv=cv, scoring='accuracy')

cv_f1 = cross_val_score(pipe, X, y, cv=cv, scoring='f1')

pp(cv_acc,cv_acc.mean(),cv_acc.std())

pp(cv_f1,cv_f1.mean(),cv_f1.std())


result = cross_validate(pipe, X, y, cv=cv, scoring='accuracy',
return_train_score=True)

train_mean = result['train_score'].mean()

val_mean = result['test_score'].mean()

pp(f'gap: {round(train_mean-val_mean,3)}')




pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)
acc = accuracy_score(y_test, pred)
f1 = f1_score(y_test, pred)
pp(acc,f1)

#cv 는 한번의 분할보다 안정적인 일반화 성능 추정에 유리하다 여러번의 fold의 결과를 평균내는것이기 때문에

pp(cv_acc.mean(),acc)
pp(cv_f1.mean(),f1)

plt.plot(range(1,6),cv_f1,marker='o')
plt.axhline(cv_f1.mean(),linestyle='--',label=f'mean={cv_f1.mean():.3f}')
plt.xticks(range(1,6))
plt.xlabel('fold')
plt.ylabel('f1_score')
plt.title('Fold5 - f1_score')
plt.legend()
plt.tight_layout()
plt.show()








































