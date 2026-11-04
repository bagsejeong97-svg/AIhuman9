# day27_basic.py
import streamlit as st

st.set_page_config(
    page_title='교육과정 상담 신청 UI',
    layout='wide'
)

st.title('교육과정 상담 신청')
name = st.text_input('이름')
sub = st.selectbox('희망 과정',
 ['Python','데이터분석','AI'])

time = st.radio('상담 희망 시간',['오전','오후','저녁'])

if st.button('신청'):
    if not name.strip():
        st.warning('warning')
    else:
        st.write('name :',name)
        st.write('과목 :',sub)
        st.write('시간: ',time)


















