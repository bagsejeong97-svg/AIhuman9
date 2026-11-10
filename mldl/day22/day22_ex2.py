# day22_ex2.py
# K-means와 PCA를 활용한 비지도학습과 차원축소

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

RANDOM_STATE = 42

# 랜덤 숫자 제네레이터
rng = np.random.default_rng(RANDOM_STATE)

# 군집 실습용 합성 고객 데이터
n = 120
df = pd.DataFrame({
    "월방문횟수": np.concatenate([
        rng.normal(5, 1.2, n//3),
        rng.normal(15, 2.0, n//3),
        rng.normal(9, 1.5, n//3)
    ]),
    "평균구매액": np.concatenate([
        rng.normal(70000, 15000, n//3),
        rng.normal(260000, 30000, n//3),
        rng.normal(140000, 20000, n//3)
    ]),
    "쿠폰사용률": np.concatenate([
        rng.normal(0.75, 0.08, n//3),
        rng.normal(0.25, 0.08, n//3),
        rng.normal(0.50, 0.10, n//3)
    ]),
    "온라인구매비율": np.concatenate([
        rng.normal(0.35, 0.08, n//3),
        rng.normal(0.80, 0.07, n//3),
        rng.normal(0.55, 0.09, n//3)
    ])
})

features = ["월방문횟수", "평균구매액", "쿠폰사용률", "온라인구매비율"]

X = df[features]

# StandardScaler 주요 설정값과 API
scaler = StandardScaler(
    with_mean=True, # 평균 중심화 적용 여부
    with_std=True # 표준편차 기준 스케일 조정 여부
)

# fit_transform() : 평균·스케일을 학습한 뒤 바로 변환
X_scaled = scaler.fit_transform(X)
pp("scaler.mean_:", scaler.mean_)
pp("scaler.scale_:", scaler.scale_)

# transform() : 학습된 기준으로 새로운 데이터를 변환
pp("transform first row:", scaler.transform(X.iloc[[0]]))

# inverse_transform() : 표준화된 값을 원래 단위로 복원
pp("inverse first row:", scaler.inverse_transform(X_scaled[[0]]))

# KMeans : K개의 중심점을 반복 갱신하며 거리 기반 군집을 형성
kmeans = KMeans(
    n_clusters=3, # 만들 군집 수 K
    init="k-means++", # 초기 중심점을 효율적으로 선택하는 방식
    n_init=10, # 서로 다른 초기 중심으로 전체 학습을 반복하는 횟수
    max_iter=300, # 한 번의 학습에서 허용하는 최대 반복 횟수
    random_state=RANDOM_STATE, # 초기 중심점 선택 난수 재현
    tol=1e-4 # 중심점 변화가 이 값보다 작아지면 수렴으로 판단
)

# fit_predict() : 군집 중심을 학습하면서 각 데이터의 군집 번호도 반환
labels = kmeans.fit_predict(X_scaled)
df["군집"] = labels
pp("labels_:", kmeans.labels_[:10]) # labels_ : 학습 데이터의 최종 군집 번호
pp("cluster_centers_:")
pp(kmeans.cluster_centers_) # cluster_centers_ : 표준화 공간에서의 군집 중심
pp("inertia_:", kmeans.inertia_) # inertia_ : 각 데이터와 소속 중심점 사이의 제곱거리 합
pp("n_iter_:", kmeans.n_iter_) # n_iter_ : 실제 수행한 중심점 갱신 반복 횟수

# predict() : 학습된 중심점을 기준으로 새 데이터의 군집 번호 반환
new_customer = pd.DataFrame([[12, 180000, 0.4, 0.7]], columns=features)
new_scaled = scaler.transform(new_customer)
pp("new cluster:", kmeans.predict(new_scaled))

# transform() : 각 데이터에서 모든 군집 중심까지의 거리를 반환
pp("center distances:", kmeans.transform(new_scaled))

# 군집 중심을 원래 단위로 복원
centers = scaler.inverse_transform(kmeans.cluster_centers_)
center_df = pd.DataFrame(centers, columns=features)
center_df["군집"] = range(len(center_df))
pp("원 단위 군집 중심:")
pp(center_df)

# groupby()와 mean()으로 군집별 평균 특성 요약
cluster_summary = df.groupby("군집")[features].mean().round(2)
pp("군집별 평균:")
pp(cluster_summary)

# value_counts() : 군집별 데이터 개수, sort_index() : 군집 번호 순으로 정렬
cluster_size = df["군집"].value_counts().sort_index()
pp("군집별 크기:")
pp(cluster_size)

# K 후보별 Inertia와 Silhouette Score 비교
results = []
inertias = []
ks = range(2, 7)
for k in ks:
    model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    k_labels = model.fit_predict(X_scaled)
    inertias.append(model.inertia_)
    results.append({
        "K": k,
        "Inertia": model.inertia_,
        # 군집 내부 응집도와 군집 간 분리도 평가
        "Silhouette": silhouette_score(X_scaled, k_labels)
    })
result_df = pd.DataFrame(results)
pp(result_df)

# Elbow Method 그래프
plt.figure(figsize=(7, 4))
plt.plot(ks, inertias, marker="o")
plt.xlabel("군집 수 K")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.grid(alpha=0.3)
plt.show()

# PCA : 여러 Feature를 분산을 많이 보존하는 새로운 주성분 축으로 변환
pca = PCA(
    n_components=2, # 유지할 주성분 수
    svd_solver="auto", # 데이터 크기에 따라 적절한 SVD 계산 방식을 자동 선택
    whiten=False, # 주성분 분산을 강제로 1로 만들지 않음
    random_state=RANDOM_STATE # 일부 solver에서 난수 재현에 사용
)

# fit_transform() : 주성분 축을 학습하고 데이터를 새 좌표로 변환
X_pca = pca.fit_transform(X_scaled)
pp("PCA shape:", X_pca.shape)

# components_ : 각 주성분을 만드는 원본 Feature 가중치
pp("components_:")
pp(pca.components_)

# explained_variance_ : 각 주성분의 분산
pp("explained_variance_:", pca.explained_variance_)

# explained_variance_ratio_ : 각 주성분이 전체 분산에서 차지하는 비율
pp("explained_variance_ratio_:", pca.explained_variance_ratio_)
pp("설명분산비율 합:", pca.explained_variance_ratio_.sum())

# singular_values_ : SVD 과정에서 계산된 특이값
pp("singular_values_:", pca.singular_values_)

# transform() : 이미 학습한 PCA 축으로 새 데이터를 변환
pp("PCA transform:", pca.transform(X_scaled[:2]))

# inverse_transform() : 축소 좌표를 원본 표준화 공간으로 근사 복원
pp("PCA inverse first:")
pp(pca.inverse_transform(X_pca[:1]))

# 군집 결과를 PCA 2차원 좌표에 시각화
df["PC1"] = X_pca[:, 0]
df["PC2"] = X_pca[:, 1]
plt.figure(figsize=(8, 6))
for cluster_id in sorted(df["군집"].unique()):
    part = df[df["군집"] == cluster_id]
    plt.scatter(
        part["PC1"],
        part["PC2"],
        label=f"Cluster {cluster_id}",
        alpha=0.7
    )
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.tight_layout()
plt.show()

up(5)