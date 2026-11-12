
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
def init_state():
    defaults = {
        "subjects": ["국어", "영어", "수학", "과학", "사회"],
        "study_records": [],
        "timer_subject": None,
        "timer_running": False,
        "timer_elapsed": 0.0,
        "timer_started_at": None,
        "timer_session_start": None,
        "todo_list": [],
        "todo_next_id": 0,
        "reflections": [],
        "reflection_next_id": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# =====================================
# 3. 공통 함수
# =====================================
def format_time(seconds):
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_elapsed():
    elapsed = st.session_state.timer_elapsed

    if st.session_state.timer_running:
        elapsed += (
            time.time() - st.session_state.timer_started_at
        )

    return elapsed


def start_timer(subject):
    if st.session_state.timer_subject != subject:
        st.session_state.timer_elapsed = 0.0
        st.session_state.timer_session_start = (
            datetime.now().isoformat(timespec="seconds")
        )

    elif st.session_state.timer_session_start is None:
        st.session_state.timer_session_start = (
            datetime.now().isoformat(timespec="seconds")
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
            "종료시간": datetime.now().isoformat(
                timespec="seconds"
            ),
            "공부시간(초)": round(elapsed, 2),
        })

    st.session_state.timer_running = False
    st.session_state.timer_elapsed = 0.0
    st.session_state.timer_started_at = None
    st.session_state.timer_subject = None
    st.session_state.timer_session_start = None


# =====================================
# 4. 학습 타이머 페이지
# =====================================
def timer_page():
    st.title("⏱️ 학습 타이머")
    st.write("과목별 공부 시간을 측정하고 기록하세요.")

    st.divider()

    st.subheader("📖 공부할 과목 선택")

    subject = st.selectbox(
        "과목",
        st.session_state.subjects,
        key="timer_subject_select"
    )

    with st.expander("➕ 과목 추가"):
        new_subject = st.text_input(
            "새 과목 이름",
            key="new_subject_input"
        )

        if st.button("과목 추가"):
            new_subject = new_subject.strip()

            if not new_subject:
                st.warning("과목 이름을 입력하세요.")
            elif new_subject in st.session_state.subjects:
                st.warning("이미 등록된 과목입니다.")
            else:
                st.session_state.subjects.append(new_subject)
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
                font-size:64px;
                font-weight:bold;
                padding:24px;
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
            type="primary",
            use_container_width=True,
            disabled=not can_start
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
            st.rerun()

    if active_subject and active_subject != subject:
        st.caption(
            "다른 과목을 시작하려면 현재 학습을 종료하세요."
        )

    st.divider()
    st.subheader("📋 학습 기록")

    if st.session_state.study_records:
        df = pd.DataFrame(st.session_state.study_records)
        display_df = df.copy()

        display_df["공부시간"] = display_df[
            "공부시간(초)"
        ].apply(format_time)

        st.dataframe(
            display_df[["날짜", "과목", "공부시간"]],
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "📥 학습 기록 CSV 다운로드",
            data=csv,
            file_name="study_records.csv",
            mime="text/csv"
        )
    else:
        st.info("아직 저장된 학습 기록이 없습니다.")


# =====================================
# 5. 오늘의 할 일 페이지
# =====================================
def todo_page():
    st.title("📝 오늘의 할 일")
    st.write("오늘 공부할 과목과 할 일을 기록하세요.")

    st.divider()
    st.subheader("➕ 할 일 추가")

    with st.form("todo_form", clear_on_submit=True):
        subject = st.selectbox(
            "과목 선택",
            st.session_state.subjects
        )

        task = st.text_input(
            "할 일",
            placeholder="예: 수학 문제집 20쪽 풀기"
        )

        submitted = st.form_submit_button(
            "추가",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not task.strip():
            st.warning("할 일을 입력해주세요")
        else:
            st.session_state.todo_list.append({
                "id": st.session_state.todo_next_id,
                "subject": subject,
                "task": task.strip(),
                "completed": False,
            })

            st.session_state.todo_next_id += 1
            st.success("할 일이 추가되었습니다.")

    st.divider()
    st.subheader("📋 오늘의 할 일 목록")

    todos = st.session_state.todo_list

    if not todos:
        st.info("아직 등록된 할 일이 없습니다.")
        return

    total = len(todos)
    completed = sum(
        1 for todo in todos if todo["completed"]
    )

    st.metric("완료한 할 일", f"{completed} / {total}")
    st.progress(completed / total)

    for todo in todos[:]:
        col1, col2 = st.columns([5, 1])

        with col1:
            checked = st.checkbox(
                f"[{todo['subject']}] {todo['task']}",
                value=todo["completed"],
                key=f"todo_check_{todo['id']}"
            )
            todo["completed"] = checked

        with col2:
            if st.button(
                "삭제",
                key=f"todo_delete_{todo['id']}"
            ):
                st.session_state.todo_list = [
                    item
                    for item in st.session_state.todo_list
                    if item["id"] != todo["id"]
                ]
                st.rerun()


# =====================================
# 6. 공부 회고 페이지 (신규)
# =====================================
def reflection_page():
    st.title("📓 공부 회고")
    st.write(
        "오늘 공부한 내용을 돌아보고 "
        "다음 학습을 계획해 보세요."
    )

    st.info(
        "💾 기록 보관 안내\n\n"
        "작성한 회고는 현재 앱에 접속한 동안 "
        "임시로 저장됩니다. 다른 페이지에 다녀와도 "
        "내용이 남아 있습니다.\n\n"
        "하지만 브라우저 연결이 끊기거나 "
        "앱이 다시 시작되면 기록이 사라질 수 있습니다. "
        "며칠 동안 보관된다고 보장할 수 없으므로 "
        "중요한 내용은 아래 다운로드 기능으로 "
        "따로 저장해 주세요."
    )

    st.divider()
    st.subheader("✏️ 오늘의 공부 회고 작성")

    with st.form(
        "reflection_form",
        clear_on_submit=True
    ):
        learned = st.text_area(
            "📖 오늘 배운 내용",
            placeholder=(
                "예: 오늘은 수학 일차방정식의 "
                "풀이 방법을 배웠다."
            ),
            height=140
        )

        next_study = st.text_area(
            "🎯 다음에 공부할 내용",
            placeholder=(
                "예: 내일은 일차방정식 응용 문제를 "
                "10개 풀어볼 것이다."
            ),
            height=140
        )

        submitted = st.form_submit_button(
            "등록",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not learned.strip() or not next_study.strip():
            st.warning(
                "오늘 배운 내용과 다음에 공부할 내용을 "
                "모두 입력해주세요."
            )
        else:
            reflection = {
                "id": st.session_state.reflection_next_id,
                "작성일시": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "오늘 배운 내용": learned.strip(),
                "다음에 공부할 내용": next_study.strip(),
            }

            st.session_state.reflections.append(reflection)
            st.session_state.reflection_next_id += 1

            st.success("공부 회고가 등록되었습니다.")

    st.divider()
    st.subheader("📚 등록한 공부 회고")

    reflections = st.session_state.reflections

    if not reflections:
        st.info("아직 등록된 공부 회고가 없습니다.")
        return

    st.write(f"총 **{len(reflections)}개**의 회고가 있습니다.")

    # 최근 작성한 회고부터 표시
    for reflection in reversed(reflections[:]):
        with st.container(border=True):
            st.caption(
                f"🕒 작성일시: {reflection['작성일시']}"
            )

            st.markdown("**📖 오늘 배운 내용**")
            st.write(reflection["오늘 배운 내용"])

            st.markdown("**🎯 다음에 공부할 내용**")
            st.write(reflection["다음에 공부할 내용"])

            if st.button(
                "🗑️ 회고 삭제",
                key=f"reflection_delete_{reflection['id']}"
            ):
                st.session_state.reflections = [
                    item
                    for item in st.session_state.reflections
                    if item["id"] != reflection["id"]
                ]
                st.rerun()

    st.divider()

    # 회고 기록 CSV 다운로드
    df = pd.DataFrame(reflections)

    csv = df[
        ["작성일시", "오늘 배운 내용", "다음에 공부할 내용"]
    ].to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 공부 회고 전체 다운로드",
        data=csv,
        file_name="study_reflections.csv",
        mime="text/csv",
        use_container_width=True
    )


# =====================================
# 7. 학습 통계 페이지
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

    today_seconds = today_df["공부시간(초)"].sum()
    total_seconds = df["공부시간(초)"].sum()
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
        subject_df.set_index("과목")["공부시간(분)"]
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
        daily_df.set_index("날짜")["공부시간(분)"]
    )


# =====================================
# 8. 사이드바 멀티페이지
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
            todo_page,
            title="오늘의 할 일",
            icon="📝"
        ),
        st.Page(
            reflection_page,
            title="공부 회고",
            icon="📓"
        ),
        st.Page(
            statistics_page,
            title="학습 통계",
            icon="📊"
        ),
    ]
}

pg = st.navigation(
    pages,
    position="sidebar",
    expanded=True
)

pg.run()
