// news-image-20261122: one-page newspaper front page for Sunday 22 November 2026.
// The picture is entry.jpg next to this file. This program checks that it is
// a complete 1024x1024 JPEG under 1 MiB, copies it to the output directory
// as entry.png, then re-reads the copy and checks it byte for byte, so two
// runs always produce identical bytes.
//
// Run it yourself: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import * as fs from 'node:fs';
import * as crypto from 'node:crypto';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// The folder this file lives in.
const DIR = path.dirname(fileURLToPath(import.meta.url));
const SRC = 'entry.jpg';
const LIMIT = 1048576; // 1 MiB
const SIDE = 1024;

type Size = { width: number; height: number };

// Dimensions from the first SOF0/SOF2 segment; undefined when the buffer
// is not a JPEG or holds no size segment before the end-of-image marker.
function jpegSize(buf: Buffer): Size | undefined {
  if (buf.length < 4 || buf[0] !== 0xff || buf[1] !== 0xd8) return undefined;
  let pos = 2;
  let found: Size | undefined;
  while (pos + 4 <= buf.length && found === undefined) {
    if (buf[pos] !== 0xff) break;
    const code = buf[pos + 1];
    if (code === 0xd9) break; // EOI: end of image, no size found
    if (code === 0x01 || (code >= 0xd0 && code <= 0xd7)) {
      pos += 2;
      continue;
    }
    const len = buf.readUInt16BE(pos + 2);
    if (len < 2 || pos + 2 + len > buf.length) break;
    if (code === 0xc0 || code === 0xc2) {
      found = { height: buf.readUInt16BE(pos + 5), width: buf.readUInt16BE(pos + 7) };
    } else {
      pos += 2 + len;
    }
  }
  return found;
}

function sha256(buf: Buffer): string {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function fail(msg: string, code: number): never {
  process.stderr.write(`news-image-20261122: ${msg}\n`);
  process.exit(code);
}

const srcPath = path.join(DIR, SRC);
if (!fs.existsSync(srcPath)) {
  fail(`no ${SRC} next to main.ts; run compose.py first`, 2);
}
const data = fs.readFileSync(srcPath);
if (data.length > LIMIT) {
  fail(`${SRC} is ${data.length} bytes, over the ${LIMIT} byte limit`, 1);
}
const size = jpegSize(data);
if (size === undefined) {
  fail(`${SRC} has no JPEG size marker`, 1);
}
if (size.width !== SIDE || size.height !== SIDE) {
  fail(`${SRC} is ${size.width}x${size.height}, must be ${SIDE}x${SIDE}`, 1);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, 'entry.png');
fs.writeFileSync(outPath, data);
const copy = fs.readFileSync(outPath);
if (copy.length !== data.length || sha256(copy) !== sha256(data)) {
  fail(`copy at ${outPath} differs from ${SRC}`, 1);
}
// Read the size markers back out of the copy itself: a truncated or
// swapped target is caught here even if its byte count happens to match.
const copySize = jpegSize(copy);
if (copySize === undefined || copySize.width !== SIDE || copySize.height !== SIDE) {
  fail(`copy at ${outPath} does not read as a ${SIDE}x${SIDE} JPEG`, 1);
}
process.stdout.write(`news-image-20261122: wrote ${outPath} (${copy.length} bytes, JPEG 1024x1024, sha256 ${sha256(copy).slice(0, 16)}...)\n`);
