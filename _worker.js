// Cloudflare Pages Advanced Mode Worker
// 同时托管静态页面和 API 代理
const COZE_API = 'https://api.coze.cn/open_api/v2/chat';
const BOT_ID = '7639602226704760878';
const TOKEN = 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X';
const SUBSCRIPTION_END = '2026-06-14';
const DAILY_LIMIT = 100;

function cors() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

async function handleChat(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: cors() });
  }
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405, headers: { ...cors(), 'Content-Type': 'application/json' }
    });
  }
  try {
    const { user = 'web-visitor', query = '', conversation_id = '' } = await request.json();
    const cozeResp = await fetch(COZE_API, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot_id: BOT_ID, user, query, stream: false, conversation_id }),
    });
    const data = await cozeResp.json();
    return new Response(JSON.stringify(data), {
      status: 200, headers: { ...cors(), 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500, headers: { ...cors(), 'Content-Type': 'application/json' }
    });
  }
}

function handleStatus() {
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
    note: '云函数无状态，调用计数仅本地可用'
  }), { status: 200, headers: { ...cors(), 'Content-Type': 'application/json' } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/chat') return handleChat(request);
    if (url.pathname === '/api/status') return handleStatus();
    // 所有其他请求走静态资源
    return env.ASSETS.fetch(request);
  }
};
