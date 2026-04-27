"""네이버 쇼핑 검색 모델"""
import os
import httpx


class NaverSearcher:
    """네이버 쇼핑 검색 클래스"""

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Args:
            client_id: 네이버 API Client ID
            client_secret: 네이버 API Client Secret
        """
        self.client_id = client_id or os.getenv("NAVER_KEY") or os.getenv("NAVER_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET")
        self.api_url = "https://openapi.naver.com/v1/search/shop.json"

    def search(self, keyword: str, limit: int = 20, sort: str = "sim") -> list[dict] | None:
        """
        네이버 쇼핑 공식 검색 API

        Args:
            keyword: 검색어
            limit: 결과 개수
            sort: 정렬 (sim=정확도, date=날짜, asc=낮은가격, dsc=높은가격)

        Returns:
            검색 결과 리스트 [{'name', 'price', 'link', 'mall', 'image'}]
            인증 정보 없으면 None
        """
        if not self.client_id or not self.client_secret:
            return None

        try:
            r = httpx.get(
                self.api_url,
                params={"query": keyword, "display": min(limit, 100), "sort": sort},
                headers={
                    "X-Naver-Client-Id": self.client_id,
                    "X-Naver-Client-Secret": self.client_secret
                },
                timeout=10,
            )

            if r.status_code != 200:
                return []

            return self._parse_results(r.json())

        except Exception:
            return []

    def _parse_results(self, data: dict) -> list[dict]:
        """API 응답 파싱"""
        items = []

        for it in data.get("items", []):
            # title에 <b>태그</b> 제거
            title = it["title"].replace("<b>", "").replace("</b>", "")

            try:
                price = int(it["lprice"])
            except (ValueError, KeyError):
                continue

            items.append({
                "mall": it.get("mallName", "네이버"),
                "name": title,
                "price": price,
                "link": it["link"],
                "image": it.get("image", ""),
            })

        return items
