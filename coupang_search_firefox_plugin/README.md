# 쿠팡 vs 네이버 가격비교 Firefox 확장 프로그램

쿠팡과 네이버 쇼핑의 가격을 한눈에 비교할 수 있는 Firefox 확장 프로그램입니다.

## 특징

- ✅ **쿠팡 차단 우회**: 실제 브라우저 환경에서 실행되어 봇 감지 우회
- ✅ **네이버 쇼핑 API**: 공식 API로 정확한 가격 정보
- ✅ **실시간 비교**: 검색 즉시 두 쇼핑몰 가격 비교
- ✅ **간편한 UI**: 깔끔한 팝업 인터페이스

## 설치 방법

### 1. Firefox에서 임시 설치 (개발자 모드)

1. Firefox 주소창에 `about:debugging` 입력
2. "임시 확장 기능 로드" 클릭
3. `manifest.json` 파일 선택

### 2. 아이콘 추가

아이콘 파일을 `icons/` 폴더에 추가하세요:
- `icon-48.png` (48x48 픽셀)
- `icon-96.png` (96x96 픽셀)

간단한 아이콘은 다음 명령으로 생성할 수 있습니다:

```bash
# ImageMagick 사용
convert -size 48x48 xc:purple -pointsize 32 -fill white -gravity center -annotate +0+0 '🛒' icons/icon-48.png
convert -size 96x96 xc:purple -pointsize 64 -fill white -gravity center -annotate +0+0 '🛒' icons/icon-96.png
```

또는 온라인 아이콘 생성기를 사용하세요.

## 사용 방법

1. Firefox 툴바의 확장 프로그램 아이콘 클릭
2. 검색어 입력 (예: "삼다수 2L 무라벨")
3. "검색" 버튼 클릭
4. 쿠팡과 네이버 결과 비교

## 네이버 API 설정

`background.js` 파일의 다음 부분에 네이버 API 키를 입력하세요:

```javascript
const clientId = NAVER_CLIENT_ID || '여기에_발급받은_Client_ID';
const clientSecret = NAVER_CLIENT_SECRET || '여기에_발급받은_Client_Secret';
```

또는 나중에 설정 페이지를 추가하여 사용자가 직접 입력하도록 할 수 있습니다.

## 작동 원리

1. **쿠팡 검색**: 
   - 백그라운드 탭으로 쿠팡 검색 페이지 열기
   - Content Script가 DOM에서 상품 정보 추출
   - 결과를 팝업으로 전송
   - 탭 자동 닫기

2. **네이버 검색**:
   - Background Script에서 네이버 쇼핑 API 호출
   - 결과를 팝업으로 전송

3. **결과 표시**:
   - 두 결과를 가격순으로 정렬하여 표시

## 주의사항

- 쿠팡 검색 시 백그라운드에서 탭이 잠깐 열렸다 닫힙니다 (정상 동작)
- 네이버 API는 하루 25,000회 호출 제한이 있습니다
- 쿠팡 페이지 구조 변경 시 `content.js`의 선택자 업데이트 필요

## 파일 구조

```
coupang_search_firefox_plugin/
├── manifest.json          # 확장 프로그램 설정
├── popup/
│   ├── popup.html        # 팝업 UI
│   └── popup.js          # 팝업 로직
├── content.js            # 쿠팡 페이지 파싱
├── background.js         # 네이버 API 호출
├── icons/                # 아이콘 (직접 추가 필요)
│   ├── icon-48.png
│   └── icon-96.png
└── README.md
```

## 개선 아이디어

- [ ] 설정 페이지 추가 (네이버 API 키 입력)
- [ ] 가격 히스토리 저장
- [ ] 알림 기능 (가격 하락 시)
- [ ] 다른 쇼핑몰 추가 (11번가, G마켓 등)
- [ ] 북마크 기능

## 라이선스

MIT License
