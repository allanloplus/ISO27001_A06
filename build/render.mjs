// 逐格渲染 slides/index.html（render 模式）並與 narration.mp3 合成 MP4
// 用法：node build/render.mjs [輸出檔] [fps] [起始秒] [結束秒]
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import path from 'node:path';
const out = process.argv[2] || 'output/ISO27001_A8.9_組態管理.mp4';
const fps = +(process.argv[3] || 24);
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto('file://' + path.resolve('slides/index.html') + '?render=1');
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1000);
const dur = await page.evaluate(() => window.TL_DURATION);
const t0 = +(process.argv[4] || 0), t1 = Math.min(dur, +(process.argv[5] || dur));
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-ss', String(t0), '-t', String(t1 - t0), '-i', 'slides/narration.mp3',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-tune', 'animation',
  '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const n = Math.ceil((t1 - t0) * fps);
for (let i = 0; i < n; i++) {
  await page.evaluate(t => window.renderAt(t), t0 + i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 240 === 0) console.log(`frame ${i}/${n}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log('done', out);
