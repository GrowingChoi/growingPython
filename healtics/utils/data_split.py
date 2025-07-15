from sklearn.model_selection import train_test_split

def split_data(df):
    df["DIET_SUCCESS"] = df["BMXBMI"].apply(lambda x: 1 if x < 25 else 0)
    
    features = ["BMXBMI", "PAQ605", "PAQ620", "HUQ010", "DPQ010", "RIDAGEYR", "RIAGENDR"]
    df = df[["DIET_SUCCESS"] + features].dropna()

    X = df.drop(columns=["DIET_SUCCESS", "BMXBMI"])  # 타겟 정의에 사용된 BMI 제거
    y = df["DIET_SUCCESS"]

    return train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
