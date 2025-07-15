import streamlit as st
import pandas as pd
import numpy as np
import re
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# ✅ 나이 문자열 처리 함수
def convert_age_to_int(age_str):
    try:
        if pd.isnull(age_str): return None
        if isinstance(age_str, (int, float)): return int(age_str)
        age_str = str(age_str).strip()
        if re.match(r"^\d{2}$", age_str): return int(age_str)
        if re.match(r"^\d{2}s?$", age_str): return int(age_str[:2]) + 5
        if re.match(r"^<\d+$", age_str): return int(age_str[1:]) - 1
        if re.match(r"^>=\d+$", age_str): return int(age_str[2:]) + 2
        if re.match(r"^<=\d+$", age_str): return int(age_str[2:]) - 2
        if re.match(r"^\d{2}[-~]\d{2}$", age_str):
            parts = re.split("[-~]", age_str)
            return (int(parts[0]) + int(parts[1])) // 2
    except:
        return None

# ✅ 이탈 위험 등급 변환 함수
def get_risk_label(prob):
    if prob >= 0.7:
        return f"🔴 고위험 {prob * 100:.1f}%"
    elif prob >= 0.3:
        return f"🟠 중위험 {prob * 100:.1f}%"
    else:
        return f"🟢 저위험 {prob * 100:.1f}%"

# ✅ 메인 함수
def show_user_data(df_user):
    st.subheader("📋 이용자 데이터")

    age_options = ["전체", "20대", "30대", "40대", "50대", "60대 이상"]
    selected_age = st.selectbox("연령선택", age_options)

    # 🔄 데이터 복사
    df = df_user.copy()

    # 연령대 생성
    df["age"] = df["age"].apply(convert_age_to_int)
    df = df.dropna(subset=["age"])
    df["age"] = df["age"].astype(int)
    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 29, 39, 49, 59, 150],
        labels=["20대", "30대", "40대", "50대", "60대 이상"]
    )

    # 평균 운동시간 계산
    df["평균운동시간"] = df[["very_active_minutes", "moderately_active_minutes"]].mean(axis=1).round(1)


    # ✅ 필터 적용
    if selected_age != "전체":
        df = df[df["age_group"] == selected_age]

    if df.empty:
        st.warning("🔍 조건에 해당하는 사용자가 없습니다.")
        return

    # ✅ 결과 구성
    display_data = []
    for idx, row in df.iterrows():
        display_data.append({
            "ID": row.get("id", f"ID_{idx}"),
            "성별": row.get("gender", "미확인"),
            "나이": row.get("age", "N/A"),
            "평균운동시간": row.get("평균운동시간", "N/A"),
            "이탈가능성": get_risk_label(row.get("churn_prob", 0.0))
        })

    result_df = pd.DataFrame(display_data)
    st.dataframe(result_df, use_container_width=True)
