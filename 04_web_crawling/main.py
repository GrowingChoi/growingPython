import streamlit as st

st.set_page_config(page_title="Team Car World Cup", layout="wide")

# 메인 타이틀
st.markdown("<h1 style='text-align: center; font-size: 60px;'>TEAM CAR WORLD CUP</h1>", unsafe_allow_html=True)

# 동그란 버튼 스타일
st.markdown("""
    <style>
    div.stButton > button {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        font-size: 20px;
        font-weight: bold;
        color: white;
        background-color: #008CBA;
        margin: 40px auto;
        display: block;
    }
    div.stButton > button:hover {
        background-color: #005f73;
    }
    </style>
""", unsafe_allow_html=True)

# 가운데 정렬된 ABOUT 버튼
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
if st.button("ABOUT DEVELOPERS"):
    st.info("👨‍💻 개발자: 홍길동, 최성장\n📧 이메일: dev@carcup.com")
st.markdown("</div>", unsafe_allow_html=True)
