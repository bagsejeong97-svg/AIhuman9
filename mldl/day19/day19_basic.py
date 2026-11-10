# day19_basic.py
# 주제:
import numpy as np
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


rng = np.random.default_rng(42)
size = 300
df = pd.DataFrame({
    "temperature": rng.uniform(60, 100, size),
    "pressure": rng.uniform(80, 140, size),
    "speed": rng.uniform(20, 80, size),
    "moisture": rng.uniform(2, 12, size)
})


a = ( 70 <= df['temperature'])  & (df['temperature'] <= 90)
b = (95 <= df['pressure']) & (df['pressure'] <= 120)
c = df['moisture'] < 9

df['quality'] = np.where(a & b &c,1,0 )

pp(df['quality'])

target = df['quality']

X = df.drop(columns=['quality'])
y = target

pp(X)
pp(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

tree = DecisionTreeClassifier(
    criterion='gini',
    splitter='best',
    max_depth=3,
    random_state=42
)

tree.fit(X_train, y_train)
pred = tree.predict(X_test)
a1 = tree.predict(X_train)

pp('학습 정확도',accuracy_score(y_train, a1))

pp('테스트 정확도',accuracy_score(y_test, pred))



importance = pd.Series(tree.feature_importances_, index=X.columns).sort_values(ascending=False)


pp(importance)

pp('가장 중요한 특성',importance.idxmax())
pp('가장중요한 특성의 값',round(importance.max(),4))
























