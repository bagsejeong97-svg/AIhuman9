# Perso AI API 문서

최종 업데이트: 2026-10-22. 변경 이력: https://developers.perso.ai/docs/changelog

API 기본 URL: https://api.perso.ai
서비스/파일 URL: https://portal-media.perso.ai
인증: 모든 요청에 `XP-API-KEY` 헤더를 포함합니다.
API 키 형식: pk_live_xxxxxxxxxxxxxxxxxxxx

예시:
```
curl -X GET https://api.perso.ai/video-translator/api/v1/languages \
  -H "XP-API-KEY: pk_live_xxxxxxxxxxxxxxxxxxxx"
```

---

## 핵심 준수 사항 (코드 작성 전 필독)

아래 항목은 가장 자주 발생하는 연동 실패 원인입니다. 기본적으로 모두 준수하세요.

1. **인증 헤더는 `Authorization: Bearer`가 아닌 `XP-API-KEY`입니다.**
   - 일부 공개 Community Spotlight 엔드포인트(추천 목록/상세, 공유 프로젝트)를 제외하고 https://api.perso.ai로 보내는 모든 요청에 `XP-API-KEY: <your-key>`를 포함해야 합니다.
   - 이 API는 Bearer JWT 인증을 사용하지 않습니다.

2. **`spaceSeq`를 이용해 다중 작업 공간을 구분합니다.**
   - 대부분의 도메인 엔드포인트는 요청 본문 또는 쿼리에 `spaceSeq`(작업 공간 ID)가 필요합니다.
   - `spaceSeq` 누락은 빈 목록이나 404의 대표 원인입니다. 확실하지 않다면 명시적으로 전달하세요.
   - `GET /portal/api/v1/spaces`(Space API)에서 `spaceSeq`를 조회합니다.
   - 작업 공간이 여러 개라면 `memberRole`과 `serviceType`을 확인하여 권한이 있는 공간을 선택합니다.
     예: `space_owner`, 더빙 서비스의 `"video_translator"`.
     접근 권한이 없는 공간을 사용하면 403이 반환됩니다.

3. **파일 업로드는 단일 호출이 아닌 3단계 과정입니다.**
   더빙/STT/립싱크 요청에 파일 바이너리를 직접 첨부하지 마세요. 먼저 아래 절차로 `mediaSeq`를 발급받습니다:
   ```
   1단계: GET /file/api/upload/sas-token?fileName=<URL 인코딩된 파일명>
                -> { blobSasUrl }          (유효기간 30분)
   2단계: PUT {blobSasUrl}             (https://api.perso.ai가 아닌 Azure Blob으로 직접 업로드)
                Headers: x-ms-blob-type: BlockBlob
                본문: 원본 파일 바이트
                반환된 blobSasUrl을 그대로 사용합니다. 호스트를 고정하지 마세요.
                호스트는 portal-media.perso.ai가 아닌 perso-saas-file-frontdoor.perso.ai일 수 있습니다.
                이 단계는 SAS 서명으로 인증하므로 XP-API-KEY가 필요하지 않습니다.
                성공 시 201, 403이면 SAS 만료이므로 1단계부터 다시 수행합니다.
   3단계: PUT /file/api/upload/video   (오디오는 /audio)
                본문: { "fileUrl": "<blobSasUrl>", ... }
                -> { "seq": <숫자> }    // 이후 API 호출에서 mediaSeq로 사용
                fileUrl의 `?...` 쿼리 문자열은 제거하는 것을 권장합니다.
                쿼리를 포함해도 등록되지만 제거하면 저장 경로가 안정적입니다.
   ```
   YouTube/TikTok/Drive URL은 `external/metadata` → `media/validate` → `upload/video/external` 외부 업로드 흐름을 사용합니다.

4. **장시간 작업은 프로젝트 ID를 발급하므로 상태를 폴링해야 합니다.**
   - 더빙·STT·오디오 분리·립싱크는 작업을 생성한 후 즉시 응답합니다.
     응답 예시: `{ "result": { "startGenerateProjectIdList": [101] } }`. ID가 여러 개일 수 있으며
     대상 언어별로 발급된 모든 ID의 진행률을 각각 조회해야 합니다.
   - 진행률 조회 경로: `GET /video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/progress`
     (`space`는 단수이며 `spaceSeq`가 필요합니다). 최소 5초 간격으로 조회하세요.
   - 상태는 `status`가 아니라 `progressReason`에 들어 있습니다. 상태값:
     `Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating |
     Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed`.
     `progressReason === "Completed"`이면 완료, `"Failed"`이면 실패입니다(`hasFailed` 참조).
   - `expectedRemainingTimeMinutes`는 참고용 추정치이며, 완료 후 음수가 될 수도 있습니다.
   - HTTP 핸들러 내부에서 폴링 반복문으로 요청을 막지 마세요. 백그라운드 워커/큐를 사용하세요.

5. **응답 파일 경로는 API 기본 도메인이 아닌 `https://portal-media.perso.ai`를 사용합니다.**
   - `videoFilePath`, `audioFilePath`, `thumbnailFilePath`, 다운로드 링크, `audioUrl`,
     `thumbnailUrl` 등의 필드는 `/perso-storage/...` 아래 상대 경로를 포함합니다.
   - 파일을 받을 때 `https://api.perso.ai`가 아닌 `https://portal-media.perso.ai`를 앞에 붙입니다.
   - 경로에 공백이나 비ASCII 문자가 원형 그대로 포함될 수 있으므로 URL 인코딩해야 합니다.
     인코딩하지 않으면 파일 요청이 실패할 수 있습니다.

6. **HTTP 오류 코드는 아래 규칙을 따릅니다.**
   - 401: `XP-API-KEY`가 없거나 오타가 있거나 만료·폐기된 키입니다.
   - 403: 키는 유효하지만 해당 Space에 대한 권한이 없습니다.
   - 404: 대개 `spaceSeq` 또는 리소스 ID가 잘못되었습니다. 경로 오류로 판단하기 전에 ID를 확인하세요.
   - 429: 요청 한도 초과입니다. 지수 백오프를 적용하세요.
   - 5xx: 백오프 후 재시도하고, 문의할 때 Usage 로그의 Request ID를 포함하세요.

   오류 응답 본문의 형태가 여러 가지이므로 방어적으로 파싱하세요.
   - 게이트웨이 인증 오류(라우팅 전 처리되므로 개별 엔드포인트에서 401이 직접 관측되는 경우는 드뭅니다):
     키 누락: `{"code":"G0001","message":"...","status":"UNAUTHORIZED"}`;
     키 무효·만료: `{"code":"A0010","message":"...","status":"UNAUTHORIZED"}`.
   - 도메인 오류 예: `{"code":"VT4009","detailCode":"UNSUPPORTED_LANGUAGE_TTS_MODEL_PAIR","message":"...","status":"BAD_REQUEST"}`.
     기계 판독용 필드는 `errorCode`가 아닌 `code`이고, `detailCode`는 상세 사유를 구별합니다.
   - 필수 파라미터 누락(RFC 7807): `{"type":"about:blank","title":"Bad Request","status":400,"detail":"Required parameter 'memberRole' is not present.",...}`.
   - 일부 서버 오류는 Spring 기본 형식으로 반환됩니다: `{"timestamp":"...","status":500,"error":"...","path":"..."}`.

7. **SAS 토큰의 `fileName`은 URL 인코딩이 필수입니다.** 공백·한국어/일본어·괄호 등을 인코딩하세요.

---


## Space API — 작업 공간
작업 공간의 배너 정보를 조회합니다.

### GET /portal/api/v1/spaces
**작업 공간 목록 조회**
인증 사용자가 속한 모든 작업 공간의 배너 목록을 반환합니다.

응답 (200):
```json
{
  "result": [
    {
      "spaceSeq": 1,
      "spaceName": "My Workspace",
      "planName": "Pro",
      "tier": "team",
      "logo": "https://...",
      "memberCount": 5,
      "seat": 10,
      "isDefaultSpaceOwned": true,
      "memberRole": "space_owner",
      "useVideoTranslatorEdit": true,
      "useStudioEdit": false,
      "serviceType": "video_translator",
      "originSpaceSeq": 1
    }
  ]
}
```

오류:
  - 404 PT0026: 작업 공간 구독 정보가 없습니다

---

### GET /portal/api/v1/spaces/{spaceSeq}
**작업 공간 정보 조회**
특정 작업 공간의 배너 정보를 조회합니다.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "spaceSeq": 1,
    "spaceName": "My Workspace",
    "planName": "Pro",
    "tier": "team",
    "logo": "https://...",
    "memberCount": 5,
    "seat": 10,
    "isDefaultSpaceOwned": true,
    "memberRole": "space_owner",
    "useVideoTranslatorEdit": true,
    "useStudioEdit": false,
    "serviceType": "video_translator",
    "originSpaceSeq": 1
  }
}
```

오류:
  - 404 PT0026: 작업 공간 구독 정보가 없습니다
  - 401 PT0027: 승인된 구성원이 아닙니다

---

## Media API — 미디어 관리
영상·오디오 업로드, 검증, 외부 미디어 가져오기 및 프로젝트 산출물 다운로드를 관리합니다.

### 직접 파일 업로드 (영상 / 오디오)

파일 업로드는 임시 SAS 토큰 발급 → Azure Blob에 바이너리 업로드 → 서버 등록 순서로 진행합니다.

**1단계: SAS 토큰 발급** [GET] 인증: XP-API-KEY
`/file/api/upload/sas-token?fileName={fileName}`
SAS 토큰 발급 API에서 `blobSasUrl`을 가져옵니다. 토큰 유효기간은 30분입니다.
> `fileName`은 URL 인코딩해야 합니다.

**2단계: Azure Blob Storage에 바이너리 업로드** [PUT] 인증: 없음
`{blobSasUrl}`
SAS URL 자체에 인증 정보가 있으므로 Authorization 헤더 없이 해당 주소로 바이너리를 PUT 업로드합니다. Perso API 서버가 아닌 Azure로 직접 전송합니다.
필수 헤더:
  x-ms-blob-type: BlockBlob
  Content-Type: application/octet-stream
```
curl -X PUT \
  -H "x-ms-blob-type: BlockBlob" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"/path/to/file.mp4" \
  "{blobSasUrl}"
```
> 성공하면 본문이 없는 HTTP 201을 반환합니다. 403이면 SAS가 만료된 것이므로 토큰을 다시 발급받으세요.

**3단계: 업로드 파일 등록** [PUT] 인증: XP-API-KEY
`/file/api/upload/video (or /audio)`
Upload Video/Audio API를 호출하여 파일을 등록합니다. `fileUrl`에는 `blobSasUrl`을 전달합니다. `?...` 쿼리 부분을 제거하는 것이 권장되며, 제거하지 않아도 등록은 가능하지만 저장 경로 안정성이 좋아집니다.
> 응답의 `seq`가 미디어 식별자이며, 이후 더빙 요청에서 `mediaSeq`로 사용합니다.

**4단계: 미디어 유효성 검사 (선택)** [POST] 인증: XP-API-KEY
`/file/api/v1/media/validate`
파일 전송 전에 확장자, 크기, 길이, 해상도 제약을 검사합니다. 선택 단계지만 긴 업로드 후 실패하는 것을 방지하려면 권장합니다.
> 2단계 전에 호출하면 잘못된 파일의 업로드를 피할 수 있습니다.

### 외부 플랫폼 업로드 (YouTube, TikTok, Google Drive)

외부 플랫폼 영상을 서버가 대신 다운로드하여 가져옵니다.

**1단계: 외부 미디어 메타데이터 조회** [POST] 인증: XP-API-KEY
`/file/api/v1/video-translator/external/metadata`
업로드 전에 미디어 길이·해상도·크기를 확인합니다.

**2단계: 미디어 유효성 검사** [POST] 인증: XP-API-KEY
`/file/api/v1/media/validate`
요금제에서 허용하는 크기·길이·해상도 제한을 검사합니다.
> 검증은 보통 1~2초 걸립니다. 생략하면 잘못된 파일에서 10초 이상 기다린 후 오류가 발생할 수 있습니다.

**3단계: 외부 영상 업로드** [PUT] 인증: XP-API-KEY
`/file/api/upload/video/external`
외부 영상 가져오기를 시작합니다. 서버 다운로드가 끝나야 응답하는 동기 작업으로 최대 10분 걸릴 수 있습니다.
> 응답의 `seq`는 이후 더빙 API에서 `mediaSeq`로 사용합니다.

### PUT /file/api/upload/video
**영상 업로드 등록**
URL로 영상 파일을 업로드 등록합니다. 먼저 SAS 토큰을 발급받고, 반환된 `blobSasUrl`에 파일을 올려야 합니다. 그 URL을 `fileUrl`로 전달합니다. 응답의 `seq`는 번역 요청의 `mediaSeq`로 사용합니다. `videoFilePath`와 `thumbnailFilePath`는 perso-storage 상대 경로이므로 https://portal-media.perso.ai 를 앞에 붙입니다. 응답 `originalName`에서는 파일 확장자가 제거됩니다.

요청 본문:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.
  - fileUrl (문자열, 필수): 영상 파일에 직접 접근할 수 있는 URL입니다(SAS 토큰 단계에서 받은 `blobSasUrl`). 안정적인 저장 경로를 위해 `?...` 쿼리 문자열을 제거하는 것을 권장하지만, 포함해도 등록할 수 있습니다.
  - fileName (문자열, 필수): 파일 이름입니다. URL 인코딩된 이름은 자동으로 디코딩됩니다.
  - sttMode (불리언, 선택): STT 프로젝트에 사용할 파일이면 true로 지정합니다. 유료 플랜에서는 길이 제한이 2시간으로 늘어나며 기본값은 false입니다.

요청 예시:
```json
{
  "spaceSeq": 1,
  "fileUrl": "https://example.com/video.mp4",
  "fileName": "my_video.mp4",
  "sttMode": false
}
```

응답 (200):
```json
{
  "seq": 456,
  "originalName": "my_video",
  "videoFilePath": "/container/directory/uuid_20260219.mp4",
  "thumbnailFilePath": "/container/directory/uuid_20260219.webp",
  "size": 52428800,
  "durationMs": 30000
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 400 F4004: 파일 크기 제한 초과
  - 400 F4007: 지원하지 않는 영상 유형
  - 401 F4001: 인증 실패

---

### PUT /file/api/upload/audio
**오디오 업로드 등록**
URL로 오디오 파일을 업로드 등록합니다. 사전에 SAS 토큰 발급 및 `blobSasUrl` 업로드가 필요합니다. Blob URL을 `fileUrl`로 전달합니다. 응답 `seq`는 `mediaSeq`입니다. `audioFilePath`와 `thumbnailFilePath`는 perso-storage 상대 경로이며, https://portal-media.perso.ai 를 앞에 붙여 접근합니다. `originalName`에는 확장자가 포함되지 않습니다.

요청 본문:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.
  - fileUrl (문자열, 필수): 오디오 파일에 직접 접근할 수 있는 URL입니다(`blobSasUrl`). 안정적인 저장 경로를 위해 `?...` 쿼리 문자열을 제거하는 것을 권장하지만, 포함해도 등록할 수 있습니다.
  - fileName (문자열, 필수): 파일 이름입니다. URL 인코딩된 이름은 자동으로 디코딩됩니다.
  - sttMode (불리언, 선택): STT 프로젝트에 사용할 파일이면 true로 지정합니다. 유료 플랜에서는 길이 제한이 2시간으로 늘어나며 기본값은 false입니다.

요청 예시:
```json
{
  "spaceSeq": 1,
  "fileUrl": "https://portal-media.perso.ai/perso-storage/...",
  "fileName": "my_audio.mp3",
  "sttMode": false
}
```

응답 (200):
```json
{
  "seq": 789,
  "originalName": "my_audio",
  "audioFilePath": "/container/directory/uuid_20260219.mp3",
  "thumbnailFilePath": "audio_thumb.png",
  "size": 5242880,
  "durationMs": 180000
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 400 F4004: 파일 크기 제한 초과
  - 400 F4007: 지원하지 않는 오디오 유형
  - 401 F4001: 인증 실패

---

### PUT /file/api/upload/video/external
**외부 영상 업로드**
YouTube·TikTok·Google Drive 등의 외부 영상을 가져옵니다. 서버가 다운로드를 마칠 때까지 대기하는 동기 작업이며 최대 10분 걸릴 수 있습니다. `videoFilePath`·`audioFilePath`·`thumbnailFilePath`는 perso-storage 상대 경로이므로 https://portal-media.perso.ai 를 앞에 붙입니다.

요청 본문:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.
  - url (문자열, 필수): 외부 영상 URL입니다(YouTube, TikTok, Google Drive).
  - lang (문자열, 선택): 언어 코드입니다(기본값: en).
  - sttMode (불리언, 선택): STT 프로젝트에 사용할 파일이면 true로 지정합니다. 유료 플랜에서는 길이 제한이 2시간으로 늘어나며 기본값은 false입니다.

요청 예시:
```json
{
  "spaceSeq": 1,
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "lang": "ko",
  "sttMode": false
}
```

응답 (200):
```json
{
  "seq": 456,
  "originalName": "Video Title",
  "videoFilePath": "/container/directory/uuid_20260219.mp4",
  "thumbnailFilePath": "/container/directory/uuid_20260219.webp",
  "size": 52428800,
  "durationMs": 30000
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 400 F4006: 유효하지 않은 외부 링크
  - 400 F40012: 지역에서 이용할 수 없는 외부 영상
  - 400 F40014: 회원 전용 콘텐츠
  - 400 F40015: 결제가 필요한 콘텐츠
  - 400 F40016: 유효하지 않은 YouTube URL
  - 401 F4001: 인증 실패
  - 403 F4031: 접근할 수 없는 Google Drive 링크
  - 403 F4032: 지역 제한 YouTube 영상
  - 403 F4033: 연령 제한 YouTube 영상
  - 403 F4035: 접근할 수 없는 외부 미디어 링크

---

### GET /file/api/upload/sas-token
**SAS 토큰 발급**
직접 업로드용 Azure Blob SAS 토큰을 발급합니다. 30분간 유효하므로 만료 전에 `blobSasUrl`에 PUT 업로드한 후 파일 등록 API를 호출하세요. 반환된 SAS URL의 호스트를 변경하지 마세요. `expirationDatetime`은 시간대 접미사가 없는 UTC 시각이므로 로컬 시각과 직접 비교하지 말고 발급 후 30분 이내에 업로드하세요.

쿼리 파라미터:
  - fileName (문자열, 필수): 파일 이름입니다(URL 인코딩 필요).

응답 (200):
```json
{
  "blobSasUrl": "https://perso-saas-file-frontdoor.perso.ai/perso-storage/{path}/uuid_20260720.mp4?sv=2024-11-04&se=2026-02-19T13%3A00%3A00Z&sr=b&sp=rw&sig=...",
  "expirationDatetime": "2026-02-19T13:00:00"
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 401 F4001: 인증 실패

---

### POST /file/api/v1/media/validate
**미디어 유효성 검사**
미디어 데이터를 실제 전송하지 않고 확장자·크기·길이·해상도를 사전 검사합니다.

요청 본문:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.
  - durationMs (정수, 필수): 미디어 길이(밀리초)입니다.
  - originalName (문자열, 필수): 원본 파일 이름입니다.
  - mediaType (문자열, 필수): 미디어 파일 유형입니다. [video, audio]
  - extension (문자열, 필수): 파일 확장자입니다. [.mp4, .webm, .mov, .mp3, .wav]
  - size (정수, 선택): 파일 크기(바이트)이며 최대 2GB입니다.
  - width (정수, 선택): 영상 가로 해상도(픽셀)입니다. mediaType이 video라면 필수이며 201~7999입니다.
  - height (정수, 선택): 영상 세로 해상도(픽셀)입니다. mediaType이 video라면 필수이며 201~7999입니다.
  - thumbnailFilePath (문자열, 선택): 썸네일 파일 경로입니다.
  - sttMode (불리언, 선택): STT 프로젝트에 사용할 파일이면 true로 지정합니다. 유료 플랜에서는 길이 제한이 2시간으로 늘어나며 기본값은 false입니다.

요청 예시:
```json
{
  "spaceSeq": 1,
  "durationMs": 30000,
  "originalName": "video.mp4",
  "mediaType": "video",
  "extension": ".mp4",
  "size": 52428800,
  "width": 1920,
  "height": 1080,
  "thumbnailFilePath": null,
  "sttMode": false
}
```

응답 (200):
```json
{
  "status": true
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 400 F4004: 파일 크기 제한 초과
  - 400 F4007: 지원하지 않는 영상/오디오 유형
  - 400 F4008: 영상 길이 제한 초과
  - 400 F4009: 영상이 너무 짧음(최소 1초)
  - 400 F40010: 영상 해상도 제한 초과
  - 400 F40011: 영상 해상도가 너무 낮음
  - 401 F4001: 인증 실패
  - 403 F4005: 요금제 사용량 제한 초과
  - 422 F4220: 유효성 검증 실패

---

### POST /file/api/v1/video-translator/external/metadata
**외부 미디어 메타데이터 조회**
외부 플랫폼(YouTube·TikTok·Google Drive)의 미디어를 내려받지 않고 메타데이터를 조회합니다. 업로드 전 정보를 확인하는 용도입니다.

요청 본문:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.
  - url (문자열, 필수): 외부 영상 URL입니다(YouTube, TikTok, Google Drive).
  - lang (문자열, 선택): 언어 코드입니다(기본값: en).
  - sttMode (불리언, 선택): STT 프로젝트에 사용할 파일이면 true로 지정합니다. 유료 플랜에서는 길이 제한이 2시간으로 늘어나며 기본값은 false입니다.

요청 예시:
```json
{
  "spaceSeq": 1,
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "lang": "ko",
  "sttMode": false
}
```

응답 (200):
```json
{
  "durationMs": 215000,
  "originalName": "Video Title",
  "thumbnailFilePath": "https://i.ytimg.com/vi/xxxxx/maxresdefault.jpg",
  "mediaType": "video",
  "size": 52428800,
  "extension": ".mp4",
  "width": 1920,
  "height": 1080
}
```

오류:
  - 400 F4003: 필수 파라미터가 없습니다
  - 400 F4006: 유효하지 않은 외부 링크
  - 400 F40016: 유효하지 않은 YouTube URL
  - 400 F40017: 유효하지 않은 미디어 URL
  - 401 F4001: 인증 실패
  - 403 F4031: 접근할 수 없는 Google Drive 링크
  - 403 F4035: 접근할 수 없는 외부 미디어 링크

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/download-info
**다운로드 가능 파일 확인**
프로젝트에서 현재 다운로드 가능한 파일을 확인합니다. 각 필드는 가능 여부를 true/false로 나타내며 프로젝트 종류에 따라 null일 수도 있습니다. true로 반환된 항목에 해당하는 `target` 값으로 다운로드를 요청하세요.

download-info의 불리언 필드와 다운로드 target 값의 대응 관계:
- hasTranslatedVideo -> target=dubbingVideo
- hasLipSyncVideo -> target=lipSyncVideo
- hasOriginalVoiceOnly -> target=originalVoiceAudio (원본 음성 트랙)
- hasTranslatedVoice -> target=voiceAudio (번역 음성: 오디오 분리 프로젝트 등 번역 음성이 없으면 500이 반환될 수 있음)
- hasOriginalBackground / hasTranslatedBackground -> target=backgroundAudio
- hasOriginalSpeakerAudioCollection -> target=originalVoiceSpeakers
- hasSpeakerSegmentExcel -> target=speakerSegmentExcel
- hasSpeakerSegmentWithTranslationExcel -> target=speakerSegmentWithTranslationExcel
- hasScriptTimestamps -> target=scriptTimestamps
- hasOriginalSubBackground -> target=originalSubBackground
- hasZipDownload -> target=all (.tar 아카이브)
- hasOriginalSubtitle / hasTranslatedSubtitle / hasOriginalSubtitleVtt -> 개별 target 없음; SRT/VTT는 target=all 아카이브에만 포함

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "hasPreviousProjectVideo": true,
  "hasTranslatedVideo": true,
  "hasLipSyncVideo": false,
  "hasOriginalSubtitle": true,
  "hasTranslatedSubtitle": true,
  "hasOriginalVoiceOnly": true,
  "hasTranslatedVoice": true,
  "hasOriginalBackground": true,
  "hasTranslatedBackground": true,
  "hasZipDownload": true,
  "hasOriginalSpeakerAudioCollection": false,
  "hasSpeakerSegmentExcel": true,
  "hasSpeakerSegmentWithTranslationExcel": true,
  "hasScriptTimestamps": true,
  "hasOriginalSubtitleVtt": true,
  "hasOriginalSubBackground": false
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/download
**파일 다운로드**
프로젝트 결과 파일을 다운로드합니다. 먼저 download-info로 사용 가능한 파일을 확인하고 적절한 `target`을 전달하세요. 반환 링크는 `/perso-storage/...` 상대 경로이므로 https://portal-media.perso.ai 를 앞에 붙이고, 공백·비ASCII 문자는 URL 인코딩하세요. `zippedFileDownloadLink`는 `.tar` 아카이브입니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - target (문자열, 필수): 다운로드할 파일 종류입니다. 먼저 download-info에서 사용 가능 여부를 확인하고 해당 target을 전달합니다. 대소문자는 구분하지 않습니다. 알 수 없는 값은 400 VT4001, 유효하지만 해당 프로젝트에 없는 파일은 500이 반환될 수 있습니다. [dubbingVideo, lipSyncVideo, audioScript, originalVoiceAudio, voiceAudio, backgroundAudio, voicewithBackgroundAudio, translatedAudio, all, originalVoiceSpeakers, speakerSegmentExcel, speakerSegmentWithTranslationExcel, scriptTimestamps, originalSubBackground]

응답 (200):
```json
{
  "result": {
    "videoFile": {
      "videoDownloadLink": "/perso-storage/.../dubbing_video.mp4"
    },
    "audioFile": {
      "voiceAudioDownloadLink": "/perso-storage/.../voice.wav",
      "backgroundAudioDownloadLink": "/perso-storage/.../background.wav",
      "voiceWithBackgroundAudioDownloadLink": "/perso-storage/.../voice_with_background.wav"
    },
    "srtFile": {
      "originalSubtitleDownloadLink": "/perso-storage/.../original.srt",
      "translatedSubtitleDownloadLink": "/perso-storage/.../translated.srt",
      "originalSubtitleVttDownloadLink": "/perso-storage/.../original.vtt"
    },
    "zippedFileDownloadLink": "/perso-storage/.../export.tar"
  }
}
```

---

## Dubbing API — 더빙·번역
영상 번역, 프로젝트 관리, 파일 다운로드를 위한 핵심 엔드포인트입니다.

### 더빙 전체 작업 흐름

미디어 업로드부터 번역 결과 다운로드까지의 전체 과정입니다.

**1단계: 미디어 업로드**
File API로 영상이나 오디오를 업로드합니다. SAS 발급 → Azure Blob 업로드 → 등록의 세부 과정은 File API를 참고하세요. 응답의 `seq`가 다음 단계의 `mediaSeq`입니다.
> File API의 직접 업로드 또는 외부 플랫폼 업로드 안내를 참고하세요.

**2단계: 작업 큐 초기화** [PUT] 인증: XP-API-KEY
`/video-translator/api/v1/projects/spaces/{spaceSeq}/queue`
Usage API의 작업 큐 조회 엔드포인트를 PUT으로 호출하여 Space의 번역 큐를 초기화합니다. 최초 생성되지 않으면 `space queue not found` 오류가 발생할 수 있습니다.
> Space마다 최초 한 번만 필요합니다. 이후 번역에서는 생략할 수 있습니다.

**3단계: 번역 요청** [POST] 인증: XP-API-KEY
`/video-translator/api/v1/projects/spaces/{spaceSeq}/translate`
첫 단계에서 얻은 `mediaSeq`로 번역을 요청합니다. `sourceLanguageCode`는 자동 감지 시 `auto`, 아니면 Language API의 언어 코드를 사용합니다.

**4단계: 진행률 조회** [GET] 인증: XP-API-KEY
`/video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/progress`
5초 간격으로 상태를 조회합니다. `progressReason` 상태: Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating | Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed.
> 5초보다 자주 폴링하지 마세요.

**5단계: 결과 다운로드** [GET] 인증: XP-API-KEY
`/video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/download?target=dubbingVideo`
완료되면 산출물을 다운로드합니다. 먼저 download-info로 다운로드 가능한 파일 종류를 확인합니다.
> 사용 가능한 target: dubbingVideo, lipSyncVideo, voiceAudio, originalVoiceAudio, backgroundAudio, voicewithBackgroundAudio, originalVoiceSpeakers, speakerSegmentExcel, speakerSegmentWithTranslationExcel, scriptTimestamps, originalSubBackground, audioScript, all. SRT 자막은 개별 target으로 받을 수 없고 `target=all`의 `.tar` 안에 포함됩니다. 다운로드 불가 항목을 요청하면 4xx 대신 500이 발생할 수 있습니다.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/translate
**번역·더빙 요청**
업로드한 미디어를 기준으로 영상/오디오 번역을 요청합니다. `mediaSeq`는 File API 업로드 응답의 `seq`입니다. 신규 연동은 언어별 TTS 모델을 지정하는 `targetLanguages`를 사용하세요. 기존 `targetLanguageCodes`와 `ttsModel` 조합도 호환용으로 동작하지만 사용 중단 예정입니다. `space queue not found` 오류가 나면 PUT 큐 초기화 API를 먼저 호출하세요.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - mediaSeq (정수, 필수): 영상/오디오 업로드 API 응답의 미디어 일련번호(seq)입니다.
  - isVideoProject (불리언, 필수): 영상 프로젝트면 true, 오디오 프로젝트면 false입니다.
  - sourceLanguageCode (문자열, 필수): 원본 언어 코드입니다. 자동 감지는 'auto', 지정하려면 Language API의 언어 코드('en', 'ko' 등)를 사용합니다. 빈 문자열 대신 'auto'를 사용하세요.
  - targetLanguageCodes (문자열[], 선택): 대상 언어 코드 배열입니다. 2026-05-14부터 사용 중단 예정이며 신규 연동은 `targetLanguages`를 사용해야 합니다. 두 필드를 동시에 보내면 `targetLanguages`가 우선합니다. 둘 중 하나는 필수입니다.
  - targetLanguages (객체[], 선택): 권장 방식인 언어·TTS 모델 쌍의 목록입니다. 지정하면 `targetLanguageCodes` 및 최상위 `ttsModel`보다 우선하며, 두 언어 설정 방식 중 하나는 필수입니다.
    - languageCode (문자열, 필수): 대상 언어 코드입니다('en', 'ko' 등). Language API가 반환하는 유효한 코드여야 합니다.
    - ttsModel (문자열, 선택): TTS 모델을 언어별로 선택합니다. 생략하면 LINNET_4, 미지원 언어에서는 ORIOLE가 기본입니다. Language API의 `supportedTtsModels`에 있어야 하며 그렇지 않으면 400 VT4009입니다. STT·오디오 분리에서는 무시됩니다.
      - ORIOLE: 자연스러운 현지어 발음. LINNET_4를 지원하지 않는 언어의 기본값입니다.
      - WREN: 풍부한 억양을 제공합니다.
      - LINNET_3: 원본의 말투를 유지합니다.
      - LINNET_4: 문맥에 따라 균형 있게 표현하며 생략 시 기본값입니다.
      - FINCH: 간소화된 기본 더빙 모델입니다. Pro 이상에서 사용 가능하며 아니면 403 VT40314입니다.
      - NIGHTINGALE: 다차원 감정 표현 모델입니다. Pro 이상에서 별도 요금이 적용되며 립싱크·SRT·RED 속도·음성 변경·문장별 재생성을 지원하지 않습니다(400 VT40918).
    - cloningStrength (정수, 선택): NIGHTINGALE 전용 원본 음성 복제 강도(1~10)입니다. 다른 모델에서는 무시하며 기본값은 7입니다.
  - numberOfSpeakers (정수, 선택): 다중 화자를 감지할 화자 수입니다(기본값: 1).
  - preferredSpeedType (문자열, 필수): 처리 속도 선호값입니다. [GREEN, RED]
  - withLipSync (불리언, 선택): 립싱크 처리를 포함할지 결정합니다. NIGHTINGALE에서는 지원하지 않습니다(400 VT40918).
  - customDictionaryBlobPath (문자열, 선택): 사용자 정의 사전 파일의 Blob 저장 경로입니다.
  - srtBlobPath (문자열, 선택): SRT 자막 파일 저장 경로입니다. NIGHTINGALE에서는 지원하지 않습니다(400 VT40918).
  - ttsModel (문자열, 선택, 사용 중단 예정): 2026-05-14부터 권장되지 않는 전체 언어 공통 TTS 모델 지정 방식입니다. 신규 연동에서는 `targetLanguages` 안에 언어별 모델을 설정하세요. 지원 모델은 Language API에서 확인합니다.
      - ORIOLE: 자연스러운 현지어 발음. LINNET_4 미지원 언어의 기본값입니다.
      - WREN: 풍부한 억양.
      - LINNET_3: 원본 화자의 말투 유지.
      - LINNET_4: 문맥에 맞춘 균형 잡힌 전달. 기본값.
      - FINCH: 간소화된 기본 더빙 모델로 Pro 이상에서 사용 가능(그 외 403 VT40314).
      - NIGHTINGALE: 감정 표현용 모델로 Pro 이상 및 별도 요금. 립싱크·SRT·RED·화자 변경·문장별 재생성 미지원(400 VT40918).
  - title (문자열, 선택): 프로젝트 제목입니다. 생략하면 미디어 파일 이름을 사용합니다.

요청 예시:
```json
{
  "mediaSeq": 12345,
  "isVideoProject": true,
  "sourceLanguageCode": "en",
  "targetLanguages": [
      { "languageCode": "ko", "ttsModel": "LINNET_4" },
      { "languageCode": "ja", "ttsModel": "NIGHTINGALE", "cloningStrength": 7 }
  ],
  "numberOfSpeakers": 2,
  "withLipSync": false,
  "preferredSpeedType": "GREEN",
  "title": "My Translation Project"
}
```

응답 (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [101, 102]
  }
}
```

오류:
  - 404 VT4043: 원본 언어를 찾을 수 없음
  - 404 VT4044: 대상 언어를 찾을 수 없음
  - 404 VT4042: 영상을 찾을 수 없음
  - 503 VT5034: 작업 큐가 가득 참
  - 402 VT4021: 크레딧 부족
  - 400 VT4009: 대상 언어와 TTS 모델 조합을 지원하지 않음
  - 400 VT40918: 해당 TTS 모델이 옵션을 지원하지 않음(NIGHTINGALE와 립싱크·SRT 업로드·RED 속도 조합)
  - 403 VT40314: 요금제에서 사용할 수 없는 TTS 모델(FINCH·NIGHTINGALE은 Pro 이상 필요)
  - 400 VT40022: cloningStrength 허용 범위 초과(1~10)

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}
**프로젝트 상세 조회**
번역 프로젝트 상세 정보를 조회합니다. `ttsModel`은 사용된 모델(ORIOLE, WREN, LINNET_3, LINNET_4, FINCH, NIGHTINGALE)이며 STT/오디오 분리는 null입니다. `progressReason`은 작업 단계 및 완료·실패 상태를 나타냅니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "seq": 101,
  "projectType": "VIDEO",
  "title": "My Translation Project",
  "userName": "oh****on",
  "isEditable": true,
  "durationMs": 120000,
  "sourceLanguage": {
    "code": "en",
    "name": "English"
  },
  "targetLanguage": {
    "code": "ko",
    "name": "Korean"
  },
  "ttsModel": "LINNET_4",
  "progress": 100,
  "progressReason": "Completed",
  "hasFailed": false,
  "failureReason": null,
  "isLipSync": false,
  "isLinkShared": false,
  "projectGenerationType": "DUBBING",
  "usedFeature": [],
  "experimentList": [],
  "thumbnailUrl": "https://...",
  "createDate": "2026-01-15T10:30:00Z",
  "updateDate": "2026-01-15T11:00:00Z"
}
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4045: 삭제된 프로젝트
  - 403 VT4031: 접근 거부
  - 409 VT4091: 영상 생성 실패

---

### GET /video-translator/api/v1/projects/spaces/{spaceSeq}
**프로젝트 목록 조회**
Space 안의 활성 프로젝트 목록을 조회합니다.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - memberRole (문자열, 필수): 목록을 요청하는 사용자의 역할입니다. [enterprise_owner, space_owner, space_manager, space_member, individual, developer]
  - size (정수, 필수): 페이지당 항목 수입니다.
  - offset (정수, 필수): 페이지네이션 시작 위치입니다.
  - sortType (문자열, 선택): 정렬 기준 필드입니다. 기본값은 update_date이며 [update_date, title] 중 선택합니다.
  - sortDirection (문자열, 필수): 정렬 방향입니다. [asc, desc]
  - type (문자열, 선택): 프로젝트 생성 유형으로 필터링합니다. [DUBBING, LIP_SYNC]

응답 (200):
```json
{
  "totalCount": 100,
  "hasNext": true,
  "pageSize": 10,
  "nextVtOffset": 10,
  "content": [
    {
      "seq": 1,
      "title": "My Project",
      "projectType": "VIDEO",
      "durationMs": 120000,
      "sourceLanguage": {
        "code": "en",
        "name": "English"
      },
      "targetLanguage": {
        "code": "ko",
        "name": "Korean"
      },
      "progress": 100,
      "hasFailed": false,
      "status": "created",
      "projectGenerationType": "DUBBING",
      "createDate": "2026-01-15T10:00:00Z"
    }
  ]
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/script
**스크립트 조회**
문장별 번역, 일치율, 화자 정보가 포함된 프로젝트 스크립트를 조회합니다. 문장별 `matchingRate`와 `rewrite`는 null일 수 있습니다. 화자의 `projectSpeakerSeq`는 임시 초안 저장 API에 필요합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - cursorId (정수, 선택): 커서 기반 페이지네이션 ID입니다. 첫 요청에서는 생략합니다.
  - size (정수, 선택): 크기 또는 항목 수입니다. Number of sentences per page. (기본값: 10000)

응답 (200):
```json
{
  "hasNext": false,
  "nextCursorId": null,
  "retranslateAvailable": true,
  "sentences": [
    {
      "seq": 1,
      "externalScriptSeq": "pvtv-e1045225d769af98305367b722c1adfb",
      "speakerOrderIndex": 0,
      "offsetMs": 0,
      "durationMs": 3500,
      "originalDraftText": "Hello, welcome.",
      "originalText": "Hello, welcome.",
      "translatedText": "...",
      "proofRead": false,
      "audioUrl": "/perso-storage/.../audio.mp3",
      "matchingRate": {
        "level": 3,
        "levelType": "GOOD"
      },
      "rewrite": {
        "speed": "normal",
        "current": 120
      }
    }
  ],
  "speakers": [
    {
      "speakerOrderIndex": 0,
      "externalSpeakerSeq": "spk_001",
      "projectSpeakerSeq": 12345,
      "voiceId": "pvsp-1351dafa5135"
    }
  ]
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/progress
**진행률 조회**
번역 프로젝트 진행률을 조회합니다. 최소 5초 간격을 권장합니다. `progressReason`이 `Completed`이면 완료, `Failed`이면 실패입니다. 호출 간격을 줄이면 제한에 걸릴 수 있습니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "projectSeq": 101,
    "progress": 65,
    "progressReason": "Transcribing",
    "hasFailed": false,
    "failureReason": null,
    "engineErrorMessage": null,
    "speedType": "fast",
    "expectedRemainingTimeMinutes": 3,
    "isCancelable": true
  }
}
```

---

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/cancel
**프로젝트 취소**
대기 중인 프로젝트를 취소합니다. GREEN 영역의 초기 내보내기 PENDING 상태에서만 가능하며, 큐 처리가 이미 시작되면 생성 직후라도 취소가 거절될 수 있습니다(400 VT4004).

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (201):
```json
{
  "result": {}
}
```

오류:
  - 400 VT4004: 취소할 수 없는 상태
  - 403 VT4033: 작업 공간 접근 권한 없음

---

### GET /video-translator/api/v1/projects/{projectSeq}/share
**공유 링크 조회**
프로젝트 외부 공유에 쓰이는 암호화 쿼리 문자열을 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.

응답 (200):
```json
{
  "shareQuery": "eyJhbGciOiJIUzI1NiJ9..."
}
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/share
**공유 활성화·비활성화**
프로젝트 공유 URL을 활성화하거나 비활성화합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.

쿼리 파라미터:
  - sharedStatus (불리언, 필수): 공유를 활성화할지(true), 비활성화할지(false) 설정합니다.

응답 (200):
```json
{
  "result": {
    "projectSeq": 1,
    "sharedStatus": true
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/video-info
**영상 정보 조회**
영상의 제목·길이·해상도·상태 등 메타데이터를 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "title": "My Video",
  "thumbnailUrl": "https://...",
  "type": "VIDEO",
  "durationMs": 120000,
  "videoStatus": "COMPLETED",
  "language": "ko",
  "aspectRatio": "16:9",
  "resolution": "1920x1080",
  "sizeByte": 52428800
}
```

오류:
  - 403 VT4033: 작업 공간 접근 권한 없음
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4042: 영상을 찾을 수 없음

---

### GET /video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/export-history
**내보내기 이력 조회**
페이지네이션을 사용하여 프로젝트 내보내기 및 업로드 이력을 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - page (정수, 선택): 페이지 번호(0부터 시작, 기본값 0)입니다.
  - size (정수, 선택): 페이지당 항목 수입니다.
  - sort (문자열, 선택): 정렬 조건입니다. Sort criteria.

응답 (200):
```json
{
  "result": {
    "page": 1,
    "totalPages": 10,
    "hasNext": true,
    "currentPageSize": 100,
    "contents": [
      {
        "exportDate": "2026-01-15T10:00:00Z",
        "projectTitle": "My Project",
        "isLipSync": true,
        "exportZipDownloadPath": "/export.zip"
      }
    ]
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/retranslation/status
**재번역 가능 여부 확인**
프로젝트를 재번역할 수 있는지 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "retranslateAvailable": true
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/used-features
**사용된 기능 조회**
사용자 정의 사전·SRT 업로드 등 프로젝트 생성 시 사용한 선택 기능을 확인합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "usedCustomDictionary": false,
    "usedSrtUpload": false
  }
}
```

---

## Editing API — 편집
프로젝트 안의 개별 오디오 문장을 수정·번역·관리합니다.

### PATCH /video-translator/api/v1/project/{projectSeq}/audio-sentence/{sentenceSeq}
**문장 번역**
특정 프로젝트 문장을 번역하거나 재번역합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - sentenceSeq (정수, 필수): 문장의 고유 식별자입니다.

요청 본문:
  - targetText (문자열, 필수): 번역할 문장 또는 수정할 번역문입니다.

요청 예시:
```json
{
  "targetText": "Updated translation text"
}
```

응답 (200):
```json
{
  "result": {
    "scriptSeq": 1,
    "translatedText": "Updated translation text",
    "matchingRate": {
      "level": 4,
      "levelType": "EXCELLENT"
    },
    "rewrite": {
      "speed": "normal",
      "current": 115,
      "optimal": {
        "min": 80,
        "max": 150
      }
    }
  }
}
```

---

### PATCH /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/generate-audio
**문장 음성 생성**
특정 문장의 번역 음성을 생성합니다. NIGHTINGALE 프로젝트에서는 사용할 수 없으며(400 VT40918), 교정 요청을 통해 재생성해야 합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - audioSentenceSeq (정수, 필수): 오디오 문장의 고유 식별자입니다.

요청 본문:
  - targetText (문자열, 필수): 음성을 생성할 텍스트입니다.

요청 예시:
```json
{
  "targetText": "Text to generate audio for"
}
```

응답 (200):
```json
{
  "result": {
    "scriptSeq": 1,
    "translatedText": "Text to generate audio for",
    "generateAudioFilePath": "/audio/1.mp3",
    "matchingRate": {
      "level": 3,
      "levelType": "Low"
    },
    "rewrite": {
      "speed": "fast",
      "current": 3,
      "optimal": {
        "min": 101,
        "max": 120
      }
    }
  }
}
```

---

### PUT /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/reset
**번역 초기화**
번역을 교정된 초기 상태로 되돌립니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - audioSentenceSeq (정수, 필수): 오디오 문장의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "speakerSeq": "pvsp-1351dafa5135",
    "proofreadOriginalText": "Hello",
    "proofreadTranslatedText": "Hello"
  }
}
```

---

### PUT /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/cancel
**문장 번역 취소**
진행 중인 특정 문장의 번역을 취소합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - audioSentenceSeq (정수, 필수): 오디오 문장의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {}
}
```

---

### POST /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/temp-save
**임시 초안 저장**
전체 처리를 시작하지 않고 문단 번역 초안을 임시 저장합니다. NIGHTINGALE에서는 원문을 변경하면 다음 교정 요청에서 재번역하기 전까지 해당 문장의 번역이 지워집니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - audioSentenceSeq (정수, 필수): 오디오 문장의 고유 식별자입니다.

요청 본문:
  - originalDraftText (문자열, 필수): 임시 저장할 원문 초안입니다.
  - projectSpeakerSeq (정수, 필수): 임시 지정할 프로젝트 화자 ID입니다. 프로젝트 버전 2의 화자 변경에는 필수이며 Get Script 응답의 `speakers[].projectSpeakerSeq`에서 얻습니다.

요청 예시:
```json
{
  "originalDraftText": "Draft translation text",
  "projectSpeakerSeq": 12345
}
```

응답 (200):
```json
{
  "result": null
}
```

오류:
  - 400 VT40026: NIGHTINGALE에서 화자 변경으로 동일 화자의 문장이 서로 겹칩니다.
  - 400 VT40027: NIGHTINGALE 프로젝트에서 원문 텍스트가 비어 있습니다.

---

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/speakers/from-sentence
**문장에서 화자 추가**
더빙 프로젝트에서 기준 문장의 원본 화자 음성을 복제해 새 화자를 추가합니다. 화자명·순서는 시스템에서 자동 지정하며 삭제된 순서는 재사용되지 않습니다. 기준 문장도 새 화자로 임시 배정되므로 음성을 다시 생성해야 합니다. 스크립트 `sentences[].seq`를 `sourceSentenceSeq`로 전달하고, 추가 후 스크립트를 다시 조회하여 `projectSpeakerSeq`를 확인하세요.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - sourceSentenceSeq (정수, 필수): 기준 문장 ID입니다. 해당 구간의 원본 화자 음성이 복제 소스로 사용됩니다. Get Script 응답의 `sentences[].seq`를 전달합니다.

요청 예시:
```json
{
  "sourceSentenceSeq": 1234
}
```

응답 (200):
```json
{
  "result": {
    "seq": 15,
    "projectSeq": 100,
    "audioSpeakerSeq": "pvtv-e1045225d769af98305367b722c1adfb",
    "displayName": "Speaker 3"
  }
}
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4042: 기준 문장을 찾을 수 없거나 해당 프로젝트에 속하지 않습니다.
  - 400 VT4007: 더빙 프로젝트가 아니므로 문장 기반 화자 추가 불가
  - 403 VT4037: 무료 플랜에서 편집 불가
  - 409 VT4099: 프로젝트 버전 2 이상 필요
  - 409 VT40915: 프로젝트 화자 수 제한 초과

---

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/speakers/bulk-change
**화자 일괄 변경**
기존 화자에 배정된 모든 문장을 새 화자에게 일괄 배정합니다. `sourceSpeakerSeq`와 `targetSpeakerSeq` 음성 ID 쌍은 항상 필요합니다. 프로젝트 v2에서는 `sourceProjectSpeakerSeq`·`targetProjectSpeakerSeq`도 함께 전달해 화자를 지정하며 더빙에서는 필수입니다. 변경된 문장은 초안으로 저장되고 재생성 대상으로 표시되므로 음성을 다시 렌더링해야 합니다. STT·오디오 분리·더빙에서 사용 가능합니다. 필요한 ID는 Get Script의 `speakers[].projectSpeakerSeq`에서 확인합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - sourceProjectSpeakerSeq (정수, 필수): 문장을 이동할 원본 화자의 `projectSpeakerSeq`입니다. 더빙에서 필수이며 프로젝트 버전 2에서는 다른 유형에도 권장됩니다.
  - targetProjectSpeakerSeq (정수, 필수): 문장을 새로 배정받을 대상 화자의 `projectSpeakerSeq`입니다. 더빙에서 필수이며 프로젝트 버전 2에서도 권장됩니다.
  - sourceSpeakerSeq (문자열, 필수): 원본 화자의 음성 ID입니다(항상 필수). `projectSpeakerSeq` 쌍을 전달하면 화자 식별에는 사용되지 않습니다.
  - targetSpeakerSeq (문자열, 필수): 대상 화자의 음성 ID입니다(항상 필수). `projectSpeakerSeq` 쌍을 전달하면 화자 식별에는 사용되지 않습니다.

요청 예시:
```json
{
  "sourceSpeakerSeq": "pvtv-3789224e24134dda077155264e8b1b64",
  "targetSpeakerSeq": "pvtv-69aaeacedfb9defbffa828828b872a26",
  "sourceProjectSpeakerSeq": 807,
  "targetProjectSpeakerSeq": 808
}
```

응답 (200):
```json
{
  "result": null
}
```

오류:
  - 400 VT4001: 원본·대상 화자가 같거나, 더빙의 `projectSpeakerSeq` 쌍이 빠졌거나, 버전 1 프로젝트에 해당 쌍을 전달했습니다.
  - 400 VT4007: STT·오디오 분리·더빙 프로젝트가 아닙니다.
  - 404 VT40414: 원본 또는 대상 화자가 프로젝트에서 활성 상태가 아닙니다.

---

### POST /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/match-rewrite
**일치율 및 재작성 정보 조회**
번역 품질 평가를 위해 문장별 일치율과 재작성 정보를 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - audioSentenceSeq (정수, 필수): 오디오 문장의 고유 식별자입니다.

요청 본문:
  - targetText (문자열, 필수): 평가할 번역 텍스트입니다.

요청 예시:
```json
{
  "targetText": "Translation text to evaluate"
}
```

응답 (200):
```json
{
  "result": {
    "matchingRate": {
      "level": 3,
      "levelType": "Low"
    },
    "rewrite": {
      "speed": "fast",
      "current": 3,
      "optimal": {
        "min": 101,
        "max": 120
      }
    }
  }
}
```

---

### POST /video-translator/api/v1/project/{projectSeq}/space/{spaceSeq}/proofread
**교정 요청**
프로젝트 번역 교정을 요청해 결과를 다시 처리합니다. NIGHTINGALE에서는 첫 교정은 무료이고 이후부터 최초 더빙과 동일한 비용이 발생합니다(`projectSeq`로 예상 비용 조회). RED 속도는 지원하지 않습니다(400 VT40918).

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - isLipSync (불리언, 선택): 교정 결과에 립싱크를 적용할지 설정합니다.
  - experimentKey (문자열, 선택): A/B 테스트 설정에 사용할 실험 키입니다.
  - preferredSpeedType (문자열, 필수): 처리 속도 옵션입니다. [GREEN, RED]

요청 예시:
```json
{
  "isLipSync": false,
  "preferredSpeedType": "GREEN"
}
```

응답 (200):
```json
{
  "result": {}
}
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/title
**제목 수정**
프로젝트 제목을 변경합니다. 비어 있거나 null이면 `Untitled`로 설정됩니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - newTitle (문자열, 선택): 변경할 프로젝트 제목입니다. 비어 있으면 `Untitled`로 설정합니다.

요청 예시:
```json
{
  "newTitle": "Updated Project Name"
}
```

응답 (200):
```json
// Empty response body
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/access
**접근 권한 수정**
프로젝트 접근 권한을 변경합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - permission (문자열, 필수): 접근 권한 유형입니다. [individual, all]

응답 (200):
```json
// Empty response body
```

오류:
  - 403 VT4033: 작업 공간 접근 권한 없음
  - 404 VT4046: 프로젝트 작업 공간을 찾을 수 없음

---

### DELETE /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}
**프로젝트 삭제**
프로젝트를 영구 삭제하며 성공 시 본문 없이 HTTP 204를 반환합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (204):
```json
// No content returned
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4045: 삭제된 프로젝트
  - 403 VT4031: 접근 거부

---

## Usage API — 사용량·크레딧
Space별 사용량, 작업 큐 상태 및 예상 크레딧 소모량을 모니터링합니다.

### GET /video-translator/api/v1/projects/spaces/{spaceSeq}/plan/status
**사용자 잔여 크레딧 조회**
Space 안의 사용자 요금제 상태와 잔여 크레딧을 조회합니다.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "spaceSeq": 12345,
    "planTier": "creator",
    "remainingQuota": {
      "remainingQuota": 500000
    },
    "resetDateTime": "2026-02-28T23:59:59Z",
    "isCancellationScheduled": false
  }
}
```

---

### GET /video-translator/api/v1/projects/spaces/{spaceSeq}/media/quota
**예상 크레딧 사용량 계산**
미디어 유형·길이·번역 방식·TTS 모델을 기준으로 소모 예상 크레딧을 계산합니다. 계산식: 크레딧 = 미디어 전체 초 × 초당 요율 × 대상 언어 수.
- 초당 요율은 TTS 모델과 번역 유형에 따라 달라집니다. 정확한 가격은 이 API로 확인하세요.
- 4K(3840×2160) 이상 영상의 더빙(FINCH 포함) 및 립싱크 비용은 3배입니다. NIGHTINGALE·STT·오디오 분리는 해상도의 영향을 받지 않습니다.
- 언어별로 다른 TTS 모델을 쓰면 `ttsModelCounts`(예: NIGHTINGALE:1,ORIOLE:2,FINCH:1)를 전달하세요. 이 경우 `targetLanguageSize`는 무시됩니다.
- NIGHTINGALE 교정은 최초 내보내기 후 첫 교정이 무료이며, 이후 교정에는 최초 더빙과 같은 비용이 듭니다. `projectSeq`를 보내 교정 비용과 `exportCount`를 확인하세요.
- `expectedUsedQuota`는 정가이며, 실제 차감되는 할인 적용 금액은 `promotionExpectedUsedQuota`입니다. 할인이 없으면 두 값이 같습니다.
- 영상은 `width`·`height`가 필수이며 빠지면 400 VT4001입니다. 오디오는 필요하지 않습니다.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - mediaType (문자열, 필수): 미디어 유형입니다. [video, audio]
  - translateType (문자열, 선택): 요청할 변환 유형입니다. TRANSLATE(더빙), TRANSLATE_WITH_LIPSYNC(더빙+립싱크), LIPSYNC(립싱크만), STT, AUDIO_SEPARATION 중 선택합니다. 설정하면 `lipSync` 값은 무시됩니다.
  - lipSync (불리언, 선택, 사용 중단 예정): 립싱크 포함 여부입니다. 대신 `translateType`을 사용하세요.
  - durationMs (정수, 필수): 미디어 길이(밀리초)입니다.
  - width (정수, 선택): 영상의 가로 해상도(픽셀)입니다. 영상 유형이면 필수입니다(누락 시 400 VT4001).
  - height (정수, 선택): 영상의 세로 해상도(픽셀)입니다. 영상 유형이면 필수입니다(누락 시 400 VT4001).
  - targetLanguageSize (정수, 선택): 대상 언어 수입니다(기본값: 1). `ttsModelCounts`를 전달하면 무시됩니다.
  - ttsModelCounts (문자열, 선택): TTS 모델별 대상 언어 개수입니다. `MODEL:count` 쌍을 쉼표로 구분합니다(예: NIGHTINGALE:1,ORIOLE:2,FINCH:1). 모델이 혼합된 경우 사용하세요.
  - projectSeq (정수, 선택): 기존 프로젝트의 교정 비용을 계산할 때 전달합니다. 응답에는 교정 비용과 `exportCount`(최초 내보내기 1, 완료된 교정마다 +1)가 포함됩니다(NIGHTINGALE에만 적용).

응답 (200):
```json
{
  "result": {
    "expectedUsedQuota": 720.0,
    "promotionExpectedUsedQuota": 540.0,
    "exportCount": null
  }
}
```

오류:
  - 400 VT4001: 잘못된 파라미터(영상 가로/세로 누락, ttsModelCounts 형식 오류, 알 수 없는 모델 또는 1 미만 수량)
  - 400 VT40918: NIGHTINGALE과 립싱크를 함께 사용할 수 없음

---

### PUT /video-translator/api/v1/projects/spaces/{spaceSeq}/queue
**사용자 작업 큐 조회·초기화**
이름은 큐 조회지만 PUT 요청을 보내면 큐가 없을 때 생성·초기화합니다. Space에 큐가 없으면 자동 생성하여 반환합니다. 최초 번역 요청 전에 초기화하지 않으면 `space queue not found` 오류가 날 수 있습니다. GET·PUT이 모두 지원되며 내부적으로 요금제와 크레딧, 번역 큐를 확인합니다.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": {
    "userSeq": 19507,
    "planName": "pro",
    "usedQueueCount": 0,
    "maxQueueCount": 3,
    "redZoneQueueCount": 0
  }
}
```

---

## Lip Sync API — 립싱크
립싱크 영상 생성을 요청하고 생성 이력을 조회합니다.

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/lip-sync
**립싱크 생성 요청**
기존 번역 프로젝트를 바탕으로 립싱크 영상 생성을 요청합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - preferredSpeedType (문자열, 필수): 처리 속도 옵션입니다. [GREEN, RED]
  - title (문자열, 선택): 프로젝트 제목입니다. 생략하면 상위 프로젝트의 제목을 사용합니다.

요청 예시:
```json
{
  "preferredSpeedType": "GREEN",
  "title": "My Lip Sync Project"
}
```

응답 (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [1, 2, 3]
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/lip-sync/generated
**생성 이력 조회**
프로젝트의 립싱크 생성 이력을 페이지 단위로 조회합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - page (정수, 선택): 페이지 번호입니다(기본값: 1).
  - pageSize (정수, 선택): 페이지당 항목 수입니다(기본값: 10).

응답 (200):
```json
{
  "result": {
    "page": 1,
    "totalPages": 10,
    "hasNext": true,
    "contents": [
      {
        "type": "VIEW",
        "projectTitle": "Lip Sync Project 1",
        "lipSyncProjectSeq": 123,
        "status": "COMPLETED",
        "createDate": "2026-01-15T04:29:37.432Z"
      },
      {
        "type": "DOWNLOAD",
        "projectTitle": "Lip Sync Project 2",
        "exportZipDownloadPath": "/export.zip",
        "createDate": "2026-01-15T04:29:37.432Z"
      }
    ]
  }
}
```

---

## STT API — 음성 인식
STT 프로젝트를 생성하고 인식된 스크립트를 조회합니다.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/stt
**STT 프로젝트 생성**
업로드한 미디어로 STT 프로젝트를 생성합니다. File API에서 반환된 `seq`를 `mediaSeq`로 사용합니다. 큐가 없다는 오류가 발생하면 Usage API의 PUT 큐 초기화 요청 후 재시도하세요.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - mediaSeq (정수, 필수): 영상/오디오 업로드 API 응답의 미디어 일련번호(seq)입니다.
  - isVideoProject (불리언, 필수): 영상 프로젝트면 true, 오디오 프로젝트면 false입니다.
  - title (문자열, 선택): 프로젝트 제목입니다. 생략하면 미디어 파일 이름을 사용합니다.

요청 예시:
```json
{
  "mediaSeq": 12345,
  "isVideoProject": true,
  "title": "My STT Project"
}
```

응답 (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [101]
  }
}
```

---

### POST /video-translator/api/v1/project/{projectSeq}/space/{spaceSeq}/stt/apply-changes
**STT 재생성**
스크립트를 수정한 다음 STT 결과 재생성을 요청합니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

응답 (200):
```json
{
  "result": null
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/stt/script
**STT 프로젝트 스크립트 조회**
완료된 STT 프로젝트의 스크립트를 조회합니다. 커서 페이지네이션을 사용하므로 첫 호출에서는 `cursorId`를 생략합니다. `originalDraftText`는 null일 수 있으며 인식 결과는 `originalText`를 사용합니다. 화자의 `voiceId`는 `externalSpeakerSeq`와 같은 pvtv- 식별자입니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - cursorId (정수, 선택): 커서 페이지네이션 ID입니다. 첫 요청에서는 생략하고 다음 요청부터 이전 결과의 마지막 커서 값을 전달합니다.
  - size (정수, 선택): 페이지 크기입니다(기본값: 10000).

응답 (200):
```json
{
  "hasNext": true,
  "nextCursorId": 123456789,
  "sentences": [
    {
      "seq": 1,
      "externalScriptSeq": "pvtv-e1045225d769af98305367b722c1adfb",
      "speakerOrderIndex": 1,
      "offsetMs": 0,
      "durationMs": 1000,
      "originalDraftText": null,
      "originalText": "Hello, world!"
    }
  ],
  "speakers": [
    {
      "speakerOrderIndex": 1,
      "externalSpeakerSeq": "pvtv-e1045225d769af98305367b722c1adfb",
      "voiceId": "pvtv-e1045225d769af98305367b722c1adfb",
      "speakerSeq": 1,
      "speakerName": "Speaker 1"
    }
  ]
}
```

---

## Audio Separation API — 오디오 분리
오디오 파일을 음성과 배경음으로 분리하는 프로젝트를 생성하고 스크립트를 조회합니다.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/audio-separation
**오디오 분리 프로젝트 생성**
미디어의 음성·배경음을 분리하는 프로젝트를 생성합니다. 큐 미설정 오류가 발생하면 Usage API의 PUT 큐 초기화 요청 후 재시도하세요.

경로 파라미터:
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

요청 본문:
  - mediaSeq (정수, 필수): 영상/오디오 업로드 API 응답의 미디어 일련번호(seq)입니다.
  - isVideoProject (불리언, 필수): 영상 프로젝트면 true, 오디오 프로젝트면 false입니다.
  - title (문자열, 선택): 프로젝트 제목입니다. 생략하면 미디어 파일 이름을 사용합니다.

요청 예시:
```json
{
  "mediaSeq": 12345,
  "isVideoProject": false,
  "title": "My Audio Separation Project"
}
```

응답 (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [102]
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/audio-separation/script
**오디오 분리 스크립트 조회**
완료된 오디오 분리 프로젝트의 스크립트를 조회합니다. 커서 페이지네이션을 사용하여 첫 호출에서는 `cursorId`를 생략합니다. `originalDraftText`는 null일 수 있으므로 `originalText`를 사용합니다. 화자 `voiceId`는 `externalSpeakerSeq`와 같은 pvtv- ID입니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - spaceSeq (정수, 필수): 작업 공간의 고유 식별자입니다.

쿼리 파라미터:
  - cursorId (정수, 선택): 커서 페이지네이션 ID입니다. 첫 요청에서는 생략하고 다음 요청부터 이전 결과의 마지막 커서 값을 전달합니다.
  - size (정수, 선택): 페이지 크기입니다(기본값: 10000).

응답 (200):
```json
{
  "hasNext": true,
  "nextCursorId": 123456789,
  "sentences": [
    {
      "seq": 1,
      "externalScriptSeq": "pvtv-e1045225d769af98305367b722c1adfb",
      "speakerOrderIndex": 1,
      "offsetMs": 0,
      "durationMs": 1000,
      "originalDraftText": null,
      "originalText": "Hello, world!",
      "audioUrl": "/perso-storage/audio.mp3"
    }
  ],
  "speakers": [
    {
      "speakerOrderIndex": 1,
      "externalSpeakerSeq": "pvtv-e1045225d769af98305367b722c1adfb",
      "voiceId": "pvtv-e1045225d769af98305367b722c1adfb",
      "speakerSeq": 1,
      "speakerName": "Speaker 1"
    }
  ]
}
```

---

## Language API — 언어
더빙과 번역에 사용할 수 있는 언어 목록을 조회합니다.

### GET /video-translator/api/v1/languages
**지원 언어 목록**
언어 코드·이름·지원 TTS 모델 목록을 반환합니다. 언어별 모델 지원 여부는 이 API에서 확인하며 별도의 모델 조회 엔드포인트는 없습니다.
- `supportedTtsModels`: 대상 언어에 사용할 수 있는 모델 목록(ORIOLE, WREN, LINNET_3, LINNET_4, FINCH, NIGHTINGALE)입니다. 더빙 전에 확인하세요. 지원하지 않는 조합은 400 VT4009이고 배열 순서에는 의미가 없습니다.
- 같은 `code`가 `languageTag`로 구분되어 여러 번 나타날 수 있습니다(예: 미국 영어 default, 영국 영어 en-GB; pt-PT, es-ES도 유사).
- `auto`는 원본 언어 자동 감지인 `sourceLanguageCode` 전용입니다. 지원 모델 목록이 비어 있어 대상 언어로 쓸 수 없습니다.
- 실험 언어는 `experiment` 필드로 표시됩니다.

응답 (200):
```json
{
  "languages": [
    {
      "code": "auto",
      "name": "Auto Detect",
      "languageTag": "default",
      "experiment": false,
      "supportedTtsModels": []
    },
    {
      "code": "en",
      "name": "English (US)",
      "languageTag": "default",
      "experiment": false,
      "supportedTtsModels": ["ORIOLE", "WREN", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
    },
    {
      "code": "en",
      "name": "English (UK)",
      "languageTag": "en-GB",
      "experiment": false,
      "supportedTtsModels": ["ORIOLE", "NIGHTINGALE"]
    },
    {
      "code": "ja",
      "name": "Japanese",
      "languageTag": "default",
      "experiment": false,
      "supportedTtsModels": ["ORIOLE", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
    }
  ]
}
```

---

## Feedback API — 평가
번역 프로젝트의 평점을 제출하고 조회합니다.

### POST /video-translator/api/v1/projects/feedbacks
**평점 등록**
프로젝트에 1~5점 평점을 제출합니다.

요청 본문:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.
  - rating (정수, 필수): 1~5 범위의 평점입니다.

요청 예시:
```json
{
  "projectSeq": 101,
  "rating": 4
}
```

응답 (200):
```json
{
  "averageRating": 4.5,
  "count": 10
}
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4045: 삭제된 프로젝트

---

### GET /video-translator/api/v1/projects/feedbacks
**평점 조회**
특정 프로젝트에 자신이 등록한 평점을 조회합니다. 등록된 평가가 없으면 HTTP 204를 반환합니다.

쿼리 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.

응답 (200):
```json
{
  "rating": 4
}
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음
  - 404 VT4045: 삭제된 프로젝트

---

## Community Spotlight API — 공개 프로젝트
추천 공개 프로젝트 및 공유 번역 프로젝트를 조회합니다.

### GET /video-translator/api/v1/projects/recommended
**추천 공개 프로젝트 목록**
Community Spotlight의 추천 프로젝트를 페이지 단위로 조회합니다. 공개 API이므로 `XP-API-KEY`가 필요하지 않습니다.

쿼리 파라미터:
  - page (정수, 선택): 페이지 번호(0부터 시작, 기본값 0)입니다.
  - size (정수, 선택): 페이지당 항목 수입니다.
  - languageCode (문자열, 선택): 원본 언어 코드로 필터링합니다(예: ko, en, ja).

응답 (200):
```json
{
  "totalCount": 100,
  "totalPages": 10,
  "page": 1,
  "size": 10,
  "isLast": false,
  "contents": [
    {
      "seq": 1,
      "title": "How to build with Framer",
      "mediaType": "VIDEO",
      "userName": "oh****on",
      "thumbnailUrl": "/thumbnail.jpg",
      "durationMs": 10000,
      "sourceLanguage": {
        "code": "en",
        "name": "English"
      },
      "targetLanguage": {
        "code": "ko",
        "name": "Korean"
      },
      "isLipSync": true,
      "feedbackAverage": {
        "averageRating": 4.5,
        "count": 10
      }
    }
  ]
}
```

---

### GET /video-translator/api/v1/projects/recommended/{projectSeq}
**추천 공개 프로젝트 상세**
추천 프로젝트의 상세 정보를 가져옵니다. 공개 API이므로 키가 필요 없고 응답이 `result`로 감싸져 있지 않습니다. 파일 경로는 `/perso-storage/...` 상대 경로이므로 https://portal-media.perso.ai 를 붙입니다.

경로 파라미터:
  - projectSeq (정수, 필수): 프로젝트의 고유 식별자입니다.

응답 (200):
```json
{
  "seq": 1,
  "title": "How to build with Framer",
  "mediaType": "VIDEO",
  "userName": "oh****on",
  "thumbnailUrl": "/thumbnail.jpg",
  "durationMs": 10000,
  "sourceLanguage": {
    "code": "en",
    "name": "English (US)",
    "languageTag": "default",
    "experiment": false,
    "supportedTtsModels": ["ORIOLE", "WREN", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
  },
  "targetLanguage": {
    "code": "ko",
    "name": "Korean",
    "languageTag": "default",
    "experiment": false,
    "supportedTtsModels": ["ORIOLE", "WREN", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
  },
  "ttsModel": "LINNET_4",
  "originalFileUrl": "/original.mp4",
  "translatedFileUrl": "/translated.mp4",
  "lipSyncFileUrl": "/lip-sync.mp4",
  "subtitleFileUrl": "/subtitle.srt",
  "isLipSync": true,
  "feedbackAverage": {
    "averageRating": 4.5,
    "count": 10
  },
  "createDate": "2026-01-15T10:00:00Z",
  "updateDate": "2026-01-15T11:00:00Z"
}
```

오류:
  - 404 VT4041: 프로젝트를 찾을 수 없음

---

### GET /video-translator/api/v1/projects/shared/{sharedQuery}
**공유 프로젝트 상세**
암호화된 공유 쿼리 문자열로 프로젝트 정보를 조회합니다. 공개 API로 키가 필요 없으며 응답에 `result` 래퍼가 없습니다. 파일 경로에는 https://portal-media.perso.ai 를 붙입니다.

경로 파라미터:
  - sharedQuery (문자열, 필수): API 입력값입니다. Encrypted share query string.

응답 (200):
```json
{
  "seq": 1,
  "title": "How to build with Framer",
  "projectType": "VIDEO",
  "userName": "oh****on",
  "durationMs": 10000,
  "sourceLanguage": {
    "code": "en",
    "name": "English (US)",
    "languageTag": "default",
    "experiment": false,
    "supportedTtsModels": ["ORIOLE", "WREN", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
  },
  "targetLanguage": {
    "code": "ko",
    "name": "Korean",
    "languageTag": "default",
    "experiment": false,
    "supportedTtsModels": ["ORIOLE", "WREN", "LINNET_3", "LINNET_4", "FINCH", "NIGHTINGALE"]
  },
  "ttsModel": "LINNET_4",
  "originalFileUrl": "/original.mp4",
  "translatedFileUrl": "/translated.mp4",
  "isLipSync": true
}
```

오류:
  - 403 VT4035: 프로젝트 공유가 비활성화됨(SHARED_NOT_ACCESSIBLE)

---
