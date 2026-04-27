// 쿠팡 검색 결과 페이지에서 상품 정보 추출
(function() {
  console.log('[Coupang Ext] Content script loaded');
  console.log('[Coupang Ext] URL:', window.location.href);
  console.log('[Coupang Ext] Document ready state:', document.readyState);

  // 페이지 HTML 일부 확인
  setTimeout(() => {
    console.log('[Coupang Ext] Page title:', document.title);
    console.log('[Coupang Ext] Body length:', document.body.innerHTML.length);

    // Akamai 감지 확인
    if (document.body.innerHTML.includes('akamai')) {
      console.error('[Coupang Ext] ❌ Akamai detected - bot protection active');
    }

    // 주요 클래스 확인
    const allClasses = new Set();
    document.querySelectorAll('[class]').forEach(el => {
      el.classList.forEach(cls => {
        if (cls.toLowerCase().includes('product') || cls.toLowerCase().includes('item')) {
          allClasses.add(cls);
        }
      });
    });
    console.log('[Coupang Ext] Product-related classes found:', Array.from(allClasses));
  }, 1000);

  // 페이지가 완전히 로드될 때까지 대기 (더 긴 시간)
  function waitForProducts(retryCount = 0) {
    console.log(`[Coupang Ext] Waiting for products... retry ${retryCount}`);

    // 다양한 선택자 시도
    const selectors = [
      'li.search-product',
      'li[class*="search-product"]',
      'ul.search-product-list li',
      '[data-component-type="s-product-item"]',
      'li[class*="product"]',
      'div[class*="product-item"]',
      '[id*="productItem"]'
    ];

    let products = [];
    let usedSelector = null;

    for (const selector of selectors) {
      products = document.querySelectorAll(selector);
      if (products.length > 0) {
        usedSelector = selector;
        console.log(`[Coupang Ext] ✅ Found ${products.length} products with selector: ${selector}`);
        break;
      } else {
        console.log(`[Coupang Ext] ❌ No products with selector: ${selector}`);
      }
    }

    if (products.length > 0) {
      extractProducts(products);
    } else if (retryCount < 8) {
      // 최대 8번 재시도 (총 16초)
      setTimeout(() => waitForProducts(retryCount + 1), 2000);
    } else {
      // 상품을 찾지 못함 - HTML 일부 출력
      console.error('[Coupang Ext] ❌ No products found after retries');
      console.log('[Coupang Ext] Page HTML sample:', document.body.innerHTML.substring(0, 500));
      sendResults([]);
    }
  }

  function extractProducts(products) {
    console.log(`[Coupang Ext] Extracting from ${products.length} products`);
    const items = [];

    products.forEach((product, index) => {
      try {
        // 다양한 선택자 시도
        const nameEl = product.querySelector('div.name') ||
                      product.querySelector('[class*="name"]') ||
                      product.querySelector('.search-product__name');

        const priceEl = product.querySelector('strong.price-value') ||
                       product.querySelector('[class*="price-value"]') ||
                       product.querySelector('.search-product__price');

        const linkEl = product.querySelector('a.search-product-link') ||
                      product.querySelector('a[href*="/vp/products/"]') ||
                      product.querySelector('a');

        const rocketEl = product.querySelector('span.badge.rocket') ||
                        product.querySelector('[class*="rocket"]');

        if (nameEl && priceEl && linkEl) {
          const priceText = priceEl.textContent.trim().replace(/,/g, '');
          const price = parseInt(priceText);

          if (!isNaN(price)) {
            const item = {
              name: nameEl.textContent.trim(),
              price: price,
              link: linkEl.getAttribute('href').startsWith('http')
                ? linkEl.getAttribute('href')
                : 'https://www.coupang.com' + linkEl.getAttribute('href'),
              mall: rocketEl ? '쿠팡 🚀' : '쿠팡'
            };
            items.push(item);
            console.log(`[Coupang Ext] Item ${index + 1}:`, item.name, item.price);
          }
        } else {
          console.log(`[Coupang Ext] Missing elements for product ${index + 1}:`, {
            name: !!nameEl,
            price: !!priceEl,
            link: !!linkEl
          });
        }
      } catch (e) {
        console.error('[Coupang Ext] 상품 파싱 에러:', e);
      }
    });

    console.log(`[Coupang Ext] Successfully extracted ${items.length} items`);
    sendResults(items);
  }

  function sendResults(items) {
    const keyword = new URLSearchParams(window.location.search).get('q');

    browser.runtime.sendMessage({
      type: 'COUPANG_RESULTS',
      keyword: keyword,
      items: items
    });
  }

  // 페이지 로드 후 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForProducts);
  } else {
    waitForProducts();
  }
})();
