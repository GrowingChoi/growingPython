import streamlit as st
import pandas as pd
import pymysql
import altair as alt

# ✅ 페이지 설정
st.set_page_config(page_title="이상형 월드컵 통계", layout="centered")
st.title("📊 가격대별 우승 Top 10 차량")

# ✅ 가격대 선택 옵션
price_labels = [
    "500만원~2000만원",
    "2000만원~3000만원",
    "3000만원~5000만원",
    "5000만원~8000만원",
    "8000만원 이상"
]

price_ranges = [
    (500, 2000),
    (2000, 3000),
    (3000, 5000),
    (5000, 8000),
    (8000, 9999999)
]

# ✅ 사이드바에서 가격대 선택
selected_label = st.sidebar.selectbox("💰 가격대로 보기", price_labels)
selected_index = price_labels.index(selected_label)
price_min, price_max = price_ranges[selected_index]

# ✅ DB 연결 및 쿼리
try:
    conn = pymysql.connect(
        host='192.168.0.15',
        user='user4',
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
