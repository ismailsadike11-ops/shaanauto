// Export every SVG in logo/svg to PNG, JPEG and vector PDF, then render the
// brand book (brand-book/index.html) to "WAREGRO - Visual Identity.pdf".
// Run:  node waregro/tools/export_assets.js
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const SVG_DIR = path.join(ROOT, 'logo', 'svg');
const PNG_DIR = path.join(ROOT, 'logo', 'png');
const JPG_DIR = path.join(ROOT, 'logo', 'jpeg');
const PDF_DIR = path.join(ROOT, 'logo', 'pdf');

function svgSize(svg) {
  const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  return { w: parseFloat(m[1]), h: parseFloat(m[2]) };
}

async function main() {
  for (const d of [PNG_DIR, JPG_DIR, PDF_DIR]) fs.mkdirSync(d, { recursive: true });
  const browser = await chromium.launch();
  const files = fs.readdirSync(SVG_DIR).filter((f) => f.endsWith('.svg')).sort();

  for (const file of files) {
    const svg = fs.readFileSync(path.join(SVG_DIR, file), 'utf8');
    const { w, h } = svgSize(svg);
    const base = file.replace(/\.svg$/, '');
    // Long edge 3000px for print-quality raster files (rendered via device scale)
    const vw = Math.ceil(w), vh = Math.ceil(h);
    const ctx = await browser.newContext({ viewport: { width: vw, height: vh }, deviceScaleFactor: 3000 / Math.max(w, h) });
    const page = await ctx.newPage();
    const inner = svg.replace(/width="\d+" height="\d+"/, `width="${w}" height="${h}"`);
    await page.setContent(`<html><body style="margin:0;background:transparent">${inner}</body></html>`);
    await page.screenshot({ path: path.join(PNG_DIR, `${base}.png`), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });

    // JPEG cannot be transparent: light variants go on white, white/linen ones on brown
    const jpgBg = file.includes('-white') ? '#952801' : '#FFFFFF';
    await page.setContent(`<html><body style="margin:0;background:${jpgBg}">${inner}</body></html>`);
    await page.screenshot({ path: path.join(JPG_DIR, `${base}.jpg`), type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: w, height: h } });

    // Vector PDF at the SVG's own size (1 SVG unit = 1 CSS px)
    await page.setContent(`<html><head><style>@page{size:${vw}px ${vh}px;margin:0}html,body{margin:0}svg{display:block}</style></head><body>${inner}</body></html>`);
    await page.pdf({ path: path.join(PDF_DIR, `${base}.pdf`), width: `${vw}px`, height: `${vh}px`, printBackground: true, pageRanges: '1' });
    await ctx.close();
  }

  // Favicons / social avatars from the app icon
  const icon = fs.readFileSync(path.join(SVG_DIR, 'waregro-app-icon-orange.svg'), 'utf8');
  const favDir = path.join(ROOT, 'logo', 'favicon');
  fs.mkdirSync(favDir, { recursive: true });
  for (const s of [16, 32, 48, 180, 192, 512]) {
    const page = await browser.newPage({ viewport: { width: s, height: s } });
    await page.setContent(`<html><body style="margin:0">${icon.replace(/width="\d+" height="\d+"/, `width="${s}" height="${s}"`)}</body></html>`);
    await page.screenshot({ path: path.join(favDir, `favicon-${s}.png`), omitBackground: true, clip: { x: 0, y: 0, width: s, height: s } });
    await page.close();
  }

  // Brand book
  const book = path.join(ROOT, 'brand-book', 'index.html');
  if (fs.existsSync(book)) {
    const page = await browser.newPage({ viewport: { width: 1123, height: 794 } });
    await page.goto('file://' + book);
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(ROOT, 'WAREGRO - Visual Identity.pdf'), width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
    await page.close();
  }
  await browser.close();
  console.log(`exported ${files.length} logos`);
}

main().catch((e) => { console.error(e); process.exit(1); });
