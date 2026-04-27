#!/bin/bash

echo "🚀 Firefox 확장 프로그램 자동 실행"
echo ""

if ! command -v web-ext &> /dev/null; then
    echo "⚠️  web-ext가 설치되지 않았습니다."
    echo ""
    echo "설치 방법:"
    echo "  npm install -g web-ext"
    echo ""
    echo "또는 수동으로 Firefox에서 about:debugging 사용"
    exit 1
fi

cd /Users/samuel.kim/dev/my/shop-search/coupang_search_firefox_plugin

echo "Firefox에서 확장 프로그램 실행 중..."
web-ext run --firefox=/Applications/Firefox.app/Contents/MacOS/firefox

