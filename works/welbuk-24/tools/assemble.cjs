// Assemble the finished Welbuk comic: front cover, pages 01-25, back cover.
// Usage (repository root): node works/welbuk-24/tools/assemble.cjs
// Renders workflow/review/page-NN.svg (the shared CLI's composed pages) at 2x with Chromium into
// deliverables/pages/, copies the covers, writes one combined PDF (each page at its own size) and a
// mobile reading edition (deliverables/reader/index.html), plus a manifest with SHA-256 hashes.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium } = require('playwright');

const W = 'works/welbuk-24';
const OUT = `${W}/deliverables`;
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
(async () => {
  fs.mkdirSync(`${OUT}/pages`, { recursive: true });
  fs.mkdirSync(`${OUT}/reader`, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1024, height: 1536 }, deviceScaleFactor: 2 });
  const files = [];
  fs.copyFileSync(`${W}/source/cover/front.png`, `${OUT}/pages/00-front-cover.png`);
  files.push(`${OUT}/pages/00-front-cover.png`);
  for (let i = 1; i <= 25; i++) {
    const id = String(i).padStart(2, '0');
    await p.goto('file://' + path.resolve(`${W}/workflow/review/page-${id}.svg`));
    await p.evaluate(() => document.fonts.ready);
    const f = `${OUT}/pages/page-${id}.png`;
    await p.screenshot({ path: f });
    files.push(f);
  }
  fs.copyFileSync(`${W}/source/cover/back.png`, `${OUT}/pages/26-back-cover.png`);
  files.push(`${OUT}/pages/26-back-cover.png`);

  await b.close();
  // Combined PDF: JPEG-compressed pages (quality 90) at each image's own size, written by Pillow.
  const pdf = `${OUT}/welbuk-a-better-way-to-care.pdf`;
  require('child_process').execFileSync('python3', ['-I', '-c',
    "import sys\nfrom PIL import Image\nims=[Image.open(f).convert('RGB') for f in sys.argv[2:]]\nims[0].save(sys.argv[1], save_all=True, append_images=ims[1:], resolution=300, quality=90)",
    pdf, ...files]);

  // Mobile reading edition: one column, pages scale to the screen width, lazy loading.
  const rel = files.map((f) => '../pages/' + path.basename(f));
  fs.writeFileSync(`${OUT}/reader/index.html`, `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Welbuk — A Better Way to Care</title>
<style>:root{color-scheme:light}body{margin:0;background:#f4f1f3;font-family:Inter,system-ui,sans-serif}
header{position:sticky;top:0;background:#FD006A;color:#fff;padding:10px 16px;font-weight:600;font-size:16px;z-index:1}
main{max-width:760px;margin:0 auto;padding:12px 8px 40px}figure{margin:0 0 12px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.12)}
img{display:block;width:100%;height:auto}figcaption{font-size:12px;color:#777;text-align:center;padding:4px}</style></head>
<body><header>Welbuk — A Better Way to Care</header><main>
${rel.map((r, i) => `<figure><img src="${r}" alt="${i === 0 ? 'Front cover' : i === rel.length - 1 ? 'Back cover' : 'Page ' + i}" loading="${i < 2 ? 'eager' : 'lazy'}"><figcaption>${i === 0 ? 'Front cover' : i === rel.length - 1 ? 'Back cover' : 'Page ' + i}</figcaption></figure>`).join('\n')}
</main></body></html>
`);
  const manifest = { title: 'Welbuk — A Better Way to Care', createdAt: new Date().toISOString(), pdf: { file: path.basename(pdf), sha256: sha(pdf) },
    pages: files.map((f) => ({ file: 'pages/' + path.basename(f), sha256: sha(f) })) };
  fs.writeFileSync(`${OUT}/manifest.json`, JSON.stringify(manifest, null, 1) + '\n');
  console.log('pages', files.length, 'pdf', pdf, (fs.statSync(pdf).size / 1e6).toFixed(1) + ' MB');
})();
