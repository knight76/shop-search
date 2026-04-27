"""검색 히스토리 관리"""
import json
from pathlib import Path
from typing import List


class SearchHistory:
    """검색 히스토리 관리 클래스"""

    def __init__(self, max_items: int = 15):
        """
        Args:
            max_items: 최대 저장 개수
        """
        self.max_items = max_items
        self.history_file = Path.home() / ".shop_search_history.json"
        self._history: List[str] = []
        self._load()

    def _load(self):
        """파일에서 히스토리 로드"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
            except Exception:
                self._history = []
        else:
            self._history = []

    def _save(self):
        """파일에 히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, keyword: str):
        """
        검색어 추가 (무조건 저장)

        Args:
            keyword: 검색어
        """
        if not keyword or not keyword.strip():
            return

        keyword = keyword.strip()

        # 중복 제거
        if keyword in self._history:
            self._history.remove(keyword)

        # 맨 앞에 추가
        self._history.insert(0, keyword)

        # 최대 개수 제한
        self._history = self._history[:self.max_items]

        # 즉시 저장
        self._save()

    def get_all(self) -> List[str]:
        """전체 히스토리 조회"""
        return self._history.copy()

    def remove(self, keyword: str):
        """
        특정 검색어 삭제

        Args:
            keyword: 삭제할 검색어
        """
        if keyword in self._history:
            self._history.remove(keyword)
            self._save()

    def clear(self):
        """전체 히스토리 삭제"""
        self._history = []
        self._save()
