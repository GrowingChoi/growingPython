## 📚 주요 목차

> 1️⃣ 🚀 프로젝트명 및 개요<br>
> 2️⃣ 👥 팀 소개<br>
> 3️⃣ 🎮 게임 사용설명서<br>
> 4️⃣ 📚 수집 데이터 설명명<br>
> 5️⃣ 🛠 기술 스택<br>
> 6️⃣ 📊 ERD (Entity Relationship Diagram)<br>
> 7️⃣ 📋 테이블 명세<br>
> 9️⃣ 💭 한줄 회고


# 🚀 프로젝트명 및 개요 

> ## 🏅 VOTE your FAVORITE !🏅
> 2010-2025 국내외 자동차 월드컵 게임 (신차 정보 데이터 비교, 신차 구매 사이트  URL 연결) 및 FAQ 조회 시스템

## 📌 프로젝트 개요
- **프로젝트명:** 2010–2025 국내외 자동차 월드컵 게임 및 FAQ 조회 시스템
- **설명:** 본 프로젝트는 사용자가 자동차 월드컵 게임을 통해 **선호도**를 파악하고, 다양한 신차 정보를 데이터로 제공하여 **차량 간 비교**가 가능합니다. 최종적으로는 가장 선호하는 차량을 선정하고, **해당 차량의 구매 사이트 URL**로 연결되어 구매에 도움을 줄 수 있도록 구매 정보를 제공합니다.
- **✨ 주요 기능:**
> - 게임 시작 전 가격 조건 필터링
> - 자동차 월드컵 게임 (16강 토너먼트 방식)
> - 신차 정보 사이트 URL 연결 기능
> - 우승차량통계 시스템 (우승차량 통계 차트)

---
# 👥 팀 소개 <a display=none>## 개발자 소개</a>

## 🙌🏻 팀명 : **챔피언스리그🏆팀**  
>  우리 팀의 이름 ‘챔피언스리그’는 프로젝트의 핵심 기능인 자동차 월드컵 게임에서 아이디어를 얻어 지어진 이름입니다. 실제 축구 챔피언스리그처럼, 자동차들 간의 치열한 토너먼트를 통해 최종 우승 차량(챔피언)을 선정하는 컨셉을 담고 있습니다. <br> "실제 챔피언스리그 경기처럼 흥미진진한 자동차 월드컵이 되시길 바랍니다🥇"

##  🙋🏻 팀원 소개
<table align="center">
  <thead>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/719dfe50-9b45-470e-bdc6-c22a57508169" width=200 alt="keun"/><br />
      <a href='https://github.com/jiyun-kang12'>강지윤</a><br />
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/15564914-0659-415c-b960-3b432cabbf76" width=200 alt="mojiho"/><br />
      <a href='https://github.com/mojiho'>모지호</a><br/>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/abe3a34e-7611-43a4-8c54-10387206ab31" width=200 alt="Jinhyeok3"/><br />
      <a href='https://github.com/Jinhyeok3'>전진혁</a><br />
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/a69165a2-1064-48d6-9d63-12105fdb814c" width=200 alt="seonguihong"/><br />
      <a href='https://github.com/seonguihong'>홍성의</a><br />
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/d9974423-da75-409f-96eb-0dfea434603a" width="200" alt="GrowingChoi"/><br />
      <a href='https://github.com/GrowingChoi'>최성장</a><br />
    </td>
  </thead>
</table>

---
##  🎮 게임 사용설명서

✨Step 1. <br>
월드컵 사이트(url: )에 접속하신 후, 게임을 시작하려면 가장 "Game Start" 버튼을 클릭해주세요!<br>
✨Step 2.<br>
게임 스타트로 넘어가면 가격을 조정할 수 있는 드롭다운 버튼이 있습니다. 원하시는 가격대로 조정해주세요!<br>
✨Step 3.<br>
게임 시작! > 월드컵은 총 16강으로 진행되며 자동차의 정보들을 비교하신 후에 원하시는 자동차 클릭<br>
✨Step 4.<br>
최종 자동차 이상형 발표!

---

## 📚 수집 데이터 설명

본 프로젝트에서 사용한 데이터 및 참고 자료는 다음과 같습니다:

---

### **신차 정보 데이터** 🚗
- **출처:** [카이즈유](https://www.carisyou.com/car/) 
- **수집 방법:** 위 웹사이트에서 **크롤링**을 통해 신차의 **차량ID**, **연비**, **연료타입**, **차급**, **외형**, **엔진**, **출력**, **이미지** 데이터를 가져왔습니다.
- **수집 목적:** 위 상세 데이터들을 수집함으로써 사용자의 폭넓은 자동차 선택 기준과 취향에 대응하고자 하였습니다.


## 🛠 기술 스택
- **프론트엔드:** Python, Streamlit
- **백엔드:** Python, Mysql(db)
- **형상관리:** GitHub
- **개발도구:** Vscode, Mysql
---
## 🌆 UI설계 (Figma)
<img width="1146" alt="Image" src="https://github.com/user-attachments/assets/509b29cb-ec18-4fd3-a0eb-124aa51d3a4f" />


## 📊 ERD (Entity Relationship Diagram)


<img width="341" alt="Image" src="https://github.com/user-attachments/assets/baf231ae-d294-4e2a-8d15-86c6f50f2c4f" />


---


## 📋 테이블 명세
<img width="814" alt="Image" src="https://github.com/user-attachments/assets/016acaf1-31fb-4002-8c68-8cfe39e94ea1" />
<img width="816" alt="Image" src="https://github.com/user-attachments/assets/e23a6894-14e4-484b-af7c-074d628d5317" />



## 💭 한줄 회고
- **강지윤:** 최최최최최최최최최최최최최종_찐최종.py
- **모지호:** 구내식당이 너무 맛있어서 하루하루 행복합니다.
- **전진혁:** html? git? master(.env)
- **홍성의:** 
- **최성장:** 
