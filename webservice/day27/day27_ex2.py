# day27_ex2.py
# Streamlit 위젯 실습

import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="AI Human", # 제목
    page_icon='😎', # 아이콘
    layout='wide' # 페이지 레이아웃
)

# AI모델 예측결과 반환한다고 가정한 함수
def simple_predict(age,score,model_name):
    bonus = 5 if model_name == '개선 모델' else 0
    result_score = min(score + bonus,100)
    if age < 20:
        result_score= min(result_score-5,0)
    label = '높음' if result_score >= 70 else '보통'
    return label,result_score

# session_state에 있는지 확인 하고 속성 변수 초기화
if 'predict_count' not in st.session_state:
    st.session_state.predict_count = 0
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

st.title('AI Human 웹서비스')
st.write('Streamlit Widget과 Session State를 활용한 기본 웹 UI')

# Sidebar
with st.sidebar:
    st.header('서비스 설정')
    model_name = st.selectbox(
        '사용 모델',
        ['기본 모델','개선 모델'],
        help='selectbox()는 목록 중 하나의 값을 반환함'
    )
    show_help = st.checkbox(
        '사용 안내 표시',
        value=True # 체크된 상태로 로딩
    )

# Tab
service_tab,flow_tab = st.tabs(
    ['에측 서비스','실행 구조']
)

# Tab 중에서 service_tab
with service_tab:
    input_col,result_col = st.columns(2) # 컬럼 분할
    with input_col:
        st.subheader('입력')
        with st.form('predict_form'):
            name = st.text_input(
                '이름',
                placeholder='이름을 입력하세요.'
            )
            age = st.number_input(
                '나이',
                min_value=0,
                max_value=150,
                value=25,
                step=1
            )
            score = st.slider(
                '입력 점수',
                min_value=0,
                max_value=100,
                value=50,
                step=1
            )
            submitted = st.form_submit_button('결과 확인')

    with result_col:
        st.subheader('결과')
        if submitted: # 결과 확인 버튼이 클릭 되면
            # 가상의 AI모델 예측 결과를 가져옴
            label,result_score = simple_predict(age,score,model_name)
            # 세션 속성변수 값 설정
            st.session_state.predict_count += 1
            st.session_state.last_result = {
                'name': name,
                'label': label,
                'score': score,
                'model': model_name
            }

        if st.session_state.last_result is not None:
            result = st.session_state.last_result
            st.success(f'판정 결과:{result['label']}')
            st.metric('결과 점수 :',result['score'])
            st.write('이름',result['name'])
            st.write('사용모델',result['model'])
            st.write('실행회수:',st.session_state.predict_count)
        else:
            st.info('입력값을 작성한 후 결과 확인을 누르세요')

# Tab 중에서  flow_tab
with flow_tab:
    st.subheader('웹브라우져와 Streamlit의 실행 흐름')
    st.markdown('''
    **Browser (Client)**
    -> HTTP 요청
    -> **Streamlit Server**
    -> Python 코드 실행
    -> 화면 생성
    -> **Browser**
    
    Widget 값이 변경되면 Streamlit 스크립트가
    위에서 아래로 다시 실행됨
    ''')

if show_help:
    st.info(
        'Sidebar에서 모델을 선택하고 입력값을 작성한 뒤'
        '결과 확인 버튼을 눌러보세요'
    )






































