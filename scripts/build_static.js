const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf-8');

const escaped = html
  .replace(/\\/g, '\\\\')
  .replace(/`/g, '\\`')
  .replace(/\$/g, '\\$');

const worker = `const HTML = \`${escaped}\`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/' || url.pathname === '/index.html' || url.pathname === '') {
      return new Response(HTML, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'public, max-age=0, must-revalidate',
        },
      });
    }
    return new Response('Not Found', { status: 404 });
  },
};
`;

const outPath = path.join(__dirname, '..', 'serve_static.js');
fs.writeFileSync(outPath, worker);
console.log(`serve_static.js built (${worker.length} bytes)`);
