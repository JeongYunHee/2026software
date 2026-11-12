
import streamlit as st

st.set_page_config(
    page_title="오늘의 할 일",
    page_icon="📝"
)

st.title("📝 오늘의 할 일")

if "todo_list" not in st.session_state:
    st.session_state.todo_list = []

with st.form("todo_form", clear_on_submit=True):
    subject = st.selectbox(
        "과목",
        ["국어", "영어", "수학", "과학", "사회", "기타"]
    )

    task = st.text_input("할 일 입력")

    submitted = st.form_submit_button("추가")

if submitted:
    if not task.strip():
        st.warning("할 일을 입력해주세요")
    else:
        st.session_state.todo_list.append({
            "subject": subject,
            "task": task.strip()
        })
        st.success("할 일이 추가되었습니다!")

st.subheader("📋 오늘의 할 일 목록")

if not st.session_state.todo_list:
    st.info("등록된 할 일이 없습니다.")
else:
    for i, item in enumerate(st.session_state.todo_list):
        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(
                f"{i + 1}. [{item['subject']}] "
                f"{item['task']}"
            )

        with col2:
            if st.button("삭제", key=f"delete_{i}"):
                st.session_state.todo_list.pop(i)
                st.rerun()
