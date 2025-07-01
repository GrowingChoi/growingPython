import pandas as pd

def predict(model):
    print("자 모델 예측 드가자~~~")
    # 테스트 데이터 로드
    X_test = pd.read_csv('data/processed/X_test.csv')

    # 예측 수행
    predictions = model.predict(X_test)
    print("예측 끝")
    return predictions
