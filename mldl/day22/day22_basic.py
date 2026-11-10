# day22_basic.py
# 주제:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.preprocessing import StandardScaler

from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

df = pd.DataFrame({
'주간도서관방문': [6, 7, 5, 1, 2, 1, 4, 5, 4, 2, 3, 2],
'일평균열람시간': [220, 245, 210, 45, 60, 50, 150, 170, 140, 80, 95, 75],
'온라인강의시간': [3, 2, 4, 10, 9, 11, 6, 5, 7, 8, 7, 9]
})

features = df.columns.to_list()
X = df[features]

scaler = StandardScaler(
    with_mean=True,
    with_std=True,
)

# X값을 표준화
X_scaled = scaler.fit_transform(X)

# K-means
kmeans = KMeans(
    n_clusters=3,
    n_init=10,
    random_state=42,
)
label = kmeans.fit_predict(X_scaled)

df['군집'] = label

a = df['군집'].value_counts().sort_index()
pp(a)

# 군집별 3개 특성의 평균
cluster_mean = df.groupby('군집')[features].mean().round(4)
pp(cluster_mean)

# #표준화 공간에서의 군집 중심
# cluster_centers = round(kmeans.cluster_centers_.mean(),4)
# pp(cluster_centers)
#
# # 각데이터의 소속 중심점 사이의 제곱거리합
# inertia = round(kmeans.inertia_,4)
# pp(inertia)
#
# # 실제 수행한 중심점 갱신 반복횟수
# n_iter = round(kmeans.n_iter_,4)
# pp(n_iter)


centers = scaler.inverse_transform(kmeans.cluster_centers_)
centers_df = pd.DataFrame(centers
                          ,columns=features)

# centers_df.index.name = '군집'

pp(centers_df)

pp(df)














