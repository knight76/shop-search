#!/bin/bash
# Firefox 확장 프로그램 데몬 종료

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PLUGIN_DIR/.web-ext.pid"

echo "🛑 Firefox 확장 프로그램 데몬 종료"
echo "================================"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  실행 중인 데몬이 없습니다"

    # 혹시 모를 좀비 프로세스 정리
    pkill -f "web-ext run" 2>/dev/null && echo "   (좀비 프로세스 정리됨)"

    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "   PID: $PID 종료 중..."
    kill "$PID"

    # 프로세스가 완전히 종료될 때까지 대기
    for i in {1..5}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    # 강제 종료가 필요한 경우
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   강제 종료 중..."
        kill -9 "$PID" 2>/dev/null || true
    fi

    echo "✅ 데몬 종료 완료"
else
    echo "⚠️  PID $PID 프로세스를 찾을 수 없습니다"
fi

# PID 파일 삭제
rm -f "$PID_FILE"

# 관련 프로세스 정리
pkill -f "web-ext run" 2>/dev/null && echo "   (관련 프로세스 정리됨)"

echo ""
echo "시작: ./bin/start.sh"
