# day14_challenge.py
# 주제:




# day14_challenge.py
# 도시 대기질 EDA 대시보드

from pathlib import Path
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

# 2. 가상 대기질 데이터 생성
rng = np.random.default_rng(100) # 시드 100 지정
# 2026년 3월 1일 부터 하루 간격으로 60개의 날짜를 생성
dates = pd.date_range("2026-03-01", periods=60, freq="D")
# pp(dates)
regions = np.resize(["강남", "종로", "마포"], 60)
# 강남,종로,마포 60번 반복

temperature = rng.uniform(8, 30, size=60)
# 8도 이상 30도미만 균등분포 난수로 60개의 기온데이터 생성
wind = rng.uniform(0.5, 6.0, size=60)
# 0.5 이상 6.0 미만 균등분포 난수로 60개 풍속데이터 생성
pm25 = np.clip(58 - wind * 5 + rng.normal(0, 9, size=60), 10, 80)
# 풍속이 강할수록 pm2.5가 감소하도록 데이터를 생성하고 범위는 10~80으로 제한
pm10 = pm25 + rng.uniform(8, 35, size=60)
# pm2.5보다 8~35만큼 큰 값이 되도록 pm10 값을 생성
df = pd.DataFrame({
    "날짜": dates,
    "지역": regions,
    "기온": temperature.round(1),
    "풍속": wind.round(1),
    "PM2.5": pm25.round(1),
    "PM10": pm10.round(1)
})

# 3. 기초통계 확인
print(df.select_dtypes(include="number").describe().round(2))

# 4. 2×2 EDA 대시보드
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
axes[0, 0].plot(df["날짜"], df["PM2.5"], linewidth=1.8)
axes[0, 0].set_title("날짜별 PM2.5")
axes[0, 0].set_xlabel("날짜")
axes[0, 0].set_ylabel("PM2.5")
axes[0, 0].tick_params(axis="x", rotation=30)

region_mean = df.groupby("지역", as_index=False)["PM2.5"].mean()
sns.barplot(data=region_mean, x="지역", y="PM2.5", errorbar=None, color=default_color, ax=axes[0, 1])
axes[0, 1].set_title("지역별 평균 PM2.5")
axes[0, 1].set_xlabel("지역")
axes[0, 1].set_ylabel("평균 PM2.5")

sns.histplot(data=df, x="PM2.5", bins=10, kde=True, color=default_color, ax=axes[1, 0])
axes[1, 0].set_title("PM2.5 분포")
axes[1, 0].set_xlabel("PM2.5")
axes[1, 0].set_ylabel("빈도")

sns.scatterplot(data=df, x="풍속", y="PM2.5", hue="지역", s=75, alpha=0.8, ax=axes[1, 1])
axes[1, 1].set_title("풍속과 PM2.5의 관계")
axes[1, 1].set_xlabel("풍속")
axes[1, 1].set_ylabel("PM2.5")

fig.suptitle("도시 대기질 EDA", fontsize=16)
fig.tight_layout()

# 5. 이미지 저장
output_path = Path("air_quality_dashboard.png")
fig.savefig(output_path, dpi=150, bbox_inches="tight")
plt.show()

# 6. 핵심 통계 출력
max_row = df.loc[df["PM2.5"].idxmax()]
print(f"\nPM2.5 평균: {df['PM2.5'].mean():.1f}")
print(f"PM2.5 최대값 발생일: {max_row['날짜'].date()}")
print(f"PM2.5 최대값 발생지역: {max_row['지역']}")
print("\n지역별 평균 PM2.5")
print(df.groupby("지역")["PM2.5"].mean().round(1))

# 7. 그래프 기반 관찰
print("\n[EDA 관찰]")
print("PM2.5는 날짜에 따라 비교적 큰 폭으로 변동합니다.")
print("지역별 평균 PM2.5에는 차이가 있지만 세 지역의 관측 수와 생성 조건을 함께 고려해야 합니다.")
print("PM2.5는 특정 구간에 집중되며 일부 높은 값도 관찰됩니다.")
print("풍속이 높은 구간에서 PM2.5가 낮아지는 경향이 보이지만 모든 점이 같은 패턴을 따르지는 않습니다.")
print("산점도의 관계만으로 풍속이 PM2.5 변화의 직접 원인이라고 단정할 수 없으며 다른 기상·환경 변수를 함께 검토해야 합니다.")





























































