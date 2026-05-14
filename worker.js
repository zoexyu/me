// 张潇予个人站 API Worker
// 路径: zoexyu.top/api/* → 这个 Worker
// KV: 调用计数 + 留言存储
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

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { ...cors, 'Content-Type': 'application/json' },
  });
}

// ========== 调用计数 ==========
async function getStats(env) {
  // 使用北京时间(UTC+8)计算日期
  const now = new Date(Date.now() + 8 * 3600000);
  const today = now.toISOString().slice(0, 10);
  const key = `stats:${today}`;
  const raw = await env.ZoeXyu_KV.get(key);
  if (raw) return JSON.parse(raw);
  return { date: today, calls: 0, successes: 0, errors: 0, last_error: null, coze_status: 'normal' };
}

async function saveStats(env, stats) {
  const key = `stats:${stats.date}`;
  await env.ZoeXyu_KV.put(key, JSON.stringify(stats), { expirationTtl: 86400 * 7 });
}

async function incrementStats(env, field) {
  const stats = await getStats(env);
  stats[field] = (stats[field] || 0) + 1;
  await saveStats(env, stats);
  return stats;
}

// ========== 留言存储 ==========
async function getMessages(env) {
  const raw = await env.ZoeXyu_KV.get('messages');
  if (raw) return JSON.parse(raw);
  return [];
}

async function saveMessages(env, msgs) {
  await env.ZoeXyu_KV.put('messages', JSON.stringify(msgs));
}

// ========== 路由处理 ==========
async function handleChat(request, env) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: cors });
  }
  if (request.method !== 'POST') {
    return json({ error: 'Method not allowed' }, 405);
  }

  const stats = await incrementStats(env, 'calls');

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

    if (!cozeResp.ok) {
      stats.errors += 1;
      stats.last_error = `Coze HTTP ${cozeResp.status}`;
      stats.coze_status = cozeResp.status === 429 ? 'exhausted' : 'error';
      await saveStats(env, stats);
      return json({ error: `Coze HTTP ${cozeResp.status}` }, 500);
    }

    stats.successes += 1;
    stats.coze_status = 'normal';
    await saveStats(env, stats);
    return json(data);
  } catch (e) {
    stats.errors += 1;
    stats.last_error = e.message;
    stats.coze_status = 'error';
    await saveStats(env, stats);
    return json({ error: e.message }, 500);
  }
}

async function handleStatus(request, env) {
  const stats = await getStats(env);
  return json({
    calls_today: stats.calls,
    calls_limit: DAILY_LIMIT,
    successes: stats.successes,
    errors: stats.errors,
    coze_status: stats.coze_status,
    last_error: stats.last_error,
    subscription_end: SUBSCRIPTION_END,
    model: '扣子(Coze) · 豆包通用模型',
  });
}

async function handleMessages(request, env) {
  // CORS 预检
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: cors });
  }

  // GET — 返回全部留言
  if (request.method === 'GET') {
    const msgs = await getMessages(env);
    return json(msgs);
  }

  // POST — 提交留言
  if (request.method === 'POST') {
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: '无效的 JSON' }, 400);
    }

    const name = (body.name || '').trim();
    const msgText = (body.message || '').trim();
    const isAnon = body.is_anonymous || false;

    if (!msgText || msgText.length > 500) {
      return json({ error: '留言不能为空且不超过500字' }, 400);
    }

    const msgs = await getMessages(env);
    const newMsg = {
      id: msgs.length + 1,
      name: isAnon ? '匿名' : (name || '匿名'),
      message: msgText,
      time: (() => { const d = new Date(); const pad = n => String(n).padStart(2,'0'); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`; })(),
      is_anonymous: isAnon,
    };
    msgs.push(newMsg);
    await saveMessages(env, msgs);

    return json({ ok: true }, 201);
  }

  return json({ error: 'Method not allowed' }, 405);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === '/api/chat') return handleChat(request, env);
    if (path === '/api/status') return handleStatus(request, env);
    if (path === '/api/messages') return handleMessages(request, env);

    return new Response('Not Found', { status: 404, headers: cors });
  },
};
