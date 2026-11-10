import time
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="학습 타이머", page_icon="📚", layout="wide")

SUBJECTS = ["국어", "수학", "영어", "한국사", "과학", "사회", "기타"]

if "records" not in st.session_state:
    st.session_state.records = []
if "running" not in st.session_state:
    st.session_state.running = False
if "started_at" not in st.session_state:
    st.session_state.started_at = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0
if "subject" not in st.session_state:
    st.session_state.subject = SUBJECTS[0]
if "segment_started" not in st.session_state:
    st.session_state.segment_started = None


def seconds_now():
    total = st.session_state.elapsed
    if st.session_state.running:
        total += time.time() - st.session_state.started_at
    return max(0, total)


def clock(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


def pause():
    if not st.session_state.running:
        return
    now = datetime.now()
    duration = max(0, time.time() - st.session_state.started_at)
    st.session_state.elapsed += duration
    st.session_state.running = False
    st.session_state.started_at = None
    if duration >= 1:
        st.session_state.records.append({
            "과목": st.session_state.subject,
            "날짜": st.session_state.segment_started.strftime("%Y-%m-%d"),
            "시작": st.session_state.segment_started.strftime("%H:%M:%S"),
            "종료": now.strftime("%H:%M:%S"),
            "공부 시간(초)": round(duration),
        })
    st.session_state.segment_started = None


st.title("📚 나의 학습 타이머")
st.caption("과목을 선택하고 공부를 시작해 보세요. 일시정지하면 학습 구간이 기록됩니다.")

selected = st.selectbox("공부할 과목", SUBJECTS, index=SUBJECTS.index(st.session_state.subject), disabled=st.session_state.running)
if not st.session_state.running:
    st.session_state.subject = selected


@st.fragment(run_every="1s")
def timer_display():
    st.markdown(
        f"<div style='text-align:center;font-size:clamp(3rem,9vw,6rem);font-weight:750;letter-spacing:3px;padding:20px 0'>{clock(seconds_now())}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<p style='text-align:center'>{'🟢 측정 중' if st.session_state.running else '⏸ 대기 / 일시정지'}</p>", unsafe_allow_html=True)


timer_display()

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("▶ 시작", use_container_width=True, type="primary", disabled=st.session_state.running):
        st.session_state.started_at = time.time()
        st.session_state.segment_started = datetime.now()
        st.session_state.running = True
        st.rerun()
with c2:
    if st.button("⏸ 일시정지", use_container_width=True, disabled=not st.session_state.running):
        pause()
        st.rerun()
with c3:
    if st.button("↺ 초기화", use_container_width=True):
        if st.session_state.running:
            pause()
        st.session_state.elapsed = 0.0
        st.rerun()

st.divider()
st.subheader("📊 공부 통계")
df = pd.DataFrame(st.session_state.records)
if df.empty:
    st.info("아직 저장된 학습 기록이 없습니다. 공부를 시작해 보세요!")
else:
    today = datetime.now().strftime("%Y-%m-%d")
    today_seconds = int(df.loc[df["날짜"] == today, "공부 시간(초)"].sum())
    total_seconds = int(df["공부 시간(초)"].sum())
    a, b, c = st.columns(3)
    a.metric("오늘 공부 시간", clock(today_seconds))
    b.metric("누적 공부 시간", clock(total_seconds))
    c.metric("기록된 학습 구간", f"{len(df)}회")

    by_subject = df.groupby("과목")["공부 시간(초)"].sum().div(60).round(1)
    st.markdown("**과목별 누적 공부 시간 (분)**")
    st.bar_chart(by_subject, horizontal=True)

    st.subheader("📝 학습 기록")
    view = df.copy()
    view["공부 시간"] = view["공부 시간(초)"].map(clock)
    st.dataframe(view[["날짜", "과목", "시작", "종료", "공부 시간"]].iloc[::-1], hide_index=True, use_container_width=True)

    st.download_button("⬇ CSV 다운로드", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="study_records.csv", mime="text/csv")

    with st.expander("기록 삭제"):
        labels = [f"{i + 1}. {r['날짜']} / {r['과목']} / {r['시작']} / {clock(r['공부 시간(초)'])}" for i, r in enumerate(st.session_state.records)]
        selected_record = st.selectbox("삭제할 학습 구간", range(len(labels)), format_func=lambda i: labels[i])
        if st.button("선택한 기록 삭제"):
            st.session_state.records.pop(selected_record)
            st.rerun()

st.caption("※ 기록은 현재 Streamlit 세션에만 저장됩니다. 장기 보관하려면 CSV로 내려받으세요.")
