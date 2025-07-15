import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ✅ 1. 데이터 준비 함수 (X, y만 반환)
def prepare_data(df):
    base_cols = ["steps", "calories", "very_active_minutes", "moderately_active_minutes", "distance"]
    df = df.dropna(subset=base_cols + ["id"])
    df_user = df.groupby("id")[base_cols].mean().reset_index()

    score = (
        (df_user["steps"] < 6400).astype(int) +
        (df_user["calories"] < 1800).astype(int) +
        (df_user["very_active_minutes"] < 6).astype(int) * 2 +
        (df_user["moderately_active_minutes"] < 8).astype(int) +
        (df_user["distance"] < 4600).astype(int)
    )

    df_user["CHURNED"] = (score >= 4).astype(int)
    X = df_user[base_cols]
    y = df_user["CHURNED"]
    return X, y

# ✅ 2. train_test_split 수행하는 함수 (X_train, X_test, y_train, y_test 반환)
def split_data(df):
    X, y = prepare_data(df)
    return train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)

# ✅ 3. 4개 모델 비교
def compare_models(X_train, X_test, y_train, y_test):
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42),
        "SVM": SVC(probability=True, random_state=42)
    }

    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results.append({
            "Model": name,
            "Accuracy": round(accuracy_score(y_test, y_pred), 4),
            "Precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "Recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "F1-score": round(f1_score(y_test, y_pred, zero_division=0), 4)
        })

    return pd.DataFrame(results)

# ✅ 4. XGBoost 단일 모델 - 기본 vs 교차검증 비교
def evaluate_basic_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4)
    }

def evaluate_cv_model(X, y, cv=5):
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    return {
        "accuracy": round(cross_val_score(model, X, y, scoring='accuracy', cv=skf).mean(), 4),
        "precision": round(cross_val_score(model, X, y, scoring='precision', cv=skf).mean(), 4),
        "recall": round(cross_val_score(model, X, y, scoring='recall', cv=skf).mean(), 4),
        "f1_score": round(cross_val_score(model, X, y, scoring='f1', cv=skf).mean(), 4)
    }

def compare_xgb_variants(df):
    X, y = prepare_data(df)
    basic = evaluate_basic_model(X, y)
    cv = evaluate_cv_model(X, y)
    return {
        "기본 모델": basic,
        "교차검증 모델": cv
    }
