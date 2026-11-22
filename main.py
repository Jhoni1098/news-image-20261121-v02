#!/usr/bin/env python3
"""news-image-20261121 v02: write the entry image to /output/entry.png.

The image itself (entry.png, in this repository) was drawn by the agent
from verified 21 November 2026 reporting. This program copies it to the
output directory and validates it, so both runs write the same bytes:
a PNG of 1024x1024 at most 1 MiB. No network, no randomness, no time.
"""
import hashlib
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
EXPECT_W, EXPECT_H = 1024, 1024


def fail(msg):
    print("error:", msg, file=sys.stderr)
    raise SystemExit(1)


def check_png(path):
    with open(path, "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        fail("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk")
    w, h = struct.unpack(">II", head[16:24])
    if (w, h) != (EXPECT_W, EXPECT_H):
        fail("entry.png is %dx%d, expected 1024x1024" % (w, h))
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB cap" % size)
    return size


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png missing from the repository")
    size = check_png(src)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    if os.path.getsize(dst) != size:
        fail("copied entry.png size %d differs from source %d"
             % (os.path.getsize(dst), size))
    src_hash = sha256(src)
    if src_hash != sha256(dst):
        fail("copied entry.png differs from the repository image")
    print("wrote %s (%d bytes, 1024x1024, sha256 %s)"
          % (dst, size, src_hash))


if __name__ == "__main__":
    main()
