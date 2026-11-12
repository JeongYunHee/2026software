import streamlit as st
from datetime import date

st.set_page_config(page_title='오늘 할일', page_icon='📝')
st.title('📝 오늘 할일')
st.caption('과목과 할 일을 입력하고 추가하세요.')

# 세션별 데이터: Streamlit Cloud 재시작 시 초기화될 수 있습니다.
if 'todos' not in st.session_state:
    st.session_state.todos = []
if 'todo_next_id' not in st.session_state:
    st.session_state.todo_next_id = 1

with st.form('todo_add', clear_on_submit=True):
    subject = st.text_input('과목', placeholder='예: 수학')
    task = st.text_input('할 일', placeholder='예: 문제집 20쪽 풀기')
    add = st.form_submit_button('➕ 추가', type='primary', use_container_width=True)

if add:
    if not subject.strip() or not task.strip():
        st.warning('과목과 할 일을 모두 입력해 주세요.')
    else:
        st.session_state.todos.append({
            'id': st.session_state.todo_next_id,
            'date': date.today().isoformat(),
            'subject': subject.strip(),
            'task': task.strip(),
            'done': False,
        })
        st.session_state.todo_next_id += 1
        st.rerun()

items = st.session_state.todos
st.subheader(f'할 일 목록 ({len(items)}개)')
if items:
    completed = sum(item['done'] for item in items)
    st.progress(completed / len(items), text=f'완료 {completed} / 전체 {len(items)}')
    for item in list(items):
        left, right = st.columns([5, 1])
        with left:
            checked = st.checkbox(
                f"[{item['subject']}] {item['task']}",
                value=item['done'], key=f"done_{item['id']}"
            )
            if checked != item['done']:
                item['done'] = checked
                st.rerun()
        with right:
            if st.button('삭제', key=f"delete_{item['id']}"):
                st.session_state.todos = [x for x in items if x['id'] != item['id']]
                st.rerun()
else:
    st.info('아직 등록된 할 일이 없습니다.')
