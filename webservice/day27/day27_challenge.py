import streamlit as st

# 채용 적합도 분석 UI
st.set_page_config(
    page_title='채용 적합도 분석',
    layout='wide'
)

# 입력값을 점수화하여 판정 결과와 총점을 반환하는 함수
def analyze(python_score, project_count, has_portfolio):
    python_part = python_score * 0.6
    project_part = min(project_count * 0.4, 20)
    portfolio_part = 20 if has_portfolio else 0
    total = python_part + project_part + portfolio_part
    label = '적합' if total >= 70 else '보완 필요'
    return label, total

if 'job_result' not in st.session_state:
    st.session_state.job_result = None

st.title('채용 적합도 분석 서비스')

with st.sidebar:
    job = st.selectbox(
        '지원 직무',
        ['Python 개발', '데이터 분석', 'AI 개발']
    )

left, right = st.columns(2)

with left:
    st.subheader('지원 정보 입력')
    with st.form('job_form'):
        python_score = st.slider(
            'Python 점수',
            min_value=0,
            max_value=100,
            value=60
        )
        project_count = st.number_input(
            '프로젝트 수',
            min_value=0,
            max_value=20,
            value=1,
            step=1
        )
        has_portfolio = st.checkbox(
            '포트폴리오 보유'
        )
        submitted = st.form_submit_button('분석')

    if submitted:
        label, total = analyze(python_score, project_count, has_portfolio)
        st.session_state.job_result = {
            '직무': job,
            '판정': label,
            '총점': round(total, 1),
            'Python': python_score,
            '프로젝트': project_count,
            '포트폴리오': has_portfolio
        }

with right:
    st.subheader('분석결과')
    # 수정: in None -> is None
    if st.session_state.job_result is None:
        st.info('지원 정보를 입력하고 분석 버튼을 누르세요.')
    else:
        result = st.session_state.job_result
        # 수정: f-string 내부에 큰따옴표/작은따옴표 구분
        if result['판정'] == '적합':
            st.success(f"판정: {result['판정']}")
        else:
            st.warning(f"판정: {result['판정']}")
        st.metric('총점', result['총점'])
        st.write('지원 직무:', result['직무'])
        st.write('마지막 입력값:', result)