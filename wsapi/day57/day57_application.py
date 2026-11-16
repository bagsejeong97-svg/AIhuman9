# day57_application.py
# 주제:
import hashlib

from fastapi import FastAPI, UploadFile, File, HTTPException



MAX_SIZE = 1024 * 1024 * 2 # 2


app = FastAPI(
    title = '온라인 쇼핑몰 상품 이미지 메타데이터 검사 API',
    description='이미지를 이용하여 추론 검사',
    version='0.0.1',
)

@app.post("/images/inspect")
async def inspect_image(file: UploadFile = File(...)):

    try:
        filename = file.filename
        extension = filename.split(".")[-1].lower()

        content = await file.read(MAX_SIZE + 1)

        if len(content) > MAX_SIZE:
            raise HTTPException(
                413, '파일 크기 초과'
            )

        if content.startswith(b"\x89PNG\r\n\x1a\n"): # png파일 시작 형식
            if extension != 'png':
                raise HTTPException(
                    415, 'png 파일이 아닙니다.'
                )
        elif content.startswith(b"\xff\xd8\xff"): # jpeg 파일 시작 형식
            if extension not in ['jpg', 'jpeg']:
                raise HTTPException(
                    415, "[jpg,jpeg]파일이 아닙니다."
                )
        else:
            raise HTTPException(
                415, '정해진 형식의 파일이 아닙니다.'
            )
        sha256 = hashlib.sha256(content).hexdigest()
        return {
            'filename': filename,
            'extension': extension,
            'content': len(content),
            'sha256': sha256
        }
    finally:
        await file.close()







































