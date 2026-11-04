# day22_ex1.py
# K-means, PCA, 군집, 차원축소

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples
from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

# 세 곳에 모여 있는 12개의 점
X = np.array([
    [1, 1], [1, 2], [2, 1], [2, 2],
    [5, 4], [5, 5], [6, 4], [6, 5],
    [9, 1], [9, 2], [10, 1], [10, 2]
], dtype=float)
pp(X)

# PCA 차원축소에서는 4개 특성을 사용하며,
# 뒤의 두 특성도 관측치별로 달라지도록 구성
X4 = np.column_stack([
    X,
    [2, 4, 3, 2, 5, 7, 6, 4, 8, 7, 9, 6],
    [7, 6, 8, 7, 3, 5, 4, 6, 2, 4, 3, 1]
])
pp(X4)

# 1. 공분산행렬(Covariance Matrix)
'''
개념 : 공분산은 두 특성이 평균에서 벗어나는 방향이 함께 움직이는 정도
      공분산행렬은 여러 특성의 분산(대각선)과 두 특성 간 공분산(비대각선)을 모은 정사각행렬
      공분산이 양수이면 함께 증가하는 경향, 음수이면 반대로 움직이는 경향을 의미
예시 : A=[1, 2, 3], B=[2, 4, 6]이면 B가 A와 같은 방향으로 움직이므로 공분산이 양수
      두 특성(A, B)의 공분산행렬은 
      [
        [1, 2], 
        [2, 4]
      ]
      이며 대각선 1, 4는 특성의 분산, 비대각선 2, 2는 특성간 분산의 관계 
'''
a = np.array([1., 2., 3.]) # 첫번째 특성
a_b = np.array([2., 4., 6.]) # 첫번째 특성이 증가하면 함께 증가하는 두번째 특성
matrix = np.column_stack([a, a_b]) # 행은 관측치, 열은 특성이 되도록 결합
pp(matrix)
# 열을 특성으로 보고 공분산 계산(n-1로 나눔)
cov_matrix = np.cov(matrix, rowvar=False, ddof=1)
pp(cov_matrix) # 공분산 행렬
pp(np.diag(cov_matrix)) # 대각선

# 2. 비지도학습 (Unsupervised Learning)
'''
개념 : 정답 라벨 y 없이 입력 특성 X의 유사성, 분포 또는 구조를 찾는 학습 방식
      군집화는 유사한 점을 묶고, PCA는 점들을 새로운 좌표축으로 표현
예시 : 점들의 원래 그룹 이름을 제공하지 않고 좌표만 이용해서 군집화
'''
unsupervised_model = KMeans(
    n_clusters=3, # 클러스터 수
    n_init=10, # 중심점 초기화 회수
    random_state=42,
)
# 좌표 X만으로 군집을 학습하고 번호 부여
unsupervised_labels = unsupervised_model.fit_predict(X)
pp('정답 없이 찾은 군집 번호: ', unsupervised_labels)

# 3. 군집(Cluster)와 군집화(Clustering)
'''
개념 : 군집은 서로 유사한 데이터의 모임, 군집화는 데이터에 모임별 식별 번호를 부여하는 작업
예시 : 가까이 모여 있는 좌표끼리 같은 군집 번호를 부여
      번호 0, 1, 2에는 크기 순서나 좋고 나쁨이 포함되어 있지 않음
'''
cluster_model = KMeans(
    n_clusters=3,
    n_init=10,
    random_state=42
)
cluster_labels = cluster_model.fit_predict(X)
pp('좌표와 군집번호')
pp(pd.DataFrame(X, columns=['x', 'y']).assign(군집=cluster_labels))

# 4. K-means
'''
개념 : K는 군집 수, means는 각 군집의 평균 위치인 중심점(Centroid)
      각 관측치를 가장 가까운 중심점에 배정하고, 중심점 위치를 다시 계산
예시 : K=3이면 점들을 3개 군집에 배정하고 중심점 3개를 학습
'''
model = KMeans(
    n_clusters=3,
    n_init=10,
    random_state=42
)
labels = model.fit_predict(X)
pp('생성된 군집 수: ', len(np.unique(labels)))
pp('군집 중심점')
pp(model.cluster_centers_.round(2))

# 5. K-means 동작 과정
'''
개념 : 초기 중심점을 고른 후, 가까운 중심점으로 점들을 배정하고 군집별 평균으로 중심점을 갱신
      배정과 갱신을 반복하여 중심점 이동이 충분히 작아지면 종료
예시 : (1, 1), (1, 2)는 중심점 (1, 1)에, (8, 8), (9, 8)은 중심점 (9, 9)에 배정
'''
step_X = np.array([[1., 1.], [1., 2.], [8., 8.], [9., 8.]])
centers = np.array([[1., 1.], [9., 9.]])
for turn in range(1, 3):
    # 각 점과 중심점 간 거리행렬
    distances = np.linalg.norm(step_X[:, None, :] - centers[None, :, :], axis=2)
    pp(distances)
    assignments = distances.argmin(axis=1) # 각 점에 가장 가까운 중심점의 인덱스
    # 군집별 평균으로 갱신
    centers = np.vstack([step_X[assignments==i].mean(axis=0) for i in range(2)])
    pp(f'{turn}회차 군집 번호: {assignments}')
    pp(f'{turn}회차 갱신 중심점: {centers}')

# 6. 유클리드 거리 (Euclidean Distance)
'''
개념 : 두 점의 각 좌표 차이를 제곱하여 더한 뒤 제곱근을 취하는 직선거리
      2차원 뿐만 아니라 특성이 많은 다차원 공간에도 같은 원리를 적용
예시 : A=(2, 3), B=(5, 7)이면 거리=루트((2-5)^2 + (3-7)^2)=5
'''
p1 = np.array([2., 3.])
p2 = np.array([5., 7.])
distance1 = np.linalg.norm(p1 - p2) # 두 점의 차이 벡터 길이 (유클리드 거리)
distance2 = np.linalg.norm(p2 - p1)
pp(distance1)
pp(distance2)

# 7. KMeans 클래스의 주요 하이퍼파라미터
'''
개념 : n_clusters는 군집 수, init은 초기 중심점 선정 방식, n_init은 초기값을 달리해서 실행하는 횟수
      max_iter는 각 실행의 반복 상한, tol은 수렴 허용 오차
예시 : K=3으로 10회 초기화를 시도하고 각 실행에서 최대 300회까지 갱신
'''
configured = KMeans(
    n_clusters=3, # 군집 수
    init='k-means++', # 초기 중심점을 분산되게 선택하도록 돕는 초기화 방식
    n_init=10, # 서로 다른 초기 중심점으로 10회 학습 후 가장 작은 Inertia 선택
    max_iter=300, # 초기화 1회 당 중심점 갱신을 허용할 최대 횟수
    tol=1e-4, # 중심점 이동이 충분히 작아졌는지를 판단하는 수렴 기준
    random_state=42
)
configured.fit(X)
pp('하이퍼파라미터 설정')
pp({
    name: configured.get_params()[name]
    for name in ['n_clusters', 'init', 'n_init', 'max_iter', 'tol', 'random_state']
})

# 8. KMeans 주요 메서드와 학습 후 속성
'''
개념 : fit()은 학습, fit_predict()은 학습과 군집 번호 반환, predict()은 새로운 점을 군집 배정
      transform()은 모든 중심점까지의 거리, labels_는 학습 점의 군집 번호
      cluster_centers_는 중심점들, inertia_는 중심점까지의 제곱거리 합, n_iter_는 학습 반복 회수
예시 : 학습 후 첫번째 점의 군집 번호와 모든 중심점까지의 거리를 확인
'''
api_model = KMeans(
    n_clusters=3,
    n_init=10,
    random_state=42
)
api_model.fit(X)
pp('labels_ 앞 3개: ', api_model.labels_[:3])
pp('첫 점에서 모든 중심점까지 거리: ', api_model.transform(X[:1]).round(3))
pp('cluster_centers_', api_model.cluster_centers_.round(2))
pp('inertia_ / n_iter_: ', round(api_model.inertia_, 3), api_model.n_iter_)

# 9. K-means 학습과 군집 번호 확인
'''
개념 : fit_predict(X)는 관측치별 군집 번호를 반환하며 그 번호를 결과 표에 붙여 비교할 수 있음
예시 : 12개의 좌표에 0 또는 1 또는 2 군집번호를 부여하고 각 군집에 몇개의 점이 있는지 계산
'''
learned = KMeans(
    n_clusters=3,
    n_init=10,
    random_state=42
)
learned_labels = learned.fit_predict(X)
learned_df = pd.DataFrame(X, columns=['x', 'y']).assign(군집=learned_labels)
pp('군집별 점 개수')
pp(learned_df['군집'].value_counts().sort_index())
pp('첫 5개 군집 배정')
pp(learned_df.head())

# 10. 중심점(Centroid)의 의미
'''
개념 : 중심점은 같은 군집으로 묶인 관측치들의 좌표별 산술평균
예시 : (1, 1), (1, 2), (2, 1), (2, 2)의 중심점은 (1.5, 1.5)
'''
centroid_points = np.array([[1., 1.], [1., 2.], [2., 1.], [2., 2.]])
centroid = centroid_points.mean(axis=0) # 각 열의 평균
pp('직접 계산한 중심점: ', centroid)
pp('K-Means로 계산한 중심점')
pp(KMeans(n_clusters=1, n_init=10, random_state=42) \
   .fit(centroid_points).cluster_centers_[0])

# 11. Inertia (군집 내부 제곱거리 합)
'''
개념 : 각 관측치에서 소속 군집 중심점까지의 거리 제곱을 모두 더한 값
      같은 데이터에서 K가 커지면 Inertia는 작아짐
예시 : (1, 1), (1, 2)의 중심점이 (1, 1.5)이면 거듭제곱의 합은 0.5
'''
inertia_model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
# 각 점이 속한 군집의 중심점
matched_centers = inertia_model.cluster_centers_[inertia_model.labels_]
manual_inertia = np.sum((X-matched_centers)**2)
pp('직접 계산한 Inertia: ', round(float(manual_inertia), 3))
pp('모델의 inertia_: ', round(inertia_model.inertia_, 3))

# 12. Elbow Method
'''
개념 : K를 늘릴 때 Inertia의 감소 폭이 크게 줄어드는 지점을 군집 수의 후보로 검토
      감소 곡선에 꺽이는 지점이 언제나 명확하게 나타나는 것은 아님
예시 : K가 2에서 3일때 100만큼 줄고 K가 3에서 4일때 10만큼 줄면 K=3을 후보로 검토
'''
elbow_ks = list(range(2, 6))
# K가 2에서 5까지 일때 inertia_ 리스트
elbow_values = [KMeans(n_clusters=k, n_init=10, random_state=42) \
    .fit(X).inertia_ for k in elbow_ks]
pp('K별 Inertia', list(zip(elbow_ks, np.round(elbow_values, 3))))
pp('인접 K로 갈 때 감소량: ', np.round(-np.diff(elbow_values), 3))

# 13. Elbow Method 그래프
# plot_ks = list(range(2, 6))
# plot_inertias = [KMeans(n_clusters=k, n_init=10, random_state=42) \
#     .fit(X).inertia_ for k in plot_ks]
# pp('그래프용 K-Inertia 표')
# pp(pd.DataFrame({'K': plot_ks, 'Inertia': np.round(plot_inertias, 3)}))
# plt.plot(plot_ks, plot_inertias, marker='o')
# plt.xlabel('K')
# plt.ylabel('Inertia')
# plt.title('Elbow Method Graph')
# plt.xticks(plot_ks)
# plt.grid(alpha=0.3)
# plt.tight_layout()
# plt.show()

# 14. Silhouette Score의 개념과 공식
'''
개념 :  a는 같은 군집의 다른 점까지의 평균거리, b는 가장 가까운 다른 군집의 점들까지의 평균거리
       개별 점의 Silhouette 값은 (b-a)/max(a,b)이며, 전체 점수는 개별 값의 평균
예시 : a=1, b=5라고 하면 (5-1)/max(1,5) = 4/5 = 0.8 이므로 자신의 군집에 더 가깝게 모여 있음
      일반적으로 1에 가까울수록 군집 분리가 좋고, 0은 경계 부근, 음수는 다른 군집에 더 가까움
'''
a_distance, b_distance = 1.0, 5.0
example_silhouette = (b_distance - a_distance) / max(a_distance, b_distance)
pp('a=1, b=5인 점의 Silhouette: ', round(example_silhouette, 3))

# 15. Silhouette Score 계산
'''
개념 : silhouette_score(X, labels)는 군집별 응집과 분리를 전체 평균 점수로 평가
      유효한 군집 수는 최소 2개이며 관측치 개수보다 적어야 함
예시 : K=3 결과에 대해 전체 점수와 각 점의 개별 점수를 출력
'''
sil_model = KMeans(n_clusters=3, n_init=10, random_state=42)
sil_labels = sil_model.fit_predict(X)
overall_sil = silhouette_score(X, sil_labels) # 모든 점의 Silhouette 평균
point_sil = silhouette_samples(X, sil_labels) # 관측치별 Silhouette 값
pp('전체 Silouette Score: ', round(overall_sil, 4))
pp('관측치별 Silouette 앞 5개: ', np.round(point_sil[:5], 4))

# 16. 새로운 관측치의 군집 예측
'''
개념 : predict()은 이미 학습한 중심점을 사용하여 새로운 좌표를 가장 가까운 군집에 배정
      새로운 관측치를 예측할 때 기존 모델을 다시 학습시키지 않음
예시 : 새로운 점 (9.5, 1.8)이 기존 세 중심점 중 어디에 가장 가까운지 확인  
'''
predict_model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
new_point = np.array([[9.5, 1.8]]) # 입력 shape : 관측치 수 1, 특성 수 2
new_cluster = predict_model.predict(new_point)
pp('새로운 점의 군집 번호: ', int(new_cluster[0]))
pp('새로운 점과 각 중심점까지 거리: ', predict_model.transform(new_point)[0].round(3))

# 17. PCA (Principal Component Analysis : 주성분 분석)
'''
개념 : PCA는 기족 특성의 선형 결합으로 새로운 직교 좌표축을 만들고
      큰 분산을 보존하도록 차원을 축소, PCA가 생성하는 것은 좌표값
예시 : 4개 특성을 가진 점을 PC1 / PC2 라는 두 좌표로 변환
'''
pca_intro = PCA(n_components=2) # 4개의 원복 특성을 투개 주성분 좌표로 변환
projected = pca_intro.fit_transform(X4)
pp('pCA 변환 전/후 shape',X4.shape,projected.shape)
pp('앞 3개 점의 PC1/ PC2 좌표')
pp(np.round(projected[:3],3))

# 18. 차원(Dimension)과 차원 축소(Dimensionality Reduction)
'''
개념 : 입력 공간 차원은 현 관측치를 표현하는 특성의 수
      차원 축소는 행(관측치) 개수를 유지하면서 열 (좌표축) 개수를 줄이는 것
'''
dimension_model = PCA(n_components=2)
reduced = dimension_model.fit_transform(X4)
pp('원복 행수와 특성 수 : ', X4.shape)
pp('변환후 행수와 특성 수: ', reduced.shape)

# 19. PC1과 PC2 (첫번째 주성분, 두번째 주성분)
'''
개념 : PC1은 투영한 데이터의 분산이 가장 큰 방향
      PC2는 PC2와 직교하면서 남은 분산이 가장 큰 방향
예시 : 각 주성분을 나타내는 벡터의 내적은 0에 가까워서 서로 직교함
'''
pc_model = PCA(n_components=2).fit(X4)
pc1,pc2 = pc_model.components_
pp(' PC1 축 벡터', pc1.round(4))
pp(' PC2 축 벡터', pc2.round(4))
pp('PC1 과 PC2 축의 내적(작교하면 0):', round(float(np.dot(pc1,pc2)),8))

# 20. PCA에서 분산(Variance)을 보존한다는 의미
'''
개념 : 분산은 값이 평균에서 얼마나 퍼져있는지를 나타내는 척도
      PCA는 분산이 큰 축부터 선택하며, 차원을 버리면 일부 변동 정보가 손실될 수 있음
예시 : 4개 주성분 중 앞의 2개가 전체 분산의 80%를 설명하면 남은 2개에는 20%가 포함됨
      이는 각 원래 값이 80% 정확이 복원된다는 의미는 아님
'''
variance_model = PCA(n_components=4).fit(X4)
# 설명분산비율 :  주성분별 전체 분산에 대한 비율
variance_ratio = variance_model.explained_variance_ratio_
pp('주성분 별 설명분산비율: ', np.round(variance_ratio, 4))
pp('앞 2개 주성분의 누적비율 : ', round(float(variance_ratio[:2].sum()),4))

# 21. PCA 클래스의 주요 하이퍼파라미터
'''
개념 : n_components는 남길 주성분 수, svd_solver는 특이값 분해 (SVD) 계산 방식
      whiten은 변환 주성분의 분산을 맞출지 여부
예시 : n_components = 2, svd_solver='auto',whiten=False
'''
pca_configured = PCA(
    n_components=2,
    svd_solver='auto',
    whiten=False,
    random_state=42
)
pca_configured.fit(X4)
pp('PCA설정: ',{key:pca_configured.get_params()[key]for key in ['n_components','svd_solver','whiten']})

# 22. PCA 주요 메서드 학습 후 속성
'''
개념 : fit()은 주성분 축 학습, transform()은 학습한 축으로 변환,
      fit_transform()은 학습과 축변환, inverse_transform()은 축소 좌표를 
    원래 특성 공간으로 근사치 복원
예시 : 4개의 특성을 두 주성분으로 변환하고 다시 복원했을 떄 원본과의 차이를 확인
'''
pca_methods = PCA(n_components=2)
pca_methods.fit(X4)
pca_coords = pca_methods.transform(X4)
pca_recovered = pca_methods.inverse_transform(pca_coords)
pp('components_의 shape: ', pca_methods.components_.shape)
pp('explained_variance_: ', pca_methods.explained_variance_.round(4))
pp('singular_values_: ', pca_methods.singular_values_.round(4))
pp('첫 관측치 원본:', X4[0])
pp('첫 관측치 근사 복원',pca_recovered.round(3))

# 23. PCA 설명분산비율 (Explained Variance Ratio)
'''
개념 : explained_variance_ratio_ 는 원본의 전체 분산 중 각 주성분이 분산을 설명하는 비율
      앞에서 부터 누적하면서 선택한 주성분들이 전체 변동의 얼마를 보존하는지 알 수 있음
예시 : PC1과 PC2 각각의 비율 및 두 주성분의 누적 비율을 출력
'''
ratio_model = PCA(n_components=2).fit(X4)
ratios = pd.Series(ratio_model.explained_variance_ratio_,index=['PC1','PC2'])
pp('주성분별 설명분산비율:', ratios.round(4))
pp('PC1 + PC2 누적 설명분산비율 : ',round(float(ratios.sum()),4))

# 24. PCA.components_ ( 주성분의 구성 가중치)
'''
개념 : components_ 의 각 행은 주성분 하나를 구성하는 원래 특성별 계수
      계수 절대값이 큰 특성은 해당 축의 방향을 형성하는데 상대적으로 크게 기여
예시 : 4개 원본 특성에서 PC1 과  PC2가 어떤 가중치로 만들어 졌는지 표로표시
      주성분 축의 부호가 뒤집혀도 표현하는 기하학적 정보는 같을 수 있음
'''
loading_model = PCA(n_components=2).fit(X4)
loading_df = pd.DataFrame(
    loading_model.components_, # 주성분 수 * 원래 특성 수 의 가중치 행렬
    index = ['PC1','PC2'],
    columns=['특성A','특성B','특성C','특성D']
)
pp('PC별 원본 특성 가중치 : ')
pp(loading_df.round(4))

# 25. PCA 2차원 군집 산점도
'''
개념 : x축과 y축은 PC1, PC2좌표, 점의 색 구분은 K-means가 부여한 군집 번호에 대응
      PCA 자체가 색이나 군집 번호를 만드는 것은 아님
예시 : 4개 특성으로 구한 군집을 같은 점의 2차원 PCA 산점도에 표시
'''
visual_labels = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(X4)
visual_coords = PCA(n_components=2).fit_transform(X4)
pp(' 군집별 점 개수:\n', pd.Series(visual_labels).value_counts().sort_index())

for cluster_id in np.unique(visual_labels):
    mask = visual_labels == cluster_id  # 현재 군집에 해당하는 관측치만 표시
    plt.scatter(visual_coords[mask, 0], visual_coords[mask, 1], label=f'Cluster {cluster_id}', alpha=0.8)
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('K-means labels on PCA coordinates')
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()



















