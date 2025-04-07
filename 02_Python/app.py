import streamlit as st

st.title("streamlit 앱 실행 예제")
st.write("하이나는 스트림릿")

name = st.text_input("이름을 입력하세요: ")

if st.button("인사하기"):
    st.write(f"안녕하세요, {name}님!")


