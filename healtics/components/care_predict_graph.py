import streamlit as st
import pandas as pd
import numpy as np
import re
import time
import platform
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ✅ 한글 폰트 설정
if platform.system() == "Darwin":
    plt.rcParams['font.family'] = 'AppleGothic'
elif platform.system() == "Windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False


# ✅ 문자열 나이를 평균 나이(int)로 변환
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
    return None


# ✅ 이탈 위험 사용자 분류 및 문자 발송
def show_prediction_graphs(df_user):
    st.subheader("📊 이탈 위험 사용자 분류 및 관리")

    df_user = df_user.copy()

    if "churn_prob" not in df_user.columns or "risk" not in df_user.columns:
        st.warning("이탈 예측 결과가 포함된 DataFrame을 입력해주세요 (churn_prob, risk 컬럼 필요)")
        return

    # 1. 필터
    selected_risk = st.selectbox("🧪 위험 등급 선택", ["고위험", "중위험", "저위험"])
    filtered = df_user[df_user["risk"] == selected_risk].reset_index(drop=True)

    if filtered.empty:
        st.warning(f"'{selected_risk}' 그룹에 해당하는 사용자가 없습니다.")
        return

    st.markdown(f"### 🔍 {selected_risk} 이용자 목록")

    # 2. 체크박스 테이블 생성
    gb = GridOptionsBuilder.from_dataframe(filtered)
    gb.configure_selection("multiple", use_checkbox=True, pre_selected_rows=[])
    grid_options = gb.build()

    grid_response = AgGrid(
        filtered,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        theme='streamlit',
        allow_unsafe_jscode=True,
        height=400
    )

    selected = grid_response.get("selected_rows", pd.DataFrame())

    # ⛑ 안전한 selected 처리
    if isinstance(selected, pd.DataFrame) and not selected.empty:
        selected_ids = selected["id"].tolist()
    else:
        selected_ids = []

    # 3. 문자 발송 섹션
    st.markdown("---")
    st.markdown("### ✉️ 선택된 사용자에게 문자 발송")

    col1, col2 = st.columns([4, 1])
    with col1:
        msg = st.text_area("보낼 문자 내용을 입력하세요:",
                           placeholder="예: 헬스케어 활동이 저조합니다. 더 많은 활동이 필요해요!")
    with col2:
        send = st.button("📩 발송하기", use_container_width=True)

    if send:
        if not selected_ids:
            st.error("❗ 하나 이상의 이용자를 선택해주세요.")
        elif not msg.strip():
            st.error("❗ 문자 내용을 입력해주세요.")
        else:
            with st.spinner("📡 문자 발송 중..."):
                time.sleep(2)
            st.success("✅ 문자가 정상적으로 발송되었습니다!")
            st.info(f"📨 보낸 내용: {msg}")
            st.markdown(f"🧾 총 **{len(selected_ids)}명**에게 발송 완료되었습니다.")
