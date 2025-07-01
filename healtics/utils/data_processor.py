import os
import pandas as pd
import re

def convert_age_to_int(age_str):
    """
    문자열 형식의 나이(age)를 평균 숫자값으로 변환
    예: "<30" → 29, ">=30" → 32, "30s" → 35, "40대" → 45, "30-39" → 34
    """
    try:
        if pd.isnull(age_str):
            return None
        age_str = str(age_str).strip()
        if age_str.startswith("<"):
            return int(age_str[1:]) - 1
        if age_str.startswith(">="):
            return int(age_str[2:]) + 2
        if age_str.endswith("s"):
            return int(age_str[:-1]) + 5
        if age_str.endswith("대"):
            return int(age_str[:-1]) + 5
        if "-" in age_str or "~" in age_str:
            parts = re.split("[-~]", age_str)
            return (int(parts[0]) + int(parts[1])) // 2
        return int(age_str)
    except:
        return None

def load_fitbit_data(base_path="data/raw/lifesnaps/rais_anonymized/csv_rais_anonymized"):
    """
    Fitbit CSV 데이터를 로드하고, 날짜/나이(age) 컬럼을 전처리한 DataFrame 반환
    """
    daily_file = os.path.join(base_path, "daily_fitbit_sema_df_unprocessed.csv")

    if not os.path.exists(daily_file):
        raise FileNotFoundError(f"❌ 파일이 존재하지 않음: {daily_file}")

    df = pd.read_csv(daily_file)

    # ✅ 날짜 컬럼 변환
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    else:
        raise ValueError("❌ 'date' 컬럼이 존재하지 않습니다.")

    # ✅ age 전처리: 문자열 → 숫자, NaN 제거
    if "age" in df.columns:
        df["age"] = df["age"].apply(convert_age_to_int)
        df = df.dropna(subset=["age"])
        df = df[df["age"] >= 10]
    else:
        raise ValueError("❌ 'age' 컬럼이 존재하지 않습니다.")

    return df
