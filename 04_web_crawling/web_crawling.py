import requests, lxml
from bs4 import BeautifulSoup
from pprint import pprint
import time

차량ID = []; 연비 = []; 연료타입 = []; 차급 = []; 외형 = []; 엔진 = []; 가격 = []; 이미지 = []; 출력 = []
# 서버와의 연결 확인
try:
    for i in range(7539, 6558, -1):
        url = f'https://www.carisyou.com/car/{i}/Spec'
        response = requests.get(url)  # url에 GET 요청을 보낸다. -> url의 HTML을 가져와
        time.sleep(4)
        response.raise_for_status()  # 요청이 성공했는지 확인한다. 실패했으면 raise 시켜 / 200대 번호가 성공이야
        parser = BeautifulSoup(response.text, 'lxml')
        # HTML을 문자열로 바꿔 html.parser를 돌려. -> 구조화된 문자열 데이터가 parser 객체에 저장돼
        elements = parser.select('div.car_gallery > h4.title, div.car_info > div.info > dl > dd,\
                                 #carInfo > div:nth-child(5) > div > div.table_box_left > table > tbody > tr:nth-child(1) > td') # 차량ID, 연비+연료타입+차급+외형, 엔진
        elements2 = parser.select('div.car_info > h4 > span') # 가격
        elements3 = parser.select('#container > div:nth-child(3) > div > div.car_detail_top > div.car_detail > div.car_gallery > p > img') # 이미지
        elements4 = parser.select('#carInfo > div:nth-child(4) > div > div.table_box_left > table > tbody > tr:nth-child(2) > td,\
                                  #carInfo > div:nth-child(4) > div > div.table_box_right > table > tbody > tr:nth-child(7) > td') # 마력 두 종류
        
        if elements2[0].text == '-': continue # 가격 없는 애 무시
        차량ID.append(elements[0].text) # 여러 개의 태그 객체를 한 번에 받아올 땐 리스트로 받아와.
        연비.append(elements[1].text.replace('\xa0', '')) # .text 메소드는 하나의 태그 객체 대상으로만 호출이 가능해서 elements.text[0] 같은 나쁜 말은 X
        연료타입.append(elements[2].text)
        차급.append(elements[3].text)
        외형.append(elements[4].text.replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', ''))
        엔진.append(elements[5].text.replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', '')) # 페이지를 넘겨야해서 안되는 거였어......

        if len(elements2) > 1: # 1억 이상 / 범위
            if len(elements2[0].text) <= 2: # 3 (억) 3943 (만원) 꼴
                elements2_real = elements2[0].text.strip().replace(',', '') + elements2[1].text.strip().replace(',', '')
                가격.append(elements2_real)
            else: # 4,322 ~ 5,233 꼴
                elements2_real = elements2[1].text.strip().replace(',', '')
                가격.append(elements2_real)
        else: # 4,322 꼴
            elements2_real = elements2[0].text.strip().replace(',', '')
            가격.append(elements2_real)

        이미지.append(elements3[0].get('src'))
        
        elements4_real = elements4[0].text.replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', '')
        if elements4_real == '-마력':
            출력.append(elements4[1].text.replace('\t', '').replace('\n', '').replace('\r', '').replace(' ', '')) 
        else: 출력.append(elements4_real)

finally:
    print('차량ID:', 차량ID, '연비:', 연비, '연료타입:', 연료타입, '차급:', 차급, '외형:', 외형, '엔진:', 엔진, '가격:', 가격, '이미지:', 이미지, '출력:', 출력, sep='\n')

import os
from datetime import datetime
import pandas as pd

save_dir = "1st_project"
os.makedirs(save_dir, exist_ok=True) # 있어도 괜찮아 넘어가~ 
d = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
file_path = f"{save_dir}/{d}.csv"
# DataFrame 생성
result_df = pd.DataFrame({
    '차량ID':차량ID,
    '연비': 연비,
    '연료타입':연료타입,
    '차급':차급,
    '외형':외형,
    '엔진':엔진,
    '가격':가격,
    '이미지':이미지,
    '출력':출력
})

# csv 파일로 저장.
result_df.to_csv(file_path, index=False)
