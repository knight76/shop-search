"""쿠팡 검색 모델"""
import urllib.parse
from curl_cffi import requests as creq
from bs4 import BeautifulSoup


class CoupangSearcher:
    """쿠팡 검색 클래스"""

    def __init__(self):
        self.base_url = "https://www.coupang.com"

    def search(self, keyword: str, limit: int = 20) -> list[dict]:
        """
        쿠팡 검색 결과 스크래핑

        Args:
            keyword: 검색어
            limit: 결과 개수

        Returns:
            검색 결과 리스트 [{'name', 'price', 'link', 'mall', 'image'}]
        """
        url = (
            f"{self.base_url}/np/search"
            f"?q={urllib.parse.quote(keyword)}&listSize={limit}&channel=user"
        )

        s = creq.Session(impersonate="chrome131")

        # 더 많은 헤더로 실제 브라우저처럼 위장
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"{self.base_url}/",
            "Sec-Ch-Ua": '"Not A(Brand";v="8", "Chromium";v="131", "Google Chrome";v="131"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        # 1) 메인 페이지 먼저 방문해서 쿠키 받기
        try:
            s.get(f"{self.base_url}/", headers=headers, timeout=10)
            import time
            time.sleep(0.5)
        except Exception:
            pass

        # 2) 검색
        r = s.get(url, headers=headers, timeout=15)

        if r.status_code != 200:
            return []

        # 봇 감지 페이지 확인
        if len(r.text) < 10000 or "akamai" in r.text.lower():
            return []

        return self._parse_results(r.text, limit)

    def _parse_results(self, html: str, limit: int) -> list[dict]:
        """HTML 파싱하여 상품 정보 추출"""
        soup = BeautifulSoup(html, "lxml")
        items = []

        for li in soup.select("li.search-product")[:limit]:
            name_el = li.select_one("div.name")
            price_el = li.select_one("strong.price-value")
            link_el = li.select_one("a.search-product-link")
            rocket = bool(li.select_one("span.badge.rocket"))
            img_el = li.select_one("img")

            if not (name_el and price_el and link_el):
                continue

            try:
                price = int(price_el.get_text(strip=True).replace(",", ""))
            except ValueError:
                continue

            # 이미지 URL
            img_url = ""
            if img_el:
                img_url = img_el.get("data-img-src") or img_el.get("src", "")
                if img_url and img_url.startswith("//"):
                    img_url = "https:" + img_url

            items.append({
                "mall": "쿠팡 🚀" if rocket else "쿠팡",
                "name": name_el.get_text(strip=True),
                "price": price,
                "link": f"{self.base_url}{link_el['href']}",
                "image": img_url,
            })

        return items
