
import streamlit as st

st.set_page_config(page_title="오늘의 할 일", page_icon="📝")

st.title("📝 오늘의 할 일")
st.write("과목별로 오늘 해야 할 일을 기록해 보세요.")

# 페이지를 이동해도 목록 유지
if "todo_list" not in st.session_state:
    st.session_state.todo_list = []

# 할 일 입력 폼
with st.form("todo_form", clear_on_submit=True):
    subject = st.selectbox(
        "과목",
        ["국어", "영어", "수학", "과학", "사회", "기타"]
    )

    task = st.text_input(
        "할 일",
        placeholder="예: 수학 문제집 10쪽 풀기"
    )

    submitted = st.form_submit_button(
        "➕ 추가",
        use_container_width=True
    )

# 추가 버튼 처리
if submitted:
    if not task.strip():
        st.warning("할 일을 입력해주세요")
    else:
        st.session_state.todo_list.append({
            "subject": subject,
            "task": task.strip(),
            "done": False
        })
        st.success("할 일이 추가되었습니다!")

st.divider()

# 할 일 목록
st.subheader("📋 할 일 목록")

if not st.session_state.todo_list:
    st.info("아직 등록된 할 일이 없습니다.")
else:
    for i, item in enumerate(st.session_state.todo_list):
        col1, col2 = st.columns([5, 1])

        with col1:
            done = st.checkbox(
                f"[{item['subject']}] {item['task']}",
                value=item["done"],
                key=f"todo_done_{i}"
            )
            item["done"] = done

        with col2:
            if st.button("삭제", key=f"todo_delete_{i}"):
                st.session_state.todo_list.pop(i)
                st.rerun()

    total = len(st.session_state.todo_list)
    completed = sum(
        item["done"] for item in st.session_state.todo_list
    )

    st.divider()
    st.write(f"완료한 할 일: **{completed} / {total}개**")
    st.progress(completed / total)
