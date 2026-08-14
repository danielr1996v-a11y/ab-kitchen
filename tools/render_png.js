#!/usr/bin/env node
/**
 * Rasterise SVG files to PNG with headless Chromium.
 *
 *   node tools/render_png.js <out-dir> <scale> <bg|transparent> <svg...>
 *
 * Each SVG is rendered at its intrinsic size multiplied by <scale>.
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const [outDir, scaleArg, bg, ...svgs] = process.argv.slice(2);
const scale = Number(scaleArg) || 1;

function intrinsicSize(svg) {
  const w = svg.match(/\bwidth="([\d.]+)"/);
  const h = svg.match(/\bheight="([\d.]+)"/);
  if (w && h) return { w: Number(w[1]), h: Number(h[1]) };
  const vb = svg.match(/viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"/);
  if (vb) return { w: Number(vb[1]), h: Number(vb[2]) };
  throw new Error('cannot determine SVG size');
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  for (const file of svgs) {
    const svg = fs.readFileSync(file, 'utf8');
    const { w, h } = intrinsicSize(svg);
    const page = await browser.newPage({
      viewport: { width: Math.round(w), height: Math.round(h) },
      deviceScaleFactor: scale,
    });
    await page.setContent(
      `<style>html,body{margin:0;padding:0;background:${bg === 'transparent' ? 'transparent' : bg}}
       svg{display:block;width:${w}px;height:${h}px}</style>${svg}`
    );
    const out = path.join(outDir, path.basename(file).replace(/\.svg$/, '.png'));
    await page.screenshot({ path: out, omitBackground: bg === 'transparent' });
    await page.close();
    console.log(`${out}  ${Math.round(w * scale)}×${Math.round(h * scale)}`);
  }
  await browser.close();
})();
