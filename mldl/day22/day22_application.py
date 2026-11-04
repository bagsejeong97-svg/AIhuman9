# day22_application.py
# 주제:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import StandardScaler

from mldl.day22.day22_basic import features
from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

data ={
'전력사용량': [82, 88, 79, 85, 91, 86, 42, 38, 45, 41, 39, 44, 65, 69, 63, 71, 67, 66],
'평균온도': [74, 77, 72, 75, 79, 76, 48, 45, 51, 47, 46, 50, 61, 64, 59, 66, 63, 62],
'진동수준': [6.8, 7.2, 6.5, 7.0, 7.6, 7.1, 2.1, 1.8, 2.4, 2.0, 1.9, 2.3, 4.2, 4.6, 4.0, 4.9, 4.5, 4.3],
'일가동시간': [20, 21, 19, 22, 21, 20, 8, 7, 9, 8, 7, 9, 14, 15, 13, 16, 15, 14]}

df = pd.DataFrame(data)

features = df.columns.to_list()
X = df[df.columns.to_list()]
pp(X)


scaler = StandardScaler(
    with_mean=True,
    with_std=True
)

X_scaled = scaler.fit_transform(X)


a = range(2,6)
result=[]
for k in a:
    kmeans = KMeans(
        n_clusters=k,
        n_init=10,
        random_state=42
    )
    label = kmeans.fit_predict(X_scaled)

    inertia = kmeans.inertia_
    sil = silhouette_score(X_scaled, label)

    result.append({'k':k,'sil':sil,'inertia':inertia})

#Silhouette Score가 가장 높은 K를 자동으로 선택합니다.
result_df = pd.DataFrame(result).sort_values(by='sil',ascending=False)

max_k = result_df.iloc[0]['k'].astype(int)

k_means = KMeans(
        n_clusters=max_k,
        n_init=10,
        random_state=42
    )

df['군집'] = k_means.fit_predict(X_scaled)
pp(df['군집'].value_counts().sort_index())
pp(df.groupby('군집')[features].mean().round(2))
pp(df)

plot_df = result_df.sort_values(by='k')
plt.plot(plot_df['k'],plot_df['inertia'],marker='o')
plt.xlabel('군집수 k')
plt.ylabel('inertia')
plt.title('설비운전 데이터 elbow method')
plt.xticks(result_df['k'])
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()














