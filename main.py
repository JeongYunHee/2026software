
import time
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="학생 학습 타이머",
    page_icon="📚",
    layout="centered"
)

# 사이드바
st.sidebar.title("📚 학습 관리")
st.sidebar.page_link(
    "pages/01_todo.py",
    label="📝 오늘의 할 일"
)

DEFAULT_SUBJECTS = ["국어", "영어", "수학", "과학", "사회", "기타"]

for key, value in {
    "subjects": DEFAULT_SUBJECTS.copy(),
    "selected_subject": "국어",
    "running": False,
    "started_at": None,
    "elapsed_before_start": 0.0,
    "records": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def elapsed_seconds():
    elapsed = st.session_state.elapsed_before_start
    if st.session_state.running and st.session_state.started_at is not None:
        elapsed += time.monotonic() - st.session_state.started_at
    return max(0.0, elapsed)


def format_time(seconds):
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def pause():
    if st.session_state.running:
        st.session_state.elapsed_before_start = elapsed_seconds()
        st.session_state.started_at = None
        st.session_state.running = False


def start():
    if not st.session_state.running:
        st.session_state.started_at = time.monotonic()
        st.session_state.running = True


def reset():
    st.session_state.running = False
    st.session_state.started_at = None
    st.session_state.elapsed_before_start = 0.0


def save_record():
    duration = elapsed_seconds()

    if duration < 1:
        st.warning("1초 이상 공부한 뒤 기록해 주세요.")
        return

    pause()

    now = datetime.now()
    st.session_state.records.append({
        "날짜": now.strftime("%Y-%m-%d"),
        "기록 시각": now.strftime("%H:%M:%S"),
        "과목": st.session_state.selected_subject,
        "공부 시간(초)": round(duration, 1),
    })

    reset()
    st.success("공부 시간이 저장되었습니다!")


st.title("📚 나의 학습 타이머")
st.caption(
    "과목을 선택하고 공부 시간을 측정해 보세요. "
    "기록은 현재 브라우저 세션에 저장됩니다."
)

# 과목 추가
with st.expander("➕ 과목 추가"):
    with st.form("add_subject_form", clear_on_submit=True):
        new_subject = st.text_input("새 과목 이름", max_chars=30)
        submitted = st.form_submit_button("과목 추가")

        if submitted:
            name = new_subject.strip()

            if not name:
                st.warning("과목 이름을 입력해 주세요.")
            elif name in st.session_state.subjects:
                st.info("이미 등록된 과목입니다.")
            else:
                st.session_state.subjects.append(name)
                st.success(f"'{name}' 과목을 추가했습니다.")


# 과목 선택
st.selectbox(
    "공부할 과목",
    st.session_state.subjects,
    key="selected_subject",
    disabled=(
        st.session_state.running
        or elapsed_seconds() >= 1
    ),
    help="측정 중인 시간을 기록하거나 초기화하면 과목을 바꿀 수 있습니다.",
)


# 타이머
@st.fragment(run_every="1s")
def timer_panel():
    st.markdown("### ⏱️ 현재 공부 시간")

    st.markdown(
        f"<div style='font-size:3.3rem;"
        f"font-weight:750;text-align:center;"
        f"padding:20px 0;"
        f"font-variant-numeric:tabular-nums'>"
        f"{format_time(elapsed_seconds())}</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "🟢 측정 중"
        if st.session_state.running
        else "⏸️ 대기 / 일시정지"
    )

    a, b, c = st.columns(3)

    with a:
        st.button(
            "▶️ 시작",
            use_container_width=True,
            disabled=st.session_state.running,
            on_click=start,
        )

    with b:
        st.button(
            "⏸️ 일시정지",
            use_container_width=True,
            disabled=not st.session_state.running,
            on_click=pause,
        )

    with c:
        st.button(
            "🔄 초기화",
            use_container_width=True,
            on_click=reset,
        )

    st.button(
        "💾 현재 공부 시간 기록",
        type="primary",
        use_container_width=True,
        on_click=save_record,
    )


timer_panel()

st.divider()

# 과목별 누적 공부 시간
st.subheader("📊 과목별 누적 공부 시간")

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)

    totals = (
        df.groupby("과목", as_index=False)["공부 시간(초)"]
        .sum()
    )

    totals["누적 공부 시간"] = (
        totals["공부 시간(초)"].map(format_time)
    )

    st.dataframe(
        totals[["과목", "누적 공부 시간"]],
        hide_index=True,
        use_container_width=True,
    )

    st.bar_chart(
        totals.set_index("과목")["공부 시간(초)"],
        x_label="과목",
        y_label="초",
    )

    st.metric(
        "총 공부 시간",
        format_time(df["공부 시간(초)"].sum()),
    )

    # 공부 기록
    st.subheader("🗂️ 공부 기록")

    display_df = df.copy()
    display_df["공부 시간"] = (
        display_df["공부 시간(초)"].map(format_time)
    )

    st.dataframe(
        display_df[
            ["날짜", "기록 시각", "과목", "공부 시간"]
        ].iloc[::-1],
        hide_index=True,
        use_container_width=True,
    )

    # CSV 다운로드
    st.download_button(
        "⬇️ 공부 기록 CSV 다운로드",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="study_records.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # 기록 삭제
    if st.button("🗑️ 모든 기록 삭제"):
        st.session_state.records = []
        st.rerun()

else:
    st.info(
        "아직 저장된 공부 기록이 없습니다. "
        "공부한 뒤 '현재 공부 시간 기록'을 눌러 주세요."
    )

st.caption(
    "⚠️ 앱 새로고침, 브라우저 세션 종료 또는 "
    "서버 재시작 시 기록이 사라질 수 있습니다. "
    "CSV로 백업해 주세요."
)
