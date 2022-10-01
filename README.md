# 어떻게 작동하는가
## 게임 - 웹API
![GameAPILogic](https://github.com/sserve-kr/DodgeGame/blob/064b8dab83a46a4297cdbc4cdb9aee75d57a068d/logicdraws/logic-GameAPILogic.drawio.png)

---

# TODO
+ API
  - 학번에 따라 임시 API 키 값 가져오게 하기
  - 최대 학번 입력 3번
+ 게임
  - 플레이 가능 횟수 추가 (메인, 결과)
+ 웹
  - API와 연동한 웹페이지 만들기 (프론트엔드 가능)
  - Github Pages 이용?
  
## 인증방식 아이디어
1. 컴퓨터에서 클라이언트로 로그인 & 학번에 따른 서버의 랜덤 토큰 값 로컬에 캐시 (서버는 랜덤 토큰 값 생성 후 학번과 함께 저장)
2. 학번 입력 시 서버에서 플레이 가능 횟수 체크 후 가능 시 AES 이용해 암호화된 Base Project Key값과 Salt 받고 캐시
3. 클라이언트에서 복호화 후 Base로 연결, 점수 Put request 넣기
