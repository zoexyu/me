// Coze API 代理 — Cloudflare Pages Function
const COZE_API = 'https://api.coze.cn/open_api/v2/chat';
const BOT_ID = '7639602226704760878';
const TOKEN = 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X';

export async function onRequest(context) {
  const { request } = context;

  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const { user = 'web-visitor', query = '', conversation_id = '' } = await request.json();

    const cozeResp = await fetch(COZE_API, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        bot_id: BOT_ID,
        user,
        query,
        stream: false,
        conversation_id,
      }),
    });

    const data = await cozeResp.json();

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }
}
