"""张潇予个人页 + Coze 代理 — 一体化服务器"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import traceback
import sys
import os

BOT_ID = '7639602226704760878'
TOKEN = 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X'
COZE_API = 'https://api.coze.cn/open_api/v2/chat'

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(HERE, 'index.html')


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_response(404)
            self.end_headers()
            return
        try:
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                html = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'personal-page.html not found')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        raw_body = self.rfile.read(length)
        try:
            body = json.loads(raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = json.loads(raw_body.decode('gbk'))
        print(f'[请求] {body.get("query", "")[:30]}', flush=True)

        payload = json.dumps({
            'bot_id': BOT_ID,
            'user': body.get('user', 'web-visitor'),
            'query': body.get('query', ''),
            'stream': False,
            'conversation_id': body.get('conversation_id', ''),
        }).encode()

        req = urllib.request.Request(
            COZE_API,
            data=payload,
            headers={
                'Authorization': f'Bearer {TOKEN}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                data = json.loads(raw)
            print(f'[成功] 返回 {len(raw)} 字节', flush=True)
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors='replace')
            print(f'[HTTP {e.code}] {err_body[:200]}', flush=True)
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'HTTP {e.code}: {err_body[:100]}'}).encode())
        except urllib.error.URLError as e:
            print(f'[网络错误] {e.reason}', flush=True)
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'网络错误: {e.reason}'}).encode())
        except Exception as e:
            print(f'[异常] {type(e).__name__}: {e}', flush=True)
            traceback.print_exc(file=sys.stdout)
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5099
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'张潇予个人站已启动 → http://localhost:{PORT}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
