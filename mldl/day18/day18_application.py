# day18_application.py
# 주제:

from include.graph_config import set_graph
from sklearn.datasets import load_wine
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

wine = load_wine(as_frame=True)

features = ['alcohol','malic_acid','total_phenols','color_intensity',
'hue']

X = wine.data[features]
y = wine.target
pp(y.value_counts().sort_index())
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 42,stratify=y)

model = LogisticRegression(
    solver='lbfgs',
    random_state=42,
max_iter=1000
)
model.fit(X_train, y_train)

a = [1,3,5,7,9,11]
result = []
for k in a:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    result.append({
        'k': k,
        '정확도': acc
    })
df = pd.DataFrame(result).round(4)

best_idx = df['정확도'].idxmax()
best_k = int(df.loc[best_idx,'k'])
best_acc = df.loc[best_idx,'정확도']







k_model = KNeighborsClassifier(n_neighbors=best_k)
k_model.fit(X_train, y_train)

pred_df = pd.DataFrame({
    '실제값' : y_test.iloc[:10],
    '예측값' : k_model.predict(X_test)[:10]

},index = y_test.index[:10]).sort_index()

pp(pred_df)
pp(df)






















