const keywordInput = document.getElementById('keyword');
const searchBtn = document.getElementById('searchBtn');
const resultsDiv = document.getElementById('results');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistory');
const currentTimeEl = document.getElementById('currentTime');

// 현재 시간 표시 및 1초마다 업데이트
function updateTime() {
  const now = new Date();
  const timeStr = now.toLocaleString('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
  currentTimeEl.textContent = timeStr;
}

updateTime();
setInterval(updateTime, 1000);

// 검색 히스토리 관리
let searchHistory = [];
let currentKeyword = '';

// 히스토리 로드
browser.storage.local.get('searchHistory').then(result => {
  searchHistory = result.searchHistory || [];
  renderHistory();
});

// Enter 키 지원
keywordInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    search();
  }
});

searchBtn.addEventListener('click', search);

// 전체 삭제
clearHistoryBtn.addEventListener('click', () => {
  if (confirm('모든 검색 기록을 삭제하시겠습니까?')) {
    searchHistory = [];
    browser.storage.local.set({ searchHistory });
    renderHistory();
  }
});

function renderHistory() {
  if (searchHistory.length === 0) {
    historyList.innerHTML = '<li class="history-empty">검색 기록이 없습니다</li>';
    return;
  }

  historyList.innerHTML = searchHistory.map((item, index) => `
    <li class="history-list-item ${item === currentKeyword ? 'active' : ''}" data-keyword="${item}">
      <span class="history-item-text" title="${item}">${item}</span>
      <span class="history-item-delete" data-keyword="${item}">×</span>
    </li>
  `).join('');

  // 히스토리 항목 클릭 이벤트
  historyList.querySelectorAll('.history-list-item').forEach(item => {
    item.addEventListener('click', (e) => {
      if (!e.target.classList.contains('history-item-delete')) {
        keywordInput.value = item.dataset.keyword;
        search();
      }
    });
  });

  // 삭제 버튼 이벤트
  historyList.querySelectorAll('.history-item-delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteHistory(btn.dataset.keyword);
    });
  });
}

function addToHistory(keyword) {
  // 중복 제거
  searchHistory = searchHistory.filter(item => item !== keyword);
  // 맨 앞에 추가
  searchHistory.unshift(keyword);
  // 최대 15개까지만 저장
  searchHistory = searchHistory.slice(0, 15);

  // 즉시 화면 업데이트
  renderHistory();

  // 저장 (비동기)
  browser.storage.local.set({ searchHistory });
}

function deleteHistory(keyword) {
  searchHistory = searchHistory.filter(item => item !== keyword);
  browser.storage.local.set({ searchHistory });
  renderHistory();
}

async function search() {
  const keyword = keywordInput.value.trim();
  if (!keyword) {
    alert('검색어를 입력해주세요');
    return;
  }

  // 히스토리에 즉시 추가 및 표시
  currentKeyword = keyword;
  addToHistory(keyword);

  searchBtn.disabled = true;
  searchBtn.textContent = '검색중...';

  showLoading();

  try {
    // 쿠팡과 네이버 동시 검색
    const [coupangItems, naverItems] = await Promise.all([
      searchCoupang(keyword),
      searchNaver(keyword)
    ]);

    displayResults(coupangItems, naverItems);
  } catch (error) {
    showError('검색 중 오류가 발생했습니다: ' + error.message);
  } finally {
    searchBtn.disabled = false;
    searchBtn.textContent = '검색';
  }
}

async function searchCoupang(keyword) {
  return new Promise((resolve) => {
    // 쿠팡 검색 페이지를 백그라운드 탭으로 열기
    const url = `https://www.coupang.com/np/search?q=${encodeURIComponent(keyword)}&channel=user`;

    console.log('[Popup] Opening Coupang tab:', url);

    browser.tabs.create({ url, active: false }).then(tab => {
      const tabId = tab.id;

      // content script로부터 결과 받기
      const messageListener = (message, sender) => {
        if (sender.tab && sender.tab.id === tabId && message.type === 'COUPANG_RESULTS') {
          console.log('[Popup] Received results:', message.items?.length || 0, 'items');
          browser.runtime.onMessage.removeListener(messageListener);

          // 탭 닫기 (결과 받은 후 1초 대기)
          setTimeout(() => {
            browser.tabs.remove(tabId);
          }, 1000);

          resolve(message.items || []);
        }
      };

      browser.runtime.onMessage.addListener(messageListener);

      // 타임아웃 (15초로 증가)
      setTimeout(() => {
        console.log('[Popup] Coupang search timeout');
        browser.runtime.onMessage.removeListener(messageListener);
        browser.tabs.remove(tabId);
        resolve([]);
      }, 15000);
    });
  });
}

async function searchNaver(keyword) {
  return new Promise((resolve) => {
    browser.runtime.sendMessage({
      type: 'SEARCH_NAVER',
      keyword: keyword
    }, (response) => {
      resolve(response.items || []);
    });
  });
}

function showLoading() {
  resultsDiv.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <div>검색 중...</div>
    </div>
  `;
}

function showError(message) {
  resultsDiv.innerHTML = `
    <div class="error">${message}</div>
  `;
}

function displayResults(coupangItems, naverItems) {
  let html = '';

  // 쿠팡 결과
  html += '<div class="section">';
  html += '<div class="section-title">';
  html += '<span class="badge badge-coupang">쿠팡</span>';
  html += `<span>${coupangItems.length}개</span>`;
  html += '</div>';

  if (coupangItems.length === 0) {
    html += '<div class="info">쿠팡 검색 결과가 없습니다. 봇 감지로 차단되었을 수 있습니다.</div>';
  } else {
    coupangItems.slice(0, 10).forEach(item => {
      html += `
        <div class="item">
          <div class="item-name">${item.name}</div>
          <div class="item-meta">
            <span class="item-price">${item.price.toLocaleString()}원</span>
            <span class="item-mall">${item.mall}</span>
          </div>
        </div>
      `;
    });
  }
  html += '</div>';

  // 네이버 결과
  html += '<div class="section">';
  html += '<div class="section-title">';
  html += '<span class="badge badge-naver">네이버</span>';
  html += `<span>${naverItems.length}개</span>`;
  html += '</div>';

  if (naverItems.length === 0) {
    html += '<div class="info">네이버 검색 결과가 없습니다.</div>';
  } else {
    naverItems.slice(0, 10).forEach(item => {
      html += `
        <div class="item">
          <div class="item-name">${item.name}</div>
          <div class="item-meta">
            <span class="item-price">${item.price.toLocaleString()}원</span>
            <span class="item-mall">${item.mall}</span>
          </div>
        </div>
      `;
    });
  }
  html += '</div>';

  resultsDiv.innerHTML = html;
}
