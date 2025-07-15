import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import re
import numpy as np
import platform
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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

# ✅ 조건별 성별 이탈률 그래프 출력
def show_healthcare_result(df):
    try:
        st.subheader("📊 항목별 남성/여성 조건 충족률")

        # ✅ id 기준 사용자 단위 요약
        base_cols = ["steps", "calories", "very_active_minutes", "moderately_active_minutes", "distance"]
        df = df.dropna(subset=base_cols + ["gender"])

        # ✅ 수치 평균 + 성별, 나이 병합
        df_user = df.groupby("id")[base_cols].mean().reset_index()
        df_meta = df.groupby("id")[["gender", "age"]].first().reset_index()
        df_user = pd.merge(df_user, df_meta, on="id", how="left")

        # ✅ 컬럼 영어로 통일
        df_user = df_user.rename(columns={
            "steps": "Steps",
            "calories": "Calories",
            "very_active_minutes": "VeryActiveMinutes",
            "moderately_active_minutes": "ModerateActiveMinutes",
            "distance": "Distance",
            "gender": "Gender"
        })

        # ✅ 성별을 한글로 변환
        df_user["Gender"] = df_user["Gender"].str.upper().map({"MALE": "남성", "FEMALE": "여성"})

        # ✅ 조건 정의
        conditions = {
            "걸음 수 < 6400": df_user["Steps"] < 6400,
            "칼로리 소모 < 1800": df_user["Calories"] < 1800,
            "매우 활동적인 시간 < 6": df_user["VeryActiveMinutes"] < 6,
            "보통 활동 시간 < 8": df_user["ModerateActiveMinutes"] < 8,
            "이동 거리 < 4600": df_user["Distance"] < 4600
        }

        # ✅ 색상 정의
        custom_colors = {"남성": "#1f77b4", "여성": "#FFB6C1"}

        # ✅ 조건별 그래프 출력
        for condition_name, condition_mask in conditions.items():
            df_temp = df_user.copy()
            df_temp["ConditionMet"] = condition_mask.astype(int)
            gender_rate = df_temp.groupby("Gender")["ConditionMet"].mean().reset_index()

            fig, ax = plt.subplots(figsize=(5, 4))
            bar_colors = [custom_colors.get(g, '#999999') for g in gender_rate["Gender"]]
            sns.barplot(data=gender_rate, x="Gender", y="ConditionMet", palette=bar_colors, ax=ax)

            for idx, row in gender_rate.iterrows():
                ax.text(idx, row["ConditionMet"] + 0.02, f"{row['ConditionMet'] * 100:.2f}%", ha='center')

            ax.set_title(f"'{condition_name}'")
            ax.set_ylabel("조건 충족률")
            ax.set_xlabel("성별")
            ax.set_ylim(0, 1)
            ax.legend(
                title="성별",
                handles=[Patch(facecolor=custom_colors[g], label=g) for g in gender_rate["Gender"] if g in custom_colors]
            )
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"그래프 생성 중 오류 발생: {e}")
