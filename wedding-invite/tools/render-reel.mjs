// Deterministically render reel.html to a 1080x1920 H.264 reel.
// Usage: NODE_PATH=$(npm root -g) node tools/render-reel.mjs <out.mp4> [--fps 30]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PAGE = pathToFileURL(path.join(ROOT, 'reel.html')).href + '?capture';
const previewMode = process.argv[2] === '--preview';
const out = path.resolve(previewMode ? process.argv[3] : (process.argv[2] || path.join(ROOT, 'veeral-konika-save-the-date.mp4')));
const fpsArg = process.argv.indexOf('--fps');
const fps = fpsArg >= 0 ? Number(process.argv[fpsArg + 1]) : 30;
const run = (cmd, args) => new Promise((resolve, reject) => {
  const p = spawn(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] });
  p.on('exit', code => code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`)));
});

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('page error:', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
await page.goto(PAGE, { waitUntil: 'networkidle' });
await page.evaluate(async () => {
  await Promise.all(['500 48px "Cormorant Garamond"', '500 80px "Great Vibes"', '500 30px Cinzel'].map(f => document.fonts.load(f, 'Veeral Konika November 2026')));
  await document.fonts.ready;
  await Promise.all([...document.images].map(img => img.complete ? null : new Promise(r => { img.onload = img.onerror = r; })));
});
const duration = await page.evaluate(() => window.__DURATION);
if (previewMode) {
  const at = Number(process.argv[4] || 0);
  await page.evaluate(t => window.__seek(t), at);
  await page.screenshot({ path: out, type: 'png' });
  await browser.close();
  console.log(`preview at ${at}s: ${out}`);
  process.exit(0);
}
const frames = Math.ceil(duration * fps);
fs.mkdirSync(path.dirname(out), { recursive: true });
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'veeral-konika-reel-'));
const silent = path.join(tmp, 'silent.mp4');
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
const ffDone = new Promise((resolve, reject) => ff.on('exit', code => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`))));
for (let f = 0; f < frames; f++) {
  await page.evaluate(t => window.__seek(t), f / fps);
  const frame = await page.screenshot({ type: 'jpeg', quality: 94 });
  if (!ff.stdin.write(frame)) await new Promise(resolve => ff.stdin.once('drain', resolve));
  if (f % 120 === 0) console.log(`rendered ${f}/${frames} frames`);
}
ff.stdin.end();
await ffDone;
await browser.close();
const music = path.join(ROOT, 'assets', 'music.m4a');
await run('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', music, '-filter_complex', '[1:a]atrim=0:16,afade=t=out:st=14.7:d=1.3,volume=0.68[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]);
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`wrote ${out}`);
