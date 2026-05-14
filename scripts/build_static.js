const fs = require('fs');
const path = require('path');

function loadAndEscape(filename) {
  const html = fs.readFileSync(path.join(__dirname, '..', filename), 'utf-8');
  return html
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$/g, '\\$');
}

const INDEX_HTML = loadAndEscape('index.html');
const WORKFLOW_HTML = loadAndEscape('workflow.html');

const worker = `const INDEX = \`${INDEX_HTML}\`;
const WORKFLOW = \`${WORKFLOW_HTML}\`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    if (pathname === '/workflow' || pathname === '/workflow.html') {
      return new Response(WORKFLOW, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'public, max-age=0, must-revalidate',
        },
      });
    }

    if (pathname === '/' || pathname === '/index.html' || pathname === '') {
      return new Response(INDEX, {
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
const kb = (worker.length / 1024).toFixed(1);
console.log(`serve_static.js built (${kb} KB)`);
