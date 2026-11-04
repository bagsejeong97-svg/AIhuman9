# day14_ex1.py
# 주제: Matplotlib , Seaborn을 활용한 데이터 시각화, EDA
from util.print_util import pp

# 라이브러리 설치 : pip install matplotlib seaborn
pp()
from pathlib import Path
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 그래프 기본 설정
sns.set_theme(style="whitegrid")  # 흰 배경에 격자선 표시하는 테마

if platform.system() == "Windows":  # 윈도우즈라면 : 나눔고딕
    plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 폰트 맑은고딕 설정
elif os_name == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
elif os_name == 'Linux':
    plt.rcParams['font.family'] = 'NanumGothic'


plt.rcParams['axes.unicode_minus'] = False # 음수기호 (-) 깨짐 방지 설정

# 그래프 이미지 저장 경로
output_dir = Path('day14_output')
output_dir.mkdir(exist_ok=True)

# 실습용 데이터 생성
months = ['1월','2월','3월','4월','5월','6월','7월','8월']
channels = ['검색','SNS','이메일']
records = [] # 각 행 데이터를 딕셔너리로 저장할 리스트

for month_no, month in enumerate(months,start=1): # 1부터 시작
    for channel_no, channel in enumerate(channels): # 0부터 시작
        ad_cost = 90 + month_no*12 + channel_no*18 # 광고비 생성
        visitors = 3000 + month_no*230 + channel_no*420 # 방문자수 생성
        order_value = 42 + month_no*1.8 + channel_no*3.5 # 평균 주문금액 생성
        sales = 220 + month_no * 31 + channel_no * 38 + ad_cost * 0.55 # 매출 생성
        records.append({
            '월' : month,
            '채널' : channel,
            '광고비' : round(ad_cost,1),
            '방문자수' : visitors,
            '주문금액': round(order_value,1),
            '매출' : round(sales,1),

        })

# 데이터프레임 생성
df = pd.DataFrame(records)
# pp(df)
# df.info()
# 숫자타입 컬럼만 선택해서 기초통계량을 소수점 두쨰 자리까지 반올림해서 출력
pp(df.select_dtypes(include='number').describe().round(2))

# 월별 전체 매출 선그래프

# 월별 매출 합계
monthly_sales = (
    df.groupby('월', sort=False, as_index=False)
['매출'].sum()
)
# pp(monthly_sales)

# 그래프크기가 9인치 x 5인치, figure, axes 획득
# fig, ax = plt.subplots(figsize=(9,5))
# ax.plot(# 선그래프
#     monthly_sales['월'], #x축
#     monthly_sales['매출'], #y축
#     marker='o',  #그래프에 o표시
#     linewidth=2,
#     label='월별 총매출'  # 범례에 표실될 이름
# )
# ax.set_title('월별 매출 추세') # 그래프 제목
# ax.set_xlabel('월') # x축 제목
# ax.set_ylabel('매출') # y축 제목
# ax.legend()# 범례표시
# ax.grid(alpha=0.3) #격자선 투명도
# fig.tight_layout() # 그래프 내위 요소들이 겹치지 않게 설ㅈ정
# fig.savefig(  #그래프를 이미지로 저장
#     output_dir/'monthly_sales_line.png', # 이미지 파일 경로
#     dpi=150, # 이미지 해상도
#     bbox_inches='tight' # 그래프 바깥쪽 불필요한 여백 제거
# )
# plt.show() #화면에 그래프 출력

## 채널별 총매출 막대 그래프

# channel_sales=(
#     df.groupby('채널', as_index=False)['매출'].sum()
#     .sort_values('매출', ascending=False)
# )
#
# fig, ax = plt.subplots(figsize=(8,5))
#
# bars = ax.bar(
#     channel_sales['채널'],
#     channel_sales['매출']
# )
# ax.set_title('채널별 총매출 비교')
# ax.set_xlabel('채널')
# ax.set_ylabel('총매출')
# ax.bar_label( #각 막대의 레이블
#     bars, # 막대그래프 객체
#     fmt = '%.0f' # 레이블 형식 : 소수점 없이 출력
# )
# fig.tight_layout()
# fig.savefig(output_dir/'channel_sales.bar.png', dpi=150, bbox_inches='tight')
# plt.show()
#

# 주문금액 히스토그램
# fig, ax = plt.subplots(figsize=(8,5))
#
# ax.hist(
#     df['주문금액'], # 데이터 Series
#     bins = 8, # 구간수
#     edgecolor = 'black', # 막대 테두리 색상
#     alpha = 0.8 # 막대 투명도
# )
#
# ax.set_title('주문금액 분포')
# ax.set_xlabel('주문금액')
# ax.set_ylabel('빈도')
# fig.tight_layout()
# fig.savefig(output_dir/'order_value_hist.png',dpi=150,bbox_inches='tight')
# plt.show()

# 광고비와 매출 산점도
# fig,ax = plt.subplots(figsize=(8,5))
#
# ax.scatter(
#     df['광고비'], # x축 시리즈
#     df['매출'], # y축 시리즈
#     s = 70, # 마커 크기
#     alpha = 0.7 #마커 투명도
# )
# ax.set_title('광고비와 매출의 관계')
# ax.set_xlabel('광고비')
# ax.set_ylabel('매출')
# ax.grid(alpha=0.2)
# fig.tight_layout()
# fig.savefig(output_dir/'ad_sales_scatter.png',dpi=150,bbox_inches='tight')
# plt.show()

# seaborn : 채널별 월별 매출 추세 선그래프

# fig,ax = plt.subplots(figsize=(9,5))
#
# sns.lineplot(
#     data = df, # 데이터프레임
#     x = '월', #x축 컬럼
#     y = '매출', #y출 컬럼
#     hue = '채널', # 색상 구분 컬럼
#     markers = 'o', # 데이터에 원형 표시
#     errorbar=None, # 신뢰구간 표시 안함
#     ax = ax # 그래프를 출력할 axis 설정
# )
# ax.set_title('채널별 월별 매출 추세')
# ax.set_xlabel('월')
# ax.set_ylabel('매출')
# fig.tight_layout()
# fig.savefig(output_dir/'seaborn_ling.png', dpi=150,bbox_inches='tight')
# plt.show()


# seaborn : 채널별 평균 매출 막대그래프

# fig,ax = plt.subplots(figsize=(8,5))
#
# sns.barplot(
#     data = df, # 데이터프레임
#     x = '채널', #x축 컬럼
#     y = '매출', #y출 컬럼
#     estimator = 'mean', # 평균 값을 막대 높이로 사용
#     errorbar = None, # 오차 막대 제거
#     # color = default_color, #모든 막대를 동일한 색상으로 설정
#     ax = ax
# )
# ax.set_title('채널별 평균 먀출')
# ax.set_xlabel('채널')
# ax.set_ylabel('평균 매출')
# fig.tight_layout()
# fig.savefig(output_dir/'seaborn_bar.png', dpi=150,bbox_inches='tight')
# plt.show()

# seaborn : 주문금액 분포 히스토 그램

# fig,ax = plt.subplots(figsize=(9,5))
#
# sns.histplot(
#     data = df, # 데이터프레임
#     x = '주문금액', #x축 컬럼
#     bins = 8,
#     kde = True, #KDE 곡선 표시
#     ax = ax
# )
# ax.set_title('주문금액 분포')
# ax.set_xlabel('주문금액')
# ax.set_ylabel('빈도')
# fig.tight_layout()
# fig.savefig(output_dir/'seaborn_hist.png', dpi=150,bbox_inches='tight')
# plt.show()
#

# seaborn : 광고비와 매출 관계 산점도

# fig,ax = plt.subplots(figsize=(8,5))
#
# sns.scatterplot(
#     data = df, # 데이터프레임
#     x = '광고비',
#     y = '매출',
#     hue = '채널',
#     s = 90,  # 점의 크기
#     alpha = 0.5,  # 점의 투명도
#     ax = ax
#
# )
# ax.set_title('채널별 광고비와 매출의 관계')
# ax.set_xlabel('광고비')
# ax.set_ylabel('매출')
# fig.tight_layout()
# fig.savefig(output_dir/'seaborn_scatter.png', dpi=150,bbox_inches='tight')
# plt.show()

# seaborn : 채널별 매출 박스 그래프

# fig,ax = plt.subplots(figsize=(8,5))
#
# sns.boxplot(
#     data = df, # 데이터프레임
#     x = '채널',
#     y = '매출',
#     width = 0.6, # 박스의 폭
#     showfliers=True,  # 이상치 (outlier)를 표시
#     ax = ax
#
# )
# ax.set_title('채널별 매출 분포')
# ax.set_xlabel('채널')
# ax.set_ylabel('매출')
# fig.tight_layout()
# fig.savefig(output_dir/'seaborn_box.png', dpi=150,bbox_inches='tight')
# plt.show()

# 채널별 총맥출 파이그래프
# 채널별 매출 합계
# channel_sales_pie = df.groupby('채널')['매출'].sum()
#
# fig, ax = plt.subplots(figsize=(7,7))
#
# ax.pie(
#     channel_sales_pie.values, # 파이 조각의 크기에 사용할 총매출 값
#     labels = channel_sales_pie.index, # 각 조각에 표시할 채널명
#     autopct = '%.1f%%', #각조각의 비율을 소수점 한자리까지 표시
#     startangle= 90,  # 첫번째 조각을 90도 위치에서 시작
#     counterclock=False, # 시게방향으로 조각 배치
#     pctdistance = 0.7, # 비율 텍스트를 중심에서 70% 위치에 표시
#     labeldistance = 1.05 # 라벨을 중심에서 105% 위치에 유지
# )
# ax.set_title('채널별 총매출 비율')
# ax.axis('equal') # 원이 타원으로 찌그러지지 않도록 종횡비를 동일하게 설정
# fig.tight_layout()
# fig.savefig(output_dir/'channel_sales_pie.png', dpi=150,bbox_inches='tight')
# plt.show()

# 2 x 2 EDA 대시보드 (그래프 4개를 한 화면에 표시)

fig,axes = plt.subplots(
    2,  #행수
    2,  #열수
    figsize=(13,9)
)

sns.lineplot(
    data = df,
    x = '월',
    y = '매출',

)
sns.lineplot(
    data=df,                              # 사용할 DataFrame
    x="월",                               # X축 : 월
    y="매출",                             # Y축 : 매출
    hue="채널",                           # 채널별 색상 구분
    marker="o",                           # 원형 마커 표시
    errorbar=None,                        # 신뢰구간 제거
    ax=axes[0, 0]                         # 첫 번째 위치에 그래프 출력
)
axes[0, 0].set_title("채널별 월별 매출")  # 첫 번째 그래프 제목
sns.barplot(
    data=df,                              # 사용할 DataFrame
    x="채널",                             # X축 : 채널
    y="매출",                             # Y축 : 매출
    estimator="mean",                     # 평균값 계산
    errorbar=None,                        # 오차막대 제거
    ax=axes[0, 1]                         # 오른쪽 위 위치
)
axes[0, 1].set_title("채널별 평균 매출")  # 두 번째 그래프 제목
sns.histplot(
    data=df,                              # 사용할 DataFrame
    x="주문금액",                         # 대상 변수
    bins=8,                               # 구간 개수
    kde=True,                             # 밀도 곡선 표시
    ax=axes[1, 0]                         # 왼쪽 아래 위치
)
axes[1, 0].set_title("주문금액 분포")     # 세 번째 그래프 제목
sns.scatterplot(
    data=df,                              # 사용할 DataFrame
    x="광고비",                           # X축 : 광고비
    y="매출",                             # Y축 : 매출
    hue="채널",                           # 채널별 색상 구분
    s=70,                                 # 점 크기
    ax=axes[1, 1]                         # 오른쪽 아래 위치
)
axes[1, 1].set_title("광고비와 매출")     # 네 번째 그래프 제목
fig.suptitle(
    "온라인 마케팅 성과 EDA",             # 전체 Figure 제목
    fontsize=16                           # 전체 제목 글자 크기
)
fig.tight_layout()                        # subplot 간 겹침 방지
fig.savefig(
    output_dir / "eda_dashboard.png",
    dpi=150,                              # 저장 이미지 해상도
    bbox_inches="tight"                   # 바깥 여백 최소화
)
plt.show()                               # 대시보드 출력








































































