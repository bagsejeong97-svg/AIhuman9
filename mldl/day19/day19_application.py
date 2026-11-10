# day19_application.py
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
size = 800
df = pd.DataFrame({
    "visits": rng.uniform(1, 30, size).astype(int),
    "avg_view_min": rng.uniform(0.5, 15.0, size),
    "cart_items": rng.uniform(0, 10, size).astype(int),
    "coupon_used": rng.uniform(0, 1, size).astype(int),
    'review_count' :rng.uniform(0, 20, size).astype(int),
})

pp(df)

#정규분포 잡음
normal = rng.normal(loc=0, scale=1.0, size=size)
# pp(normal)
df['score'] = df['visits']*0.08 + df['avg_view_min']*0.25 + df['cart_items']*0.5 + df['coupon_used']*1.2 + df['review_count']*0.05 + normal

median = df['score'].median()

df['score'] = np.where(df['score'] > median,1,0 )

X = df.drop(columns=['score'])
y = df['score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42,stratify=y)


tree = DecisionTreeClassifier(
    criterion='gini',
    splitter='best',
    max_depth=4,
    random_state=42
)

forest = RandomForestClassifier(
    n_estimators=150,
    criterion='gini',
    random_state=42,
    n_jobs=-1
)

tree.fit(X_train, y_train)
forest.fit(X_train, y_train)


tree_pred = tree.predict(X_test)
forest_pred = forest.predict(X_test)


tree_accuracy = accuracy_score(y_test, tree_pred)

forest_accuracy = accuracy_score(y_test, forest_pred)

if tree_accuracy > forest_accuracy:
     result = 'DecisionTreeClassifier'
else:
     result = 'RandomForestClassifier'


pp('D정확도:',tree_accuracy)
pp('F정확도: ',forest_accuracy)

pp('정확도가 더 높은값',result)


cm = confusion_matrix(y_test, forest_pred)

pp(cm)

importance = pd.Series(
    forest.feature_importances_,
    index=X.columns
).sort_values(ascending=False)


importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': forest.feature_importances_,
}).sort_values(by='importance', ascending=False)

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

