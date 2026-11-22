// Entry for the 22 November 2026 news-image competition.
// Sunday's front page is entry.jpg in this folder. This script makes
// sure the picture is a genuine 1024 by 1024 JPEG smaller than one
// mebibyte, writes it out as entry.png in the output folder, and then
// reads the copy back to prove it matches the original exactly. Two
// runs must leave identical bytes behind.
//
// Try it: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const IMAGE = 'entry.jpg';
const MAX = 1048576;
const DIM = 1024;

class JpegCheck {
  private bytes: Buffer;

  constructor(bytes: Buffer) {
    this.bytes = bytes;
  }

  get size(): number {
    return this.bytes.length;
  }

  get isJpeg(): boolean {
    return this.bytes.length >= 2 && this.bytes[0] === 0xff && this.bytes[1] === 0xd8;
  }

  // Walk the marker segments from the start of the file until the first
  // frame header (SOF0 or SOF2) gives up the width and height.
  dimensions(): { width: number; height: number } | null {
    if (!this.isJpeg) return null;
    let at = 2;
    const data = this.bytes;
    while (at + 4 <= data.length) {
      if (data[at] !== 0xff) return null;
      const tag = data[at + 1];
      if (tag === 0xd9) return null;
      if (tag === 0x01 || (tag >= 0xd0 && tag <= 0xd7)) {
        at += 2;
        continue;
      }
      const seg = data.readUInt16BE(at + 2);
      if (seg < 2 || at + 2 + seg > data.length) return null;
      if (tag === 0xc0 || tag === 0xc2) {
        return {
          width: data.readUInt16BE(at + 7),
          height: data.readUInt16BE(at + 5),
        };
      }
      at += 2 + seg;
    }
    return null;
  }

  fingerprint(): string {
    return createHash('sha256').update(this.bytes).digest('hex');
  }
}

function abort(text: string, code: number): never {
  process.stderr.write(`news-image-20261122: ${text}\n`);
  process.exit(code);
}

const origin = join(ROOT, IMAGE);
if (!existsSync(origin)) {
  abort(`cannot find ${IMAGE} next to main.ts; run compose.py to make it`, 2);
}
const first = new JpegCheck(readFileSync(origin));
if (first.size > MAX) {
  abort(`${IMAGE} weighs ${first.size} bytes, above the ${MAX} byte ceiling`, 1);
}
const dims = first.dimensions();
if (dims === null) {
  abort(`${IMAGE} has no readable JPEG frame header`, 1);
}
if (dims.width !== DIM || dims.height !== DIM) {
  abort(`${IMAGE} is ${dims.width} by ${dims.height}, wanted ${DIM} by ${DIM}`, 1);
}
const target = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(target, { recursive: true });
const dest = join(target, 'entry.png');
writeFileSync(dest, readFileSync(origin));
const second = new JpegCheck(readFileSync(dest));
if (second.size !== first.size || second.fingerprint() !== first.fingerprint()) {
  abort(`the file at ${dest} is not a faithful copy of ${IMAGE}`, 1);
}
const again = second.dimensions();
if (again === null || again.width !== DIM || again.height !== DIM) {
  abort(`the file at ${dest} does not parse as a ${DIM} by ${DIM} JPEG`, 1);
}
process.stdout.write(
  `news-image-20261122: wrote ${dest} (${second.size} bytes, JPEG 1024x1024, sha256 ${second.fingerprint().slice(0, 16)}...)\n`,
);
