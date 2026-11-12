
def show_today_todos():
    st.title("📝 오늘 할일")
    st.caption("과목과 할 일을 입력한 뒤 추가 버튼을 누르세요.")

    with st.form("add_todo_form", clear_on_submit=True):
        subject = st.text_input("과목", placeholder="예: 수학")
        task = st.text_input("할 일", placeholder="예: 문제집 20쪽 풀기")
        submitted = st.form_submit_button(
            "➕ 추가", type="primary", use_container_width=True
        )

    if submitted:
        subject = subject.strip()
        task = task.strip()

        if not subject or not task:
            st.warning("과목과 할 일을 모두 입력해 주세요.")
        else:
            st.session_state.todos.append({
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "subject": subject,
                "task": task,
                "done": False,
            })
            save_todos()
            st.rerun()

    st.subheader(f"할 일 목록 ({len(st.session_state.todos)}개)")

    if not st.session_state.todos:
        st.info("아직 등록된 할 일이 없습니다.")
        return

    completed = sum(item["done"] for item in st.session_state.todos)
    st.caption(f"완료 {completed}개 / 전체 {len(st.session_state.todos)}개")

    for item in list(st.session_state.todos):
        left, right = st.columns([5, 1])

        with left:
            checked = st.checkbox(
                f"[{item['subject']}] {item['task']}",
                value=item["done"],
                key=f"todo_{item['id']}",
            )
            if checked != item["done"]:
                item["done"] = checked
                save_todos()
                st.rerun()

        with right:
            if st.button("삭제", key=f"delete_{item['id']}"):
                st.session_state.todos = [
                    todo for todo in st.session_state.todos
                    if todo["id"] != item["id"]
                ]
                save_todos()
                st.rerun()
