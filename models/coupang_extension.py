"""Firefox 확장 프로그램을 통한 쿠팡 검색"""
import time
import webbrowser
from typing import Optional
from .extension_bridge import ExtensionBridge


class CoupangExtensionSearcher:
    """Firefox 확장 프로그램을 통한 쿠팡 검색"""

    def __init__(self, bridge: ExtensionBridge):
        self.bridge = bridge

    def search(self, keyword: str, limit: int = 20, timeout: int = 30) -> Optional[list]:
        """
        Firefox 확장 프로그램으로 쿠팡 검색

        Args:
            keyword: 검색어
            limit: 결과 개수
            timeout: 대기 시간 (초)

        Returns:
            검색 결과 리스트 또는 None
        """
        # 기존 결과 초기화
        self.bridge.clear_results(keyword)

        # Firefox에서 쿠팡 검색 페이지 열기
        # 확장 프로그램이 자동으로 검색 수행
        url = f"https://www.coupang.com/np/search?q={keyword}&channel=user"

        try:
            webbrowser.get('firefox').open(url)
        except Exception:
            # Firefox가 기본 브라우저가 아닌 경우
            webbrowser.open(url)

        # 결과 대기
        start_time = time.time()
        while time.time() - start_time < timeout:
            results = self.bridge.get_results(keyword)
            if results is not None:
                return results
            time.sleep(0.5)

        # 타임아웃
        return None
