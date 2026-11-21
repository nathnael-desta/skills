#!/usr/bin/env python3
"""Automatic changed-region detection for a before/after screenshot pair, used by
build_report.py for "auto_marks". Needs numpy and scipy (the builder skips auto marks with a
warning when they are missing).

usage: python3 -I autodiff.py BEFORE.png AFTER.png [naive|shift] [--out FILE.json]

Output JSON: {"strategy", "regions": [{"space": "before"|"after"|"common", "rect": [x,y,w,h]}], "ms"}
  space "common" = naive strategy (both pages compared in the same coordinates).
"""
import bisect
import json
import sys
import time
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

T = 24          # max channel difference below which pixels count as equal (anti-alias noise)
CELL = 8        # grid cell size for merging
MIN_PX = 2      # changed pixels a cell needs to count as changed
DIL = 2         # dilation in cells (~16px) used to merge nearby changes


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)


def background(img):
    """Most common colour on a sparse sample of the page."""
    s = img[::5, ::5].reshape(-1, 3).astype(np.int32)
    codes = (s[:, 0] << 16) | (s[:, 1] << 8) | s[:, 2]
    vals, counts = np.unique(codes, return_counts=True)
    c = int(vals[counts.argmax()])
    return np.array([c >> 16, (c >> 8) & 255, c & 255], dtype=np.int16)


def mask_to_boxes(mask):
    """Boolean pixel mask -> merged pixel-accurate boxes [x,y,w,h]."""
    H, W = mask.shape
    gh, gw = -(-H // CELL), -(-W // CELL)
    pad = np.zeros((gh * CELL, gw * CELL), dtype=bool)
    pad[:H, :W] = mask
    counts = pad.reshape(gh, CELL, gw, CELL).sum(axis=(1, 3))
    on = counts >= MIN_PX
    if not on.any():
        return []
    dil = ndimage.binary_dilation(on, iterations=DIL) if DIL else on
    lab, n = ndimage.label(dil)
    boxes = []
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        cells = on[sl] & (lab[sl] == k)
        if not cells.any():
            continue
        cy, cx = np.nonzero(cells)
        x0 = max(0, (sl[1].start + cx.min()) * CELL)
        y0 = max(0, (sl[0].start + cy.min()) * CELL)
        x1 = min(W, (sl[1].start + cx.max() + 1) * CELL)
        y1 = min(H, (sl[0].start + cy.max() + 1) * CELL)
        # tighten to the actual changed pixels inside the cell box
        py, px = np.nonzero(mask[y0:y1, x0:x1])
        if py.size == 0:
            continue
        boxes.append([int(x0 + px.min()), int(y0 + py.min()),
                      int(px.max() - px.min() + 1), int(py.max() - py.min() + 1)])
    return boxes


def naive(A, B):
    """Plain pixel diff in shared coordinates; the shorter page is padded with white."""
    H = max(A.shape[0], B.shape[0])
    Ap = np.full((H, A.shape[1], 3), 255, dtype=np.int16)
    Bp = np.full((H, B.shape[1], 3), 255, dtype=np.int16)
    Ap[:A.shape[0]] = A
    Bp[:B.shape[0]] = B
    mask = np.abs(Ap - Bp).max(axis=2) > T
    return [{"space": "common", "rect": r} for r in mask_to_boxes(mask)]


def lis_by_second(pairs):
    """Longest subsequence of (i, j) pairs (sorted by i) with strictly increasing j."""
    tails, tail_idx, prev = [], [], [-1] * len(pairs)
    for n, (_, j) in enumerate(pairs):
        k = bisect.bisect_left(tails, j)
        if k == len(tails):
            tails.append(j); tail_idx.append(n)
        else:
            tails[k] = j; tail_idx[k] = n
        prev[n] = tail_idx[k - 1] if k > 0 else -1
    out, n = [], (tail_idx[-1] if tail_idx else -1)
    while n != -1:
        out.append(pairs[n]); n = prev[n]
    return out[::-1]


def shift(A, B):
    """Row-aligned diff (patience-style anchors on exact row content), so
    content that merely moved down/up by a layout shift is an 'equal' block and is
    never compared. Only rows outside equal blocks, or paired rows that differ, count."""
    bg = background(A)
    nonA = np.abs(A - bg).max(axis=2) > T
    nonB = np.abs(B - bg).max(axis=2) > T
    Ha, Hb = A.shape[0], B.shape[0]

    # exact row ids; background-only rows are never used as anchors
    ids = {}
    rowsA = [ids.setdefault(r.tobytes(), len(ids)) for r in A.astype(np.uint8)]
    rowsB = [ids.setdefault(r.tobytes(), len(ids)) for r in B.astype(np.uint8)]
    blankA = ~nonA.any(axis=1)
    blankB = ~nonB.any(axis=1)

    # patience diff: anchors are rows whose content occurs exactly once on each side;
    # the longest increasing run of those pairs gives the row alignment
    cntA, cntB = Counter(), Counter()
    posA, posB = {}, {}
    for i, k in enumerate(rowsA):
        cntA[k] += 1; posA[k] = i
    for j, k in enumerate(rowsB):
        cntB[k] += 1; posB[k] = j
    pairs = sorted((posA[k], posB[k]) for k in posA
                   if k in posB and cntA[k] == 1 and cntB[k] == 1
                   and not blankA[posA[k]] and not blankB[posB[k]])
    anchors = lis_by_second(pairs)

    mA = np.zeros((Ha, A.shape[1]), dtype=bool)
    mB = np.zeros((Hb, B.shape[1]), dtype=bool)
    pi, pj = 0, 0
    for i, j in anchors + [(Ha, Hb)]:
        i1, j1 = pi, pj
        i2, j2 = i, j
        if i2 > i1 or j2 > j1:
            if i2 - i1 == j2 - j1:
                # same number of rows between anchors: pair in order; a differing pixel counts
                # on a side only where that page has content (removed -> before, added -> after)
                d = np.abs(A[i1:i2] - B[j1:j2]).max(axis=2) > T
                mA[i1:i2] |= d & nonA[i1:i2]
                mB[j1:j2] |= d & nonB[j1:j2]
            else:
                # inserted, deleted or unequal gap: non-background pixels count
                mA[i1:i2] |= nonA[i1:i2]
                mB[j1:j2] |= nonB[j1:j2]
        pi, pj = i + 1, j + 1
    out = []
    for space, m, X, Y in (("before", mA, A, B), ("after", mB, B, A)):
        for r in mask_to_boxes(m):
            if not pure_shift(X, Y, r):
                out.append({"space": space, "rect": r})
    return out


def pure_shift(X, Y, box, max_dy=64, ctx_y=12, ctx_x=40, tol=0.002):
    """True when the box and its surrounding context reappear unchanged in Y at one
    vertical offset. The context check stops a changed glyph from matching an identical
    glyph elsewhere; a block re-centred by a grown neighbour moves with its context."""
    H, W = X.shape[0], X.shape[1]
    x, y, w, h = box
    x0, x1 = max(0, x - ctx_x), min(W, x + w + ctx_x)
    y0, y1 = max(0, y - ctx_y), min(H, y + h + ctx_y)
    patch = X[y0:y1, x0:x1]
    ph, pw = patch.shape[0], patch.shape[1]
    budget = tol * ph * pw            # mismatches allowed: frac <= tol
    for dy in range(-max_dy, max_dy + 1):
        if dy == 0 or y0 + dy < 0 or y1 + dy > Y.shape[0]:
            continue
        # compare in row chunks and stop as soon as the budget is exceeded (exact, same result)
        bad, ok = 0, True
        for s0 in range(0, ph, 8):
            seg = patch[s0:s0 + 8]
            ys = y0 + dy + s0
            bad += np.count_nonzero(np.abs(seg - Y[ys:ys + seg.shape[0], x0:x1]).max(axis=2) > T)
            if bad > budget:
                ok = False
                break
        if ok:
            return True
    return False


STRATEGIES = {"naive": naive, "shift": shift}


def pair_regions(regions, max_dy=120):
    """Pair a before-space region with the after-space region that is the same change
    (x ranges overlap, vertical position within max_dy: a layout shift moves it a little).
    Returns [{"before": rect|None, "after": rect|None}] in page order."""
    bs = sorted((r["rect"] for r in regions if r["space"] == "before"), key=lambda r: (r[1], r[0]))
    as_ = sorted((r["rect"] for r in regions if r["space"] == "after"), key=lambda r: (r[1], r[0]))
    out, used = [], set()
    for b in bs:
        hit = None
        for k, a in enumerate(as_):
            if k in used or abs(a[1] - b[1]) > max_dy or a[0] > b[0] + b[2] or b[0] > a[0] + a[2]:
                continue
            hit = k
            break
        if hit is None:
            out.append({"before": b, "after": None})
        else:
            used.add(hit)
            out.append({"before": b, "after": as_[hit]})
    out += [{"before": None, "after": a} for k, a in enumerate(as_) if k not in used]
    return sorted(out, key=lambda m: (m["before"] or m["after"])[1])


def run(before_path, after_path, strategy):
    A = load(before_path)
    B = load(after_path)
    t0 = time.perf_counter()
    regions = STRATEGIES[strategy](A, B)
    ms = (time.perf_counter() - t0) * 1000
    return {"strategy": strategy, "regions": regions, "ms": round(ms, 1)}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    strategy = argv[3] if len(argv) > 3 and not argv[3].startswith("--") else "shift"
    result = run(argv[1], argv[2], strategy)
    text = json.dumps(result, indent=1)
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w") as f:
            f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
