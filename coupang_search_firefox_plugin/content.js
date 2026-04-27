// 쿠팡 검색 결과 페이지에서 상품 정보 추출
(function() {
  console.log('[Coupang Ext] Content script loaded');

  // 페이지가 완전히 로드될 때까지 대기 (더 긴 시간)
  function waitForProducts(retryCount = 0) {
    console.log(`[Coupang Ext] Waiting for products... retry ${retryCount}`);

    // 다양한 선택자 시도
    const selectors = [
      'li.search-product',
      'li[class*="search-product"]',
      'ul.search-product-list li',
      '[data-component-type="s-product-item"]'
    ];

    let products = [];
    for (const selector of selectors) {
      products = document.querySelectorAll(selector);
      if (products.length > 0) {
        console.log(`[Coupang Ext] Found ${products.length} products with selector: ${selector}`);
        break;
      }
    }

    if (products.length > 0) {
      extractProducts(products);
    } else if (retryCount < 5) {
      // 최대 5번 재시도 (총 10초)
      setTimeout(() => waitForProducts(retryCount + 1), 2000);
    } else {
      // 상품을 찾지 못함
      console.log('[Coupang Ext] No products found after retries');
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
    browser.runtime.sendMessage({
      type: 'COUPANG_RESULTS',
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
