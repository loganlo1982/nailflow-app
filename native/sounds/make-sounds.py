# (lệnh 556) NailFlow notification sounds – synthesized from scratch (sine / FM / noise), no samples: original work, released CC0 by the salon owner.
import numpy as np, wave, json
SR = 44100
def env(n, a=0.005, d=0.25):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / d); return e
def tone(f, dur, a=0.005, d=0.25, harm=((1, 1.0),), fm=None):
    n = int(SR * dur); t = np.arange(n) / SR; s = np.zeros(n)
    for k, g in harm:
        ph = 2 * np.pi * f * k * t
        if fm: ph += fm[1] * np.sin(2 * np.pi * f * fm[0] * t)
        s += g * np.sin(ph)
    return s * env(n, a, d)
def bell(f, dur=1.2, d=0.5): return tone(f, dur, 0.002, d, harm=((1, 1), (2.76, .35), (5.4, .18), (8.9, .08)))
def place(total, parts):
    out = np.zeros(int(SR * total))
    for at, s in parts:
        i = int(SR * at); j = min(len(out), i + len(s)); out[i:j] += s[:j - i]
    return out
def norm(s, peak=0.89): s = s / (np.max(np.abs(s)) + 1e-9) * peak; return s
S = {}
# 1 YOUR TURN – urgent: 3 fast rising square-ish beeps ×2
beep = lambda f: tone(f, 0.11, 0.002, 0.2, harm=((1, 1), (3, .3), (5, .12)))
S['nf_alarm'] = place(1.6, [(0.0, beep(880)), (0.14, beep(1175)), (0.28, beep(1568)), (0.8, beep(880)), (0.94, beep(1175)), (1.08, beep(1568))])
# 2 YOUR TURN – fast double bell, repeated
S['nf_rush'] = place(1.8, [(0, bell(1320, .6, .25)), (0.16, bell(1320, .6, .25)), (0.9, bell(1320, .6, .25)), (1.06, bell(1320, .6, .25))])
# 3 booking – door chime (two notes down, a major third) – own intervals
S['nf_door'] = place(2.2, [(0, bell(988, 1.6, .7)), (0.45, bell(784, 1.6, .8))])
# 4 booking – three-note chime up (C E G)
S['nf_chime'] = place(2.0, [(0, bell(1047, 1.2, .45)), (0.2, bell(1319, 1.2, .45)), (0.4, bell(1568, 1.4, .6))])
# 5 message – soft bubble pop (pitch drop) + a second smaller one
def pop(f0, f1, dur=0.12):
    n = int(SR * dur); t = np.arange(n) / SR; f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.05)
S['nf_pop'] = place(0.6, [(0, pop(900, 1500)), (0.13, pop(1100, 1800))])
# 6 message – woodblock knock-knock
def knock(f): return tone(f, 0.18, 0.001, 0.035, harm=((1, 1), (2.3, .5), (4.1, .2)))
S['nf_knock'] = place(0.7, [(0, knock(700)), (0.17, knock(760))])
# 7 soft – single glass ping
S['nf_ping'] = place(1.4, [(0, tone(1760, 1.4, 0.003, 0.35, harm=((1, 1), (2, .15))))])
# 8 soft – marimba two notes (FM)
def mar(f): return tone(f, 0.9, 0.002, 0.18, harm=((1, 1), (4, .25)), fm=(1, 0.6))
S['nf_marimba'] = place(1.2, [(0, mar(523)), (0.18, mar(659))])
for k, s in S.items():
    s = norm(s); fade = int(SR * 0.02); s[-fade:] *= np.linspace(1, 0, fade)
    x = (s * 32767).astype('<i2')
    with wave.open(k + '.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
    print(k, round(len(s) / SR, 2), 's')
