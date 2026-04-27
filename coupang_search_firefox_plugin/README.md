# 쿠팡 vs 네이버 가격비교 Firefox 확장 프로그램

쿠팡과 네이버 쇼핑의 가격을 한눈에 비교할 수 있는 Firefox 확장 프로그램입니다.

## 특징

- ✅ **쿠팡 차단 우회**: 실제 브라우저 환경에서 실행되어 봇 감지 우회
- ✅ **네이버 쇼핑 API**: 공식 API로 정확한 가격 정보
- ✅ **실시간 비교**: 검색 즉시 두 쇼핑몰 가격 비교
- ✅ **간편한 UI**: 깔끔한 팝업 인터페이스

## 설치 및 실행

### 1. 의존성 설치

```bash
./bin/install.sh
```

이 스크립트는 다음을 확인/설치합니다:
- `web-ext` (npm 전역 패키지)
- Firefox 설치 여부

### 2. 데몬 시작

```bash
./bin/start.sh
```

Firefox가 자동으로 실행되며 확장 프로그램이 로드됩니다.

### 3. 데몬 종료

```bash
./bin/stop.sh
```

### 4. 수동 실행 (개발 모드)

```bash
cd coupang_search_firefox_plugin
web-ext run --firefox=/Applications/Firefox.app/Contents/MacOS/firefox --verbose
```

## 사용 방법

### Streamlit 앱과 연동 (기본)

1. **확장 프로그램 데몬 시작**
   ```bash
   ./bin/start.sh
   ```

2. **Streamlit 앱 실행** (상위 디렉토리)
   ```bash
   cd ..
   ./.venv/bin/python -m streamlit run app.py
   ```

3. **브라우저에서 검색**
   - http://localhost:8544 접속
   - 검색어 입력 (예: "삼다수 2L 무라벨 12개")
   - 쿠팡 결과가 백그라운드에서 자동으로 스크랩됩니다

### 팝업 단독 사용 (옵션)

1. Firefox 툴바의 확장 프로그램 아이콘 클릭
2. 검색어 입력
3. "검색" 버튼 클릭

## 네이버 API 설정

`background.js` 파일의 다음 부분에 네이버 API 키를 입력하세요:

```javascript
const clientId = NAVER_CLIENT_ID || '여기에_발급받은_Client_ID';
const clientSecret = NAVER_CLIENT_SECRET || '여기에_발급받은_Client_Secret';
```

또는 나중에 설정 페이지를 추가하여 사용자가 직접 입력하도록 할 수 있습니다.

## 작동 원리

### Streamlit 연동 방식

1. **검색 요청 큐**:
   - Streamlit에서 검색 시 `http://localhost:8765/queue`에 요청 추가
   - Background Script가 2초마다 polling하여 큐 확인

2. **쿠팡 검색 (백그라운드)**:
   - Background Script가 큐에서 검색어 감지
   - 백그라운드 탭(`active: false`)으로 쿠팡 검색 페이지 열기
   - Content Script가 DOM에서 상품 정보 추출 (최대 8회 재시도)
   - 결과를 Background Script로 전송

3. **결과 전송 및 정리**:
   - Background Script가 결과를 Streamlit으로 POST 전송
   - 백그라운드 탭 자동 닫기
   - Streamlit에서 쿠팡/네이버 결과 비교 표시

### 주요 컴포넌트

- `background.js`: 큐 polling, 탭 관리, Streamlit 통신
- `content.js`: 쿠팡 페이지 스크랩 (다중 선택자, 재시도 로직)
- `popup/`: 단독 사용 시 UI (옵션)

## 주의사항

- **백그라운드 실행**: 쿠팡 검색 시 백그라운드 탭이 자동으로 열렸다 닫힙니다 (포커스 안빼앗김)
- **브릿지 서버**: Streamlit 실행 시 `http://localhost:8765` 포트 사용
- **네이버 API**: 하루 25,000회 호출 제한 (무료 플랜)
- **페이지 구조 변경**: 쿠팡 사이트 변경 시 `content.js`의 선택자 업데이트 필요
- **첫 검색 시간**: 초기 로딩 시 20-30초 소요 가능 (쿠팡 페이지 로딩 + 스크랩)

## 파일 구조

```
coupang_search_firefox_plugin/
├── manifest.json          # 확장 프로그램 설정
├── bin/                   # 데몬 관리 스크립트
│   ├── install.sh        # 의존성 설치
│   ├── start.sh          # 데몬 시작
│   └── stop.sh           # 데몬 종료
├── popup/
│   ├── popup.html        # 팝업 UI
│   ├── popup.js          # 팝업 로직
│   └── popup_test.html   # 테스트 페이지
├── content.js            # 쿠팡 페이지 스크랩
├── background.js         # 큐 polling, Streamlit 통신
├── icons/                # 아이콘
└── README.md
```

## 트러블슈팅

### 검색이 안될 때

1. **데몬 상태 확인**
   ```bash
   ps aux | grep web-ext
   ```

2. **브릿지 서버 확인**
   ```bash
   curl http://localhost:8765/queue
   ```

3. **로그 확인**
   ```bash
   tail -f .web-ext.log
   ```

4. **Firefox 콘솔 확인**
   - F12 → Console 탭
   - `[Background]` 로그 확인

### 데몬 재시작

```bash
./bin/stop.sh && ./bin/start.sh
```

## 개선 아이디어

- [x] Streamlit 연동
- [x] 백그라운드 탭 실행 (포커스 안빼앗김)
- [x] 자동 탭 닫기
- [ ] 설정 페이지 추가 (네이버 API 키 입력)
- [ ] 가격 히스토리 저장
- [ ] 알림 기능 (가격 하락 시)
- [ ] 다른 쇼핑몰 추가 (11번가, G마켓 등)

## 라이선스

MIT License
