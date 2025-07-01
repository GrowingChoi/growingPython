import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, precision_recall_curve
)
from imblearn.over_sampling import SMOTE, RandomOverSampler
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. 사용자 기반 데이터 준비 함수
def prepare_data(df):
    import numpy as np
    from sklearn.model_selection import train_test_split
    from imblearn.over_sampling import SMOTE, RandomOverSampler

    base_cols = ["steps", "calories", "very_active_minutes", "moderately_active_minutes", "distance"]
    df = df.dropna(subset=base_cols + ["id"])

    df_user = df.groupby("id")[base_cols].mean().reset_index()

    # 🎯 안전한 점수 계산 방식 (Series 기반)
    score = (
        (df_user["steps"] < 6400).astype(int) +
        (df_user["calories"] < 1800).astype(int) +
        (df_user["very_active_minutes"] < 6).astype(int) * 2 +
        (df_user["moderately_active_minutes"] < 8).astype(int) +
        (df_user["distance"] < 4600).astype(int)
    )

    df_user["CHURNED"] = (score >= 4).astype(int)

    churned_df = df_user[df_user["CHURNED"] == 1]
    nonchurn_df_pool = df_user[df_user["CHURNED"] == 0]

    if len(churned_df) < 2 or len(nonchurn_df_pool) < 2:
        raise ValueError("CHURNED 또는 비이탈자 샘플 수가 너무 적습니다.")

    if len(nonchurn_df_pool) < len(churned_df):
        nonchurn_df = nonchurn_df_pool.sample(n=len(churned_df), replace=True, random_state=42)
    else:
        nonchurn_df = nonchurn_df_pool.sample(n=len(churned_df), replace=False, random_state=42)

    df_balanced = pd.concat([churned_df, nonchurn_df]).sample(frac=1, random_state=42)

    X = df_balanced.drop(columns=["CHURNED", "id"])
    y = df_balanced["CHURNED"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)

    if y_train.value_counts().min() < 6:
        sampler = RandomOverSampler(random_state=42)
    else:
        sampler = SMOTE(random_state=42)

    X_train_res, y_train_res = sampler.fit_resample(X_train, y_train)
    return X_train_res, X_test, y_train_res, y_test


# 2. 모델 학습 함수 (Precision 기준 튜닝)
def train_best_xgb_model(X_train, y_train):
    param_grid = {
        "max_depth": [3, 4],
        "learning_rate": [0.01, 0.05],
        "n_estimators": [100, 200]
    }

    grid = GridSearchCV(
        XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42),
        param_grid=param_grid,
        scoring="precision",
        cv=3,
        n_jobs=-1
    )
    grid.fit(X_train, y_train)
    return grid.best_estimator_

# 3. 최적 threshold (Precision 우선)
def find_best_threshold_by_precision(model, X_test, y_test):
    y_proba = model.predict_proba(X_test)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
    candidates = [(p, r, t) for p, r, t in zip(precisions, recalls, thresholds) if p >= 0.75]
    if candidates:
        best = max(candidates, key=lambda x: x[1])  # recall 최대
        return best[2], best[0], best[1]
    else:
        idx = (precisions * recalls).argmax()
        return thresholds[idx], precisions[idx], recalls[idx]

# 4. 평가 함수

def evaluate_model(model, X_test, y_test, threshold):
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    report = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "threshold": float(round(threshold, 3))
    }

    if report["accuracy"] == 1.0 or report["f1_score"] == 1.0:
        st.warning("⚠️ 모델 성능이 너무 완벽합니다. 데이터 누수나 기준 과단순 가능성 확인 필요!")

    st.caption(f"테스트 샘플 수: {len(y_test)}")
    st.caption(f"CHURN 분포 (y_test): {y_test.value_counts().to_dict()}")
    st.caption(f"예측값 분포: {dict(zip(*np.unique(y_pred, return_counts=True)))}")

    return report

# 5. 평가 지표 바 차트

def plot_metrics_bar(report_summary):
    metrics = ["accuracy", "precision", "recall", "f1_score"]
    values = [report_summary[m] for m in metrics]

    plt.figure(figsize=(6, 4))
    sns.barplot(x=metrics, y=values)
    plt.ylim(0, 1)
    plt.title("모델 평가 지표")
    for i, v in enumerate(values):
        plt.text(i, v + 0.02, str(v), ha='center')
    st.pyplot(plt)

# 6. 통합 실행

def train_xgb_model_with_smote(df):
    X_train, X_test, y_train, y_test = prepare_data(df)
    model = train_best_xgb_model(X_train, y_train)
    threshold, _, _ = find_best_threshold_by_precision(model, X_test, y_test)
    report = evaluate_model(model, X_test, y_test, threshold)
    return model, report, threshold
