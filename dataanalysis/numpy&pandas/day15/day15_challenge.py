# day15_challenge.py
# 주제:
from util.print_util import pp
from pathlib import Path

pp()

BASE_DIR = Path(__file__).parent # 현재 경로의 상위 경로
DATA_FILE = BASE_DIR / 'assets' / 'day15_challenge_data.csv' # CSV 파일 경로
OUTPUT_DIR = Path(__file__).with_name('day15_challenge') # 결과 파일 저장 디렉토리
OUTPUT_DIR.mkdir(exist_ok=True)

# day15_challenge.py
# 공유오피스 회의실 이용 데이터 EDA

import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


if platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 1. 데이터 로드 함수
def load_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    pp("[원본 크기]", df.shape)
    pp("[결측치]\n", df.isna().sum())
    pp("[예약ID 중복]", df.duplicated(subset="예약ID").sum())
    return df

# 2. 데이터 정제 함수
def clean_data(df):
    result = df.copy()
    for col in ["예약ID", "회의실", "예약상태"]:
        result[col] = result[col].astype("string").str.strip()
    result["예약상태"] = result["예약상태"].replace({"사용완료": "이용완료", "used": "이용완료", "cancel": "취소", "no-show": "노쇼"})
    result["예약시작"] = pd.to_datetime(result["예약시작"], errors="coerce")
    result["예약종료"] = pd.to_datetime(result["예약종료"], errors="coerce")
    result["정원"] = pd.to_numeric(result["정원"], errors="coerce")
    result["실제인원"] = pd.to_numeric(result["실제인원"], errors="coerce")
    result.loc[result["정원"].le(0), "정원"] = pd.NA
    result = result.dropna(subset=["예약시작", "예약종료", "정원", "예약상태"])
    result = result.drop_duplicates(subset="예약ID", keep="last")
    result["예약시간_분"] = (result["예약종료"] - result["예약시작"]).dt.total_seconds() / 60
    result = result[result["예약시간_분"].gt(0)].copy()
    result["실제인원"] = result["실제인원"].fillna(0)
    result["이용률"] = result["실제인원"] / result["정원"] * 100
    hour = result["예약시작"].dt.hour
    result["예약시간대"] = pd.cut(hour, bins=[-1, 11, 17, 23], labels=["오전", "오후", "저녁"])
    result["요일"] = result["예약시작"].dt.day_name().replace({"Monday": "월", "Tuesday": "화", "Wednesday": "수", "Thursday": "목", "Friday": "금", "Saturday": "토", "Sunday": "일"})
    return result

# 3. KPI 함수
def make_kpi(df):
    total = len(df)
    used_rate = df["예약상태"].eq("이용완료").mean() * 100
    cancel_rate = df["예약상태"].eq("취소").mean() * 100
    no_show_rate = df["예약상태"].eq("노쇼").mean() * 100
    avg_util = df.loc[df["예약상태"].eq("이용완료"), "이용률"].mean()
    return {"전체예약": total, "이용완료율": used_rate, "취소율": cancel_rate, "노쇼율": no_show_rate, "평균이용률": avg_util}

# 4. 요약표 함수
def make_summary(df):
    room = (
        df.groupby("회의실")
        .agg(
            예약건수=("예약ID", "count"),
            평균예약시간=("예약시간_분", "mean"),
            평균이용률=("이용률", "mean"),
            노쇼건수=("예약상태", lambda s: s.eq("노쇼").sum()),
        )
    )
    room["노쇼율"] = room["노쇼건수"] / room["예약건수"] * 100
    pivot = pd.pivot_table(df, index="요일", columns="예약시간대", values="예약ID", aggfunc="count", fill_value=0, observed=False)
    day_order = ["월", "화", "수", "목", "금", "토", "일"]
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])
    return room, pivot

# 5. 시각화 함수
def draw_charts(df, room_summary):
    room_plot = room_summary.reset_index().sort_values("평균이용률", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=room_plot, x="회의실", y="평균이용률", color="C0", ax=ax)
    ax.set_title("회의실별 평균 이용률")
    ax.set_ylabel("이용률(%)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "room_utilization.png", dpi=150, bbox_inches="tight")
    plt.show()
    time_plot = df["예약시간대"].value_counts().rename_axis("예약시간대").reset_index(name="예약건수")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=time_plot, x="예약시간대", y="예약건수", color="C0", ax=ax)
    ax.set_title("시간대별 예약 건수")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "booking_by_time.png", dpi=150, bbox_inches="tight")
    plt.show()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="예약시간대", y="예약시간_분", color="C0", ax=ax)
    ax.set_title("시간대별 예약시간 분포")
    ax.set_ylabel("예약시간(분)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "booking_duration_boxplot.png", dpi=150, bbox_inches="tight")
    plt.show()

# 6. 메인 실행
df = load_data(DATA_FILE)
clean_df = clean_data(df)
kpi = make_kpi(clean_df)
room_summary, time_pivot = make_summary(clean_df)
pp("\n[KPI]")
for key, value in kpi.items():
    if key == "전체예약":
        pp(f"{key}: {value}건")
    else:
        pp(f"{key}: {value:.1f}%")
pp("\n[회의실별 요약]\n", room_summary.round(2))
pp("\n[요일×시간대 예약 건수]\n", time_pivot)
draw_charts(clean_df, room_summary)
clean_df.to_csv(OUTPUT_DIR / "cleaned_meeting_room.csv", index=False, encoding="utf-8-sig")
room_summary.to_csv(OUTPUT_DIR / "room_summary.csv", encoding="utf-8-sig")
time_pivot.to_csv(OUTPUT_DIR / "weekday_time_pivot.csv", encoding="utf-8-sig")

# 7. 인사이트
most_booked = room_summary["예약건수"].idxmax()
low_util = room_summary["평균이용률"].idxmin()
high_no_show = room_summary["노쇼율"].idxmax()
peak_time = clean_df["예약시간대"].value_counts().idxmax()
pp("\n[인사이트]")
pp(f"1. 예약 건수가 가장 많은 회의실은 '{most_booked}'입니다.")
pp(f"2. 평균 이용률이 가장 낮은 회의실은 '{low_util}'입니다.")
pp(f"3. 노쇼율이 가장 높은 회의실은 '{high_no_show}'입니다.")
pp(f"4. 예약이 가장 많은 시간대는 '{peak_time}'입니다.")
pp("5. 낮은 이용률이나 높은 노쇼율의 원인은 EDA만으로 단정하지 않고 예약 목적·팀 규모·취소 시점 정보를 추가 확인해야 합니다.")
pp("[추가 확인사항] 예약 목적, 취소 시각, 예약자 조직/팀 규모")


