# day27_ex1.py
# Streamlit 기본 위젯

# 설치 : Alt + F 12 > pip install streamlit
# 실행 : Alt + F 12 > streamlit run ./webservice/day27/day27_ex1.py

# 포트 변경법
#1) - .streamlit 폴더 생성
#2) 생성한 폴더에 config.toml 파일 생성
#3) 생성한 파일에 아래 텍스트 입력
#   [server]
#   port=9999
#4) 서버 재실행


import streamlit as st


st.title('AI Human') # 페이지 제목
st.write('Python으로 만든 웹 UI입니다.') # 텍스트 출력
"hello streamlit!" # Magic 텍스트 출력
st.header('header') # 헤더 텍스트 출력
st.subheader('subheader') # 서브헤더 텍스트 출력
st.markdown('#대제목') # 마크다운 출력
st.markdown('##중제목')
st.markdown('###소제목')
st.success('성공')# 성공 메세지 출력
st.error('에러')# 에러 메세지 출력

# 텍스트 입력
name = st.text_input('이름',placeholder='이름을 입력하세요')
if name.strip():
    st.write(f'입력하신 이름은 "{name}"입니다.')
#숫자 입력
age = st.number_input(
    '나이',
    min_value=0, #최소값
    max_value=150, # 최대값
    value=20, # 현제값
    step=1, # 증강
)

if age > 0:
    st.write(f'입력하신 나이는 "{age}"입니다')

# 셀렉트 박스
model = st.selectbox(
    '모델',
    ['기본 모델','개선 모델']
)
if model:
    st.write(f'선택하신 모델은 "{model}" 입니다')

# 라디오
sex = st.radio(
    '성별',
    ['남성','여성']
)

if sex:
    st.write(f'선택하신 성별은 "{sex}" 입니다!')

# 체크 박스
hobby_study = st.checkbox('공부')
hobby_training = st.checkbox('운동')

if hobby_study:
    st.write(f'선택하신 취미는 "공부"입니다.')
if hobby_training:
    st.write(f'선택하신 취미는 "운동"입니다.')

# 버튼
if st.button('확인'):
    st.success('확인 버튼 누름!')

# session_state : 브라우져 탭 내에서 rerun 발생해도 값을 보존
if 'count' not in st.session_state:
    st.session_state['count'] = 0
if st.button('증가'):
    st.session_state['count'] += 1
st.write('현재 count 값:', st.session_state['count'])

# 왼쪽 사이드 바
with st.sidebar:
    st.header('사이드바 헤더')
    model = st.selectbox(
        '모델',
        ['Model A','Model B']
    )

# CSS 스타일 지정
st.markdown('''

<style>
    /* 왼쪽 컨테이너 */
    .st-key-left_box{
        border:2px solid #4A09E2;
        border-radius:12px;
        padding:20px;
        background-color:#f8fbff;
    }
     /* 오른쪽 컨테이너 */
    .st-key-right_box{
        border:2px solid #2E8B57;
        border-radius:12px;
        padding:20px;
        background-color:#f7fff9;
    }
    /* 왼쪽 컨테이너 내부 제목 */
    .st-key-left_box{
        color: #1f5990;
    }
    /* 오른쪽 컨테이너 내부 제목 */
    .st-key-right_box{
        color: #257346;
    }
</style>

''',unsafe_allow_html=True)

# 화면 컬럼 분할
left,right = st.columns([3,1])

# 왼쪽 컬럼에 위젯 추가
with left:
    # st.container : 다른 위젯들을 포함하는 위젯
    # .st-key-left_box 스타일을 적용
    with st.container(border=True,key='left_box'):
        st.write(model)
        st.subheader('입력')
        text = st.text_input('문장')



with right:
    # .st-key-left_box 스타일을 적용
    with st.container(border=True,key='right_box'):
        st.subheader('결과')

# 탭
tab1,tab2=st.tabs(['서비스','사용안내'])
with tab1:
    st.write('AI 서비스 화면')
with tab2:
    st.write('사용안내')

# 폼 리셋(초기화) 함수
def reset_form():
    st.session_state.age=0
    st.session_state.age=50

# 폼
with st.form(
    key = 'predict_form', # 폼 식별자
    clear_on_submit=True    # 폼 전송 후 폼 위젯 값 초기화
):
    age = st.number_input('나이',0,150)
    score = st.slider('점수',0,100,50)
    submitted = st.form_submit_button( # 폼 위젯 값 전송 버튼
        '예측',
        type = 'primary',
        use_container_width=True # 포함하고 있는 위젯의 넓이 만큼 넓게

    )
    reset = st.form_submit_button(
        '초기화',
        on_click=reset_form,# 클릭 이벤트 핸들러(클릭이 발생하면 실행할 함수)
        use_container_width=True
    )

if submitted: # 예측 버튼을 눌렀다면
    st.write(age,score)

enable = st.checkbox("Enable camera")
picture = st.camera_input("Take a picture", disabled=not enable)

if picture:
    st.image(picture)

# HTML 코디










































