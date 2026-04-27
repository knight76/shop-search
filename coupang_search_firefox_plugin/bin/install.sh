#!/bin/bash
# Firefox 확장 프로그램 설치 스크립트

set -e

echo "🔧 Firefox 확장 프로그램 설치"
echo "================================"

# web-ext 설치 확인
if ! command -v web-ext &> /dev/null; then
    echo "📦 web-ext를 설치합니다..."
    npm install -g web-ext
    echo "✅ web-ext 설치 완료"
else
    echo "✅ web-ext 이미 설치됨 ($(web-ext --version))"
fi

# Firefox 경로 확인
FIREFOX_PATH="/Applications/Firefox.app/Contents/MacOS/firefox"
if [ ! -f "$FIREFOX_PATH" ]; then
    echo "❌ Firefox를 찾을 수 없습니다: $FIREFOX_PATH"
    echo "Firefox를 먼저 설치하세요: https://www.mozilla.org/firefox/"
    exit 1
else
    echo "✅ Firefox 발견: $FIREFOX_PATH"
fi

echo ""
echo "설치 완료! 다음 명령어로 시작하세요:"
echo "  ./bin/start.sh"
