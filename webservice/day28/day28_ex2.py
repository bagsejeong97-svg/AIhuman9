
# 마우스로 숫자를 그려서 MNIST CNN 모델로 예측하는 streamlit UI

# pip install streamlit_drawable_canvas pillow

from pathlib import Path
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image #이미지 처리
from streamlit_drawable_canvas import st_canvas # 그림그리기 영역


#__file__ : 현제 실행중인 파이썬의 경로
# resolve() : 상대 경로 > 절대 경로
BASE_DIR = Path(__file__).resolve().parent

# 모델 파일 경로
MODEL_PATH = BASE_DIR / 'mnist_cnn.keras'

# 파일 업로드 디렉토리
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) # 없으면 생성

st.set_page_config(
    page_title='손글씨 숫자 인식', #브라우저 탭에 표시되는 제목
    page_icon='✍️', # 브라우저 탭에 표시되는 아이콘
    layout='centered', # 중앙 배치
)

# CNN 모델 불러오기
# rerun 회수와 관계 없이 자원을 한번만 캐시에 저장
@st.cache_resource
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

# Canvas 이미지를 MNIST 형태로 전처리

# 사용자가 Canvas에 그린 이미지를 CNN 모델이 사용할 수 있는 형태로 변환하는 함수
def preprocess_canvas(canvas_image):
    # 배열로 부터 이미지 생성
    image = Image.fromarray(
         canvas_image.astype('uint8'), # 1바이트 부호 없는 정수로 변환
         mode = 'RGBA' # R:Red, G:Green, B:Blue, A:Alpha(투명도)
     )
    image = image.convert('L') # RGBA 컬러 이미지 > 8비트 흑백 이미지

     # 이미지에서 실제 픽셀이 존재하는 영역의 경계 상자(Bounding Box)
    bbox = image.getbbox()

    if bbox is None: #경계 상자 없음 = 아무것도 안 그림
         return None,None

     # 이미지에서 경계 상자 영역만 잘라냄
    image = image.crop(bbox)

     # 잘라낸 경계 상자 넓이와 높이
    width, height = image.size

     # 넓이와 높이 중 최대값을 구함 : 정사각형으로 만들기 위해
    side = max(width, height)

    square = Image.new( # 이미지 생성
         'L', # 8비트 흑백 이미지
         (side, side), # 넓이와 높이를 동일하게 정사각형으로
         color=0 # 배경색상
    )

     # 숫자를 정사각형의 가로/세로 중앙에 배치하기 위한 계산
    left = (side - width) // 2
    top = (side - height) // 2

     # 계산한 경계 상자 중앙에 이미지를 붙여넣기
    square.paste(
         image,
         (left, top)
    )

    # 경계 상자 크기를 20X20으로 리사이징 : MNIST 는 28X28 전체 크기에서 20X20 영역에 숫자가 있음
    digit = square.resize(
        (20,20),
        Image.Resampling.LANCZOS # 이미지 축소 시 품질을 높이기 위한 보간 방식
    )

    # MNIST와 동일한 28X28 크기의 검은색 배경 이미지를 생성
    mnist_image = Image.new(
        'L',
        (28,28),
        color=0
    )

    # 왼쪽4, 오른쪽4 픽셀 위치에 숫자를 붙임
    mnist_image.paste(
        digit,
        (4,4)
    )

    # 이미지를 넘파이 배열로 변환
    array = np.array(
        mnist_image, # 변환할 이미지
        dtype = np.float32 # TensorFlow 에서 사용할 실수타입
    ) / 255.0 # 0~255 > 0.0 ~ 1.0

    # 넘파이 배열이 (28,28) 이므로 모델에 부여하기 위해 모양 변경
    batch = array.reshape(1,28,28,1)

    return batch,mnist_image # 모델 입력 데이터, 이미지 반환


## UI

st.title('손글씨 숫자 인식')
st.write('아래 검은 화면에 마우스로 **0~9 숫자 하나**를 크게 작성해 보세요!')

if not MODEL_PATH.exists():
    st.error(f'모델 파일 없습니다: {MODEL_PATH}')
    st.stop()

# CNN 모델 로드
try:
    model = load_model()
except Exception as error:
    st.error(f'모델 로드 오류: {error}')
    st.stop()

st.success('MNIST 숫자 인식 모델을 불러왔습니다')

# 숫자를 그릴 Canvas 생성
canvas = st_canvas(
    fill_color='rgba(255,255,255,1)',
    stroke_width=18, # 마우스로 그리는 선의 두꼐
    stroke_color='#FFFFFF', # 선색상 (흰색)
    background_color='#000000', # 배경 색상(검은색)
    width=280, #가로크기
    height=280, #세로크기
    drawing_mode='freedraw', # 자유그리기 모드
    return_image_data=True, #Canvas로 그린 결과를 image_data 속성으로 가져올 수 있도록 설정
    key='digit_canvas' # 위젯 식별자
)

# 파일 업로드 / 다운로드

st.divider() #구분선

st.subheader('업로드 파일 다운로드')

st.write('파일을 업로드하면 업로드한 파일을''**다운로드 버튼을 통해 다시 내려받을 수 있습니다.**')

upload_file = st.file_uploader(
    '다운로드할 파일을 업로드하세요.',
    key='download_file_uploader'
)

if upload_file is not None: #업로드 된경우

    safe_file_name = Path(upload_file.name).name # 업로드한 파일명
    save_path = UPLOAD_DIR / safe_file_name # 실제 저장할 전체 경로
    upload_data = upload_file.getvalue() # 업로드된 파일의 bytes

    with open(save_path, 'wb') as file: # binary 쓰기 모드
        file.write(upload_data) # 파일로 저장

    st.success('파일이 서버에 저장되었습니다.')

    # 업로드된 파일 정보 표시
    st.write(f'파일명: {safe_file_name}')
    st.write(f'파일크기: {upload_file.size:,}bytes')
    st.write(f'파일형식: {upload_file.type}')
    st.write(f'저장경로: {save_path}')

    # 실제 저장된 파일을 다운로드를 위해서 바이너리 모드로 읽음
    with open(save_path, 'rb') as file:
        saved_file_data = file.read()

    # 다운로드 버튼
    st.download_button(
        label = '저장된 파일 다운로드',
        data = saved_file_data,
        file_name = safe_file_name,
        mime = upload_file.type or 'application/octet-stream',
        use_container_width = True
    )

if st.button('숫자 인식', type='primary',use_container_width=True):
    if canvas.image_data is None: # Canvas에 이미지 데이터가 없다면
        st.warning('먼저 숫자를 작성하세요!')
    else:
        batch,preview = preprocess_canvas(canvas.image_data)
        if batch is None: #전처리 결과가 없다면
            st.warning('먼저 숫자를 작성하세요.')
        else:
            # 모델 예측
            # 모델에 입력할 이미지를 가지고 모델 예측
            probabilities = model.predict(batch,verbose=0)[0]
            # 가장 높은 확률값을 가지고 있는 배열의 인덱스
            predicted = int(np.argmax(probabilities))
            # 예측된 숫자의 확률값
            confidence = float(probabilities[predicted])

            st.divider()


            left,right = st.columns([1,2])

            with left:
                st.subheader('모델 입력')
                st.image(
                    preview.resize((140,140)), # 28X28이미지는 작으므로 140X140으로 확대
                    caption = '28X28 변환 이미지' # 이미지 설명
                )

            with right:
                st.subheader('인식 결과')
                st.metric('예측 숫자',predicted)
                st.metric('예측 확률',f'{confidence*100:.2f}%')


        # 숫자별 예측 확률 그래프

        st.subheader('숫자별 예측 확률')

        # 숫자오 숫자별 예측 확률 디셔너리
        chart_data = {
            str(number):
                float(probability) for number, probability in enumerate(probabilities)
        }

        st.bar_chart(chart_data)























































































