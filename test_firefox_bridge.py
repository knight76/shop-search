#!/usr/bin/env python3
"""Firefox 확장 프로그램 연동 테스트"""
import time
import requests
import json


def test_bridge_server():
    """브릿지 서버 연결 테스트"""
    print("=" * 60)
    print("🧪 Firefox 확장 프로그램 브릿지 테스트")
    print("=" * 60)

    # 1. 서버 상태 확인
    print("\n1️⃣ 브릿지 서버 상태 확인...")
    try:
        response = requests.get("http://localhost:8765/", timeout=2)
        print(f"   ✅ 서버 응답: {response.json()}")
    except Exception as e:
        print(f"   ❌ 서버 연결 실패: {e}")
        print("   💡 Streamlit 앱이 실행 중인지 확인하세요")
        return False

    # 2. 큐 상태 확인
    print("\n2️⃣ 큐 상태 확인...")
    try:
        response = requests.get("http://localhost:8765/queue", timeout=2)
        data = response.json()
        print(f"   큐 상태: {data}")
    except Exception as e:
        print(f"   ❌ 큐 확인 실패: {e}")
        return False

    # 3. 테스트 검색 요청 추가
    print("\n3️⃣ 테스트 검색 요청 추가...")
    test_keyword = "테스트상품"

    # 직접 POST로 검색 요청 추가
    try:
        # 먼저 기존 검색 모듈 import
        from models.extension_bridge import ExtensionBridge

        bridge = ExtensionBridge(port=8765)
        bridge.add_search_request(test_keyword, limit=5)
        print(f"   ✅ 검색 요청 추가: '{test_keyword}'")
    except Exception as e:
        print(f"   ❌ 요청 추가 실패: {e}")
        return False

    # 4. 큐에 요청이 들어갔는지 확인
    print("\n4️⃣ 큐에 요청 확인...")
    time.sleep(0.5)
    try:
        response = requests.get("http://localhost:8765/queue", timeout=2)
        data = response.json()

        if data.get("type") == "SEARCH_REQUEST":
            print(f"   ✅ 큐에 요청 있음: {data.get('keyword')}")
        else:
            print(f"   ⚠️  큐가 비어있음 (Firefox가 이미 가져갔을 수 있음)")
    except Exception as e:
        print(f"   ❌ 큐 확인 실패: {e}")

    # 5. Firefox 확장이 가져가는지 10초 대기
    print("\n5️⃣ Firefox 확장이 요청을 polling하는지 확인 (10초 대기)...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8765/queue", timeout=2)
            data = response.json()

            if data.get("status") == "empty":
                print(f"   ✅ Firefox가 요청을 가져갔습니다! ({i+1}초 소요)")
                break
            else:
                print(f"   ⏳ {i+1}초... 아직 큐에 있음")
        except Exception as e:
            print(f"   ❌ 에러: {e}")
            break
    else:
        print("   ❌ 10초 내에 Firefox가 요청을 가져가지 않았습니다")
        print("   💡 확인사항:")
        print("      - Firefox 확장이 실행 중인가? (web-ext)")
        print("      - background.js의 polling이 동작하는가?")
        return False

    # 6. 결과 대기
    print("\n6️⃣ 검색 결과 대기 (20초)...")
    for i in range(20):
        time.sleep(1)
        results = bridge.get_results(test_keyword)

        if results is not None:
            print(f"   ✅ 결과 수신! ({i+1}초 소요)")
            print(f"   상품 수: {len(results)}개")
            if results:
                print(f"   첫 번째 상품: {results[0].get('name', 'N/A')[:50]}...")
            return True
        else:
            print(f"   ⏳ {i+1}초... 대기 중")

    print("   ❌ 20초 내에 결과를 받지 못했습니다")
    print("   💡 확인사항:")
    print("      - content.js가 제대로 스크랩하는가?")
    print("      - background.js가 결과를 브릿지로 전송하는가?")
    print("      - Firefox 콘솔(F12)에서 [Background], [Coupang Ext] 로그 확인")

    return False


if __name__ == "__main__":
    success = test_bridge_server()

    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 성공! Python ↔ Firefox 연동이 정상 작동합니다")
    else:
        print("❌ 테스트 실패! 위의 확인사항을 점검하세요")
    print("=" * 60)
