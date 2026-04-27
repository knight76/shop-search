"""
쿠팡 vs 네이버 가격비교 - MVC 패턴
Controller: 메인 로직만 처리
"""
import streamlit as st
from dotenv import load_dotenv

# Model
from models.coupang import CoupangSearcher
from models.naver import NaverSearcher

# View
from views.components import (
    render_sidebar,
    render_search_input,
    render_items,
    render_error,
    render_info,
)

# .env 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="가격비교", page_icon="🛒", layout="wide")
st.title("🛒 쿠팡 vs 네이버 가격비교")


# 캐시된 검색 함수
@st.cache_data(ttl=600, show_spinner=False)
def search_coupang_cached(keyword: str, limit: int):
    """쿠팡 검색 (캐시)"""
    searcher = CoupangSearcher()
    return searcher.search(keyword, limit)


@st.cache_data(ttl=600, show_spinner=False)
def search_naver_cached(keyword: str, limit: int):
    """네이버 검색 (캐시)"""
    searcher = NaverSearcher()
    return searcher.search(keyword, limit)


# 메인 로직
def main():
    """메인 컨트롤러"""
    # 사이드바 렌더링
    limit = render_sidebar(limit=20)

    # 검색어 입력
    keyword = render_search_input()

    if not keyword:
        st.info("👆 검색어를 입력하세요")
        return

    # 2컬럼 레이아웃
    col_c, col_n = st.columns(2)

    # 쿠팡 검색
    with col_c:
        st.subheader("🅒 쿠팡")
        with st.spinner("쿠팡 검색 중..."):
            try:
                coupang_items = search_coupang_cached(keyword, limit)

                if not coupang_items:
                    render_error("🚫 쿠팡 봇 감지 시스템에 의해 차단되었습니다")
                    render_info(
                        "**대안:**\n"
                        "- 네이버 쇼핑 검색 결과를 확인하세요\n"
                        "- 직접 쿠팡 웹사이트/앱에서 검색하세요"
                    )
                else:
                    render_items(coupang_items, "쿠팡 결과 없음")

            except Exception as e:
                render_error(f"쿠팡 에러: {e}")

    # 네이버 검색
    with col_n:
        st.subheader("🅝 네이버")
        with st.spinner("네이버 검색 중..."):
            try:
                naver_items = search_naver_cached(keyword, limit)

                if naver_items is None:
                    render_info(
                        "🔑 네이버 API 키가 설정되지 않았습니다.\n\n"
                        "1. https://developers.naver.com/apps/#/register 접속\n"
                        "2. 검색 API 신청\n"
                        "3. .env 파일에 키 입력 후 재시작"
                    )
                else:
                    render_items(naver_items, "네이버 결과 없음")

            except Exception as e:
                render_error(f"네이버 에러: {e}")


if __name__ == "__main__":
    main()
