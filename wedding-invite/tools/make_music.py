"""Synthesizes a gentle, royalty-free background score for the invite.

Tanpura drone + santoor-style melody (Bilawal / major scale, folk feel) + dholak keherwa,
with bell chimes on the day changes. Everything is additive synthesis, so there is nothing
to license.

    python3 tools/make_music.py assets/music.wav [duration] [rhythm_start] [bell_times,comma,separated]
    ffmpeg -i assets/music.wav -c:a aac -b:a 192k assets/music.m4a
"""
import sys
import wave

import numpy as np

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 67.9
N = int(SR * (DUR + 2.5))
rng = np.random.default_rng(7)

SA = 293.66  # D4 as Sa
SEMI = {'S': 0, 'R': 2, 'G': 4, 'M': 5, 'P': 7, 'D': 9, 'N': 11}


def freq(sw, octave=0):
    return SA * 2 ** ((SEMI[sw] + 12 * octave) / 12)


def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i]


def santoor(f, vel=1.0, length=2.4):
    t = np.arange(int(length * SR)) / SR
    out = np.zeros_like(t)
    for detune in (-0.0012, 0.0012):  # two strings per course -> shimmer
        for k in range(1, 9):
            fk = f * k * (1 + 0.0007 * k * k) * (1 + detune)
            if fk > 14000:
                break
            tau = 1.6 / k ** 0.75
            out += (1 / k ** 1.25) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    hammer = rng.standard_normal(len(t)) * np.exp(-t / 0.004) * 0.25
    att = np.minimum(1, t / 0.002)
    return vel * 0.22 * (out * att + hammer)


def tanpura(f, length=4.5):
    t = np.arange(int(length * SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, 22):
        fk = f * k
        if fk > 9000:
            break
        bloom = 1 + 1.6 * np.exp(-((t - 0.25 * k ** 0.35) ** 2) / 0.35)  # jawari swell of upper partials
        out += (1 / k ** 0.85) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * (bloom if k > 3 else 1)
    env = np.minimum(1, t / 0.03) * np.exp(-t / 3.2)
    return 0.05 * out * env


def bell(f=1568.0, vel=1.0, length=3.0):
    t = np.arange(int(length * SR)) / SR
    out = np.zeros_like(t)
    for r, a, tau in ((1, 1, 1.4), (2.76, .5, .9), (5.4, .3, .5), (8.93, .18, .3), (2.0, .25, 1.1)):
        out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    return vel * 0.06 * out * np.minimum(1, t / 0.001)


def dhol_bass(vel=1.0):
    t = np.arange(int(0.45 * SR)) / SR
    f = 62 + 70 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.22)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.003) * 0.15
    return vel * 0.42 * (body + click)


def dhol_treble(vel=1.0, pitch=1.0):
    t = np.arange(int(0.25 * SR)) / SR
    out = np.zeros_like(t)
    for r, a in ((1, 1), (1.59, .6), (2.14, .4), (2.65, .25)):
        out += a * np.sin(2 * np.pi * 460 * pitch * r * t) * np.exp(-t / (0.07 / r ** 0.5))
    noise = rng.standard_normal(len(t)) * np.exp(-t / 0.012)
    return vel * 0.16 * (out + 0.5 * noise)


def ghungroo(vel=1.0):
    t = np.arange(int(0.18 * SR)) / SR
    n = rng.standard_normal(len(t))
    # crude high-pass via differencing, metallic jingle
    n = np.diff(np.concatenate([[0], n]))
    return vel * 0.03 * n * np.exp(-t / 0.05)


mel = np.zeros(N)
drone = np.zeros(N)
drums = np.zeros(N)
bells = np.zeros(N)

# ---- Drone throughout: Pa(low) Sa Sa Sa(low), one pluck every 1.15 s
cycle = [(freq('P', -2), .9), (freq('S', -1), 1.0), (freq('S', -1), .9), (freq('S', -2), 1.1)]
tt, k = 0.0, 0
while tt < DUR + 1:
    f, v = cycle[k % 4]
    add(drone, tt, v * tanpura(f))
    tt += 1.15
    k += 1

# ---- Opening alaap (free rhythm) during the doors / Ganesh slide
for t0, sw, octv, v in [(0.4, 'S', 0, .8), (1.3, 'G', 0, .7), (2.0, 'P', 0, .75), (2.7, 'D', 0, .6), (3.1, 'P', 0, .7),
                        (3.8, 'S', 1, .8), (4.3, 'N', 0, .5), (4.55, 'D', 0, .55), (4.8, 'P', 0, .6)]:
    add(mel, t0, santoor(freq(sw, octv), v, 3.0))
for t0, f in [(0.7, 1568.0), (1.0, 2093.0), (2.4, 1760.0)]:
    add(bells, t0, bell(f, .9))

# ---- Rhythmic section from the title slide
BPM = 96
E8 = 60 / BPM / 2
START = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
PHRASE = [  # (swar, octave, eighths)
    ('P', 0, 2), ('D', 0, 1), ('P', 0, 1), ('G', 0, 2), ('R', 0, 1), ('G', 0, 1),
    ('S', 0, 4), ('R', 0, 2), ('G', 0, 2),
    ('G', 0, 2), ('P', 0, 1), ('D', 0, 1), ('S', 1, 2), ('D', 0, 1), ('P', 0, 1),
    ('P', 0, 6), (None, 0, 2),
    ('S', 1, 2), ('N', 0, 1), ('D', 0, 1), ('P', 0, 2), ('G', 0, 1), ('P', 0, 1),
    ('D', 0, 2), ('P', 0, 2), ('G', 0, 2), ('R', 0, 2),
    ('G', 0, 2), ('R', 0, 1), ('S', 0, 1), ('R', 0, 2), ('G', 0, 1), ('R', 0, 1),
    ('S', 0, 6), (None, 0, 2),
]
END = DUR - 3.2
t = START
rep = 0
while t < END:
    for sw, octv, n8 in PHRASE:
        if t >= END:
            break
        if sw is not None:
            o = octv + (1 if rep % 2 == 1 and sw in 'SRG' and octv == 0 else 0)
            f = freq(sw, o)
            if n8 >= 3:  # santoor tremolo on long notes
                strikes = int(n8 * E8 / 0.085)
                for s in range(strikes):
                    add(mel, t + s * 0.085, santoor(f, (0.62 if s % 2 else 0.5) * (1 - 0.25 * s / strikes), 1.2))
            else:
                add(mel, t, santoor(f, 0.85 if n8 == 2 else 0.7, 2.0))
                if n8 == 2 and rep % 2 == 0:
                    add(mel, t + E8, santoor(f, 0.35, 1.0))
        t += n8 * E8
    rep += 1
# final resolution on Sa
add(mel, END + 0.05, santoor(freq('S', 0), 0.9, 3.0))
add(mel, END + 0.05, santoor(freq('S', 1), 0.6, 3.0))
add(bells, END + 0.05, bell(1175.0, 1.0, 3.5))

# ---- Dholak keherwa (8 eighths / bar)
bar = 8 * E8
nbars = int((END - START) / bar)
for b in range(nbars):
    t0 = START + b * bar
    fill = (b % 4 == 3)
    for i in range(8):
        tt = t0 + i * E8
        if i in (0, 4):
            add(drums, tt, dhol_bass(1.0 if i == 0 else 0.75))
        if i == 3 or (i == 6 and not fill):
            add(drums, tt, dhol_bass(0.55))
        if i in (1, 2, 5, 7):
            add(drums, tt, dhol_treble(0.8 if i in (2, 7) else 0.6, 1.0 if i != 5 else 1.12))
        if fill and i >= 5:
            add(drums, tt + E8 / 2, dhol_treble(0.55, 1.2))
            add(drums, tt, dhol_treble(0.7, 0.95))
        add(drums, tt, ghungroo(0.9 if i % 2 == 0 else 0.6))
add(drums, START + nbars * bar, dhol_bass(1.0))

# ---- Bells on day changes and the finale (slide starts from index.html)
for t0 in ([float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else (5.0, 15.0, 28.75, 46.25, 60.0)):
    add(bells, t0, bell(1568.0, 0.8))
    add(bells, t0 + 0.12, bell(2349.0, 0.5))

# ---- Mix, light reverb, master
mix = 0.85 * mel + 1.0 * drone + 0.75 * drums + 0.9 * bells
ir_t = np.arange(int(1.6 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.45)
ir[0] = 0
ir /= np.sqrt(np.sum(ir ** 2))
from numpy.fft import irfft, rfft  # noqa: E402

L = len(mix) + len(ir)
nfft = 1 << (L - 1).bit_length()
wet = irfft(rfft(mix, nfft) * rfft(ir, nfft), nfft)[:len(mix)]
out = mix + 0.22 * wet
fade_in = np.minimum(1, np.arange(N) / (0.3 * SR))
t_axis = np.arange(N) / SR
fade_out = np.clip((DUR - t_axis) / 2.5, 0, 1)
out *= fade_in * fade_out
out = out[:int(DUR * SR)]
out = np.tanh(out / np.max(np.abs(out)) * 1.2) / np.tanh(1.2) * 0.89
stereo = np.stack([out, np.roll(out, 220) * 0.97 + out * 0.03], axis=1)
pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', OUT, f'{len(out) / SR:.1f}s')
