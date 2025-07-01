import joblib
import os

def save_model(model, filename='models/churn_model.pkl'):
    print("자 모델 저장 드가자~~~")
    # 모델 저장 디렉토리 생성
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, filename)
    print(f"모델 저장 완료스 → {filename}")
