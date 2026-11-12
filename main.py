
import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

# =====================================
# 1. 기본 설정
# =====================================
st.set_page_config(
    page_title="학생 학습 관리",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# 2. 세션 상태 초기화
# =====================================
if "subjects" not in st.session_state:
    st.session_state.subjects = [
        "국어", "영어", "수학", "과학", "사회"
    ]

if "study_records" not in st.session_state:
    st.session_state.study_records = []

if "timer_subject" not in st.session_state:
    st.session_state.timer_subject = None

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_elapsed" not in st.session_state:
    st.session_state.timer_elapsed = 0.0

if "timer_started_at" not in st.session_state:
    st.session_state.timer_started_at = None

if "timer_session_start" not in st.session_state:
    st.session_state.timer_session_start = None


# =====================================
# 3. 타이머 공통 함수
# =====================================
def get_elapsed():
    elapsed = st.session_state.timer_elapsed

    if st.session_state.timer_running:
        elapsed += (
            time.time()
            - st.session_state.timer_started_at
        )

    return elapsed


def format_time(seconds):
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def start_timer(subject):
    if st.session_state.timer_subject != subject:
        st.session_state.timer_elapsed = 0.0
        st.session_state.timer_session_start = (
            datetime.now().isoformat()
        )

    elif st.session_state.timer_session_start is None:
        st.session_state.timer_session_start = (
            datetime.now().isoformat()
        )

    st.session_state.timer_subject = subject
    st.session_state.timer_started_at = time.time()
    st.session_state.timer_running = True


def pause_timer():
    if st.session_state.timer_running:
        st.session_state.timer_elapsed = get_elapsed()
        st.session_state.timer_running = False
        st.session_state.timer_started_at = None


def stop_timer():
    elapsed = get_elapsed()

    if (
        st.session_state.timer_subject is not None
        and elapsed > 0
    ):
        st.session_state.study_records.append({
            "날짜": date.today().isoformat(),
            "과목": st.session_state.timer_subject,
            "시작시간": st.session_state.timer_session_start,
            "종료시간": datetime.now().isoformat(),
            "공부시간(초)": round(elapsed, 2)
        })

    st.session_state.timer_running = False
    st.session_state.timer_elapsed = 0.0
    st.session_state.timer_started_at = None
    st.session_state.timer_subject = None
    st.session_state.timer_session_start = None


# =====================================
# 4. 첫 번째 페이지: 학습 타이머
# =====================================
def timer_page():
    st.title("📚 학생 학습 타이머")
    st.write("과목별 공부 시간을 측정하고 기록하세요.")

    st.divider()

    st.subheader("📖 공부할 과목 선택")

    subject = st.selectbox(
        "과목",
        st.session_state.subjects
    )

    with st.expander("➕ 과목 추가"):
        new_subject = st.text_input("새 과목 이름")

        if st.button("과목 추가"):
            new_subject = new_subject.strip()

            if not new_subject:
                st.warning("과목 이름을 입력하세요.")
            elif new_subject in st.session_state.subjects:
                st.warning("이미 등록된 과목입니다.")
            else:
                st.session_state.subjects.append(
                    new_subject
                )
                st.success("과목이 추가되었습니다.")
                st.rerun()

    st.divider()

    st.subheader("⏱️ 학습 타이머")

    active_subject = st.session_state.timer_subject

    if active_subject:
        st.info(f"현재 학습 과목: {active_subject}")
    else:
        st.info("과목을 선택하고 시작 버튼을 누르세요.")

    @st.fragment(run_every=1)
    def timer_display():
        elapsed = get_elapsed()

        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:65px;
                font-weight:bold;
                padding:25px;
            ">
                {format_time(elapsed)}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.timer_running:
            st.success("🟢 공부 중")
        elif st.session_state.timer_subject:
            st.warning("🟡 일시정지")
        else:
            st.info("⚪ 대기 중")

    timer_display()

    col1, col2, col3 = st.columns(3)

    with col1:
        can_start = (
            not st.session_state.timer_running
            and (
                active_subject is None
                or active_subject == subject
            )
        )

        if st.button(
            "▶️ 시작 / 재개",
            use_container_width=True,
            disabled=not can_start,
            type="primary"
        ):
            start_timer(subject)
            st.rerun()

    with col2:
        if st.button(
            "⏸️ 일시정지",
            use_container_width=True,
            disabled=not st.session_state.timer_running
        ):
            pause_timer()
            st.rerun()

    with col3:
        if st.button(
            "⏹️ 종료 및 저장",
            use_container_width=True,
            disabled=active_subject is None
        ):
            stop_timer()
            st.success("학습 기록이 저장되었습니다.")
            st.rerun()

    if active_subject and active_subject != subject:
        st.caption(
            "다른 과목을 시작하려면 현재 학습을 종료하세요."
        )

    st.divider()

    st.subheader("📋 학습 기록")

    if st.session_state.study_records:
        df = pd.DataFrame(
            st.session_state.study_records
        )

        display_df = df.copy()
        display_df["공부시간"] = display_df[
            "공부시간(초)"
        ].apply(format_time)

        st.dataframe(
            display_df[
                ["날짜", "과목", "공부시간"]
            ],
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 학습 기록 CSV 다운로드",
            data=csv,
            file_name="study_records.csv",
            mime="text/csv"
        )

    else:
        st.info("아직 저장된 학습 기록이 없습니다.")


# =====================================
# 5. 두 번째 페이지: 학습 통계
# =====================================
def statistics_page():
    st.title("📊 학습 통계")

    records = st.session_state.study_records

    if not records:
        st.info("학습 기록이 없습니다.")
        return

    df = pd.DataFrame(records)

    today = date.today().isoformat()

    today_df = df[df["날짜"] == today]

    today_seconds = today_df[
        "공부시간(초)"
    ].sum()

    total_seconds = df[
        "공부시간(초)"
    ].sum()

    subject_count = df["과목"].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "오늘 공부 시간",
            format_time(today_seconds)
        )

    with col2:
        st.metric(
            "전체 누적 공부 시간",
            format_time(total_seconds)
        )

    with col3:
        st.metric(
            "학습한 과목 수",
            subject_count
        )

    st.divider()

    st.subheader("📚 과목별 누적 학습 시간")

    subject_df = (
        df.groupby("과목")["공부시간(초)"]
        .sum()
        .reset_index()
    )

    subject_df["공부시간(분)"] = (
        subject_df["공부시간(초)"] / 60
    ).round(1)

    st.bar_chart(
        subject_df.set_index("과목")[
            "공부시간(분)"
        ]
    )

    st.divider()

    st.subheader("📅 날짜별 학습 시간")

    daily_df = (
        df.groupby("날짜")["공부시간(초)"]
        .sum()
        .reset_index()
    )

    daily_df["공부시간(분)"] = (
        daily_df["공부시간(초)"] / 60
    ).round(1)

    st.line_chart(
        daily_df.set_index("날짜")[
            "공부시간(분)"
        ]
    )


# =====================================
# 6. 사이드바 멀티페이지
# =====================================
pages = {
    "학습 관리": [
        st.Page(
            timer_page,
            title="학습 타이머",
            icon="⏱️",
            default=True
        ),
        st.Page(
            statistics_page,
            title="학습 통계",
            icon="📊"
        )
    ]
}

pg = st.navigation(
    pages,
    position="sidebar",
    expanded=True
)

pg.run()
