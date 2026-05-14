// Coze API 代理 — Vercel Serverless Function
const COZE_API = 'https://api.coze.cn/open_api/v2/chat';
const BOT_ID = '7639602226704760878';
const TOKEN = process.env.COZE_TOKEN || 'pat_zxYCgqUkQVuJgp7JoEVGGMsihr0IMViGEnAqxvsiMXrZoyTho9jdcvDwjQSNx64X';

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { user = 'web-visitor', query = '', conversation_id = '' } = req.body;

  try {
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
    return res.status(200).json(data);
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
};
