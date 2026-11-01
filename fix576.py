#!/usr/bin/env python3
# LAMWEB 2.99.576 - LENH 576 (anh Logan 31/10 01:11): /colors uses the 6 NEW hands holding a polish bottle (Downloads\\tay-dep, task RENDER 01:09, CHAT ok).
# The tap on a color paints the NAILS and the BOTTLE (polish + cap) in that color, with their own shine, right to the cuticle and to the glass (570 way).
# Fixed here: the grey strip at the bottle edge (polish seen through the glass, not in -bottle.png) is now part of the bottle (grown by its grey colour,
#   never into the clear glass). Zoom: the window takes the bottle + the nails (like the PLA product photo). All 6 hands used (white 01-04, Hispanic 05-06).
# New files: assets/hands/tay-01..06.jpg + tay-01..06-shade.png (replace). The old tay-07/08 stay (not used).
# Run: python3 fix576.py <file colors/index.php>  -> check only;  ... go -> backup to ~/app/old + patch
import sys, os, shutil, time, hashlib, json
p = sys.argv[1]; go = len(sys.argv) > 2 and sys.argv[2] == 'go'
s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
A = json.loads(r'''[["const L = ['01', '02', '05', '07']; return L[h % L.length];", "const L = ['01', '02', '03', '04', '05', '06']; return L[h % L.length]; /* (2.99.576) the 6 hands holding a bottle (tay-dep): white 01-04, Hispanic 05-06 */"], ["img(`../assets/hands/tay-${n}.jpg?v=570`), img(`../assets/hands/tay-${n}-shade.png?v=570`)", "img(`../assets/hands/tay-${n}.jpg?v=576`), img(`../assets/hands/tay-${n}-shade.png?v=576`)"], ["    let w = HW * 0.56, h = w / ar; if (h > HH) { h = HH; w = h * ar; }\n    const S = 16, gw = Math.ceil(HW / S), gh = Math.ceil(HH / S), I = new Float64Array((gw + 1) * (gh + 1)); // (2.99.563) sums of the nail mask on a 16 px grid (the photo is 2x bigger)\n    for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < gw; gx++) { const v = H.mo[Math.min(HH - 1, gy * S + 8) * HW + Math.min(HW - 1, gx * S + 8)] > 128 ? 1 : 0; I[(gy + 1) * (gw + 1) + gx + 1] = v + I[gy * (gw + 1) + gx + 1] + I[(gy + 1) * (gw + 1) + gx] - I[gy * (gw + 1) + gx]; }\n    const ww = Math.round(w / S), wh = Math.round(h / S), mx = Math.round(ww * 0.12), my = Math.round(wh * 0.1); let best = -1, bx = 0, by = 0; // nails counted only INSIDE (not cut at the edge)\n    for (let gy = 0; gy + wh <= gh; gy++) for (let gx = 0; gx + ww <= gw; gx++) { const ya = gy + my, yb = gy + wh - my, xa = gx + mx, xb = gx + ww - mx, n = I[yb * (gw + 1) + xb] - I[ya * (gw + 1) + xb] - I[yb * (gw + 1) + xa] + I[ya * (gw + 1) + xa] - 0.6 * ((I[(gy + wh) * (gw + 1) + gx + ww] - I[gy * (gw + 1) + gx + ww] - I[(gy + wh) * (gw + 1) + gx] + I[gy * (gw + 1) + gx]) - (I[yb * (gw + 1) + xb] - I[ya * (gw + 1) + xb] - I[yb * (gw + 1) + xa] + I[ya * (gw + 1) + xa])); if (n > best) { best = n; bx = gx; by = gy; } }\n    const cx = Math.min(HW - w / 2, Math.max(w / 2, (bx + ww / 2) * S)), cy = Math.min(HH - h / 2, Math.max(h / 2, (by + wh / 2) * S));\n", "    // (2.99.576) the window = the nails AND the bottle (like a product photo), shaped like the space on screen\n    let bx0 = HW, by0 = HH, bx1 = 0, by1 = 0; for (let y = 0; y < HH; y += 8) for (let x = 0; x < HW; x += 8) if (H.mo[y * HW + x] > 128) { if (x < bx0) bx0 = x; if (x > bx1) bx1 = x; if (y < by0) by0 = y; if (y > by1) by1 = y; }\n    if (bx1 < bx0) { bx0 = 0; by0 = 0; bx1 = HW; by1 = HH; }\n    let w = (bx1 - bx0) * 1.06 + 40, h = (by1 - by0) * 1.06 + 40; if (w / h > ar) h = w / ar; else w = h * ar; if (w > HW) { w = HW; h = w / ar; } if (h > HH) { h = HH; w = h * ar; }\n    const cx = Math.min(HW - w / 2, Math.max(w / 2, (bx0 + bx1) / 2)), cy = Math.min(HH - h / 2, Math.max(h / 2, (by0 + by1) / 2));\n"]]''')
n = [s.count(a) for a, _ in A]
print(p, 'sha', sha(s), 'anchors', *n, 'already', '?v=576`' in s)
if '?v=576`' in s: sys.exit('STOP: already patched - nothing changed')
if n != [1] * len(A): sys.exit('STOP: an anchor is not found exactly once - nothing changed')
t = s
for a, b in A: t = t.replace(a, b)
if not go: print('NEW would be sha', sha(t)); sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M')
shutil.copy2(p, f'{bk}/colors-index.php.pre-576-{st}')
mode = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, mode)
print('NEW sha', sha(t), 'backup', f'{bk}/colors-index.php.pre-576-{st}')
