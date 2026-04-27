"""Streamlit UI 컴포넌트"""
import streamlit as st


def render_sidebar(limit: int = 20) -> int:
    """
    사이드바 렌더링

    Args:
        limit: 기본 결과 개수

    Returns:
        사용자가 선택한 결과 개수
    """
    with st.sidebar:
        st.header("⚙️ 설정")
        limit = st.slider("결과 개수 (각 사이트별)", 5, 50, limit, 5)

        st.divider()
        st.caption("🔑 네이버 API 상태")
        import os
        if (os.getenv("NAVER_KEY") or os.getenv("NAVER_CLIENT_ID")) and os.getenv("NAVER_CLIENT_SECRET"):
            st.success("설정 완료")
        else:
            st.error(".env 또는 환경변수에 NAVER_KEY/SECRET 필요")

        st.divider()
        st.caption("💡 캐싱: 동일 검색어 10분")
        if st.button("🗑️ 캐시 초기화"):
            st.cache_data.clear()
            st.success("캐시 초기화 완료")

    return limit


def render_search_input() -> str | None:
    """
    검색 입력창 렌더링

    Returns:
        검색어 또는 None
    """
    keyword = st.text_input(
        "검색어",
        placeholder="예: 갤럭시버즈3 프로",
        help="Enter 누르면 검색됩니다",
    )
    return keyword if keyword else None


def render_items(items: list[dict], empty_msg: str = "결과 없음"):
    """
    상품 목록 렌더링

    Args:
        items: 상품 리스트
        empty_msg: 결과 없을 때 메시지
    """
    if not items:
        st.warning(empty_msg)
        return

    # 가격순 정렬
    items = sorted(items, key=lambda x: x["price"])

    for it in items:
        cols = st.columns([1, 4])
        with cols[0]:
            if it.get("image"):
                st.image(it["image"], width=80)
        with cols[1]:
            st.markdown(
                f"**{it['price']:,}원** · `{it['mall']}`  \n"
                f"[{it['name'][:60]}{'...' if len(it['name']) > 60 else ''}]({it['link']})"
            )
        st.divider()


def render_error(message: str):
    """에러 메시지 렌더링"""
    st.error(message)


def render_info(message: str):
    """정보 메시지 렌더링"""
    st.info(message)
