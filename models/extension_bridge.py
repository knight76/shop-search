"""Firefox 확장 프로그램과의 통신 브릿지"""
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ExtensionBridgeHandler(BaseHTTPRequestHandler):
    """확장 프로그램 요청 처리"""

    callback: Optional[Callable] = None
    search_results = {}

    def do_POST(self):
        """POST 요청 처리"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode('utf-8'))

            if data.get('type') == 'SEARCH_RESULT':
                # 검색 결과 저장
                keyword = data.get('keyword')
                items = data.get('items', [])
                ExtensionBridgeHandler.search_results[keyword] = items

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())

                if ExtensionBridgeHandler.callback:
                    ExtensionBridgeHandler.callback(keyword, items)

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        """GET 요청 처리 (상태 확인)"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'running'}).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """로그 비활성화"""
        pass


class ExtensionBridge:
    """Firefox 확장 프로그램 통신 브릿지"""

    def __init__(self, port: int = 8765):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self, callback: Optional[Callable] = None):
        """서버 시작"""
        if self.server:
            return

        ExtensionBridgeHandler.callback = callback

        try:
            self.server = HTTPServer(('localhost', self.port), ExtensionBridgeHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Extension bridge started on port {self.port}")
        except OSError as e:
            if "Address already in use" in str(e):
                logger.warning(f"Port {self.port} already in use")
            else:
                raise

    def stop(self):
        """서버 중지"""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.thread = None

    def get_results(self, keyword: str) -> Optional[list]:
        """검색 결과 조회"""
        return ExtensionBridgeHandler.search_results.get(keyword)

    def clear_results(self, keyword: str = None):
        """결과 초기화"""
        if keyword:
            ExtensionBridgeHandler.search_results.pop(keyword, None)
        else:
            ExtensionBridgeHandler.search_results.clear()
