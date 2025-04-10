import streamlit as st
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import pymysql
import re

# 저장 경로 설정
save_dir = "1st_project"
os.makedirs(save_dir, exist_ok=True)

# 숫자 추출 유틸 함수
def extract_number(text):
    if not text:
        return None
    match = re.search(r'\d+', text.replace(',', ''))
    return int(match.group()) if match else None

# 크롤링 & 저장 함수
def crawl_and_save_to_csv():
    모델명 = []; 연비 = []; 연료타입 = []; 차급 = []; 외형 = []; 엔진 = []
    가격 = []; 이미지 = []; 출력 = []

    for i in range(7539, 7000, -1):
        try:
            url = f'https://www.carisyou.com/car/{i}/Spec'
            response = requests.get(url)
            time.sleep(0.2)
            response.raise_for_status()
            parser = BeautifulSoup(response.text, 'lxml')

            elements = parser.select('div.car_gallery > h4.title, div.car_info > div.info > dl > dd,\
                                     #carInfo > div:nth-child(5) > div > div.table_box_left > table > tbody > tr:nth-child(1) > td')
            elements2 = parser.select('div.car_info > h4 > span')
            elements3 = parser.select('#container > div:nth-child(3) > div > div.car_detail_top > div.car_detail > div.car_gallery > p > img')
            elements4 = parser.select('#carInfo > div:nth-child(4) > div > div.table_box_left > table > tbody > tr:nth-child(2) > td,\
                                      #carInfo > div:nth-child(4) > div > div.table_box_right > table > tbody > tr:nth-child(7) > td')

            if not (elements and elements2 and elements3 and elements4):
                st.warning(f"[{i}] 요소 누락")
                continue

            if elements2[0].text.strip() == '-':
                continue

            모델명.append(elements[0].text.strip())
            연비.append(elements[1].text.strip().replace('\xa0', ''))
            연료타입.append(elements[2].text.strip())
            차급.append(elements[3].text.strip())
            외형.append(elements[4].text.strip().replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', ''))
            엔진.append(elements[5].text.strip().replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', ''))

            if len(elements2) > 1:
                if len(elements2[0].text.strip()) <= 2:
                    price = elements2[0].text.strip().replace(',', '') + elements2[1].text.strip().replace(',', '')
                    가격.append(price)
                else:
                    가격.append(elements2[1].text.strip().replace(',', ''))
            else:
                가격.append(elements2[0].text.strip().replace(',', ''))

            이미지.append(elements3[0].get('src'))

            출력_raw = elements4[0].text.strip().replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', '')
            if '마력' not in 출력_raw and len(elements4) > 1:
                출력_raw = elements4[1].text.strip()
            숫자 = extract_number(출력_raw)
            출력.append(숫자)

        except Exception as e:
            st.warning(f"[{i}] 에러 발생: {e}")
            continue

    d = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_path = f"{save_dir}/{d}.csv"

    result_df = pd.DataFrame({
        '모델명': 모델명,
        '연비': 연비,
        '연료타입': 연료타입,
        '차급': 차급,
        '외형': 외형,
        '엔진': 엔진,
        '가격': 가격,
        '이미지': 이미지,
        '출력': 출력
    })

    result_df.to_csv(file_path, index=False)
    return file_path, result_df

# DB 삽입 함수
def insert_csv_to_db(file_path, df):
    conn = pymysql.connect(
        host='192.168.0.15',
        user='user5',
        password='9999',
        database='test_db',
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    for idx, row in df.iterrows():
        sql = """
        INSERT INTO car_info (
            model, fuel_effic, fuel_type, car_level, outfit, engine_type,
            price, img_url, horse_power
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            hp = int(row['출력']) if pd.notna(row['출력']) and isinstance(row['출력'], (int, float)) else None
            cursor.execute(sql, (
                row['모델명'],
                int(row['연비']) if pd.notna(row['연비']) and str(row['연비']).isdigit() else None,
                row['연료타입'],
                row['차급'],
                row['외형'],
                row['엔진'],
                int(row['가격']) if pd.notna(row['가격']) and str(row['가격']).isdigit() else None,
                row['이미지'],
                hp
            ))
        except Exception as e:
            st.warning(f"[{idx}] DB 삽입 실패 - 모델명: {row.get('모델명', 'N/A')} / 에러: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Carisyou 크롤링 → DB", layout="centered")
st.title("🚗 Carisyou 크롤링 → DB 업로드")

if st.button("✅ 데이터 수집 및 DB 저장"):
    with st.spinner("데이터 수집 중입니다..."):
        csv_path, df = crawl_and_save_to_csv()
        st.success(f"CSV 저장 완료 ✅\n📁 경로: {csv_path}")
        insert_csv_to_db(csv_path, df)
        st.success("🎉 MySQL 저장 완료!")
