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
    search_queue = []  # 검색 요청 큐

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
        """GET 요청 처리 (검색 요청 큐 확인)"""
        # 쿼리 파라미터 제거 (캐시 방지용 ?t=timestamp 등)
        path = self.path.split('?')[0]

        if path == '/queue':
            # 큐에서 요청 가져오기
            if ExtensionBridgeHandler.search_queue:
                request = ExtensionBridgeHandler.search_queue.pop(0)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(request).encode())
            else:
                # 큐가 비어있음
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'empty'}).encode())
        else:
            # 상태 확인
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
        import sys
        sys.stderr.write(f"[DEBUG] ExtensionBridge.start() called, port={self.port}\n")
        sys.stderr.flush()
        if self.server:
            sys.stderr.write(f"[DEBUG] Server already running\n")
            sys.stderr.flush()
            return

        ExtensionBridgeHandler.callback = callback

        try:
            sys.stderr.write(f"[DEBUG] Creating HTTPServer on port {self.port}...\n")
            sys.stderr.flush()
            self.server = HTTPServer(('localhost', self.port), ExtensionBridgeHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            sys.stderr.write(f"[DEBUG] ✅ Extension bridge started on port {self.port}\n")
            sys.stderr.flush()
            logger.info(f"Extension bridge started on port {self.port}")
        except OSError as e:
            sys.stderr.write(f"[DEBUG] ❌ OSError: {e}\n")
            sys.stderr.flush()
            if "Address already in use" in str(e):
                logger.warning(f"Port {self.port} already in use")
            else:
                raise
        except Exception as e:
            sys.stderr.write(f"[DEBUG] ❌ Unexpected error: {e}\n")
            sys.stderr.flush()
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

    def add_search_request(self, keyword: str, limit: int = 20):
        """검색 요청 추가"""
        ExtensionBridgeHandler.search_queue.append({
            'type': 'SEARCH_REQUEST',
            'keyword': keyword,
            'limit': limit
        })
        logger.info(f"Added search request to queue: {keyword}")
