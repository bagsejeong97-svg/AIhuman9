# day15_basic.py
# 주제:



from util.print_util import pp

import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import platform

# 그래프 기본설정
sns.set_theme(style="whitegrid")

if platform.system().lower() == "windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기본 폰트: 맑은 고딕

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

BASE_DIR = Path(__file__).parent # 현재 경로의 상위 경로
DATA_FILE = BASE_DIR / 'assets' / 'day15_basic_data.csv' # CSV 파일 경로
OUTPUT_DIR = Path(__file__).with_name('day15_basic') # 결과 파일 저장 디렉토리
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE,encoding='utf-8-sig')
pp(df.shape)
pp(df.dtypes)
pp(df.isna().sum())
pp(df.duplicated().sum())

df['장르']= df['장르'].str.strip()
df['대출상태'] = df['대출상태'].str.strip()

df['장르'] = df['장르'].replace({
    'fiction' : '소설'
})

df['대출상태'] = df['대출상태'].replace({
    '반납완료' : '반납'
})


df['대출일'] = pd.to_datetime(df['대출일'], errors='coerce')
df = df.dropna(subset=['대출일'])
pp(df['대출일'])


df['대출일수'] = pd.to_numeric(df['대출일수'],errors='coerce')

median_day = df['대출일수'].median()
df['대출일수'] = df['대출일수'].fillna(median_day)
pp(df['대출일수'])

df = df.drop_duplicates(
    subset= ['대출ID'],
    keep = 'last',
)
pp(df['대출ID'])

# 총대출건수
total_count = len(df)
# 평균 대출 일수
avg_day = df['대출일수'].mean()
#반납완료율
complete = df['대출상태'].eq('반납').mean()*100
pp(f'총대출건수: {total_count}건')
pp(f'평균 대출 일 수: {avg_day:.0f}일')
pp(f'반납완료율: {complete:.1f}%')

# 장르별 대출건수
genres = (
    df.groupby('장르')
    .agg(
        장르별대출건수 = ('장르','count'),
        평균대출일수 = ('대출일수','mean')
    )
)
#genres 내에 생긴 평균대출일수에 소수점 부분 삭제
genres['평균대출일수'] = genres['평균대출일수'].astype(int)
pp(genres)

# 장르별 대출건수 막대그래프
genres_plot =genres.reset_index().sort_values('장르별대출건수',ascending=False)
fig,ax = plt.subplots(figsize=(10,10))

sns.barplot(
    data=genres_plot,
    x = '장르',
    y = '장르별대출건수',
    ax=ax
)
ax.set_title('장르별대출건수')
ax.set_xlabel('장르')
ax.set_ylabel('건수')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'day15_basic_bar.png',dpi=150,bbox_inches='tight')
plt.show()


# genres_avg = genres.reset_index().sort_values('평균대출일수,ascending',ascending=False)
fig,ax = plt.subplots(figsize=(10,10))

sns.histplot(
    df['대출일수'],
    bins=10,
    alpha = 0.5,
    kde = True
)
ax.set_title('대출일수')
ax.set_xlabel('대출일수')
ax.set_ylabel('빈도')
fig.tight_layout()
fig.savefig(OUTPUT_DIR/'day15_basic_hist.png',dpi=150,bbox_inches='tight')
plt.show()

genres_avg = genres.reset_index().sort_values('평균대출일수',ascending=False).iloc[0]['장르']
pp('[인사이트]')
pp('가장 많이 대출한 장르:',genres['장르별대출건수'].idxmax())
pp('평균대출일수가 가장 많은 장르:',genres_avg)
pp(f'총대출건수:{total_count} \n평균대출일수는: {avg_day:.0f}\n반납완료율: {complete:.1f}%')













