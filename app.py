"""
쿠팡 vs 네이버 가격비교 - MVC 패턴
Controller: 메인 로직만 처리
"""
import streamlit as st
from dotenv import load_dotenv

# Model
from models.coupang import CoupangSearcher
from models.coupang_extension import CoupangExtensionSearcher
from models.extension_bridge import ExtensionBridge
from models.naver import NaverSearcher
from models.history import SearchHistory

# View
from views.components import (
    render_sidebar,
    render_search_history,
    render_items,
    render_error,
    render_info,
)

# .env 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="가격비교", page_icon="🛒", layout="wide")
st.title("🛒 쿠팡 vs 네이버 가격비교")


# Extension Bridge 초기화
@st.cache_resource
def get_extension_bridge():
    """Extension Bridge 싱글톤"""
    bridge = ExtensionBridge(port=8765)
    bridge.start()
    return bridge


def search_coupang_via_extension(keyword: str, limit: int):
    """쿠팡 검색 (Firefox 확장 프로그램 사용)"""
    bridge = get_extension_bridge()
    searcher = CoupangExtensionSearcher(bridge)
    return searcher.search(keyword, limit, timeout=20)


@st.cache_data(ttl=600, show_spinner=False)
def search_naver_cached(keyword: str, limit: int):
    """네이버 검색 (캐시)"""
    searcher = NaverSearcher()
    return searcher.search(keyword, limit)


# 메인 로직
def main():
    """메인 컨트롤러"""
    # 검색 히스토리 초기화
    if 'history_manager' not in st.session_state:
        st.session_state.history_manager = SearchHistory(max_items=15)

    history_manager = st.session_state.history_manager

    # 세션 상태에서 현재 검색어 가져오기
    if 'current_keyword' not in st.session_state:
        st.session_state.current_keyword = ""

    # 사이드바
    with st.sidebar:
        # 검색 히스토리
        selected_from_history = render_search_history(
            history_manager,
            st.session_state.current_keyword
        )

        st.divider()

        # 설정
        limit = render_sidebar(limit=20)

    # 히스토리에서 선택한 검색어가 있으면 사용
    if selected_from_history:
        st.session_state.current_keyword = selected_from_history
        # 검색어 입력창도 업데이트
        if 'search_input' not in st.session_state:
            st.session_state.search_input = selected_from_history

    # 검색어 입력
    keyword = st.text_input(
        "검색어",
        value=st.session_state.get('search_input', ''),
        placeholder="예: 갤럭시버즈3 프로",
        help="Enter 누르면 검색됩니다",
        key="search_box"
    )

    # 검색어 업데이트
    if keyword:
        st.session_state.search_input = keyword
        st.session_state.current_keyword = keyword

    if not keyword:
        st.info("👆 검색어를 입력하세요")
        return

    # 히스토리에 무조건 저장
    previous_history = history_manager.get_all()
    history_manager.add(keyword)

    # 히스토리가 변경되었으면 페이지 새로고침
    if keyword not in previous_history:
        st.rerun()

    # 2컬럼 레이아웃
    col_c, col_n = st.columns(2)

    # 쿠팡 검색 (Firefox 확장 프로그램 사용)
    with col_c:
        st.subheader("🅒 쿠팡 (via Firefox 확장)")
        with st.spinner("Firefox 확장 프로그램으로 쿠팡 검색 중... (새 탭이 열립니다)"):
            try:
                coupang_items = search_coupang_via_extension(keyword, limit)

                if coupang_items is None:
                    render_info(
                        "⏳ Firefox 확장 프로그램 대기 중...\n\n"
                        "1. Firefox에서 쿠팡 검색 탭이 열렸는지 확인\n"
                        "2. 확장 프로그램이 실행 중인지 확인 (web-ext)\n"
                        "3. 브릿지 서버: http://localhost:8765"
                    )
                elif not coupang_items:
                    render_error("검색 결과가 없습니다")
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
