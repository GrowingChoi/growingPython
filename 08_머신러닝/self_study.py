## 필요한 라이브러리 import
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier

## 1. 데이터 받아오기
dataset = load_breast_cancer()
x, y = dataset['data'], dataset['target']
x.shape, y.shape

## 2. 바로 데이터 전처리


## 3. 모델 생성



## 4. 모델 학습( 전처리된 데이터로 )



## 5. 모델 테스트



## 6. 결과값으로 모델 평가



## 7. plot로 좌표이미지 생성하기 



