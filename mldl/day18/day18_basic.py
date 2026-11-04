# day18_basic.py
# 주제:
from include.graph_config import set_graph
from sklearn.datasets import load_iris
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
RANDOM_SEED = 42

iris = load_iris(as_frame=True)



X = iris.data
y = iris.target



X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=RANDOM_SEED,stratify=y)


model = LogisticRegression(max_iter=1000,solver='lbfgs')

model.fit(X_train,y_train)

prediction = model.predict(X_test)
# 예측 값
pp(prediction)
pp(model.predict(X_test))

# 정확도
acc=accuracy_score(y_test,prediction)
pp(round(acc,4))

result_df = pd.DataFrame({
    '실제값' : y_test.reset_index(drop=True).iloc[:5],
    '예측값' : prediction[:5]
})
pp(result_df)

proba = model.predict_proba(X_test[:3])

df = pd.DataFrame(
    proba,
    columns= iris.target_names,
    ).round(4)
pp(df)

































