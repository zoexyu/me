// 张潇予个人站 API Worker
// 路径: zoexyu.top/api/* 和 /messages → 这个 Worker
const COZE_API = 'https://api.coze.cn/open_api/v2/chat';
const BOT_ID = '7639602226704760878';
const TOKEN = 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X';
const SUBSCRIPTION_END = '2026-06-14';
const DAILY_LIMIT = 100;

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    // 聊天 API
    if (path === '/api/chat' && request.method === 'POST') {
      try {
        const body = await request.json();
        const { user = 'web-visitor', query = '', conversation_id = '' } = body;
        const cozeResp = await fetch(COZE_API, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ bot_id: BOT_ID, user, query, stream: false, conversation_id }),
        });
        const data = await cozeResp.json();
        return new Response(JSON.stringify(data), {
          status: 200,
          headers: { ...cors, 'Content-Type': 'application/json' },
        });
      } catch (e) {
        return new Response(JSON.stringify({ error: e.message }), {
          status: 500,
          headers: { ...cors, 'Content-Type': 'application/json' },
        });
      }
    }

    // 状态 API
    if (path === '/api/status') {
      const days = Math.max(0, Math.ceil((new Date(SUBSCRIPTION_END) - new Date()) / 86400000));
      return new Response(JSON.stringify({
        calls_today: '?',
        calls_limit: DAILY_LIMIT,
        successes: '?',
        errors: 0,
        coze_status: 'normal',
        last_error: null,
        subscription_end: SUBSCRIPTION_END,
        model: '扣子(Coze) · 豆包通用模型',
        note: 'Workers 无状态，调用计数仅本地可用',
      }), {
        status: 200,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    // 留言板（无状态版本，仅返回示例）
    if (path === '/messages') {
      if (request.method === 'POST') {
        return new Response(JSON.stringify({ ok: false, error: '留言功能云版本开发中' }), {
          status: 501,
          headers: { ...cors, 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify([]), {
        status: 200,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not Found', { status: 404, headers: cors });
  },
};
