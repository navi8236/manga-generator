// Render tools/page25.html (typeset feature summary) to a 1024x1536 page PNG with a provenance record.
// Usage (repository root): node works/welbuk-24/tools/render-page25.cjs
const { chromium } = require('playwright');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
(async () => {
  const W = 'works/welbuk-24';
  const src = path.resolve(W, 'tools/page25.html');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1024, height: 1536 }, deviceScaleFactor: 1 });
  await p.goto('file://' + src);
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.panel')].some((pn) => pn.scrollHeight > pn.clientHeight + 1) || document.querySelector('.pb .grid').getBoundingClientRect().bottom > document.querySelector('footer').getBoundingClientRect().top - 6);
  const buf = await p.screenshot();
  await b.close();
  if (over) throw new Error('content overflows a panel or the footer; shorten it');
  const digest = crypto.createHash('sha256').update(buf).digest('hex');
  const dest = `${W}/assets/generated/page-25-${digest.slice(0, 16)}.png`;
  fs.writeFileSync(dest, buf);
  fs.writeFileSync(dest.replace(/\.png$/, '.json'), JSON.stringify({
    operation: 'typeset feature summary rendered from HTML with Chromium (no image model)',
    source: path.relative('.', src),
    sourceSha256: crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex'),
    sha256: digest,
  }, null, 1) + '\n');
  console.log(dest);
})();
