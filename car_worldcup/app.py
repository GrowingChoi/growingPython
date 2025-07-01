import streamlit as st
import DbConnection as db
import random
import URL as ur
import time
import pymysql
import altair as alt
import pandas as pd


# ✅ 상태 초기화
if "entered" not in st.session_state:
    st.session_state.entered = False
if "show_price_select" not in st.session_state:
    st.session_state.show_price_select = False
if "show_intro_page" not in st.session_state:
    st.session_state.show_intro_page = False
if "show_dev_page" not in st.session_state:
    st.session_state.show_dev_page = False

# ✅ Step 1: 입장 페이지
if not st.session_state.entered and not st.session_state.show_intro_page and not st.session_state.show_dev_page:
    st.title("🔥 Vote your favorite!! 🔥")
    st.markdown("## 원하시는 메뉴를 선택해주세요")
    btn_cols = st.columns(3)

    with btn_cols[0]:
        st.image("https://github.com/user-attachments/assets/9d041e15-8185-4f7c-aa9a-b6cccaf274f1", width=190)
        if st.button("👑 CarWorldCup start!"):
            st.session_state.entered = True
            st.session_state.show_price_select = True
            st.rerun()

    with btn_cols[1]:
        st.image("https://github.com/user-attachments/assets/5af7745b-1813-4384-9d74-4047e2333e4e", width=190)
        if st.button("📊 역대 우승차량 보기"):
            st.session_state.show_intro_page = True
            st.rerun()

    with btn_cols[2]:
        st.image("https://github.com/user-attachments/assets/f03fb64c-d876-467a-866c-592b54a391eb", width=190)
        if st.button(" 🧑🏻‍💻 DEVELOPERS 소개 "):
            st.session_state.show_dev_page = True
            st.rerun()

    st.stop()
    

# ✅ Step 2: 자기소개 페이지
# if st.session_state.show_intro_page:
#     st.title("👋 팀원소개")
#     profiles = [
#         {"name": "지원", "img": "imgs/1.png", "desc": "맛있는 걸 좋아하는 활발한 성격!"},
#         {"name": "민수", "img": "imgs/2.png", "desc": "조용하지만 배려심 넘치는 친구"},
#         {"name": "하늘", "img": "imgs/3.png", "desc": "유쾌하고 장난기 많은 스타일"},
#         {"name": "지우", "img": "imgs/4.png", "desc": "책과 커피를 좋아하는 감성파"},
#         {"name": "태호", "img": "imgs/5.png", "desc": "운동과 여행을 사랑하는 열정남"},
#     ]

#     for profile in profiles:
#         st.image(profile["img"], width=200, caption=profile["name"])
#         st.markdown(f"**{profile['desc']}**")
#         st.markdown("---")

#     if st.button("🏠 홈으로 돌아가기"):
#         for key in ["entered", "show_price_select", "show_intro_page"]:
#             st.session_state[key] = False
#         st.rerun()

#     st.stop()

if st.session_state.show_intro_page:
    st.set_page_config(page_title="자동차 월드컵 통계", layout="centered")
    st.title("📊 가격대별 우승 Top 10 차량")

        # ✅ 가격대 선택 옵션
    price_labels = [
        "0만원~3000만원",
        "3000만원~5000만원",
        "5000만원~7000만원",
        "7000만원~1억원",
        "1억원~2억원",
        "2억원이상"
    ]

    price_ranges = [
        (0, 3000),
        (3000, 5000),
        (5000, 7000),
        (7000, 10000),
        (10000, 20000),
        (20000, 9999999)
    ]

    # ✅ 사이드바에서 가격대 선택
    selected_label = st.sidebar.selectbox("💰 가격대로 보기", price_labels)
    selected_index = price_labels.index(selected_label)
    price_min, price_max = price_ranges[selected_index]

    # ✅ DB 연결 및 쿼리
    try:
        conn = pymysql.connect(
            host='192.168.0.15',
            user='user5',
            password='9999',
            db='test_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        query = f"""
            SELECT model, win_log
            FROM winner_info
            WHERE price >= {price_min} AND price < {price_max}
            ORDER BY win_log DESC
            LIMIT 10
        """

        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows)

        conn.close()

        if df.empty:
            st.warning("⚠️ 해당 가격대에 우승 기록이 있는 차량이 없습니다.")
            st.stop()

        # ✅ Altair 시각화
        bar = alt.Chart(df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusBottomLeft=5).encode(
            y=alt.Y('model:N', sort='-x', title=None, axis=alt.Axis(labelFontSize=13)),
            x=alt.X('win_log:Q', title='우승 횟수'),
            color=alt.Color('model:N', legend=None),
            tooltip=[
                alt.Tooltip('model:N', title='차량명'),
                alt.Tooltip('win_log:Q', title='우승 횟수')
            ]
        )

        text = alt.Chart(df).mark_text(
            align='left',
            baseline='middle',
            dx=5,
            fontSize=13
        ).encode(
            y=alt.Y('model:N', sort='-x'),
            x='win_log:Q',
            text='win_log:Q'
        )

        chart = (bar + text).properties(width=600, height=400)
        st.markdown(f"### 💸 {selected_label} 가격대")
        st.altair_chart(chart, use_container_width=False)

    except Exception as e:
        st.error("❌ 오류 발생")
        st.code(str(e))


        if st.button("🏠 홈으로 돌아가기"):
            for key in ["entered", "show_price_select", "show_dev_page"]:
                st.session_state[key] = False
            st.rerun()

        st.stop()




    if st.button("🏠 홈으로 돌아가기"):
        for key in ["entered", "show_price_select", "show_intro_page"]:
            st.session_state[key] = False
        st.rerun()

    st.stop()



# ✅ Step 3: 가격 선택 페이지
if st.session_state.get("show_price_select", False) and "selected_price" not in st.session_state:
    st.title("💰 가격대를 선택해주세요!")
    st.markdown("### 원하는 가격 범위를 골라주세요")

    selected = st.selectbox(
        "가격 범위 선택",
        ["0만원~3000만원",
        "3000만원~5000만원",
        "5000만원~7000만원",
        "7000만원~1억원",
        "1억원~2억원",
        "2억원이상"]
    )

    connnn = db.DbConnection() 
    res = connnn.select_all_data(selected) 

    # 선택 완료 버튼
    if st.button("선택 완료"):
        if len(res) < 16:
            st.warning("🚗 해당 가격대의 차량 수가 충분하지 않습니다! 다른 가격대를 골라주세요.", icon="⚠️")
        else:
            st.session_state.selected_price = selected
            st.session_state.show_price_select = False
            st.rerun()
    st.stop()



#✅ Step 3: 개발자 소개 페이지
if st.session_state.show_dev_page:
    st.set_page_config(page_title="개발자 소개 페이지", layout="centered")
    st.title("🧑🏻‍💻 DEVELOPERS 소개")

    profiles = [
        {"name": "지윤", "img": "https://github.com/user-attachments/assets/719dfe50-9b45-470e-bdc6-c22a57508169", 
         "desc": "Olá, meu nome é Jiyoon. Na verdade, eu sou coreana. Mas estou usando este idioma porque o Cristiano Ronaldo é português. Tornar-me alguém que está sempre em destaque é o meu sonho. Então, continue acompanhando minha jornada~!"},
        {"name": "지호", "img": "https://github.com/user-attachments/assets/704ffbf8-e5cb-407d-b680-d8f298a030d1", 
         "desc": "자기소개\nAhoj, jsem Mo Jiho.\nMám rád baseball, tenis a fotbal.\nV korejském baseballu fandím týmu Hanwha, bohužel. 😢"},
        {"name": "진혁", "img": "https://github.com/user-attachments/assets/abe3a34e-7611-43a4-8c54-10387206ab31", 
         "desc": "자기소개\n 안녕하세요, 진혁입니다. 전공은 화학이지만 요즘은 컴퓨터 앞에서 코드를 짜며 경기장에서 온 힘을 다해 뛰고 있습니다. 필요한 시약이나 화학 관련 궁금증 있으시면, 마치 상대 골문을 노리는 것처럼 주저하지 말고 편하게 말씀해 주세요. 언제나 최선을 다해 도와드리겠습니다!"},
        {"name": "성의", "img": "https://github.com/user-attachments/assets/a69165a2-1064-48d6-9d63-12105fdb814c",
         "desc": "자기소개\n Salut, j'aime beaucoup les jeux vidéo et j'y joue souvent. Merci d'avance pour les bons moments à venir !"},
        {"name": "성장", "img": "https://github.com/user-attachments/assets/d9974423-da75-409f-96eb-0dfea434603a", 
         "desc": "자기소개 \n Hei! Jeg heter Seongjang Choi.  På fritiden liker jeg å trene – egentlig liker jeg nesten all slags sport, bortsett fra biljard 😅  Jeg er ikke så flink, men jeg har det gøy uansett!  Jeg synes også programmering er ganske gøy.  Så hvis du har problemer med koding, bare kom og spør meg!"},
    ]

    for profile in profiles:
        st.image(profile["img"], width=200, caption=profile["name"])
        formatted_desc = profile["desc"].replace("\n", "<br>")
        st.markdown(f"{formatted_desc}", unsafe_allow_html=True)
        st.markdown("---")  # 구분선

    if st.button("🏠 홈으로 돌아가기"):
        for key in ["entered", "show_price_select", "show_dev_page"]:
            st.session_state[key] = False
        st.rerun()

    st.stop()



#✅ Step 4: 월드컵 시작 전 초기화
if "round" not in st.session_state:
    st.session_state.round = 1
    connnn = db.DbConnection() 
    res = connnn.select_all_data(st.session_state.selected_price)
    # 차량 수 충분할 경우 정상적으로 진행
    st.session_state.car = random.sample(res, 16)
    st.session_state.winners = []
    st.session_state.index = 0

# ✅ 종료 조건
if len(st.session_state.car) == 1:
    connnn = db.DbConnection() 
    st.title("🏆 이상형 월드컵 결과")
    final_car = st.session_state.car[0]
    st.success(f"🎉 당신의 이상형은: {final_car.model} ({final_car.price}만원)")
    st.image(final_car.img_url, width=400)

    # ✅ insert 중복 방지를 위한 플래그 확인
    if "winner_saved" not in st.session_state or not st.session_state.winner_saved:
        winner_info = connnn.insert_winner_info(final_car)
        st.session_state.winner_saved = True
        if winner_info == 'success':
            st.write('우승차량에 기록되었습니다!')
        

    if st.button("다시 시작하기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    url = ur.get_url(final_car.model)
    st.caption('더보기 : ' + url)
    st.stop()


# ✅ 인덱스 초과 시 다음 라운드로
if st.session_state.index + 1 >= len(st.session_state.car):
    st.session_state.car = st.session_state.winners
    st.session_state.winners = []
    st.session_state.index = 0
    st.session_state.round += 1
    st.rerun()

# ✅ 현재 대결 차량 객체
left_car = st.session_state.car[st.session_state.index]
right_car = st.session_state.car[st.session_state.index + 1]

# ✅None 값 처리 - 20250410 : growing 추가
def display_value(value, unit=""):
    return f"{value}{unit}" if value is not None else "-"

cols = st.columns([5, 1, 5])

with cols[0]:
    st.image(left_car.img_url, use_container_width=True)
    st.markdown(f"""
        <div style='text-align: center; max-width: 300px; margin: 0 auto;'>
            <h4 style="margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {left_car.model}
            </h4>
            <h3>💰 <b>가격:</b> {left_car.price}만원</h3>
            <p>🚗 <b>등급:</b> {left_car.car_level}</p>
            <p>🚀 <b>외형:</b> {left_car.outfit}</p>
            <p>⛽ <b>연료:</b> {left_car.fuel_type}</p>
            <p>⚙️ <b>엔진:</b> {left_car.engine_type}</p>
            <p>💨 <b>마력:</b> {display_value(left_car.horse_power)}</p>
            <p>🛣️ <b>연비:</b> {left_car.fuel_effic}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("💖 선택!", key="left"):
        st.session_state.winners.append(left_car)
        st.session_state.index += 2
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with cols[1]:
    st.markdown(
        """
        <div style='height: 100%; display: flex; justify-content: center; margin-top: 220px;'>
            <span style='font-size: 48px; font-weight: bold; color: red;'>VS</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with cols[2]:
    st.image(right_car.img_url, use_container_width=True)
    st.markdown(f"""
        <div style='text-align: center; max-width: 300px; margin: 0 auto;'>
            <h4 style="margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {right_car.model}
            </h4>
            <h3>💰 <b>가격:</b> {right_car.price}만원</h3>
            <p>🚗 <b>등급:</b> {right_car.car_level}</p>
            <p>🚀 <b>외형:</b> {left_car.outfit}</p>
            <p>⛽ <b>연료:</b> {right_car.fuel_type}</p>
            <p>⚙️ <b>엔진:</b> {right_car.engine_type}</p>
            <p>💨 <b>마력:</b> {display_value(right_car.horse_power)}</p>
            <p>🛣️ <b>연비:</b> {right_car.fuel_effic}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("💖 선택!", key="right"):
        st.session_state.winners.append(right_car)
        st.session_state.index += 2
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


