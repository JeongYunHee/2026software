import streamlit as st

st.set_page_config(
    page_title="학생 학습 관리",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 멀티페이지 등록
pg = st.navigation(
    [
        st.Page(
            "pages/timer.py",
            title="학습 타이머",
            icon="⏱️",
            default=True
        ),
        st.Page(
            "pages/1_todo.py",
            title="할 일 관리",
            icon="📝"
        )
    ],
    position="sidebar"
)

pg.run()
