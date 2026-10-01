import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import path from 'node:path';
const out = process.argv[2];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto('file://' + path.resolve('slides/index.html') + '?render=1');
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1500);
const scenes = await page.evaluate(() => window.TIMELINE.scenes.map(s => [s.id, s.end]));
for (const [id, end] of scenes) {
  await page.evaluate(t => window.renderAt(t), end - 1.2);
  await page.screenshot({ path: `${out}/${id}.png`, clip: { x: 0, y: 0, width: 1280, height: 720 } });
}
console.log(await page.evaluate(() => [...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)===i)));
await browser.close();
