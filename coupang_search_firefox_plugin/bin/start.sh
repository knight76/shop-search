#!/bin/bash
# Firefox 확장 프로그램 데몬 시작

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PLUGIN_DIR/.web-ext.pid"
LOG_FILE="$PLUGIN_DIR/.web-ext.log"

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  이미 실행 중입니다 (PID: $PID)"
        echo "   중지하려면: ./bin/stop.sh"
        exit 1
    else
        # PID 파일은 있지만 프로세스는 없음
        rm -f "$PID_FILE"
    fi
fi

echo "🚀 Firefox 확장 프로그램 데몬 시작"
echo "================================"

cd "$PLUGIN_DIR"

# 백그라운드로 web-ext 실행
nohup web-ext run \
    --firefox=/Applications/Firefox.app/Contents/MacOS/firefox \
    --verbose \
    > "$LOG_FILE" 2>&1 &

WEB_EXT_PID=$!
echo "$WEB_EXT_PID" > "$PID_FILE"

sleep 2

# 프로세스가 정상적으로 시작되었는지 확인
if ps -p "$WEB_EXT_PID" > /dev/null 2>&1; then
    echo "✅ 데몬 시작 완료"
    echo "   PID: $WEB_EXT_PID"
    echo "   로그: $LOG_FILE"
    echo ""
    echo "📌 확인:"
    echo "   - Firefox 창이 열렸는지 확인"
    echo "   - 브릿지 서버: http://localhost:8765/queue"
    echo ""
    echo "중지: ./bin/stop.sh"
else
    echo "❌ 데몬 시작 실패"
    echo "   로그 확인: tail -f $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
