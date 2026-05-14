"""张潇予个人页 + Coze 代理 — 一体化服务器"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import traceback
import sys
import os
from datetime import datetime, date

BOT_ID = '7639602226704760878'
TOKEN = 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X'
COZE_API = 'https://api.coze.cn/open_api/v2/chat'
SUBSCRIPTION_END = '2026-06-14'  # 代理订阅到期日
DAILY_LIMIT = 100  # Coze 免费每日调用次数

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(HERE, 'index.html')

# 状态追踪
today = date.today().isoformat()
stats = {
    'date': today,
    'calls': 0,
    'successes': 0,
    'errors': 0,
    'last_error': None,
    'coze_status': 'normal',  # normal | exhausted | error
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            self._json_response(200, {
                'calls_today': stats['calls'],
                'calls_limit': DAILY_LIMIT,
                'successes': stats['successes'],
                'errors': stats['errors'],
                'coze_status': stats['coze_status'],
                'last_error': stats['last_error'],
                'subscription_end': SUBSCRIPTION_END,
                'model': '扣子(Coze) · 豆包通用模型',
            })
            return

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
            self.wfile.write(b'index.html not found')

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

        # 日切重置
        global stats
        td = date.today().isoformat()
        if stats['date'] != td:
            stats = {'date': td, 'calls': 0, 'successes': 0, 'errors': 0,
                     'last_error': None, 'coze_status': 'normal'}

        stats['calls'] += 1

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
            stats['successes'] += 1
            stats['coze_status'] = 'normal'
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors='replace')
            print(f'[HTTP {e.code}] {err_body[:200]}', flush=True)
            stats['errors'] += 1
            stats['last_error'] = f'HTTP {e.code}'
            if e.code == 429:
                stats['coze_status'] = 'exhausted'
            else:
                stats['coze_status'] = 'error'
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'HTTP {e.code}: {err_body[:100]}'}).encode())
        except urllib.error.URLError as e:
            print(f'[网络错误] {e.reason}', flush=True)
            stats['errors'] += 1
            stats['last_error'] = str(e.reason)
            stats['coze_status'] = 'error'
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'网络错误: {e.reason}'}).encode())
        except Exception as e:
            print(f'[异常] {type(e).__name__}: {e}', flush=True)
            traceback.print_exc(file=sys.stdout)
            stats['errors'] += 1
            stats['last_error'] = str(e)[:100]
            stats['coze_status'] = 'error'
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _json_response(self, code, data):
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
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
