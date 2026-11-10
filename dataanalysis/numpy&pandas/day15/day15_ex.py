# day15_ex.py
# 주제:
from util.print_util import pp
# EDA 미니프로젝트 : 고객 문의 데이터
pp()
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import platform

# 경로 \  # CSV경로

BASE_DIR = Path(__file__).parent # 현재 경로의 상위 경로
DATA_FILE = BASE_DIR / 'assets' / 'day15_ex_data.csv' # CSV 파일 경로
OUTPUT_DIR = Path(__file__).with_name('day15_ouput') # 결과 파일 저장 디렉토리
OUTPUT_DIR.mkdir(exist_ok=True)
# 그래프 기본설정
sns.set_theme(style="whitegrid")

# 폰트 한국어 설정
if platform.system() == "Windows":  # 윈도우즈라면 : 나눔고딕
    plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 폰트 맑은고딕 설정
elif os_name == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
elif os_name == 'Linux':
    plt.rcParams['font.family'] = 'NanumGothic'

# 원시 데이터 불러오기
df = pd.read_csv(DATA_FILE,encoding='utf-8-sig')
pp(df.shape)
df.info()


clean_df = df.copy()

text_cols = ['문의ID','접수일','채널','문의유형','담당팀','처리상태']


for col in text_cols:
    clean_df[col] = clean_df[col].astype('string').str.strip()

clean_df['채널'] = clean_df['채널'].replace(
    {
        'email' : '이메일',
        'E-mail': '이메일',
        'chat' : '채팅',
        '전화상담' : '전화'
    }
)

clean_df["문의유형"] = clean_df["문의유형"].replace(
    {
        "배송문의": "배송",
        "결재": "결제",
        "환불요청": "환불"
    }
)

clean_df["처리상태"] = clean_df["처리상태"].replace(
    {
        "처리완료": "완료",
        "closed": "완료",
        "processing": "진행중"
    }
)

pp('[표준화된 채널',sorted(clean_df['채널'].dropna().unique()))
pp('[표준화된 문의유형]',sorted(clean_df['문의유형'].dropna().unique()))

# 날짜형, 수치형 변환
clean_df['접수일'] = pd.to_datetime(clean_df['접수일'], errors='coerce')
clean_df['처리시간_분']= pd.to_numeric(clean_df['처리시간_분'], errors='coerce')
clean_df['만족도']= pd.to_numeric(clean_df['만족도'], errors='coerce')

# 중복과 유효 범위 정리

before_rows = len(clean_df)

clean_df = clean_df.drop_duplicates(subset='문의ID', keep='last')

invalid_time = clean_df['처리시간_분'].le(0)# le(0) : 0보다 작거나 같다

invalid_score = ~clean_df['만족도'].between(1,5)& clean_df['만족도'].notna()

clean_df.loc[invalid_time,'처리시간_분'] = pd.NA
clean_df.loc[invalid_score,'만족도'] = pd.NA

pp('[중복/필수값 처리 후 제거 행]',before_rows - len(clean_df))

# 결측치 대체
median_time = clean_df['처리시간_분'].median()
median_score = clean_df['만족도'].median()

clean_df['처리시간-분']=clean_df['처리시간_분'].fillna(median_time)
clean_df['만족도']=clean_df['만족도'].fillna(median_score)
clean_df['담당팀']=clean_df['담당팀'].fillna('미확인')

pp('[정제 후 결측치]',clean_df.isna().sum())


# 파생변수 생성
clean_df['접수월']=clean_df['접수일'].dt.to_period('M').astype(str)
clean_df['처리지연']=clean_df['처리시간_분'].ge(60) # ge(60) : 60보다 크거나 같음

# KPI 계산

total_inquiries = len(clean_df)
completed_rate = clean_df['처리상태'].eq('완료').mean()*100
avg_time = clean_df['처리시간_분'].mean()
avg_score = clean_df['만족도'].mean()
pp('[KPI]')
pp(f'총 문의 건수: {total_inquiries}건')
pp(f'처리 완료율: {completed_rate:.1f}%')
pp(f'평균 처리시간: {avg_time:.1f}분')
pp(f'평균 만족도: {avg_score:.2f}점')

# 문의 유형벌 집계
summary = (
    clean_df.groupby('문의유형')
    .agg(
        문의건수 = ('문의ID','count'),
        평균처리시간 = ('처리시간_분','mean'),
        평균만족도 = ('만족도','mean'),
        지연건수= ('처리지연',sum)
    )
    .sort_values('문의건수',ascending=False)
)

summary['지연율']= summary['지연건수']/summary['문의건수']*100

pp('{문의유형별 요약}')
pp(summary.round(2))


# 채널별 집계
channel_summary = (
    clean_df['채널']
    .value_counts()
    .rename_axis('채널')
    .reset_index(name='문의건수')
)
pp('[채널별 문의 건수]')
pp(channel_summary)

# 문의 유형별 건수 시각화
count_plot = summary.reset_index()

fig,ax = plt.subplots(figsize=(9,5))
sns.barplot(
    data = count_plot,
    x = '문의유형',
    y = '문의건수',
    color = 'C0',
    ax = ax
)
ax.set_title('문의유형별 문의 건수')
ax.set_xlabel('문의유형')
ax.set_ylabel('건수')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'inquiry_count_by_type.png',
            dpi=150,bbox_inches='tight')
plt.show()

# 문의 유형별 평균 처리시간 시각화

time_plot = summary.reset_index().sort_values('평균처리시간',ascending=False)

fig,ax = plt.subplots(figsize=(9,5))

sns.barplot(
    data = time_plot,
    x = '문의유형',
    y = '평균처리시간',
    color = 'C0',
    ax = ax
)

ax.set_title('문의유형별 평균 처리시간')
ax.set_xlabel('문의유형')
ax.set_ylabel('분')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'avg_handling_time_by_type.png',dpi=150,bbox_inches='tight')

plt.show()

# 분석 결과 저장
clean_df.to_csv(OUTPUT_DIR / 'day15_cleaned.csv', index=False,encoding='utf-8-sig')


summary.to_csv(OUTPUT_DIR / 'day15_summary.csv', index=False,encoding='utf-8-sig')



# 인사이트 5줄 출력
top_type = summary['문의건수'].idxmax() # 최대값 인덱스
slow_type = summary['평균처리시간'].idxmax()
low_score_type = summary['평균만족도'].idxmin() # 최소값 인덱스

top_channel = channel_summary.iloc[0]['채널']

pp('[인사이트]')
pp(f'1. 가장 많은 문의 유형{top_type}')
pp(f'2.평균 처리시간이 가장 긴 문의유형은 {slow_type}')
pp(f'3.평균 만족도가 가장 낮은 문의 유형은  {low_score_type}')
pp(f'4.문의가 가장 많이 유입된 채널은   {top_channel}')
pp(f'5. 처리시간과 만족도의 원인 관계는 단정하지 않고 세부 처리 단계 데이터를 추가 확인해야함')







































