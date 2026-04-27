"""Firefox 확장 프로그램을 통한 쿠팡 검색"""
import time
from typing import Optional
from .extension_bridge import ExtensionBridge


class CoupangExtensionSearcher:
    """Firefox 확장 프로그램을 통한 쿠팡 검색 (백그라운드)"""

    def __init__(self, bridge: ExtensionBridge):
        self.bridge = bridge

    def search(self, keyword: str, limit: int = 20, timeout: int = 30) -> Optional[list]:
        """
        Firefox 확장 프로그램으로 쿠팡 검색 (백그라운드)

        Args:
            keyword: 검색어
            limit: 결과 개수
            timeout: 대기 시간 (초)

        Returns:
            검색 결과 리스트 또는 None
        """
        # 기존 결과 초기화
        self.bridge.clear_results(keyword)

        # 검색 요청을 큐에 추가 (Firefox 확장이 polling으로 확인)
        self.bridge.add_search_request(keyword, limit)

        # 결과 대기
        start_time = time.time()
        while time.time() - start_time < timeout:
            results = self.bridge.get_results(keyword)
            if results is not None:
                return results
            time.sleep(0.5)

        # 타임아웃
        return None
