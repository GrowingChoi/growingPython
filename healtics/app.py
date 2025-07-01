import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from components.model_train import (
    train_best_xgb_model,
    train_xgb_model_with_smote,
    plot_metrics_bar
)
from utils.data_processor import load_fitbit_data
from components.care_analytic import show_healthcare_result
from components.care_graph import show_healthcare_graph
from components.care_predict import show_prediction_summary, prepare_data, get_cross_val_probs
from components.care_predict_graph import show_prediction_graphs
from components.model_compare import compare_models, split_data
from components.care_userData import show_user_data

# ├── Sidebar state
if 'show_healthcare_sub' not in st.session_state:
    st.session_state['show_healthcare_sub'] = False
if 'show_prediction_sub' not in st.session_state:
    st.session_state['show_prediction_sub'] = False
if 'main_menu' not in st.session_state:
    st.session_state['main_menu'] = "지표 확인"

# ├── Sidebar menu
with st.sidebar:
    st.title("📌 LNB 메뉴")

    if st.button("지표 확인"):
        st.session_state['main_menu'] = "지표 확인"
        st.session_state['show_healthcare_sub'] = False
        st.session_state['show_prediction_sub'] = False

    if st.button("헬스케어 분석"):
        st.session_state['main_menu'] = "헬스케어 분석"
        st.session_state['show_healthcare_sub'] = False
        st.session_state['show_prediction_sub'] = False

    if st.button("예측 결과 열기/닫기"):
        st.session_state['show_prediction_sub'] = not st.session_state['show_prediction_sub']
        st.session_state['main_menu'] = "예측 결과"

    if st.session_state['show_prediction_sub']:
        sub_menu = st.radio("예측 결과", ["결과", "이용자 관리"], key="pred_sub")
        st.session_state['main_menu'] = f"예측 결과 - {sub_menu}"

    if st.button("이용자 데이터"):
        st.session_state['main_menu'] = "이용자 데이터"
        st.session_state['show_healthcare_sub'] = False
        st.session_state['show_prediction_sub'] = False

    # if st.button("모델 비교"):
    #     st.session_state['main_menu'] = "모델 비교"

# ├── Data loading
with st.spinner("📂 Fitbit 데이터 로드 중..."):
    df = load_fitbit_data()
    st.sidebar.success("✅ 데이터 로드 완료!")

# ├── Overview function

def show_overview():
    st.header("🔢 연령별 사용자 수치")
    try:
        df_user, X, y = prepare_data(df)

        # 🔍 원본 df에서 age 정보 병합
        df_user = df_user.copy()
        df_user = pd.merge(df_user, df[["id", "age"]].drop_duplicates(), on="id", how="left")

        # age 변환 및 필터링
        df_user["age"] = pd.to_numeric(df_user["age"], errors="coerce")
        df_user = df_user.dropna(subset=["age"])
        df_user = df_user[df_user["age"] >= 10]

        # 연령대 구간
        bins = [0, 29, 39, 49, 59, 69, 150]
        labels = ['20대', '30대', '40대', '50대', '60대', '70대 이상']
        df_user["age_group"] = pd.cut(df_user["age"], bins=bins, labels=labels)

        # 분포 계산
        age_dist = df_user["age_group"].value_counts().sort_index()
        total = age_dist.sum()
        age_percent = (age_dist / total) * 100 if total > 0 else pd.Series(data=[0]*len(age_dist), index=age_dist.index)

        # 📊 출력
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.pie(
                names=age_percent.index,
                values=age_percent.values,
                title='연령대별 사용자 비율',
                width=600,
                height=600,
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("사용자 수: ", len(df_user))
            age_df = age_percent.round(2).reset_index()
            age_df.columns = ["연령대", "비율 (%)"]
            st.dataframe(age_df)

        # with st.expander("📌 디버그 로그 보기"):
        #     st.write("df_user 샘플:", df_user[["id", "age", "age_group"]].head())
        #     st.write("age null 비율:", df_user["age"].isnull().mean())
        #     st.write("age_group 분포:", df_user["age_group"].value_counts(dropna=False))

    except Exception as e:
        st.error(f"데이터 준비 오류: {e}")


# ├── Render content
menu = st.session_state.get("main_menu", "지표 확인")

if menu == "지표 확인":
    show_overview()

elif menu == "헬스케어 분석":
    df_user, X, y = prepare_data(df)

    # 🔹 성별 및 나이 추가 병합
    demographics = df[["id", "gender", "age"]].drop_duplicates()
    df_user = pd.merge(df_user, demographics, on="id", how="left")

    # 🔹 이탈 확률 및 위험군 추가
    probs = get_cross_val_probs(X, y)
    df_user["churn_prob"] = probs
    df_user["risk"] = pd.cut(df_user["churn_prob"], bins=[-0.01, 0.3, 0.7, 1.01], labels=["저위험", "중위험", "고위험"])

    show_healthcare_result(df_user)

elif menu == "예측 결과 - 결과":
    show_prediction_summary(df)

elif menu == "예측 결과 - 이용자 관리":

    df_user, X, y = prepare_data(df)
    probs = get_cross_val_probs(X, y)
    df_user["churn_prob"] = probs
    df_user["risk"] = pd.cut(df_user["churn_prob"], bins=[-0.01, 0.3, 0.7, 1.01], labels=["저위험", "중위험", "고위험"])
    
    # 🔹 성별 및 나이 추가 병합 (필요 시)
    demographics = df[["id", "gender", "age"]].drop_duplicates()
    df_user = pd.merge(df_user, demographics, on="id", how="left")

    show_prediction_graphs(df_user)


elif menu == "이용자 데이터":

    # 1. 예측 대상 데이터 준비
    df_user, X, y = prepare_data(df)

    # 2. 이탈 확률 및 등급 부여
    df_user["churn_prob"] = get_cross_val_probs(X, y)
    df_user["risk"] = pd.cut(df_user["churn_prob"], bins=[-0.01, 0.3, 0.7, 1.01], labels=["저위험", "중위험", "고위험"])

    # 3. 성별, 나이 정보 병합
    demographics = df[["id", "gender", "age"]].drop_duplicates()
    df_user = pd.merge(df_user, demographics, on="id", how="left")

    # 4. 사용자 UI 출력 
    show_user_data(df_user)


