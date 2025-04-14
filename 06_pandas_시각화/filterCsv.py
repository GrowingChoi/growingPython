import pandas as pd

# 파일 불러오기
df = pd.read_csv("baekjoon_filtered_problems.csv")

# 정답률 전처리
df['정답률'] = df['정답률'].astype(str).str.replace('%', '').astype(float)

# 필터링
easy_problems = df[(df['정답률'] >= 40)]
hard_problems = df[df['정답률'] <= 20]
middle_problems = df[(df['정답률'] > 20) & (df['정답률'] < 40)]

# print(f"Easy problems count: {len(easy_problems)}")
# print(f"Hard problems count: {len(hard_problems)}")
# print(f"Middle problems count: {len(middle_problems)}")

# 각 묶음에 대해 최소한의 문제 비율 설정
easy_count = 2  # easy 문제 2개
middle_count = 2  # middle 문제 2개
hard_count = 1  # hard 문제 1개

# 가능한 묶음의 수는 easy 문제의 개수와 hard 문제의 개수로 제한됨
group_count = min(len(easy_problems) // easy_count, len(middle_problems) // middle_count, len(hard_problems) // hard_count)

# 그룹 생성
grouped_problems = []

for _ in range(group_count):
    # 각 그룹에서 필요한 문제를 샘플링
    easy_sample = easy_problems.sample(n=easy_count)
    middle_sample = middle_problems.sample(n=middle_count)
    hard_sample = hard_problems.sample(n=hard_count)
    
    # 샘플링된 문제들을 합친 후 섞기
    group = pd.concat([easy_sample, middle_sample, hard_sample]).sample(frac=1).reset_index(drop=True)
    grouped_problems.append(group)

# 최종 결과 결합
final_result = pd.concat(grouped_problems, ignore_index=True)

# CSV로 저장
final_result.to_csv("baekjoon_sorted_grouped_problems.csv", index=False)
