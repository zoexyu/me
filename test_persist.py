import http.client, json, subprocess, time

def check():
    conn = http.client.HTTPConnection('127.0.0.1', 5099, timeout=10)
    conn.request('GET', '/status')
    data = json.loads(conn.read())
    conn.close()
    return data['calls_today']

def chat():
    body = json.dumps({'user': 'test', 'query': 'hi', 'conversation_id': ''})
    conn = http.client.HTTPConnection('127.0.0.1', 5099, timeout=20)
    conn.request('POST', '/api/chat', body, {'Content-Type': 'application/json'})
    conn.getresponse().read()
    conn.close()

# 先查
print(f'Before chat: {check()} calls')
# 发两条
chat()
chat()
print(f'After 2 chats: {check()} calls')
print('Restarting...')
subprocess.run('MSYS_NO_PATHCONV=1 taskkill /F /PID {}'.format(
    subprocess.run('netstat -ano | grep ":5099" | grep LISTENING', shell=True, capture_output=True, text=True)
    .stdout.strip().split()[-1]), shell=True, capture_output=True)
time.sleep(1)
subprocess.Popen(['python', 'e:/自己.skill/server.py', '5099'])
time.sleep(2)
print(f'After restart: {check()} calls')
