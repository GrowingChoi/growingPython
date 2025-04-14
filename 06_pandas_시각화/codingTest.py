from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

base_url = "https://www.acmicpc.net/problemset/"
result = []

for page in range(1, 11):  # 1페이지부터 10페이지까지
    url = f"{base_url}{page}"
    driver.get(url)
    time.sleep(2)  # 페이지가 로드될 때까지 기다림

    # 테이블 요소 찾기
    table = driver.find_element(By.ID, 'problemset')

    rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # 첫 줄은 헤더 제외

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) < 4:
            continue

        problem_id = cols[0].text.strip()
        title_tag = cols[1].find_element(By.TAG_NAME, 'a')
        title = title_tag.text.strip()
        problem_url = f"{title_tag.get_attribute('href')}"
        accuracy_text = cols[5].text.strip().replace('%', '')
        submit = cols[4].text.strip()
        correct_person = cols[3].text.strip()

        try:
            accuracy = float(accuracy_text)
        except ValueError:
            continue

        if accuracy <= 50 or accuracy >= 70:
            result.append({
                '문제 번호': problem_id,
                '제목': title,
                '맞춘사람' : correct_person,
                '제출' : submit,
                '정답률': accuracy,
                'URL': problem_url
            })

# DataFrame으로 저장
df = pd.DataFrame(result)

# 정답률 기준 오름차순 정렬 (높은 순: ascending=False)
df = df.sort_values(by='정답률', ascending=False)

# 정답률을 퍼센트 문자열로 다시 변환
df['정답률'] = df['정답률'].map(lambda x: f"{x:.1f}%")

# CSV 저장
df.to_csv("baekjoon_filtered_problems.csv", index=False, encoding='utf-8-sig')

# 콘솔 출력
print(df.to_markdown(index=False))

# 브라우저 종료
driver.quit()