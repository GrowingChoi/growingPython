import streamlit as st
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import f1_score
import plotly.express as px
from components.model_train import prepare_data, train_xgb_model_with_smote

# 문자열 나이 변환 함수
def convert_age_to_numeric(age_str):
    try:
        if isinstance(age_str, str):
            if '<' in age_str:
                return int(age_str.replace('<', '')) - 1
            elif '>' in age_str:
                return int(age_str.replace('>', '')) + 1
            elif '-' in age_str:
                a, b = age_str.split('-')
                return (int(a) + int(b)) // 2
            else:
                return int(age_str)
        return age_str
    except:
        return None

# 메인 함수
def show_healthcare_graph(df):
    try:
        # ✅ 나이 변환
        if "나이" not in df.columns and "age" in df.columns:
            df["나이"] = df["age"].apply(convert_age_to_numeric)

        df["나이"] = pd.to_numeric(df["나이"], errors="coerce")

        # ✅ 연령대 파생
        bins = [0, 29, 39, 49, 59, 120]
        labels = ["20대", "30대", "40대", "50대", "60대"]
        try:
            df["연령대"] = pd.cut(df["나이"], bins=bins, labels=labels)
        except Exception as e:
            st.error(f"연령대 구간 생성 중 오류 발생: {e}")
            return

        # ✅ 1. 기본 모델 학습
        X_train, X_test, y_train, y_test = prepare_data(df)
        basic_model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
        basic_model.fit(X_train, y_train)
        basic_f1 = f1_score(y_test, basic_model.predict(X_test), zero_division=0)

        # ✅ 2. 튜닝 모델 학습
        tuned_model, report, _ = train_xgb_model_with_smote(df)
        tuned_f1 = report["f1_score"]

        # ✅ 3. 비교 시각화
        st.subheader("📊 머신러닝 모델 학습 결과")
        comparison = pd.DataFrame({
            "모델": ["기본 모델", "튜닝 모델"],
            "F1 Score": [basic_f1, tuned_f1]
        })

        fig = px.bar(
            comparison, x="모델", y="F1 Score", color="모델",
            text="F1 Score", range_y=[0, 1.0],
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"그래프 생성 실패: {e}")
