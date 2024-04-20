import streamlit as st
import datetime
from PIL import Image
import pandas as pd
from RecommendationModel import recommender

# -------------------------------------------------------------
# -------------------------- Setting --------------------------
# -------------------------------------------------------------

# spot = pd.read_csv('Demand_Forecasting/Recommend/spot.csv')
# senior = pd.read_csv('Demand_Forecasting/Recommend/senior.csv')
# rcd_data = pd.read_csv('Demand_Forecasting/Recommend/recommend_data.csv')
spot = pd.read_csv('Demand_Forecasting/spot.csv')
senior = pd.read_csv('Demand_Forecasting/senior.csv')
rcd_data = pd.read_csv('Demand_Forecasting/recommend_data.csv')

cat_list = ['공연전시', '교육_체험', '도시탐방', '레저관광', '맛집_카페', '문화관광', '역사_유적지',
     '테마파크', '휴식_힐링','온천', '음식점', '자연', '즐길거리', '키즈', '기타']

title = "시니어에 집중할 시간"
# -------------------------------------------------------------
# ------------------------- 화면 구성 --------------------------
# -------------------------------------------------------------

# -------------------------------------------------------------
# -------------------- 왼쪽 화면 (사이드바) --------------------
# -------------------------------------------------------------

st.sidebar.title(title)

select_cat = st.sidebar.multiselect(
    '제일 좋았었던 관광지는 무엇이었나요? (필수 선택, 복수 응답 가능)', cat_list, key='select_cat', default='자연')

hate_cat = st.sidebar.multiselect(
    '맘에 들지 않았거나 추천 받고 싶지 않은 관광지가 있나요? (필수 X, 복수 응답 가능)', cat_list, key='hate_cat', default='기타')

answer_list = list()

answer_list.append(st.sidebar.radio(
    "짧은 휴가나 당일치기 여행을 좋아하시나요?",
    ['네','아니오'],
    horizontal=True,
    key='ans1') == '네')

answer_list.append(st.sidebar.radio(
    "가성비 여행을 선호하시나요?",
    ['네','아니오'],
    horizontal=True,
    key='ans2'
    ) == '네')

answer_list.append(st.sidebar.radio(
    "여행 목적이 친지 또는 친족 방문일까요?",
    ['네','아니오'],
    horizontal=True,
    key='ans3'
    ) == '네')

day_selected = int(st.sidebar.date_input("선택한 날짜에 사람이 많을지 확인해드릴게요! (2022년 12월 2일 ~ 31일)",
                                         datetime.date(2022,12,2), 
                                         min_value=datetime.date(2022,12,2),
                                         max_value=datetime.date(2022,12,31), key='day_selected').day)

if day_selected < 10:
    date = f'2022120{day_selected}'
else:
    date = f'202212{day_selected}'

st.sidebar.write(f'2022년 12월 {day_selected}일')

new_check = st.sidebar.checkbox('색다른 경험을 해보고 싶어요! (추천)',key='new_check')

# start_button = st.sidebar.button(
#     "추천 받기 📊", key='start_button', on_click=result
# )
sorted_list = st.sidebar.radio('오름차순 선택', ['가나다 순', '반대로'], key='sorted_list')

# -------------------------------------------------------------
# ------------------------ 오른쪽 화면 -------------------------
# -------------------------------------------------------------

st.title(title)
st.markdown("휴대폰 이용자 분들은 :green[**왼쪽 위 화살표**]를 클릭해주세요!")

def result_():
    result1 = st.session_state.result1
    result2 = st.session_state.result2
rcd = recommender(spot, senior, rcd_data)
try:
    result_fin = rcd.recommend_fin(act_wanted = select_cat, date = date, answer = answer_list, non_recmd = hate_cat, new = new_check)
except:
    st.sidebar.error("추천할 관광지를 찾지 못했어요.. 다른 관광지 종류를 선택해주세요!")

col1, col2 = st.columns(2)

with col1:
    if new_check:
        st.subheader('색다른 경험만을 위한 추천 관광지에요!')
        # st.markdown(':orange[can] :green[write] :blue[text] :violet[in] :gray[pretty] :rainbow[colors].')

    else:
        st.subheader('맞춤 추천 관광지에요!')
    result_fin = [result_fin[0], sorted(result_fin[1],reverse=(sorted_list != '가나다 순')),
                sorted(result_fin[2],reverse=(sorted_list != '가나다 순'))]

    result1 = st.selectbox(f"{len(result_fin[1])}개의 관광지가 있어요",result_fin[1],label_visibility="visible",
                            key='result1',on_change=result_)
    st.link_button(f"{st.session_state.result1} 검색결과 보기", f'https://www.google.com/search?q={st.session_state.result1}')
    st.image(Image.open(f'jeju_picture/제주도 {result1}.jpg'))

with col2:
    st.subheader("사람이 적을 것으로 예상되는 관광지만 모아봤어요!")
    if result_fin[2] == None:
        st.write('선택하신 날짜에는 모든 관광지가 사람이 많을 것으로 예상해요!')
    result2 = st.selectbox(f"{len(result_fin[2])}개의 관광지가 있어요",result_fin[2],label_visibility="visible",
                            key='result2',on_change=result_)
    st.link_button(f"{st.session_state.result2} 검색결과 보기", f'https://www.google.com/search?q={st.session_state.result2}')
    st.image(Image.open(f'jeju_picture/제주도 {result2}.jpg'))

if new_check:
    try:
        st.sidebar.success(f"AI가 추천하는 색다른 관광지{tuple(result_fin[0])}를 확인해보세요!")
    except:
        st.sidebar.error(f"색다른 관광지({result_fin[0]})를 찾지 못했어요..")
else:
    st.sidebar.success("AI가 선정한 추천 리스트를 확인해보세요!")

