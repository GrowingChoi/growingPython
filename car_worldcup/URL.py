from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager import driv
import time

service = Service(executable_path=ChromeDriverManager().install())
option = webdriver.ChromeOptions()
option.add_argument('--headless')
browser = webdriver.Chrome(service=service, options=option)
browser.implicitly_wait(2)

def get_url(model:str):
    """
    carisyou 사이트에 기재되어 있는 모델명을 str으로 입력받아
    관련 검색창 링크를 반환해주는 함수
    """
    browser.get(f'https://www.carisyou.com/')
    
    # 주어진 모델명으로 검색
    query_textfield = browser.find_element(By.CSS_SELECTOR, '#header > div.header_search > div > div.search_con > form > span > label > input[type=text]')
    query_textfield.send_keys(model)
    query_textfield.send_keys(Keys.ENTER)
    
    # 검색창에서 고유 url 번호 따와
    query_urls = [url.get_attribute('href') for url in browser.find_elements(By.CSS_SELECTOR, '#container > div:nth-child(9) > div > div.full_box_left > \
                                                                             div.search_detail_con > div > div > div > table > tbody > tr > td:nth-child(2) > a')]
    for url in query_urls:
        browser.get(url)
        car_name = browser.find_element(By.CSS_SELECTOR, '#container > div:nth-child(4) > div > div.car_detail_top > div.car_detail > div.car_gallery > h4.title')
        print('car_name.text.strip():',car_name.text.strip(),'model.strip():',model.strip())
        if car_name.text.strip() == model.strip():
            return url
        else:
            continue
    return '검색 결과가 없습니다.'
