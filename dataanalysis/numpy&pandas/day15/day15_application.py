# day15_application.py
# 주제:
# day15_application.py
# 온라인 쇼핑 반품 데이터 EDA

from pathlib import Path
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from util.print_util import pp

pp()

BASE_DIR = Path(__file__).parent # 현재 경로의 상위 경로
DATA_FILE = BASE_DIR / 'assets' / 'day15_application_data.csv' # CSV 파일 경로
OUTPUT_DIR = Path(__file__).with_name('day15_application') # 결과 파일 저장 디렉토리
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")

if platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 1. 데이터 점검
df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
pp("[크기]", df.shape)
pp("[자료형]\n", df.dtypes)
pp("[결측치]\n", df.isna().sum())
pp("[주문ID 중복]", df.duplicated(subset="주문ID").sum())

# 2. 문자열·날짜·수치형 정제
clean_df = df.copy()
for col in ["주문ID", "카테고리", "반품여부", "반품사유", "고객등급"]:
    clean_df[col] = clean_df[col].astype("string").str.strip()
clean_df["주문일"] = pd.to_datetime(clean_df["주문일"], errors="coerce")
clean_df["주문금액"] = pd.to_numeric(clean_df["주문금액"], errors="coerce")
clean_df["수량"] = pd.to_numeric(clean_df["수량"], errors="coerce")
clean_df["반품여부"] = clean_df["반품여부"].replace({"반품": "Y", "yes": "Y", "YES": "Y", "정상": "N", "no": "N", "NO": "N"})
clean_df["반품사유"] = clean_df["반품사유"].replace({"size": "사이즈", "SIZE": "사이즈"})
clean_df.loc[clean_df["반품여부"].eq("N") & clean_df["반품사유"].isna(), "반품사유"] = "해당없음"

# 3. 비정상 수치와 중복 처리
clean_df.loc[clean_df["주문금액"].le(0), "주문금액"] = pd.NA
clean_df.loc[clean_df["수량"].le(0), "수량"] = pd.NA
clean_df["주문금액"] = clean_df["주문금액"].fillna(clean_df["주문금액"].median())
clean_df["수량"] = clean_df["수량"].fillna(clean_df["수량"].median())
clean_df = clean_df.dropna(subset=["주문일", "카테고리", "반품여부"])
clean_df = clean_df.drop_duplicates(subset="주문ID", keep="last")

# 4. KPI 계산
order_count = len(clean_df)
total_sales = clean_df["주문금액"].sum()
return_rate = clean_df["반품여부"].eq("Y").mean() * 100
returned_avg_sales = clean_df.loc[clean_df["반품여부"].eq("Y"), "주문금액"].mean()
pp("\n[KPI]")
pp(f"유효 주문 건수: {order_count}건")
pp(f"전체 주문금액: {total_sales:,.0f}원")
pp(f"반품률: {return_rate:.1f}%")
pp(f"반품 주문 평균금액: {returned_avg_sales:,.0f}원")

# 5. 카테고리별 요약
category_summary = (
    clean_df.groupby("카테고리")
    .agg(
        주문건수=("주문ID", "count"),
        주문금액합계=("주문금액", "sum"),
        반품건수=("반품여부", lambda s: s.eq("Y").sum()),
    )
)
category_summary["반품률"] = category_summary["반품건수"] / category_summary["주문건수"] * 100
category_summary = category_summary.sort_values("반품률", ascending=False)
pp("\n[카테고리별 요약]\n", category_summary.round(2))

# 6. 카테고리별 반품률
plot_df = category_summary.reset_index()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=plot_df, x="카테고리", y="반품률", color="C0", ax=ax)
ax.set_title("카테고리별 반품률")
ax.set_ylabel("반품률(%)")
plt.tight_layout()
plt.show()

# 7. 반품사유별 건수
reason_df = clean_df.loc[clean_df["반품여부"].eq("Y"), "반품사유"].value_counts().rename_axis("반품사유").reset_index(name="건수")
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=reason_df, x="반품사유", y="건수", color="C0", ax=ax)
ax.set_title("반품사유별 건수")
plt.tight_layout()
plt.show()

# 8. 주문금액 분포
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(data=clean_df, x="주문금액", bins=10, color="C0", ax=ax)
ax.set_title("주문금액 분포")
plt.tight_layout()
plt.show()

# 9. 인사이트
top_return_category = category_summary["반품률"].idxmax()
top_reason = reason_df.iloc[0]["반품사유"] if not reason_df.empty else "없음"
high_value_return = clean_df.loc[clean_df["반품여부"].eq("Y"), "주문금액"].median()
pp("\n[인사이트]")
pp(f"1. 반품률이 가장 높은 카테고리는 '{top_return_category}'입니다.")
pp(f"2. 가장 많이 기록된 반품사유는 '{top_reason}'입니다.")
pp(f"3. 반품 주문금액의 중앙값은 {high_value_return:,.0f}원입니다.")
pp("4. 카테고리별 반품률 차이는 상품 특성 외에 고객 구성이나 프로모션 영향도 받을 수 있습니다.")
pp("5. 반품률 개선 우선순위는 반품률과 주문 규모를 함께 비교해 판단하는 것이 적절합니다.")
pp("[추가 확인 데이터] 상품 옵션·사이즈 정보, 프로모션/쿠폰 적용 여부")
