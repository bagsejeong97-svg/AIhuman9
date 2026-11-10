# ============================================================
# day11_extra.py
# AI휴먼 11일차 추가 실습 풀이
# 주제: K-Drama CSV 데이터 전처리 종합 실습
# 사용 파일: kdrama_ko.csv
# ============================================================

# 표 형태의 데이터를 처리하기 위해 pandas를 pd라는 별칭으로 불러옵니다.
import pandas as pd


# ============================================================
# CSV 파일을 DataFrame으로 변환
# ============================================================

# 실습에 사용할 CSV 파일명을 지정합니다.
filename = "kdrama_ko.csv"

# UTF-8-SIG 인코딩으로 CSV 파일을 읽어 DataFrame으로 변환합니다.
df = pd.read_csv(filename, encoding="utf-8-sig")

# 정상적으로 읽혔는지 앞 5행을 출력합니다.
print("\n[원본 데이터 앞 5행]")
print(df.head())


# ============================================================
# 데이터의 전체 구조 확인
# ============================================================

# shape 속성을 이용해 전체 행 수와 열 수를 확인합니다.
print("\n[행 수와 열 수]")
print(df.shape)

# columns 속성을 리스트로 변환해 전체 컬럼명을 확인합니다.
print("\n[전체 컬럼명]")
print(df.columns.tolist())

# dtypes 속성으로 컬럼별 자료형을 확인합니다.
print("\n[컬럼별 dtype]")
print(df.dtypes)

# info()를 이용해 행 수, Non-Null 개수, dtype 등을 한 번에 확인합니다.
print("\n[DataFrame 정보]")
df.info()


# ============================================================
# 결측치 확인
# ============================================================

# isna()로 결측 여부를 확인하고 sum()으로 컬럼별 결측치 개수를 계산합니다.
missing_by_column = df.isna().sum()

# 컬럼별 결측치 개수를 출력합니다.
print("\n[컬럼별 결측치 개수]")
print(missing_by_column)

# 컬럼별 결측치 개수를 다시 합하여 전체 결측치 개수를 계산합니다.
missing_total_before = df.isna().sum().sum()

# 전체 결측치 개수를 출력합니다.
print("\n[전체 결측치 개수]")
print(missing_total_before)


# ============================================================
# 결측치가 존재하는 컬럼만 확인
# ============================================================

# 결측치 개수가 0보다 큰 컬럼만 Boolean 조건으로 선택합니다.
columns_with_missing = missing_by_column[missing_by_column > 0]

# 실제 결측치가 존재하는 컬럼만 출력합니다.
print("\n[결측치가 존재하는 컬럼]")
print(columns_with_missing)


# ============================================================
# 결측치가 포함된 행 조회
# ============================================================

# axis=1은 각 행을 기준으로 하나 이상의 True가 있는지 확인한다는 의미입니다.
missing_row_condition = df.isna().any(axis=1)

# loc를 이용해 하나 이상의 결측치가 있는 행만 선택합니다.
rows_with_missing = df.loc[missing_row_condition]

# 결측치가 포함된 행을 출력합니다.
print("\n[결측치가 포함된 행]")
print(rows_with_missing)


# ============================================================
# 평점 결측치 처리 방법 비교
# ============================================================

# 원본을 보존하기 위해 평점 결측 행을 삭제한 별도 DataFrame을 만듭니다.
rating_drop_df = df.dropna(subset=["평점"])

# 평점 컬럼의 중앙값을 계산합니다.
rating_median_for_missing = df["평점"].median()

# 원본을 복사해 평점 대체용 DataFrame을 만듭니다.
rating_fill_df = df.copy()

# 평점의 결측치를 중앙값으로 대체합니다.
rating_fill_df["평점"] = rating_fill_df["평점"].fillna(
    rating_median_for_missing
)

# 두 방식의 행 수를 비교합니다.
print("\n[평점 결측치 처리 방법 비교]")
print(f"원본 행 수: {df.shape[0]}")
print(f"결측 행 삭제 후 행 수: {rating_drop_df.shape[0]}")
print(f"중앙값 대체 후 행 수: {rating_fill_df.shape[0]}")


# ============================================================
# 중복행 확인
# ============================================================

# duplicated()는 앞에서 이미 등장한 완전 동일 행을 True로 표시합니다.
duplicate_flags = df.duplicated()

# True의 개수를 합하여 전체 중복행 개수를 계산합니다.
duplicate_count_before = duplicate_flags.sum()

# 전체 중복행 개수를 출력합니다.
print("\n[중복행 개수]")
print(duplicate_count_before)

# loc를 이용해 실제 중복된 행만 선택합니다.
duplicate_rows = df.loc[duplicate_flags]

# 중복된 행을 출력합니다.
print("\n[실제 중복행]")
print(duplicate_rows)


# ============================================================
# 중복행 제거
# ============================================================

# 원본 DataFrame을 보존하기 위해 별도 복사본을 만듭니다.
clean_df = df.copy()

# 중복 제거 이전의 행 수를 저장합니다.
rows_before_duplicate_removal = clean_df.shape[0]

# 완전히 동일한 중복행을 제거합니다.
clean_df = clean_df.drop_duplicates()

# 삭제로 인해 불연속적인 Index를 0부터 다시 정리합니다.
clean_df = clean_df.reset_index(drop=True)

# 중복 제거 이후의 행 수를 저장합니다.
rows_after_duplicate_removal = clean_df.shape[0]

# 제거 전후 행 수를 출력합니다.
print("\n[중복 제거 전후 행 수]")
print(f"제거 전: {rows_before_duplicate_removal}")
print(f"제거 후: {rows_after_duplicate_removal}")

# 중복행이 남아 있는지 다시 확인합니다.
print("\n[중복 제거 후 중복행 개수]")
print(clean_df.duplicated().sum())


# ============================================================
# 평점 이상치 탐지
# 정상 범위: 0 <= 평점 <= 10
# ============================================================

# 0보다 작거나 10보다 큰 평점을 이상치 조건으로 정의합니다.
rating_outlier_condition = (
    (clean_df["평점"] < 0)
    | (clean_df["평점"] > 10)
)

# loc를 이용해 평점 이상치가 있는 행만 선택합니다.
rating_outliers = clean_df.loc[
    rating_outlier_condition,
    ["제목", "방영연도", "평점"],
]

# 평점 이상치를 출력합니다.
print("\n[평점 이상치]")
print(rating_outliers)


# ============================================================
# 방영연도 이상치 탐지
# 정상 범위: 2000 <= 방영연도 <= 2030
# ============================================================

# 정상 범위를 벗어나는 방영연도를 이상치로 판단합니다.
year_outlier_condition = (
    (clean_df["방영연도"] < 2000)
    | (clean_df["방영연도"] > 2030)
)

# 방영연도 이상치가 있는 행만 선택합니다.
year_outliers = clean_df.loc[
    year_outlier_condition,
    ["제목", "방영연도"],
]

# 방영연도 이상치를 출력합니다.
print("\n[방영연도 이상치]")
print(year_outliers)


# ============================================================
# 회차 이상치 탐지
# 정상 범위: 1 <= 회차 <= 200
# ============================================================

# 0 이하이거나 200보다 큰 회차를 이상치로 판단합니다.
episode_outlier_condition = (
    (clean_df["회차"] <= 0)
    | (clean_df["회차"] > 200)
)

# 회차 이상치가 포함된 행을 선택합니다.
episode_outliers = clean_df.loc[
    episode_outlier_condition,
    ["제목", "회차"],
]

# 회차 이상치를 출력합니다.
print("\n[회차 이상치]")
print(episode_outliers)


# ============================================================
# 전처리 전 이상치 개수 저장
# ============================================================

# 원본 DataFrame에서 평점 이상치 개수를 계산합니다.
rating_outlier_before = (
    (df["평점"] < 0)
    | (df["평점"] > 10)
).sum()

# 원본 DataFrame에서 방영연도 이상치 개수를 계산합니다.
year_outlier_before = (
    (df["방영연도"] < 2000)
    | (df["방영연도"] > 2030)
).sum()

# 원본 DataFrame에서 회차 이상치 개수를 계산합니다.
episode_outlier_before = (
    (df["회차"] <= 0)
    | (df["회차"] > 200)
).sum()


# ============================================================
# 이상치를 결측치로 변경
# ============================================================

# 평점의 정상 범위를 벗어난 값을 pd.NA로 변경합니다.
clean_df.loc[
    (clean_df["평점"] < 0) | (clean_df["평점"] > 10),
    "평점",
] = pd.NA

# 방영연도의 정상 범위를 벗어난 값을 pd.NA로 변경합니다.
clean_df.loc[
    (clean_df["방영연도"] < 2000) | (clean_df["방영연도"] > 2030),
    "방영연도",
] = pd.NA

# 회차의 정상 범위를 벗어난 값을 pd.NA로 변경합니다.
clean_df.loc[
    (clean_df["회차"] <= 0) | (clean_df["회차"] > 200),
    "회차",
] = pd.NA


# ============================================================
# 이상치로 인해 생긴 결측치까지 중앙값으로 대체
# ============================================================

# 현재 정상 범위의 평점 데이터로 중앙값을 계산합니다.
rating_median = clean_df["평점"].median()

# 평점의 기존 결측치와 이상치로 만든 결측치를 중앙값으로 대체합니다.
clean_df["평점"] = clean_df["평점"].fillna(rating_median)

# 정상 방영연도의 중앙값을 계산합니다.
year_median = clean_df["방영연도"].median()

# 방영연도의 이상치를 중앙값으로 대체합니다.
clean_df["방영연도"] = clean_df["방영연도"].fillna(year_median)

# 정상 회차의 중앙값을 계산합니다.
episode_median = clean_df["회차"].median()

# 회차의 이상치를 중앙값으로 대체합니다.
clean_df["회차"] = clean_df["회차"].fillna(episode_median)


# ============================================================
# 나머지 문자열 컬럼의 결측치 처리
# ============================================================

# 문자열 계열 컬럼 중 이번 실습에서 결측치 대체 대상으로 사용할 컬럼을 정의합니다.
text_columns = [
    "방영일",
    "방송사",
    "방영요일",
    "시청등급",
    "장르",
    "태그",
    "감독",
    "극본",
    "출연진",
    "제작사",
]

# 지정한 문자열 컬럼의 결측치를 "정보없음"으로 한 번에 대체합니다.
clean_df[text_columns] = clean_df[text_columns].fillna("정보없음")

# 결측치 처리 후 전체 결측치 개수를 확인합니다.
print("\n[결측치 처리 후 전체 결측치]")
print(clean_df.isna().sum().sum())


# ============================================================
# 컬럼 자료형 변환
# ============================================================

# 중앙값 대체 후 방영연도를 정수형으로 변환합니다.
clean_df["방영연도"] = clean_df["방영연도"].astype("int64")

# 중앙값 대체 후 회차를 정수형으로 변환합니다.
clean_df["회차"] = clean_df["회차"].astype("int64")

# 평점을 실수형으로 명확하게 변환합니다.
clean_df["평점"] = clean_df["평점"].astype("float64")

# 순위 값에 포함된 # 문자를 제거합니다.
rank_text = clean_df["순위"].str.replace("#", "", regex=False)

# # 문자를 제거한 순위를 숫자형으로 변환합니다.
clean_df["순위"] = pd.to_numeric(rank_text, errors="coerce")

# 순위에 변환 실패 값이 있는지 확인합니다.
print("\n[순위 숫자 변환 후 결측치 개수]")
print(clean_df["순위"].isna().sum())

# 정상적으로 숫자 변환되었으므로 순위를 정수형으로 변환합니다.
clean_df["순위"] = clean_df["순위"].astype("int64")

# 제목 컬럼을 Pandas string 자료형으로 변환합니다.
clean_df["제목"] = clean_df["제목"].astype("string")

# 최종 dtype을 출력합니다.
print("\n[자료형 변환 후 dtype]")
print(clean_df.dtypes)


# ============================================================
# 이상치 처리 결과 재검사
# ============================================================

# 전처리 후 평점 이상치 개수를 계산합니다.
rating_outlier_after = (
    (clean_df["평점"] < 0)
    | (clean_df["평점"] > 10)
).sum()

# 전처리 후 방영연도 이상치 개수를 계산합니다.
year_outlier_after = (
    (clean_df["방영연도"] < 2000)
    | (clean_df["방영연도"] > 2030)
).sum()

# 전처리 후 회차 이상치 개수를 계산합니다.
episode_outlier_after = (
    (clean_df["회차"] <= 0)
    | (clean_df["회차"] > 200)
).sum()

# 이상치 재검사 결과를 출력합니다.
print("\n[이상치 처리 후 재검사]")
print(f"평점 이상치: {rating_outlier_after}")
print(f"방영연도 이상치: {year_outlier_after}")
print(f"회차 이상치: {episode_outlier_after}")


# ============================================================
# 전처리 전후 비교
# ============================================================

# 전처리 이전 전체 행 수를 저장합니다.
rows_before = df.shape[0]

# 전처리 이후 전체 행 수를 저장합니다.
rows_after = clean_df.shape[0]

# 전처리 이후 전체 결측치 개수를 계산합니다.
missing_total_after = clean_df.isna().sum().sum()

# 전처리 이후 중복행 개수를 계산합니다.
duplicate_count_after = clean_df.duplicated().sum()

# 전처리 전후 주요 데이터 품질 지표를 DataFrame으로 만듭니다.
comparison_df = pd.DataFrame(
    {
        "점검항목": [
            "행 수",
            "전체 결측치",
            "중복행 수",
            "평점 이상치",
            "방영연도 이상치",
            "회차 이상치",
        ],
        "전처리전": [
            rows_before,
            missing_total_before,
            duplicate_count_before,
            rating_outlier_before,
            year_outlier_before,
            episode_outlier_before,
        ],
        "전처리후": [
            rows_after,
            missing_total_after,
            duplicate_count_after,
            rating_outlier_after,
            year_outlier_after,
            episode_outlier_after,
        ],
    }
)

# 전처리 전후 비교표를 출력합니다.
print("\n[전처리 전후 비교표]")
print(comparison_df)


# ============================================================
# 정제 후 평점 상위 10개 드라마 확인
# ============================================================

# 필요한 컬럼만 선택한 뒤 평점을 기준으로 내림차순 정렬합니다.
top10 = clean_df[
    ["순위", "제목", "방영연도", "평점"]
].sort_values(
    by="평점",
    ascending=False,
).head(10)

# 평점 상위 10개 데이터를 출력합니다.
print("\n[정제 후 평점 상위 10개 드라마]")
print(top10)


# ============================================================
# 최종 검증
# ============================================================

# 최종 중복행 개수를 출력합니다.
print("\n[최종 중복행 개수]")
print(clean_df.duplicated().sum())

# 최종 전체 결측치 개수를 출력합니다.
print("\n[최종 전체 결측치 개수]")
print(clean_df.isna().sum().sum())

# 평점의 최솟값과 최댓값을 출력합니다.
print("\n[최종 평점 범위]")
print(clean_df["평점"].min(), "~", clean_df["평점"].max())

# 방영연도의 최솟값과 최댓값을 출력합니다.
print("\n[최종 방영연도 범위]")
print(clean_df["방영연도"].min(), "~", clean_df["방영연도"].max())

# 회차의 최솟값과 최댓값을 출력합니다.
print("\n[최종 회차 범위]")
print(clean_df["회차"].min(), "~", clean_df["회차"].max())


# ============================================================
# 정제된 CSV 파일 저장
# ============================================================

# 정제된 데이터를 저장할 파일명을 지정합니다.
output_filename = "kdrama_clean.csv"

# Index를 제외하고 UTF-8-SIG 형식으로 CSV 파일을 저장합니다.
clean_df.to_csv(
    output_filename,
    index=False,
    encoding="utf-8-sig",
)

# 저장 완료 메시지를 출력합니다.
print("\n[저장 완료]")
print(output_filename)
