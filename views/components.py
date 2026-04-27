"""Streamlit UI 컴포넌트"""
import streamlit as st
from typing import Optional


def render_search_history(history_manager, current_keyword: str = "") -> Optional[str]:
    """
    검색 히스토리 렌더링

    Args:
        history_manager: SearchHistory 인스턴스
        current_keyword: 현재 검색어

    Returns:
        클릭된 검색어 또는 None
    """
    st.markdown("### 📜 검색 기록")

    history = history_manager.get_all()

    if not history:
        st.caption("검색 기록이 없습니다")
        return None

    # 전체 삭제 버튼
    if st.button("🗑️ 전체 삭제", key="clear_all_history"):
        history_manager.clear()
        st.rerun()

    st.divider()

    # 히스토리 목록
    selected_keyword = None
    for i, keyword in enumerate(history):
        col1, col2 = st.columns([4, 1])

        with col1:
            # 현재 검색어면 하이라이트
            if keyword == current_keyword:
                st.markdown(f"**🔍 {keyword}**")
            else:
                if st.button(keyword, key=f"history_{i}", use_container_width=True):
                    selected_keyword = keyword

        with col2:
            if st.button("×", key=f"delete_{i}"):
                history_manager.remove(keyword)
                st.rerun()

    return selected_keyword


def render_sidebar(limit: int = 20, sort: str = "sim") -> tuple[int, str]:
    """
    사이드바 렌더링

    Args:
        limit: 기본 결과 개수
        sort: 네이버 정렬 옵션

    Returns:
        (limit, sort) 튜플
    """
    with st.sidebar:
        st.header("⚙️ 설정")
        limit = st.slider("결과 개수 (각 사이트별)", 5, 50, limit, 5)

        st.divider()
        st.caption("🔢 네이버 정렬")
        sort = st.selectbox(
            "정렬 기준",
            options=["sim", "date", "asc", "dsc"],
            format_func=lambda x: {
                "sim": "정확도순 (추천)",
                "date": "날짜순",
                "asc": "낮은가격순",
                "dsc": "높은가격순"
            }[x],
            index=0,
            label_visibility="collapsed"
        )

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

    return limit, sort




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
