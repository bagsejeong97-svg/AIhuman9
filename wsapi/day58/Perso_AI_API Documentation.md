# Perso AI API Documentation

Last updated: 2026-10-22. Changelog: https://developers.perso.ai/docs/changelog

API Base URL: https://api.perso.ai
Service/File URL: https://portal-media.perso.ai
Authentication: Include `XP-API-KEY` header in every request.
API Key format: pk_live_xxxxxxxxxxxxxxxxxxxx

Example:
```
curl -X GET https://api.perso.ai/video-translator/api/v1/languages \
  -H "XP-API-KEY: pk_live_xxxxxxxxxxxxxxxxxxxx"
```

---

## CRITICAL RULES (read before writing any code)

These are the most common failure points. Apply them by default.

1. **Authentication header is `XP-API-KEY`, not `Authorization: Bearer`.**
   - Every request to https://api.perso.ai must include `XP-API-KEY: <your-key>`, except a few public community endpoints (Community Spotlight: List/Get Featured Projects and Get Shared Project) which need no auth.
   - Bearer JWT is never used for this API.

2. **Multi-tenancy via `spaceSeq`.**
   - Most domain endpoints require a `spaceSeq` (Space ID) in the request body or query.
   - Missing `spaceSeq` is the #1 cause of empty lists or 404s — when in doubt, pass it explicitly.
   - Obtain `spaceSeq` from `GET /portal/api/v1/spaces` (the Space API).
   - If several spaces are returned, pick one you have permission for: check `memberRole`
     (e.g. `space_owner`) and `serviceType` (dubbing work uses `"video_translator"`).
     Using a space you lack permission on returns 403.

3. **File upload is a 3-step flow, not a single call.**
   Do NOT try to attach binary files to Dubbing/STT/Lip-Sync requests directly. First produce a `mediaSeq`:
   ```
   Step 1:  GET  /file/api/upload/sas-token?fileName=<URL-encoded name>
                -> { blobSasUrl }          (valid 30 minutes)
   Step 2:  PUT  {blobSasUrl}              (direct to Azure Blob, NOT https://api.perso.ai)
                Headers: x-ms-blob-type: BlockBlob
                Body: raw file bytes
                Use the blobSasUrl exactly as returned. Do NOT hardcode the host — it may be
                perso-saas-file-frontdoor.perso.ai rather than portal-media.perso.ai.
                No XP-API-KEY is needed here (the SAS signature is the auth); if sent it is ignored.
                201 on success. 403 = SAS expired, go back to Step 1.
   Step 3:  PUT /file/api/upload/video   (or /audio)
                Body: { "fileUrl": "<blobSasUrl>", ... }
                -> { "seq": <number> }    // use this as mediaSeq in downstream APIs
                Stripping the '?...' query string from fileUrl is recommended (the file still
                registers with it, but strip it for stable storage paths).
   ```
   For YouTube/TikTok/Drive URLs, use the External flow instead: `external/metadata` → `media/validate` → `upload/video/external`.

4. **Long-running jobs return generated project IDs — poll them.**
   - Dubbing, STT, Audio Separation, Lip-Sync create projects and return immediately with
     `{ "result": { "startGenerateProjectIdList": [101] } }`. There can be more than one ID
     (one per target language) — poll each.
   - Poll `GET /video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/progress`
     (note the singular `space`; `spaceSeq` is required) at intervals of at least 5 seconds.
   - Status lives in `progressReason`, not `status`. Values:
     `Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating |
     Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed`.
     Done when `progressReason === "Completed"`; failed when `"Failed"` (see `hasFailed`).
   - Treat `expectedRemainingTimeMinutes` as a rough hint only — it can go negative after completion.
   - Never block an HTTP handler on the polling loop — use a background worker/queue.

5. **Response file paths resolve against `https://portal-media.perso.ai`, not the API base.**
   - Fields like `videoFilePath`, `audioFilePath`, `thumbnailFilePath`, download links, `audioUrl`,
     and `thumbnailUrl` contain relative paths under `/perso-storage/...`.
   - Prepend `https://portal-media.perso.ai` (not `https://api.perso.ai`) to download the file.
   - These paths can contain spaces and non-ASCII characters verbatim, so URL-encode the path
     when fetching — an unencoded path fails.

6. **HTTP error codes follow a predictable map.**
   - 401 = `XP-API-KEY` header missing, misspelled, or key is Expired/Revoked.
   - 403 = key is valid but lacks permission on this Space.
   - 404 = usually `spaceSeq` or resource ID wrong. Verify the IDs before assuming the endpoint is broken.
   - 429 = rate limited. Back off exponentially.
   - 5xx = retry with backoff; include the Request ID from Usage logs when escalating.

   Error response bodies come in a few distinct shapes — parse defensively:
   - Gateway auth errors (handled before routing, so per-endpoint 401s are rarely seen directly):
     missing key `{"code":"G0001","message":"...","status":"UNAUTHORIZED"}`;
     invalid/expired key `{"code":"A0010","message":"...","status":"UNAUTHORIZED"}`.
   - Domain errors: `{"code":"VT4009","detailCode":"UNSUPPORTED_LANGUAGE_TTS_MODEL_PAIR","message":"...","status":"BAD_REQUEST"}`.
     The machine-readable field is `code` (not `errorCode`); `detailCode` disambiguates the reason.
   - Missing required parameter (RFC 7807): `{"type":"about:blank","title":"Bad Request","status":400,"detail":"Required parameter 'memberRole' is not present.",...}`.
   - Some server errors return the raw Spring shape: `{"timestamp":"...","status":500,"error":"...","path":"..."}`.

7. **`fileName` for SAS token must be URL-encoded.** Spaces, Korean/Japanese characters, parentheses all need encoding.

---


## Space API
Retrieve space banner information.

### GET /portal/api/v1/spaces
**List Space Banners**
Retrieve the list of space banners for all spaces the authenticated user belongs to.

Response (200):
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

Errors:
  - 404 PT0026: Space subscription info not found

---

### GET /portal/api/v1/spaces/{spaceSeq}
**Get Space Banner**
Retrieve the banner information for a specific space.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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

Errors:
  - 404 PT0026: Space subscription info not found
  - 401 PT0027: Not an approved member

---

## Media API
Upload video and audio files, validate media, manage external media imports, and download project output files.

### Direct File Upload (Video / Audio)

Uploading a file requires a multi-step process: obtain a temporary SAS token, upload the binary to Azure Blob Storage, then register the uploaded file with the server.

**Step 1: Get SAS Token** [GET] Auth: XP-API-KEY
`/file/api/upload/sas-token?fileName={fileName}`
Call the Get SAS Token endpoint to obtain a blobSasUrl. The token is valid for 30 minutes.
> The fileName must be URL-encoded.

**Step 2: Upload Binary to Azure Blob Storage** [PUT] Auth: None
`{blobSasUrl}`
Upload the file binary directly to the blobSasUrl via a PUT request. The SAS URL already contains authentication, so no Authorization header is required. This request goes directly to Azure — not to the Perso API server.
Required headers:
  x-ms-blob-type: BlockBlob
  Content-Type: application/octet-stream
```
curl -X PUT \
  -H "x-ms-blob-type: BlockBlob" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"/path/to/file.mp4" \
  "{blobSasUrl}"
```
> Returns 201 Created on success (empty body). A 403 means the SAS token has expired — call Get SAS Token again.

**Step 3: Register Uploaded File** [PUT] Auth: XP-API-KEY
`/file/api/upload/video (or /audio)`
Call Upload Video or Upload Audio to register the file. Pass the blobSasUrl as fileUrl. Stripping the query string (the '?...' portion) is recommended — the file still registers with it included, but stripping it keeps the stored path stable.
> The response includes a seq (media sequence) — use this as mediaSeq when requesting a translation via the Dubbing API.

**Step 4: Validate Media (Optional)** [POST] Auth: XP-API-KEY
`/file/api/v1/media/validate`
Call Validate Media to pre-check file constraints (extension, size, duration, resolution) before upload. This is optional but recommended to fail fast instead of waiting for a long upload to fail.
> Can be called before Step 2 to avoid uploading an invalid file.

### External Platform Upload (YouTube, TikTok, Google Drive)

Import videos from external platforms. The server downloads the video on your behalf.

**Step 1: Get External Metadata** [POST] Auth: XP-API-KEY
`/file/api/v1/video-translator/external/metadata`
Preview the media info (duration, resolution, size) before uploading.

**Step 2: Validate Media** [POST] Auth: XP-API-KEY
`/file/api/v1/media/validate`
Check constraints (size, duration, resolution) against your plan limits.
> Validates in 1-2 seconds. Skipping this step may result in a 10+ second wait before an error on invalid media.

**Step 3: Upload External Video** [PUT] Auth: XP-API-KEY
`/file/api/upload/video/external`
Start the import. This is synchronous — the server downloads the file before responding (may take up to 10 minutes).
> The response includes a seq for use as mediaSeq in the Dubbing API.

### PUT /file/api/upload/video
**Upload Video**
Upload a video file via URL. The server downloads the file from the given URL and stores it. Before calling this endpoint, you must first obtain a SAS token via the Get SAS Token endpoint and upload the file to the returned blobSasUrl. Pass the blob URL as the fileUrl parameter. The response includes a seq (media sequence) which is used as mediaSeq when requesting a translation. Note: videoFilePath and thumbnailFilePath in the response are relative paths containing perso-storage. To access the actual file, prepend https://portal-media.perso.ai (e.g. https://portal-media.perso.ai/perso-storage/.../video.mp4). The originalName in the response has its file extension removed (e.g. 'my_video.mp4' becomes 'my_video').

Request body:
  - spaceSeq (integer, required): The unique identifier of the space.
  - fileUrl (string, required): Direct access URL of the video file (the blobSasUrl from the SAS token step). Stripping the '?...' query string is recommended for a stable storage path, though it also registers with the query string included.
  - fileName (string, required): File name. URL-encoded names are automatically decoded.
  - sttMode (boolean, optional): Set to true when the file will be used for an STT project. On paid plans this raises the duration limit to 2 hours. Defaults to false.

Request example:
```json
{
  "spaceSeq": 1,
  "fileUrl": "https://example.com/video.mp4",
  "fileName": "my_video.mp4",
  "sttMode": false
}
```

Response (200):
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

Errors:
  - 400 F4003: Missing required parameter
  - 400 F4004: File size limit exceeded
  - 400 F4007: Invalid video type
  - 401 F4001: Unauthorized

---

### PUT /file/api/upload/audio
**Upload Audio**
Upload an audio file via URL. The server downloads the file from the given URL and stores it. Before calling this endpoint, you must first obtain a SAS token via the Get SAS Token endpoint and upload the file to the returned blobSasUrl. Pass the blob URL as the fileUrl parameter. The response includes a seq (media sequence) which is used as mediaSeq when requesting a translation. Note: audioFilePath and thumbnailFilePath in the response are relative paths containing perso-storage. To access the actual file, prepend https://portal-media.perso.ai (e.g. https://portal-media.perso.ai/perso-storage/.../audio.mp3). The originalName in the response has its file extension removed (e.g. 'my_audio.mp3' becomes 'my_audio').

Request body:
  - spaceSeq (integer, required): The unique identifier of the space.
  - fileUrl (string, required): Direct access URL of the audio file (the blobSasUrl from the SAS token step). Stripping the '?...' query string is recommended for a stable storage path, though it also registers with the query string included.
  - fileName (string, required): File name. URL-encoded names are automatically decoded.
  - sttMode (boolean, optional): Set to true when the file will be used for an STT project. On paid plans this raises the duration limit to 2 hours. Defaults to false.

Request example:
```json
{
  "spaceSeq": 1,
  "fileUrl": "https://portal-media.perso.ai/perso-storage/...",
  "fileName": "my_audio.mp3",
  "sttMode": false
}
```

Response (200):
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

Errors:
  - 400 F4003: Missing required parameter
  - 400 F4004: File size limit exceeded
  - 400 F4007: Invalid audio type
  - 401 F4001: Unauthorized

---

### PUT /file/api/upload/video/external
**Upload External Video**
Upload a video from an external platform (YouTube, TikTok, Google Drive). This is a synchronous operation — the server waits for the download to complete before responding. Timeout may take up to 10 minutes. Note: videoFilePath, audioFilePath, and thumbnailFilePath in the response are relative paths containing perso-storage. To access the actual file, prepend https://portal-media.perso.ai (e.g. https://portal-media.perso.ai/perso-storage/.../video.mp4).

Request body:
  - spaceSeq (integer, required): The unique identifier of the space.
  - url (string, required): External video URL (YouTube, TikTok, Google Drive).
  - lang (string, optional): Language code. (default: en)
  - sttMode (boolean, optional): Set to true when the file will be used for an STT project. On paid plans this raises the duration limit to 2 hours. Defaults to false.

Request example:
```json
{
  "spaceSeq": 1,
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "lang": "ko",
  "sttMode": false
}
```

Response (200):
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

Errors:
  - 400 F4003: Missing required parameter
  - 400 F4006: Not a valid external link
  - 400 F40012: Region unavailable external video
  - 400 F40014: Members only content
  - 400 F40015: Payment required content
  - 400 F40016: Invalid YouTube URL
  - 401 F4001: Unauthorized
  - 403 F4031: Unaccessible Google Drive link
  - 403 F4032: Geo-restricted YouTube video
  - 403 F4033: Age-restricted YouTube video
  - 403 F4035: Unaccessible external media link

---

### GET /file/api/upload/sas-token
**Get SAS Token**
Issue an Azure Blob Storage SAS token for direct file upload. This is the first step for uploading video or audio files. The token expires 30 minutes after issuance. Upload your file to the returned blobSasUrl via a PUT request before the expiration time, then call the Upload Video or Upload Audio endpoint with the blob URL. Use the blobSasUrl host exactly as returned — do not hardcode it, as it may be perso-saas-file-frontdoor.perso.ai rather than portal-media.perso.ai. Note that expirationDatetime is a naive UTC timestamp with no timezone suffix; do not parse it and compare against local time (that makes it look already expired or near-expiry) — simply upload within 30 minutes of issuance.

Query parameters:
  - fileName (string, required): File name (URL encoding required).

Response (200):
```json
{
  "blobSasUrl": "https://perso-saas-file-frontdoor.perso.ai/perso-storage/{path}/uuid_20260720.mp4?sv=2024-11-04&se=2026-02-19T13%3A00%3A00Z&sr=b&sp=rw&sig=...",
  "expirationDatetime": "2026-02-19T13:00:00"
}
```

Errors:
  - 400 F4003: Missing required parameter
  - 401 F4001: Unauthorized

---

### POST /file/api/v1/media/validate
**Validate Media**
Pre-validate media file metadata before upload. Checks extension, file size, duration, and resolution constraints without transferring the actual file.

Request body:
  - spaceSeq (integer, required): The unique identifier of the space.
  - durationMs (integer, required): Media duration in milliseconds.
  - originalName (string, required): Original file name.
  - mediaType (string, required): Type of the media file. [video, audio]
  - extension (string, required): File extension. [.mp4, .webm, .mov, .mp3, .wav]
  - size (integer, optional): File size in bytes (max 2GB).
  - width (integer, optional): Video width in pixels. Required when mediaType is 'video'. Min 201, max 7999.
  - height (integer, optional): Video height in pixels. Required when mediaType is 'video'. Min 201, max 7999.
  - thumbnailFilePath (string, optional): Thumbnail file path.
  - sttMode (boolean, optional): Set to true when the file will be used for an STT project. On paid plans this raises the duration limit to 2 hours. Defaults to false.

Request example:
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

Response (200):
```json
{
  "status": true
}
```

Errors:
  - 400 F4003: Missing required parameter
  - 400 F4004: File size limit exceeded
  - 400 F4007: Invalid video/audio type
  - 400 F4008: Video duration limit exceeded
  - 400 F4009: Video duration too short (min 1s)
  - 400 F40010: Video resolution limit exceeded
  - 400 F40011: Video resolution too low
  - 401 F4001: Unauthorized
  - 403 F4005: Plan usage limit exceeded
  - 422 F4220: Validation failed

---

### POST /file/api/v1/video-translator/external/metadata
**Get External Metadata**
Retrieve metadata from an external platform video (YouTube, TikTok, Google Drive) without downloading the file. Use this to preview media info before uploading.

Request body:
  - spaceSeq (integer, required): The unique identifier of the space.
  - url (string, required): External video URL (YouTube, TikTok, Google Drive).
  - lang (string, optional): Language code. (default: en)
  - sttMode (boolean, optional): Set to true when the file will be used for an STT project. On paid plans this raises the duration limit to 2 hours. Defaults to false.

Request example:
```json
{
  "spaceSeq": 1,
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "lang": "ko",
  "sttMode": false
}
```

Response (200):
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

Errors:
  - 400 F4003: Missing required parameter
  - 400 F4006: Not a valid external link
  - 400 F40016: Invalid YouTube URL
  - 400 F40017: Invalid media URL
  - 401 F4001: Unauthorized
  - 403 F4031: Unaccessible Google Drive link
  - 403 F4035: Unaccessible external media link

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/download-info
**Check Download Availability**
Before downloading files, check which files are currently available for download in your project. Each field returns true/false to indicate availability. Some fields may return null depending on the project type (video vs audio). Use the corresponding download target value for any field that returned true when calling the download endpoint.

Mapping between download-info boolean fields and download target values:
- hasTranslatedVideo -> target=dubbingVideo
- hasLipSyncVideo -> target=lipSyncVideo
- hasOriginalVoiceOnly -> target=originalVoiceAudio (original voice track)
- hasTranslatedVoice -> target=voiceAudio (translated voice; returns 500 if the project has no translated voice, e.g. Audio Separation projects)
- hasOriginalBackground / hasTranslatedBackground -> target=backgroundAudio
- hasOriginalSpeakerAudioCollection -> target=originalVoiceSpeakers
- hasSpeakerSegmentExcel -> target=speakerSegmentExcel
- hasSpeakerSegmentWithTranslationExcel -> target=speakerSegmentWithTranslationExcel
- hasScriptTimestamps -> target=scriptTimestamps
- hasOriginalSubBackground -> target=originalSubBackground
- hasZipDownload -> target=all (.tar archive)
- hasOriginalSubtitle / hasTranslatedSubtitle / hasOriginalSubtitleVtt -> no individual target; SRT/VTT files are only included in the target=all archive

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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
**Download Files**
Download project output files. Use the download-info endpoint first to check which files are available, then pass the corresponding target value. All returned download links are relative paths under /perso-storage/... — prepend https://portal-media.perso.ai to fetch them, and URL-encode the path since it may contain spaces or non-ASCII characters. zippedFileDownloadLink points to a .tar archive.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - target (string, required): The type of file to download. Use the download-info endpoint to check which targets are available. See the download-info endpoint description for the mapping between download-info boolean fields and target values. Matching is case-insensitive (voicewithBackgroundAudio and voiceWithBackgroundAudio both work). An unknown value returns 400 VT4001; a value that is valid in the enum but not present for this project may return 500. [dubbingVideo, lipSyncVideo, audioScript, originalVoiceAudio, voiceAudio, backgroundAudio, voicewithBackgroundAudio, translatedAudio, all, originalVoiceSpeakers, speakerSegmentExcel, speakerSegmentWithTranslationExcel, scriptTimestamps, originalSubBackground]

Response (200):
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

## Dubbing API
Core endpoints for video translation, project management, and file downloads.

### End-to-End Dubbing Workflow

Complete workflow from file upload to downloading the translated result.

**Step 1: Upload Media**
Upload your video or audio file using the File API. See the File API page for the detailed upload flow (SAS token → Azure Blob upload → register). The response seq value is your mediaSeq for the next step.
> Refer to the File API 'Direct File Upload' or 'External Platform Upload' guide.

**Step 2: Initialize Queue** [PUT] Auth: XP-API-KEY
`/video-translator/api/v1/projects/spaces/{spaceSeq}/queue`
Call the Usage API's Get User Queue endpoint to ensure the space has a translation queue. Despite being named 'Get User Queue', calling it with PUT creates/initializes the queue. Without this, the first translation request in a new space will fail with 'space queue not found'.
> Only required once per space. Subsequent translations do not need this step.

**Step 3: Request Translation** [POST] Auth: XP-API-KEY
`/video-translator/api/v1/projects/spaces/{spaceSeq}/translate`
Submit the translation request with the mediaSeq from Step 1. Use sourceLanguageCode 'auto' for automatic detection, or a specific code from the Language API.

**Step 4: Poll Progress** [GET] Auth: XP-API-KEY
`/video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/progress`
Poll the project status every 5 seconds. progressReason values: Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating | Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed.
> Do not poll more frequently than every 5 seconds.

**Step 5: Download Result** [GET] Auth: XP-API-KEY
`/video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/download?target=dubbingVideo`
Once complete, download the output files. Use the download-info endpoint first to check available file types.
> Working target values: dubbingVideo, lipSyncVideo, voiceAudio, originalVoiceAudio, backgroundAudio, voicewithBackgroundAudio, originalVoiceSpeakers, speakerSegmentExcel, speakerSegmentWithTranslationExcel, scriptTimestamps, originalSubBackground, audioScript, all. Subtitles (SRT) cannot be fetched as an individual target — they are only delivered inside the target=all archive (.tar). Requesting a file that download-info reports as false may return 500 rather than a 4xx.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/translate
**Request Translation**
Submit a video or audio translation request based on uploaded media files. The mediaSeq is the seq value returned from the Upload Video or Upload Audio endpoint in the File API. New integrations should use `targetLanguages` (per-language TTS model selection). The legacy `targetLanguageCodes` + `ttsModel` pair is still accepted for backward compatibility, but is deprecated. If you receive a 'space queue not found' error, you must first call the PUT /video-translator/api/v1/projects/spaces/{spaceSeq}/queue endpoint (Usage API) to initialize the queue before retrying.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - mediaSeq (integer, required): The media sequence (seq) returned from the Upload Video or Upload Audio API response.
  - isVideoProject (boolean, required): Whether this is a video project (true) or audio project (false).
  - sourceLanguageCode (string, required): Source language code. Use 'auto' for automatic language detection, or a specific code from the Language API (e.g. 'en', 'ko'). Do not send an empty string — use 'auto' instead.
  - targetLanguageCodes (string[], optional): (Deprecated since 2026-05-14) Array of target language codes to translate into. New integrations should use `targetLanguages` instead. If both fields are provided, `targetLanguages` takes precedence. Either `targetLanguageCodes` or `targetLanguages` must be provided.
  - targetLanguages (object[], optional): Recommended. List of target language and TTS model pairs. When provided, this field takes precedence over `targetLanguageCodes` and the top-level `ttsModel`. Either `targetLanguageCodes` or `targetLanguages` must be provided.
    - languageCode (string, required): Target language code (e.g. 'en', 'ko'). Must be a valid code returned by the Language API.
    - ttsModel (string, optional): TTS model for this language. If omitted, LINNET_4 is used, or ORIOLE when the language does not support LINNET_4. Must be in the language's supportedTtsModels (Language API), otherwise 400 VT4009. Ignored for STT / AudioSeparation.
      - ORIOLE: Natural local pronunciation. Default where LINNET_4 is unavailable.
      - WREN: Rich intonation.
      - LINNET_3: Keeps the original manner of speech.
      - LINNET_4: Balanced delivery that follows the context. Default when omitted.
      - FINCH: Simplified basic dubbing. Pro plan and above (403 VT40314 otherwise).
      - NIGHTINGALE: Multi-dimensional emotional expression. Pro plan and above, priced separately; no lip sync, SRT, RED speed, voice change or per-sentence regeneration (400 VT40918).
    - cloningStrength (integer, optional): NIGHTINGALE only. How strongly the original voice is cloned, 1 to 10. Ignored for other TTS models. (default: 7)
  - numberOfSpeakers (integer, optional): Number of speakers in the video for multi-speaker detection. (default: 1)
  - preferredSpeedType (string, required): Processing speed preference. [GREEN, RED]
  - withLipSync (boolean, optional): Whether to include lip sync processing. Not supported with NIGHTINGALE (400 VT40918).
  - customDictionaryBlobPath (string, optional): Storage path to a custom dictionary file.
  - srtBlobPath (string, optional): Storage path to an SRT subtitle file. Not supported with NIGHTINGALE (400 VT40918).
  - ttsModel (string, optional) (deprecated): (Deprecated since 2026-05-14) Single TTS model applied to all target languages. New integrations should specify `ttsModel` per language inside `targetLanguages`. Each value must be in the target language's supportedTtsModels (see the Language API).
    - ORIOLE: Natural local pronunciation. Default where LINNET_4 is unavailable.
    - WREN: Rich intonation.
    - LINNET_3: Keeps the original manner of speech.
    - LINNET_4: Balanced delivery that follows the context. Default when omitted.
    - FINCH: Simplified basic dubbing. Pro plan and above (403 VT40314 otherwise).
    - NIGHTINGALE: Multi-dimensional emotional expression. Pro plan and above, priced separately; no lip sync, SRT, RED speed, voice change or per-sentence regeneration (400 VT40918).
  - title (string, optional): Project title. If omitted, the media file name is used.

Request example:
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

Response (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [101, 102]
  }
}
```

Errors:
  - 404 VT4043: Source language not found
  - 404 VT4044: Target language not found
  - 404 VT4042: Video not found
  - 503 VT5034: Queue full
  - 402 VT4021: Insufficient credits
  - 400 VT4009: Target language and TTS model pair is not supported
  - 400 VT40918: The TTS model does not support this option (NIGHTINGALE with lip sync, SRT upload or RED speed)
  - 403 VT40314: The TTS model is not available on the plan (FINCH and NIGHTINGALE require Pro or above)
  - 400 VT40022: cloningStrength out of range (1 to 10)

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}
**Get Project**
Retrieve detailed information about a specific translation project. ttsModel is the project's TTS model (ORIOLE, WREN, LINNET_3, LINNET_4, FINCH, NIGHTINGALE; null for STT / audio separation projects). The progressReason field indicates the current status: Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating | Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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

Errors:
  - 404 VT4041: Project not found
  - 404 VT4045: Project deleted
  - 403 VT4031: Access denied
  - 409 VT4091: Video generation failed

---

### GET /video-translator/api/v1/projects/spaces/{spaceSeq}
**List Projects**
Retrieve a list of active projects within a space.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - memberRole (string, required): The role of the member requesting the list. [enterprise_owner, space_owner, space_manager, space_member, individual, developer]
  - size (integer, required): Number of items per page.
  - offset (integer, required): Starting position for pagination.
  - sortType (string, optional): Sort field. (default: update_date) [update_date, title]
  - sortDirection (string, required): Sort direction. [asc, desc]
  - type (string, optional): Filter by project generation type. [DUBBING, LIP_SYNC]

Response (200):
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
**Get Script**
Retrieve the project script with sentence-level translations, matching rates, and speaker information. matchingRate and rewrite can be null for a given sentence. Each speaker exposes a projectSpeakerSeq, which is the value required by the Temp Save Draft endpoint.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - cursorId (integer, optional): Cursor-based pagination ID. Omit for the first request.
  - size (integer, optional): Number of sentences per page. (default: 10000)

Response (200):
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
**Poll Progress**
Poll the current progress of a translation project. Recommended polling interval: every 5 seconds. Completion: progressReason === 'Completed'. Failure: progressReason === 'Failed'. Do not poll more frequently than every 5 seconds to avoid rate limiting. progressReason values: Enqueue Pending | Slow Mode Pending | Uploading | Transcribing | Translating | Generating Voice | Analyzing Lip Sync | Applying Lip Sync | Completed | Failed.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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
**Cancel Project**
Cancel a pending project. Only available for GREEN zone projects in PENDING initial export state. Cancellation only works while the project is still queued (pending); when the GREEN queue is empty, processing starts immediately, so a 400 VT4004 (cancellation not allowed) is common even right after creation.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (201):
```json
{
  "result": {}
}
```

Errors:
  - 400 VT4004: Cancellation not allowed
  - 403 VT4033: No access to the space

---

### GET /video-translator/api/v1/projects/{projectSeq}/share
**Get Share Link**
Retrieve the encrypted share query string for sharing a project externally.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.

Response (200):
```json
{
  "shareQuery": "eyJhbGciOiJIUzI1NiJ9..."
}
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/share
**Toggle Share**
Enable or disable the share URL for a project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.

Query parameters:
  - sharedStatus (boolean, required): Whether to enable (true) or disable (false) sharing.

Response (200):
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
**Get Video Info**
Retrieve metadata for an individual video including title, duration, resolution, and status.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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

Errors:
  - 403 VT4033: No access to the space
  - 404 VT4041: Project not found
  - 404 VT4042: Video not found

---

### GET /video-translator/api/v1/projects/{projectSeq}/space/{spaceSeq}/export-history
**Get Export History**
Retrieve the export and upload history for a project with pagination.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - page (integer, optional): Page number (zero-based). (default: 0)
  - size (integer, optional): Number of items per page.
  - sort (string, optional): Sort criteria.

Response (200):
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
**Check Retranslation Status**
Check whether retranslation is available for a project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
```json
{
  "retranslateAvailable": true
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/used-features
**Get Used Features**
Check which optional features were used when creating the project, such as custom dictionary or SRT upload.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
```json
{
  "result": {
    "usedCustomDictionary": false,
    "usedSrtUpload": false
  }
}
```

---

## Editing API
Edit, translate, and manage individual audio sentences within a project.

### PATCH /video-translator/api/v1/project/{projectSeq}/audio-sentence/{sentenceSeq}
**Translate Sentence**
Request translation or retranslation for a specific sentence within a project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - sentenceSeq (integer, required): The unique identifier of the sentence.

Request body:
  - targetText (string, required): The text to translate or the updated translation.

Request example:
```json
{
  "targetText": "Updated translation text"
}
```

Response (200):
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
**Generate Audio**
Generate a translated audio file for a specific sentence. Not available for NIGHTINGALE projects (400 VT40918) — use Request Proofread to re-render.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - audioSentenceSeq (integer, required): The unique identifier of the audio sentence.

Request body:
  - targetText (string, required): The text to generate audio for.

Request example:
```json
{
  "targetText": "Text to generate audio for"
}
```

Response (200):
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
**Reset Translation**
Reset a translation back to its original proofread state.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - audioSentenceSeq (integer, required): The unique identifier of the audio sentence.

Response (200):
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
**Cancel Translation**
Cancel an in-progress translation for a specific sentence.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - audioSentenceSeq (integer, required): The unique identifier of the audio sentence.

Response (200):
```json
{
  "result": {}
}
```

---

### POST /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/temp-save
**Temp Save Draft**
Temporarily save a translation draft for a paragraph without triggering full processing. On NIGHTINGALE projects, changing the original text clears that sentence's translation until the next proofread re-translates it.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - audioSentenceSeq (integer, required): The unique identifier of the audio sentence.

Request body:
  - originalDraftText (string, required): The draft original text to temporarily save.
  - projectSpeakerSeq (integer, required): The speaker identifier to temporarily assign. Required for project version 2 speaker changes. Obtain it from the speakers[].projectSpeakerSeq field of the Get Script response.

Request example:
```json
{
  "originalDraftText": "Draft translation text",
  "projectSpeakerSeq": 12345
}
```

Response (200):
```json
{
  "result": null
}
```

Errors:
  - 400 VT40026: NIGHTINGALE project: the speaker change makes this sentence overlap another sentence of the same speaker
  - 400 VT40027: NIGHTINGALE project: original text is empty

---

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/speakers/from-sentence
**Add Speaker from Sentence**
Add a new speaker to a dubbing project by cloning a voice from a reference sentence. The original speaker audio of the reference sentence segment becomes the clone source, and the request completes synchronously once the clone is ready (typically a few seconds). The speaker name (e.g. 'Speaker 3') and speakerOrderIndex are assigned automatically by the system — the next number after the project's highest existing speaker order (indexes of deleted speakers are never reused); the order index matches the SPEAKER_NN labels used in deliverables. The reference sentence is also reassigned to the new speaker as a draft change, so regenerate its audio afterwards to apply the new voice. Pass the sentences[].seq value from the Get Script response as sourceSentenceSeq. After adding, call Get Script again to obtain the new speaker's projectSpeakerSeq for use with the Temp Save Draft endpoint.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - sourceSentenceSeq (integer, required): The reference sentence identifier. The original speaker audio of this sentence segment is used as the clone source. Use the sentences[].seq value from the Get Script response.

Request example:
```json
{
  "sourceSentenceSeq": 1234
}
```

Response (200):
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

Errors:
  - 404 VT4041: Project not found
  - 404 VT4042: Reference sentence not found, or it does not belong to this project
  - 400 VT4007: Not a dubbing project — sentence-based speaker add is available for dubbing projects only
  - 403 VT4037: Editing is not available on the Free plan
  - 409 VT4099: Project version 2 or later is required
  - 409 VT40915: Speaker count limit exceeded for this project

---

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/speakers/bulk-change
**Bulk Change Speakers**
Change the speaker of every script assigned to a source speaker to a target speaker in one call. The sourceSpeakerSeq/targetSpeakerSeq voice-id pair is always required. Send sourceProjectSpeakerSeq/targetProjectSpeakerSeq as well to identify the speakers by those values — a speaker that already has a voice-library voice applied can then still be selected. These two fields are required for Dubbing projects and recommended for all project version 2 projects. The changed sentences are saved as draft changes carrying the target speaker's voice and are marked for regeneration — regenerate the project afterwards to render the audio. Available for STT / Audio Separation / Dubbing projects. Obtain both values from the speakers[].projectSpeakerSeq field of the Get Script response. (STT / Audio Separation projects also keep the existing request format: the sourceSpeakerSeq/targetSpeakerSeq voice-id pair, plus targetProjectSpeakerSeq on project version 2.)

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - sourceProjectSpeakerSeq (integer, required): projectSpeakerSeq of the speaker whose scripts are moved. Required for Dubbing, recommended elsewhere on project version 2. Use a speakers[].projectSpeakerSeq value from the Get Script response.
  - targetProjectSpeakerSeq (integer, required): projectSpeakerSeq of the speaker the scripts are changed to. Required for Dubbing, recommended elsewhere on project version 2. Use a speakers[].projectSpeakerSeq value from the Get Script response.
  - sourceSpeakerSeq (string, required): Voice id of the source speaker (always required). Not used for speaker identification when the projectSpeakerSeq pair is sent.
  - targetSpeakerSeq (string, required): Voice id of the target speaker (always required). Not used for speaker identification when the projectSpeakerSeq pair is sent.

Request example:
```json
{
  "sourceSpeakerSeq": "pvtv-3789224e24134dda077155264e8b1b64",
  "targetSpeakerSeq": "pvtv-69aaeacedfb9defbffa828828b872a26",
  "sourceProjectSpeakerSeq": 807,
  "targetProjectSpeakerSeq": 808
}
```

Response (200):
```json
{
  "result": null
}
```

Errors:
  - 400 VT4001: source and target speakers are the same, the projectSpeakerSeq pair is missing on a Dubbing project, or the pair was sent to a project version 1 project
  - 400 VT4007: Not an STT / Audio Separation / Dubbing project
  - 404 VT40414: source or target speaker is not an active speaker in the project

---

### POST /video-translator/api/v1/project/{projectSeq}/audio-sentence/{audioSentenceSeq}/match-rewrite
**Get Match Rate & Rewrite**
Query the matching rate and rewrite information for a translated sentence to evaluate translation quality.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - audioSentenceSeq (integer, required): The unique identifier of the audio sentence.

Request body:
  - targetText (string, required): The translated text to evaluate.

Request example:
```json
{
  "targetText": "Translation text to evaluate"
}
```

Response (200):
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
**Request Proofread**
Submit a proofread request for the project's translations. This re-processes all translations with quality improvements. For NIGHTINGALE projects the first proofread is free and each later one costs the same as the initial dubbing (see Estimate Quota Usage with projectSeq); RED speed is not supported (400 VT40918).

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - isLipSync (boolean, optional): Whether to enable lip sync for the proofread output.
  - experimentKey (string, optional): Experiment key for A/B testing configurations.
  - preferredSpeedType (string, required): Processing speed preference. [GREEN, RED]

Request example:
```json
{
  "isLipSync": false,
  "preferredSpeedType": "GREEN"
}
```

Response (200):
```json
{
  "result": {}
}
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/title
**Update Title**
Update the title of a project. If the title is empty or null, it defaults to 'Untitled'.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - newTitle (string, optional): The new project title. Defaults to 'Untitled' if empty.

Request example:
```json
{
  "newTitle": "Updated Project Name"
}
```

Response (200):
```json
// Empty response body
```

---

### PATCH /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/access
**Update Access**
Modify the access permissions for a project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - permission (string, required): The access permission type. [individual, all]

Response (200):
```json
// Empty response body
```

Errors:
  - 403 VT4033: No access to the space
  - 404 VT4046: Project space not found

---

### DELETE /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}
**Delete Project**
Permanently delete a project. Returns 204 No Content on success.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (204):
```json
// No content returned
```

Errors:
  - 404 VT4041: Project not found
  - 404 VT4045: Project deleted
  - 403 VT4031: Access denied

---

## Usage API
Monitor quota consumption, queue status, and estimated credit usage.

### GET /video-translator/api/v1/projects/spaces/{spaceSeq}/plan/status
**Get User Quota**
Retrieve the quota information and plan status for a user within a space.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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
**Estimate Quota Usage**
Calculate the credits that will be consumed for a given media file based on its type, duration, translation type and TTS models. Credits = whole seconds of media × rate per second × number of target languages.
- The rate per second differs by TTS model and translation type; use this API to get the price.
- Video at 4K (3840×2160) or above costs 3× for dubbing (FINCH included) and lip sync. NIGHTINGALE, STT and audio separation are not affected by resolution.
- Send ttsModelCounts to price a mix of models per language (e.g. NIGHTINGALE:1,ORIOLE:2,FINCH:1); targetLanguageSize is then ignored.
- NIGHTINGALE proofread: the first proofread after the initial export is free; each later proofread costs the same as the initial dubbing. Send projectSeq to get the proofread price and exportCount.
- expectedUsedQuota is the list price. promotionExpectedUsedQuota is the discounted price that will actually be deducted; it equals expectedUsedQuota when no discount applies.
- width and height are required for video — omitting them returns 400 VT4001. Not needed for audio.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - mediaType (string, required): The type of media. [video, audio]
  - translateType (string, optional): What will be requested. TRANSLATE = dubbing, TRANSLATE_WITH_LIPSYNC = dubbing + lip sync, LIPSYNC = lip sync only. When set, lipSync is ignored. [TRANSLATE, TRANSLATE_WITH_LIPSYNC, LIPSYNC, STT, AUDIO_SEPARATION]
  - lipSync (boolean, optional) (deprecated): Whether lip sync is included. Use translateType instead.
  - durationMs (integer, required): Media duration in milliseconds.
  - width (integer, optional): Video width in pixels. Required when mediaType is video (400 VT4001 if missing).
  - height (integer, optional): Video height in pixels. Required when mediaType is video (400 VT4001 if missing).
  - targetLanguageSize (integer, optional): Number of target languages. Ignored when ttsModelCounts is sent. (default: 1)
  - ttsModelCounts (string, optional): Number of target languages per TTS model as MODEL:count pairs separated by commas, e.g. NIGHTINGALE:1,ORIOLE:2,FINCH:1. Use this whenever target languages use different models.
  - projectSeq (integer, optional): Existing project to price a proofread for. The response then contains the proofread price and exportCount (initial export = 1, +1 per completed proofread; counted for NIGHTINGALE only).

Response (200):
```json
{
  "result": {
    "expectedUsedQuota": 720.0,
    "promotionExpectedUsedQuota": 540.0,
    "exportCount": null
  }
}
```

Errors:
  - 400 VT4001: Invalid parameter (missing width/height for video, malformed ttsModelCounts, unknown model or count below 1)
  - 400 VT40918: NIGHTINGALE cannot be combined with lip sync

---

### PUT /video-translator/api/v1/projects/spaces/{spaceSeq}/queue
**Get User Queue**
Despite the name, calling this with PUT initializes (creates) the queue if it does not exist. Retrieve or initialize the queue for a user within a space. If no queue exists, a new one is automatically created and returned. This endpoint must be called before requesting a translation if the space does not yet have an initialized queue — otherwise the translation request will fail with a 'space queue not found' error. Both GET and PUT methods are supported. Internally, the service fetches the user's plan options from the Credit service, retrieves quota information, and looks up the TranslateQueue — creating a new one if it does not exist.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
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

## Lip Sync API
Request lip sync video generation and retrieve generation history.

### POST /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/lip-sync
**Request Lip Sync**
Submit a lip sync video generation request for a translated project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - preferredSpeedType (string, required): Processing speed preference. [GREEN, RED]
  - title (string, optional): Project title. If omitted, the parent project title is used.

Request example:
```json
{
  "preferredSpeedType": "GREEN",
  "title": "My Lip Sync Project"
}
```

Response (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [1, 2, 3]
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/lip-sync/generated
**Get Generation History**
Retrieve a paginated list of lip sync generation history for a project.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - page (integer, optional): Page number. (default: 1)
  - pageSize (integer, optional): Number of items per page. (default: 10)

Response (200):
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

## STT API
Create Speech-to-Text projects and retrieve generated STT scripts.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/stt
**Create STT Project**
Create a Speech-to-Text (STT) project from an uploaded media file. The mediaSeq is the seq value returned from the Upload Video or Upload Audio endpoint in the File API. If you receive a 'space queue not found' error, first call PUT /video-translator/api/v1/projects/spaces/{spaceSeq}/queue (Usage API) to initialize the queue, then retry.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - mediaSeq (integer, required): The media sequence (seq) returned from the Upload Video or Upload Audio API response.
  - isVideoProject (boolean, required): Whether this is a video project (true) or audio project (false).
  - title (string, optional): Project title. If omitted, the media file name is used.

Request example:
```json
{
  "mediaSeq": 12345,
  "isVideoProject": true,
  "title": "My STT Project"
}
```

Response (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [101]
  }
}
```

---

### POST /video-translator/api/v1/project/{projectSeq}/space/{spaceSeq}/stt/apply-changes
**Regenerate STT**
Request regeneration of the STT (Speech-to-Text) results for a project after applying script edits.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Response (200):
```json
{
  "result": null
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/stt/script
**Get STT Project Script**
Retrieve the script for a completed STT project. Uses cursor-based pagination — omit cursorId on the first request. Each sentence's originalDraftText may be null; use originalText for the transcribed content. Each speaker's voiceId carries the same pvtv- identifier as externalSpeakerSeq.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - cursorId (integer, optional): Cursor-based pagination ID. Omit on the first request; pass the last item's cursor value on subsequent requests.
  - size (integer, optional): Page size. (default: 10000)

Response (200):
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

## Audio Separation API
Create Audio Separation projects that split media into voice and background audio tracks, and retrieve the generated script.

### POST /video-translator/api/v1/projects/spaces/{spaceSeq}/audio-separation
**Create Audio Separation Project**
Create an Audio Separation project that splits a media file into voice and background audio tracks. If you receive a 'space queue not found' error, first call PUT /video-translator/api/v1/projects/spaces/{spaceSeq}/queue (Usage API) to initialize the queue, then retry.

Path parameters:
  - spaceSeq (integer, required): The unique identifier of the space.

Request body:
  - mediaSeq (integer, required): The media sequence (seq) returned from the Upload Video or Upload Audio API response.
  - isVideoProject (boolean, required): Whether this is a video project (true) or audio project (false).
  - title (string, optional): Project title. If omitted, the media file name is used.

Request example:
```json
{
  "mediaSeq": 12345,
  "isVideoProject": false,
  "title": "My Audio Separation Project"
}
```

Response (200):
```json
{
  "result": {
    "startGenerateProjectIdList": [102]
  }
}
```

---

### GET /video-translator/api/v1/projects/{projectSeq}/spaces/{spaceSeq}/audio-separation/script
**Get Audio Separation Project Script**
Retrieve the script for a completed Audio Separation project. Uses cursor-based pagination — omit cursorId on the first request. Each sentence's originalDraftText may be null; use originalText for the transcribed content. Each speaker's voiceId carries the same pvtv- identifier as externalSpeakerSeq.

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.
  - spaceSeq (integer, required): The unique identifier of the space.

Query parameters:
  - cursorId (integer, optional): Cursor-based pagination ID. Omit on the first request; pass the last item's cursor value on subsequent requests.
  - size (integer, optional): Page size. (default: 10000)

Response (200):
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

## Language API
Retrieve the list of languages available for dubbing and translation.

### GET /video-translator/api/v1/languages
**List Languages**
Returns all supported languages with their codes, names, and the TTS models each language supports. This is the only endpoint for checking TTS model support — there is no dedicated model-lookup endpoint.
- supportedTtsModels: valid ttsModel values when the language is a translation target — ORIOLE, WREN, LINNET_3, LINNET_4, FINCH, NIGHTINGALE. Validate against it before submitting a translation — an unsupported pair returns 400 VT4009. The array is unordered.
- The same code can appear more than once, distinguished by languageTag (e.g. English (US) = "default", English (UK) = "en-GB"; likewise pt-PT, es-ES).
- code "auto" (Auto Detect) is for sourceLanguageCode only — it has an empty supportedTtsModels and cannot be a target.
- Experimental languages are flagged via experiment.

Response (200):
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

## Feedback API
Submit and retrieve feedback ratings for translated projects.

### POST /video-translator/api/v1/projects/feedbacks
**Submit Feedback**
Submit a feedback rating for a specific project. Ratings must be between 1 and 5.

Request body:
  - projectSeq (integer, required): The unique identifier of the project.
  - rating (integer, required): Feedback score from 1 to 5.

Request example:
```json
{
  "projectSeq": 101,
  "rating": 4
}
```

Response (200):
```json
{
  "averageRating": 4.5,
  "count": 10
}
```

Errors:
  - 404 VT4041: Project not found
  - 404 VT4045: Project has been deleted

---

### GET /video-translator/api/v1/projects/feedbacks
**Get Feedback**
Retrieve the feedback rating you submitted for a specific project. Returns 204 No Content if no feedback has been submitted.

Query parameters:
  - projectSeq (integer, required): The unique identifier of the project.

Response (200):
```json
{
  "rating": 4
}
```

Errors:
  - 404 VT4041: Project not found
  - 404 VT4045: Project has been deleted

---

## Community Spotlight API
Browse featured public projects and shared translations.

### GET /video-translator/api/v1/projects/recommended
**List Featured Projects**
Retrieve a paginated list of projects featured in the Community Spotlight. This is a public endpoint — no XP-API-KEY is required.

Query parameters:
  - page (integer, optional): Page number (zero-based). (default: 0)
  - size (integer, optional): Number of items per page.
  - languageCode (string, optional): Filter by source language code (e.g. ko, en, ja).

Response (200):
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
**Get Featured Project**
Retrieve detailed information about a specific featured project. This is a public endpoint — no XP-API-KEY is required. The response is not wrapped in a result object. File URLs are relative /perso-storage/... paths (prepend https://portal-media.perso.ai).

Path parameters:
  - projectSeq (integer, required): The unique identifier of the project.

Response (200):
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

Errors:
  - 404 VT4041: Project not found

---

### GET /video-translator/api/v1/projects/shared/{sharedQuery}
**Get Shared Project**
Retrieve project information using an encrypted share query string. This is a public endpoint — no XP-API-KEY is required. The response is not wrapped in a result object. File URLs are relative /perso-storage/... paths (prepend https://portal-media.perso.ai).

Path parameters:
  - sharedQuery (string, required): Encrypted share query string.

Response (200):
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

Errors:
  - 403 VT4035: Sharing is disabled for this project (SHARED_NOT_ACCESSIBLE)

---