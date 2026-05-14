// 状态接口 — Cloudflare Pages Function（无状态版本）
const SUBSCRIPTION_END = '2026-06-14';
const DAILY_LIMIT = 100;

export async function onRequest(context) {
  const days = Math.max(0, Math.ceil(
    (new Date(SUBSCRIPTION_END) - new Date()) / (1000 * 60 * 60 * 24)
  ));

  return new Response(JSON.stringify({
    calls_today: '?',
    calls_limit: DAILY_LIMIT,
    successes: '?',
    errors: 0,
    coze_status: 'normal',
    last_error: null,
    subscription_end: SUBSCRIPTION_END,
    model: '扣子(Coze) · 豆包通用模型',
    note: '云函数无状态，调用计数仅本地服务器可用',
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
