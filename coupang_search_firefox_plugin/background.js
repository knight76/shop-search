// 네이버 API 키 (사용자가 설정해야 함)
let NAVER_CLIENT_ID = '';
let NAVER_CLIENT_SECRET = '';

// Streamlit 브릿지 설정
const STREAMLIT_BRIDGE_URL = 'http://localhost:8765';

// 설정 로드
browser.storage.local.get(['naverClientId', 'naverClientSecret']).then(result => {
  NAVER_CLIENT_ID = result.naverClientId || '';
  NAVER_CLIENT_SECRET = result.naverClientSecret || '';
});

// 메시지 리스너
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'SEARCH_NAVER') {
    searchNaver(message.keyword).then(items => {
      sendResponse({ items });
    });
    return true; // 비동기 응답
  }

  if (message.type === 'COUPANG_RESULTS') {
    // 쿠팡 검색 결과를 Streamlit으로 전송
    sendResultsToStreamlit(message.keyword, message.items);
  }
});

// Streamlit으로 결과 전송
async function sendResultsToStreamlit(keyword, items) {
  try {
    await fetch(STREAMLIT_BRIDGE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: 'SEARCH_RESULT',
        keyword: keyword,
        items: items
      })
    });
    console.log('[Background] Sent results to Streamlit:', items.length, 'items');
  } catch (error) {
    console.error('[Background] Failed to send to Streamlit:', error);
  }
}

async function searchNaver(keyword) {
  // 환경변수나 storage에서 API 키 가져오기
  // 여기서는 ~/.zshrc의 환경변수를 사용할 수 없으므로
  // extension의 storage를 사용하거나, 사용자에게 입력받아야 함

  // 임시: 하드코딩된 키 사용 (나중에 설정 페이지 추가 필요)
  const clientId = NAVER_CLIENT_ID || 'd6Jp29D5Kpib0gZcJHvM';
  const clientSecret = NAVER_CLIENT_SECRET || 'Mzb7qEUj2b';

  if (!clientId || !clientSecret) {
    console.warn('네이버 API 키가 설정되지 않았습니다');
    return [];
  }

  try {
    const response = await fetch(
      `https://openapi.naver.com/v1/search/shop.json?query=${encodeURIComponent(keyword)}&display=20&sort=asc`,
      {
        headers: {
          'X-Naver-Client-Id': clientId,
          'X-Naver-Client-Secret': clientSecret
        }
      }
    );

    if (!response.ok) {
      console.error('네이버 API 에러:', response.status);
      return [];
    }

    const data = await response.json();
    const items = [];

    for (const item of data.items || []) {
      const title = item.title.replace(/<\/?b>/g, ''); // <b> 태그 제거
      const price = parseInt(item.lprice);

      if (!isNaN(price)) {
        items.push({
          name: title,
          price: price,
          link: item.link,
          mall: item.mallName || '네이버'
        });
      }
    }

    return items;
  } catch (error) {
    console.error('네이버 검색 에러:', error);
    return [];
  }
}
