# day14_application.py
# 채용 평가 데이터 시각화

import platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 그래프 기본 설정
sns.set_theme(style="whitegrid")
if platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
default_color = plt.rcParams["axes.prop_cycle"].by_key()["color"][0]  # 기본 컬러 사이클

# 2. 채용 평가 데이터 생성
rng = np.random.default_rng(42)
jobs = rng.choice(["Backend", "Frontend", "Data"], size=60)
# 3가지 중 60개 랜덤하게 생성

coding = np.clip(rng.normal(72, 12, size=60), 0, 100)
# 평균 72, 표준편차 12인 정규분표에서 60명의 코딩점수를 생성, 범위 0~100
interview = np.clip(rng.normal(75, 10, size=60), 0, 100)
# 평균 75, 표준편차 10인 정규분표에서 60명의 면접점수를 생성, 범위 0~100

df = pd.DataFrame({
    "직무": jobs,
    "코딩점수": coding.round(1),
    "면접점수": interview.round(1)
})

# 3. 최종점수와 합격여부 계산
df["최종점수"] = (df["코딩점수"] * 0.6 + df["면접점수"] * 0.4).round(1)
df["합격여부"] = np.where(df["최종점수"] >= 75, "합격", "불합격")

# 4. 최종점수 분포
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(data=df, x="최종점수", bins=10, kde=True, color=default_color, ax=ax)
ax.set_title("지원자 최종점수 분포")
ax.set_xlabel("최종점수")
ax.set_ylabel("빈도")
fig.tight_layout()
plt.show()

# 5. 코딩점수와 면접점수 관계
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=df,
    x="코딩점수",
    y="면접점수",
    hue="합격여부",
    s=80,
    alpha=0.8,
    ax=ax
)
ax.set_title("코딩점수와 면접점수")
fig.tight_layout()
plt.show()

# 6. 직무별 평균 최종점수
job_mean = df.groupby("직무", as_index=False)["최종점수"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=job_mean, x="직무", y="최종점수", errorbar=None, color=default_color, ax=ax)
ax.set_title("직무별 평균 최종점수")
ax.set_xlabel("직무")
ax.set_ylabel("평균 최종점수")
fig.tight_layout()
plt.show()

# 7. 통계와 관찰 결과 출력
pass_rate = (df["합격여부"] == "합격").mean() * 100
print(f"전체 합격률: {pass_rate:.1f}%")
print("\n직무별 평균 최종점수")
print(df.groupby("직무")["최종점수"].mean().round(1))
print("\n[관찰]")
print("최종점수는 중간 점수대에 비교적 많이 분포합니다.")
print("합격자는 코딩점수와 면접점수가 모두 높은 영역에 상대적으로 많이 나타납니다.")
print("직무별 평균점수 차이는 표본 구성에 따라 달라질 수 있으므로 차이의 원인을 단정하면 안 됩니다.")
