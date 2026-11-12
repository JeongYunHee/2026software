import streamlit as st
from datetime import date

st.set_page_config(page_title='공부회고', page_icon='📖')
st.title('📖 공부회고')
st.caption('오늘의 공부를 돌아보고 내일의 목표를 적어 보세요.')

if 'study_reviews' not in st.session_state:
    st.session_state.study_reviews = []
if 'review_next_id' not in st.session_state:
    st.session_state.review_next_id = 1

with st.form('review_add', clear_on_submit=True):
    review_date = st.date_input('날짜', value=date.today())
    subject = st.text_input('공부한 과목', placeholder='예: 영어, 수학')
    good = st.text_area('잘한 점', placeholder='오늘 잘한 점을 적어 보세요.')
    improve = st.text_area('아쉬운 점', placeholder='보완할 점을 적어 보세요.')
    goal = st.text_area('내일의 목표', placeholder='내일 실천할 목표를 적어 보세요.')
    save = st.form_submit_button('💾 회고 저장', type='primary', use_container_width=True)

if save:
    if not subject.strip():
        st.warning('공부한 과목을 입력해 주세요.')
    else:
        st.session_state.study_reviews.insert(0, {
            'id': st.session_state.review_next_id,
            'date': review_date.isoformat(),
            'subject': subject.strip(),
            'good': good.strip(),
            'improve': improve.strip(),
            'goal': goal.strip(),
        })
        st.session_state.review_next_id += 1
        st.rerun()

st.subheader('저장한 공부회고')
if not st.session_state.study_reviews:
    st.info('아직 작성한 회고가 없습니다.')
else:
    for review in list(st.session_state.study_reviews):
        with st.expander(f"{review['date']} · {review['subject']}"):
            st.markdown('**잘한 점**')
            st.write(review['good'] or '작성하지 않음')
            st.markdown('**아쉬운 점**')
            st.write(review['improve'] or '작성하지 않음')
            st.markdown('**내일의 목표**')
            st.write(review['goal'] or '작성하지 않음')
            if st.button('이 회고 삭제', key=f"review_delete_{review['id']}"):
                st.session_state.study_reviews = [
                    x for x in st.session_state.study_reviews if x['id'] != review['id']
                ]
                st.rerun()
