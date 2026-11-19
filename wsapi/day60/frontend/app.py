"""Streamlit Presentation Layer — 탭별 UI, 모든 실제 API 호출은 FastAPI에 위임."""
import json
import os
import sys
from pathlib import Path
import streamlit as st

# 'streamlit run frontend/app.py' 실행 시 모듈 검색 경로를 명확히 합니다.
sys.path.insert(0,str(Path(__file__).resolve().parent))
import api_client as api

st.set_page_config(page_title="Perso AI Studio | Day60",layout="wide",page_icon="🎙️")
st.title("Perso API 통합 미디어 스튜디오")
st.caption("Day60 | Streamlit → FastAPI → Perso / PostgreSQL | 실제 API 호출 시 과금 가능")

if "space_seq" not in st.session_state:
    st.session_state.space_seq=0
if "media_seq" not in st.session_state:
    st.session_state.media_seq=0

with st.sidebar:
    st.subheader("연결 설정")
    st.write("백엔드:",api.BASE)
    try:
        health=api.get("/api/health")
        st.success("FastAPI 연결 정상" if health.get("ok") else "응답 확인 필요")
    except api.ApiError as exc:
        st.error(str(exc))
    space=st.number_input("Space Seq",min_value=0,step=1,key="space_seq")
    if st.button("Space 목록 조회"):
        try:
            data=api.get("/api/spaces")
            st.json(data)
            st.info("목록의 실제 spaceSeq를 위 필드에 입력해 주세요.")
        except api.ApiError as exc:st.error(str(exc))
    if st.button("언어 목록 조회"):
        try:st.json(api.get("/api/languages"))
        except api.ApiError as exc:st.error(str(exc))

upload_tab,create_tab,status_tab,result_tab=st.tabs(["1. 미디어 업로드","2. 작업 생성","3. 작업 이력/상태","4. 결과/스크립트"])

with upload_tab:
    st.subheader("SAS → Blob → Media 등록")
    kind=st.radio("미디어 유형",["audio","video"],horizontal=True)
    allowed=["wav","mp3"] if kind=="audio" else ["mp4","mov","webm"]
    file=st.file_uploader("업로드할 파일을 선택하세요",type=allowed)
    st.warning("최대 파일 크기는 백엔드 MAX_UPLOAD_MB 값입니다. 실제 업로드에는 네트워크와 API 비용이 발생할 수 있습니다.")
    if st.button("실제 업로드 수행",disabled=file is None or space<=0):
        try:
            with st.spinner("Perso에 업로드하고 DB에 등록하고 있습니다..."):
                output=api.upload_file(file,int(space),kind)
            st.session_state.media_seq=output["mediaSeq"]
            st.success(f"업로드 완료: mediaSeq={output['mediaSeq']}")
            st.json(output)
        except api.ApiError as exc:st.error(str(exc))

with create_tab:
    st.subheader("STT / Audio Separation / Dubbing / Lip Sync")
    task=st.selectbox("처리 기능",["stt","audio-separation","dubbing","lip-sync"])
    media=st.number_input("mediaSeq (업로드 결과)",min_value=0,step=1,key="media_seq")
    title=st.text_input("프로젝트 제목",value="day60 실습")
    media_kind=st.radio("업로드 미디어",["audio","video"],horizontal=True)
    if task=="dubbing":
        src=st.text_input("원본 언어 코드",value="auto")
        dst=st.text_input("번역 언어 코드",value="ko")
        tts=st.text_input("TTS 모델",value="LINNET_4",help="/api/languages의 supportedTtsModels를 확인하세요")
        speakers=st.number_input("화자 수",min_value=1,max_value=20,value=1)
        inline_lip=st.checkbox("더빙 생성과 함께 립싱크",value=False)
    if task=="lip-sync":
        parent=st.number_input("완료된 Dubbing projectSeq",min_value=0,step=1)
    speed=st.selectbox("생성 속도",["GREEN","RED"])
    confirmed=st.checkbox("Perso API의 실제 과금 가능성을 확인했고 생성을 승인합니다.",value=False)
    if st.button("작업 생성 요청",disabled=not confirmed or space<=0):
        if task!="lip-sync" and media<=0:
            st.error("업로드로 발급받은 mediaSeq를 입력해 주세요.")
        elif task=="lip-sync" and parent<=0:
            st.error("완료된 더빙 프로젝트 ID를 입력해 주세요.")
        else:
            if task=="lip-sync":
                body={"space_seq":int(space),"parent_project_seq":int(parent),
                  "title":title,"preferred_speed_type":speed,"confirm_cost":True}
                path="/api/jobs/lip-sync"
            else:
                body={"space_seq":int(space),"media_seq":int(media),"kind":task,
                  "is_video_project":media_kind=="video","title":title,"confirm_cost":True,
                  "preferred_speed_type":speed}
                if task=="dubbing":
                    body.update({"source_language_code":src,"target_language_code":dst,
                      "tts_model":tts,"number_of_speakers":int(speakers),"with_lip_sync":inline_lip})
                path="/api/jobs"
            try:
                with st.spinner("Perso 프로젝트 생성 중..."):
                    out=api.post(path,body)
                st.success(f"생성 요청 완료: projectSeqList={out['projectSeqList']}")
                st.json(out)
            except api.ApiError as exc:st.error(str(exc))

with status_tab:
    st.subheader("PostgreSQL 작업 이력")
    if st.button("DB 작업 목록 새로고침"):
        try:
            jobs=api.get("/api/jobs",space_seq=int(space) if space>0 else None)
            st.session_state.jobs=jobs
        except api.ApiError as exc:st.error(str(exc))
    jobs=st.session_state.get("jobs",[])
    if jobs:
        st.dataframe(jobs,use_container_width=True,hide_index=True)
    else:st.info("'DB 작업 목록 새로고침'을 눌러 기록을 조회하세요.")
    pid=st.number_input("상태를 확인할 projectSeq",min_value=1,value=1,step=1,key="status_pid")
    st.caption("자동 폴링은 5초 간격이며 Completed/Failed에서 멈춥니다. "
               "일시적 장애는 서버의 GET 재시도·백오프가 처리합니다.")
    poll_key = f"{int(space)}:{int(pid)}"
    # 작업을 바꾸면 이전 작업을 자동으로 계속 조회하지 않도록 해제합니다.
    if st.session_state.get("poll_key") != poll_key:
        st.session_state.poll_key = poll_key
        st.session_state.auto_poll = False
        st.session_state.pop("latest_progress", None)
        st.session_state.poll_error_count = 0
    if st.session_state.pop("poll_stop_pending", False):
        # 토글 위젯 생성 전에 상태를 변경합니다.
        st.session_state.auto_poll = False
    auto_poll = st.toggle("5초 간격 자동 상태 조회", key="auto_poll", disabled=space<=0)
    if st.button("진행 상태 1회 조회 / DB 갱신", disabled=space<=0 or auto_poll):
        try:
            st.session_state.latest_progress = api.get(
                f"/api/jobs/{int(space)}/{int(pid)}/progress")
        except api.ApiError as exc:
            st.error(str(exc))

    # Fragment는 전체 페이지를 다시 실행하지 않고 지정 간격마다 해당 영역을 갱신합니다.
    # 중복 요청 방지를 위해 Streamlit이 한 세션에서 이 함수를 순차적으로 실행합니다.
    @st.fragment(run_every="5s" if auto_poll else None)
    def progress_panel(selected_space: int, selected_project: int, enabled: bool):
        if enabled:
            try:
                latest = api.get(f"/api/jobs/{selected_space}/{selected_project}/progress")
                st.session_state.latest_progress = latest
                st.session_state.poll_error_count = 0
                if str(latest.get("status", "")).lower() in {"completed", "failed"}:
                    st.session_state.poll_stop_pending = True
                    st.session_state.poll_error_count = 0
                    st.rerun()
            except api.ApiError as exc:
                # 일시적 오류 시 다음 5초 주기에 다시 조회; HTTP 재시도는 백엔드 책임입니다.
                st.session_state.poll_error_count = st.session_state.get("poll_error_count", 0) + 1
                if st.session_state.poll_error_count >= 3:
                    st.session_state.poll_stop_pending = True
                    st.error("연속 3회 조회 실패로 자동 폴링을 중단합니다. 상태와 API 한도를 확인하세요.")
                    st.rerun()
                st.warning(f"조회 실패 ({st.session_state.poll_error_count}/3): {exc}")
        latest = st.session_state.get("latest_progress")
        if latest:
            st.write("현재 상태:", latest["status"])
            if latest.get("progress") is not None:
                st.progress(min(100, max(0, int(latest["progress"]))))
            st.json(latest)
        elif not enabled:
            st.info("자동 조회를 켜거나 1회 조회 버튼을 누르세요.")

    progress_panel(int(space), int(pid), bool(auto_poll and space > 0))

with result_tab:
    st.subheader("스크립트 및 결과 링크")
    result_pid=st.number_input("조회할 projectSeq",min_value=1,value=1,step=1,key="result_pid")
    if st.button("스크립트 조회",disabled=space<=0):
        try:
            script=api.get(f"/api/jobs/{int(space)}/{int(result_pid)}/script")
            st.json(script)
            sentences=script.get("sentences",[]) if isinstance(script,dict) else []
            if sentences:
                st.text_area("전사 텍스트",value="\n".join(str(s.get("originalText") or "") for s in sentences),height=240)
        except api.ApiError as exc:st.error(str(exc))
    if st.button("다운로드 가능 산출물 조회",disabled=space<=0):
        try:st.json(api.get(f"/api/jobs/{int(space)}/{int(result_pid)}/files"))
        except api.ApiError as exc:st.error(str(exc))
    target=st.selectbox("다운로드 대상",["all","dubbingVideo","lipSyncVideo","voiceAudio",
      "originalVoiceAudio","backgroundAudio","voicewithBackgroundAudio","audioScript"])
    if st.button("파일 링크 조회",disabled=space<=0):
        try:
            out=api.get(f"/api/jobs/{int(space)}/{int(result_pid)}/download",target=target)
            st.json(out)
            for key,url in out.get("urls",{}).items():
                st.link_button(f"{key} 열기",url)
        except api.ApiError as exc:st.error(str(exc))
