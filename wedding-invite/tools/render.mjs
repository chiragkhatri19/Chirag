// Renders index.html frame-by-frame with headless Chromium and encodes it with ffmpeg.
//
//   NODE_PATH=$(npm root -g) node tools/render.mjs stills <outDir> <t1> <t2> ...
//   NODE_PATH=$(npm root -g) node tools/render.mjs video <out.mp4> [--fps 30] [--workers 4] [--audio assets/music.m4a]
//
// The page exposes window.__seek(t) and window.__DURATION, so every frame is deterministic.
import { createRequire } from 'module';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath, pathToFileURL } from 'url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PAGE = pathToFileURL(path.join(ROOT, 'index.html')).href + '?capture';

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(PAGE, { waitUntil: 'networkidle' });
  await page.evaluate(async () => {
    const probes = ['86px "Rozha One"', '40px "Tiro Devanagari Hindi"', '34px "Cinzel"', '120px "Great Vibes"', '40px "Cormorant Garamond"', 'italic 40px "Cormorant Garamond"'];
    await Promise.all(probes.map(f => document.fonts.load(f, 'श्री गणेश Veeral Konika 0123')));
    await document.fonts.ready;
    await Promise.all([...document.images].map(img => img.complete ? null : new Promise(r => { img.onload = img.onerror = r; })));
  });
  return page;
}

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'], ...opts });
    p.on('exit', code => code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`)));
  });
}

async function stills(outDir, times) {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await openPage(browser);
  for (const t of times) {
    await page.evaluate(t => window.__seek(t), t);
    await page.screenshot({ path: path.join(outDir, `t${String(t).replace('.', '_')}.png`) });
  }
  await browser.close();
}

async function renderSegment(browser, from, to, fps, file) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(fps), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('exit', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
  for (let f = from; f < to; f++) {
    await page.evaluate(t => window.__seek(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 150 === 0) console.log(`  ${path.basename(file)}: frame ${f - from}/${to - from}`);
  }
  ff.stdin.end();
  await done;
  await page.close();
}

async function video(out, { fps = 30, workers = Math.max(1, os.cpus().length), audio = null }) {
  const browser = await chromium.launch();
  const probe = await openPage(browser);
  const duration = await probe.evaluate(() => window.__DURATION);
  await probe.close();
  const total = Math.ceil(duration * fps);
  console.log(`duration ${duration.toFixed(2)}s, ${total} frames, ${workers} workers`);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'invite-'));
  const per = Math.ceil(total / workers);
  const segs = [];
  const jobs = [];
  for (let w = 0; w < workers; w++) {
    const a = w * per, b = Math.min(total, a + per);
    if (a >= b) break;
    const file = path.join(tmp, `seg${w}.mp4`);
    segs.push(file);
    jobs.push(renderSegment(browser, a, b, fps, file));
  }
  await Promise.all(jobs);
  await browser.close();
  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, segs.map(s => `file '${s}'`).join('\n'));
  const args = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list];
  if (audio) args.push('-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push('-c:v', 'copy', '-movflags', '+faststart', out);
  await run('ffmpeg', args);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('wrote', out);
}

const [mode, target, ...rest] = process.argv.slice(2);
if (mode === 'stills') {
  await stills(target, rest.map(Number));
} else if (mode === 'video') {
  const opt = {};
  for (let i = 0; i < rest.length; i += 2) opt[rest[i].replace(/^--/, '')] = rest[i + 1];
  await video(target, { fps: +(opt.fps || 30), workers: +(opt.workers || os.cpus().length), audio: opt.audio || null });
} else {
  console.log('usage: render.mjs stills <dir> <t...> | video <out.mp4> [--fps 30] [--workers 4] [--audio file]');
  process.exit(1);
}
