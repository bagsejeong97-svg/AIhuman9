import datetime
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="스마트 가계부",
    page_icon="💰",
    layout="wide"
)

# --- 기본 스타일 및 이모지 카테고리 설정 ---
CATEGORY_EMOJI = {
    "🍔 식비": "🍔 식비",
    "🚌 교통": "🚌 교통",
    "🛍️ 쇼핑": "🛍️ 쇼핑",
    "🏠 주거/통신": "🏠 주거/통신",
    "🎬 취미/유흥": "🎬 취미/유흥",
    "💡 기타": "💡 기타"
}

# Session State 초기화
if "vils" not in st.session_state:
    st.session_state.vils = pd.DataFrame(columns=["날짜", "년도", "월", "항목명", "분류", "금액", "메모"])

st.title("💰 스마트 개인 지출 관리")

# --- 사이드바: 필터 & 백업 ---
st.sidebar.header("🗓️ 기간 선택 및 설정")
now = datetime.datetime.now()

selected_year = st.sidebar.selectbox("년도", range(2020, 2031), index=now.year - 2020)
selected_month = st.sidebar.selectbox("월", range(1, 13), index=now.month - 1)

st.sidebar.markdown("---")
st.sidebar.subheader("📦 데이터 백업")

if not st.session_state.vils.empty:
    csv = st.session_state.vils.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        label="📥 CSV 내보내기",
        data=csv,
        file_name=f"지출내역_{now.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

uploaded_file = st.sidebar.file_uploader("📤 CSV 불러오기", type=["csv"])
if uploaded_file is not None:
    try:
        df_up = pd.read_csv(uploaded_file)
        df_up['날짜'] = pd.to_datetime(df_up['날짜']).dt.date
        st.session_state.vils = df_up
        st.sidebar.success("데이터 불러오기 완료!")
    except Exception:
        st.sidebar.error("파일 형식 오류")

# --- 메인 탭 ---
tab1, tab2, tab3 = st.tabs(["⚡ 빠른 입력", "📊 분석 대시보드", "📝 내역 수정/삭제"])

# ----------------------------------------------------
# TAB 1: 입력 편의성 극대화 (빠른 입력 폼)
# ----------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📝 일반 입력")
        with st.form("detail_input_form", clear_on_submit=True):
            input_date = st.date_input("결제 날짜", datetime.date.today())
            item = st.text_input("항목명", placeholder="예: 점심 식사, 버스비")
            sub = st.selectbox("분류", list(CATEGORY_EMOJI.keys()))
            price = st.number_input("금액(원)", min_value=0, step=1000, value=0)
            memo = st.text_input("메모 (선택)", placeholder="결제 수단, 장소 등")

            submitted = st.form_submit_button("➕ 저장하기", type="primary", use_container_width=True)

            if submitted:
                if not item.strip():
                    st.warning("항목명을 입력해 주세요.")
                elif price <= 0:
                    st.warning("금액을 입력해 주세요.")
                else:
                    new_row = pd.DataFrame([{
                        "날짜": input_date,
                        "년도": input_date.year,
                        "월": input_date.month,
                        "항목명": item,
                        "분류": sub,
                        "금액": price,
                        "메모": memo
                    }])
                    st.session_state.vils = pd.concat([st.session_state.vils, new_row], ignore_index=True)
                    st.success(f"✅ 추가됨: {item} ({price:,}원)")

    with col_right:
        st.subheader("⚡ 텍스트 한 줄 빠른 입력")
        st.caption("공백으로 구분해 입력하세요 예) `식비 12000 점심식사` 또는 `교통 1500`")

        with st.form("quick_input_form", clear_on_submit=True):
            quick_text = st.text_input("한 줄 입력", placeholder="분류 금액 항목명 (예: 식비 15000 커피와디저트)")
            quick_submitted = st.form_submit_button("🚀 빠른 추가", use_container_width=True)

            if quick_submitted and quick_text.strip():
                parts = quick_text.strip().split(maxsplit=2)

                # 파싱 로직
                cat_found = "💡 기타"
                p_val = 0
                item_val = "지출"

                for part in parts:
                    if part.isdigit():
                        p_val = int(part)
                    else:
                        matched = False
                        for cat in CATEGORY_EMOJI.keys():
                            if part in cat:
                                cat_found = cat
                                matched = True
                                break
                        if not matched:
                            item_val = part

                if p_val > 0:
                    today = datetime.date.today()
                    new_row = pd.DataFrame([{
                        "날짜": today,
                        "년도": today.year,
                        "월": today.month,
                        "항목명": item_val,
                        "분류": cat_found,
                        "금액": p_val,
                        "메모": "빠른입력"
                    }])
                    st.session_state.vils = pd.concat([st.session_state.vils, new_row], ignore_index=True)
                    st.success(f"⚡ 빠른 추가 완료: [{cat_found}] {item_val} - {p_val:,}원")
                else:
                    st.error("금액(숫자)을 올바르게 포함해서 입력해 주세요.")

# ----------------------------------------------------
# TAB 2: 디자인 강화된 요약 및 차트 대시보드
# ----------------------------------------------------
with tab2:
    df = st.session_state.vils

    if not df.empty:
        # 필터링
        year_df = df[df["년도"] == selected_year]
        month_df = year_df[year_df["월"] == selected_month]

        st.subheader(f"📌 {selected_year}년 {selected_month}월 지출 대시보드")

        total_month = month_df["금액"].sum()
        count_month = len(month_df)
        daily_avg = int(total_month / 30) if total_month > 0 else 0
        max_item = month_df.loc[month_df["금액"].idxmax()]["항목명"] if not month_df.empty else "-"

        # 핵심 지표 카드 배치
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💳 이번 달 총지출", f"{total_month:,} 원")
        c2.metric("📅 하루 평균 (30일 기준)", f"{daily_avg:,} 원")
        c3.metric("🔢 총 결제 건수", f"{count_month} 건")
        c4.metric("🔥 가장 큰 지출", max_item)

        st.markdown("---")

        if not month_df.empty:
            ch1, ch2 = st.columns(2)

            with ch1:
                st.markdown("### 📊 카테고리별 지출 비율")
                cat_sum = month_df.groupby("분류")["금액"].sum().reset_index()
                st.bar_chart(cat_sum, x="분류", y="금액")

            with ch2:
                st.markdown("### 📈 일별 지출 추이")
                daily_sum = month_df.groupby("날짜")["금액"].sum().reset_index()
                st.line_chart(daily_sum, x="날짜", y="금액")
        else:
            st.info("해당 월의 등록된 지출 내역이 없습니다.")
    else:
        st.info("등록된 지출 내역이 없습니다. 첫 지출을 등록해 보세요!")

# ----------------------------------------------------
# TAB 3: 전체 내역 관리 (st.data_editor 활용)
# ----------------------------------------------------
with tab3:
    st.subheader("📋 전체 내역 조회 및 편집")

    if not st.session_state.vils.empty:
        st.caption("💡 셀을 직접 더블클릭하여 수정하거나, 행을 선택 후 Delete 키로 삭제할 수 있습니다.")

        edited_df = st.data_editor(
            st.session_state.vils,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "금액": st.column_config.NumberColumn("금액(원)", format="%d 원"),
                "분류": st.column_config.SelectboxColumn("분류", options=list(CATEGORY_EMOJI.keys()))
            }
        )

        st.session_state.vils = edited_df

        st.markdown("---")
        if st.button("🗑️ 전체 데이터 초기화", type="primary"):
            st.session_state.vils = pd.DataFrame(columns=["날짜", "년도", "월", "항목명", "분류", "금액", "메모"])
            st.rerun()
    else:
        st.info("관리할 지출 내역이 없습니다.")