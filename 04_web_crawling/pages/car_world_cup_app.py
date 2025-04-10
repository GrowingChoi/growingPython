import streamlit as st
import random
import time

# 페이지 기본 설정
st.set_page_config(page_title="Car World Cup", layout="centered")

# 상태 초기화
if 'stage' not in st.session_state:
    st.session_state.stage = 'setup'
    st.session_state.animate = False
    st.session_state.match_index = 0
    st.session_state.all_cars = []
    st.session_state.current_round = []
    st.session_state.next_round = []
    st.session_state.total_round = 16

# CSS 애니메이션 정의
st.markdown("""
    <style>
    .fadeout {
        animation: fadeSlideOut 1s forwards;
    }
    @keyframes fadeSlideOut {
        0% { opacity: 1; transform: translateX(0); }
        100% { opacity: 0; transform: translateX(-100px); }
    }
    div.stButton > button {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        font-size: 18px;
        font-weight: bold;
        color: white;
        background-color: #008CBA;
        border: none;
        cursor: pointer;
        display: block;
        margin: 30px auto;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        transition: background-color 0.3s;
    }
    div.stButton > button:hover {
        background-color: #005f73;
    }
    </style>
""", unsafe_allow_html=True)

# 임시 차량 데이터
mock_cars = [
    {
        "car_name": f"차량 {i+1}",
        "image_url": f"https://via.placeholder.com/300x200.png?text=Car+{i+1}",
        "fuel_type": random.choice(["가솔린", "디젤", "전기", "하이브리드"]),
        "year": str(random.randint(2020, 2024)),
        "price": str(random.randint(1500, 5000))
    }
    for i in range(32)
]

def run_worldcup():
    st.title("🚘 자동차 월드컵")
    st.markdown("<h4 style='text-align: center;'>✨ 마음에 드는 자동차 이상형 찾기 ✨</h4>", unsafe_allow_html=True)

    if st.session_state.stage == 'setup':
        container = st.container()
        with container:
            css_class = "fadeout" if st.session_state.animate else ""
            container.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)

            price_range = st.selectbox("가격대를 선택하세요 (단위: 만원)", options=[
                "1000만원 이하", "1000~2000만원", "2000~3000만원",
                "3000~4000만원", "4000~5000만원", "5000만원 이상"
            ])

            round_count = st.selectbox("몇 강으로 진행할까요?", options=[16, 32])
            
            if st.button("🚗 월드컵 시작하기", key="start_wc"):
                st.session_state.total_round = round_count
                st.session_state.animate = True
                st.rerun()

        if st.session_state.animate:
            time.sleep(1)
            st.session_state.all_cars = random.sample(mock_cars, st.session_state.total_round)
            st.session_state.current_round = st.session_state.all_cars.copy()
            st.session_state.next_round = []
            st.session_state.match_index = 0
            st.session_state.stage = 'battle'
            st.rerun()

    elif st.session_state.stage == 'battle':
        total_matches = len(st.session_state.current_round) // 2
        current_match = st.session_state.match_index

        if current_match < total_matches:
            st.subheader(f"⚔️ {len(st.session_state.current_round)}강 - {current_match + 1}번째 경기")

            car1 = st.session_state.current_round[current_match * 2]
            car2 = st.session_state.current_round[current_match * 2 + 1]

            col1, col2 = st.columns(2)
            for i, (col, car) in enumerate(zip([col1, col2], [car1, car2])):
                with col:
                    st.image(car["image_url"], use_container_width=True)
                    st.markdown(f"### {car['car_name']}")
                    st.markdown(f"- 연료: {car['fuel_type']}")
                    st.markdown(f"- 연식: {car['year']}년")
                    st.markdown(f"- 가격: {car['price']}만원")

                    if st.button(f"✅ 선택하기", key=f"select_{current_match}_{i}"):
                        st.session_state.next_round.append(car)
                        st.session_state.match_index += 1
                        st.rerun()

        else:
            # 다음 라운드로 전환
            if len(st.session_state.next_round) == 1:
                winner = st.session_state.next_round[0]
                st.success(f"🏆 우승 차량: {winner['car_name']} 🎉")
                st.image(winner["image_url"], use_container_width=True)
                st.markdown(f"- 연료: {winner['fuel_type']}")
                st.markdown(f"- 연식: {winner['year']}년")
                st.markdown(f"- 가격: {winner['price']}만원")
                st.balloons()
            else:
                st.session_state.current_round = st.session_state.next_round.copy()
                st.session_state.next_round = []
                st.session_state.match_index = 0
                st.rerun()

run_worldcup()
