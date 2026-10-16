// Background removal for every *.jpg in a folder -> <name>_cut.png (needs @imgly/background-removal-node).
import { removeBackground } from '@imgly/background-removal-node';
import fs from 'fs';
import path from 'path';

const dir = path.resolve(process.argv[2] || '.');
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.jpg'))) {
  const blob = await removeBackground('file://' + path.join(dir, f), { model: 'medium', output: { format: 'image/png', quality: 1 } });
  fs.writeFileSync(path.join(dir, f.replace(/\.jpg$/, '_cut.png')), Buffer.from(await blob.arrayBuffer()));
  console.log('cut', f);
}
