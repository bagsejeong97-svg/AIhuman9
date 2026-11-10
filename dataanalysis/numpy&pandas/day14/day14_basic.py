# day14_basic.py
# 주제:
from util.print_util import pp

pp()
from pathlib import Path
import platform
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    '월': ['1월', '2월', '3월', '4월', '5월', '6월'],
'소설': [120, 135, 128, 150, 164, 172],
'IT': [80, 95, 110, 118, 125, 140],
'경제': [65, 72, 78, 85, 92, 98]})


df['월별대출건수']= df['소설'] + df['IT'] + df['경제']
# pp(df[['월','월별대출건수']])

if platform.system() == "Windows":  # 윈도우즈라면 : 나눔고딕
    plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 폰트 맑은고딕 설정
output_dir = Path('day14_output')
output_dir.mkdir(exist_ok=True)


# 월별 전체 대출건수 선그래프
fig, ax = plt.subplots(figsize=(10,10))
ax.plot(
    df['월'],
    df['월별대출건수'],
    label = '월별 전체 대출 건수',
    linewidth=2,
)
ax.set_title('월별 전체 대출 건수')
ax.set_xlabel('월별')
ax.set_ylabel('총 대출 건수')
ax.legend()
fig.tight_layout()
fig.savefig(output_dir / 'day14_basic.png',dpi=150,bbox_inches='tight')
# plt.show()

# 막대 그래프
num = df[['소설','IT','경제']].sum()
pp(num)

fig, ax = plt.subplots(figsize=(8,5))

bars = ax.bar(
    num.index,
    num.values,
)
ax.set_title('장르별 총대출 건 수')
ax.set_xlabel('장르')
ax.set_ylabel('대출건수')
ax.bar_label(
    bars
)
fig.tight_layout()
fig.savefig(output_dir / 'day14_basic_bar.png',dpi=150,bbox_inches='tight')
plt.show()

# 선 그래프는 시간이 지날수로 대출건수가 증가하는것을 알수있고 막대 그래프는 장르마다 대출건수를 한번에 볼수 있다





















