"""Trilha: Apple Loops decodificados pelo ffmpeg, arranjados numa grade de 128 BPM, e efeitos
sintetizados em numpy. Mixagem em float32 estéreo a 48 kHz."""
import os, subprocess, functools, json
import numpy as np
from scipy import signal

SR = 48000
BPM = 128.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
LOOPS = "/Library/Audio/Apple Loops/Apple"
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "audio_cache")
os.makedirs(CACHE, exist_ok=True)

@functools.lru_cache(None)
def _catalog():
    return {r["name"]: r for r in json.load(open(os.path.join(ROOT, "loops.json")))}

@functools.lru_cache(None)
def loop(name, tempo=None):
    """Decodifica um Apple Loop para estéreo float32. tempo: BPM de destino (atempo preserva a altura)."""
    r = _catalog()[name]
    tag = f"{name}_{tempo or 'orig'}".replace(" ", "_").replace("/", "_")
    out = os.path.join(CACHE, tag + ".f32")
    if not os.path.exists(out):
        af = []
        if tempo and r.get("bpm") and abs(tempo - r["bpm"]) > 0.05:
            af = ["-af", f"atempo={tempo / r['bpm']:.6f}"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", r["path"], *af, "-ac", "2", "-ar", str(SR),
                        "-f", "f32le", out], check=True)
    a = np.fromfile(out, dtype=np.float32).reshape(-1, 2)
    if tempo or r.get("bpm"):
        # recorta no comprimento exato em batidas, para que a repetição não escorregue
        bpm = tempo or r["bpm"]
        beats = int(r.get("beat count") or 0)
        if beats:
            n = int(round(beats * 60.0 / bpm * SR))
            if len(a) >= n - 2000:
                a = a[:n] if len(a) >= n else np.pad(a, ((0, n - len(a)), (0, 0)))
    return a

class Mix:
    def __init__(self, seconds):
        self.buf = np.zeros((int(seconds * SR) + SR, 2), np.float32)

    def add(self, x, at, gain=1.0, fade_in=0.0, fade_out=0.0, length=None, pan=0.0):
        if x is None or len(x) == 0:
            return
        x = x.copy()
        if length is not None:
            n = int(length * SR)
            if len(x) < n:
                reps = int(np.ceil(n / len(x)))
                x = np.tile(x, (reps, 1))
            x = x[:n]
        if fade_in > 0:
            k = min(len(x), int(fade_in * SR))
            x[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None] ** 2
        if fade_out > 0:
            k = min(len(x), int(fade_out * SR))
            x[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None] ** 2
        if pan:
            x[:, 0] *= np.sqrt((1 - pan) / 2) * np.sqrt(2)
            x[:, 1] *= np.sqrt((1 + pan) / 2) * np.sqrt(2)
        i = int(at * SR)
        if i < 0:
            x = x[-i:]; i = 0
        j = min(len(self.buf), i + len(x))
        self.buf[i:j] += x[: j - i] * gain

    def automate(self, a, b, g0, g1):
        i, j = int(a * SR), int(b * SR)
        self.buf[i:j] *= np.linspace(g0, g1, j - i, dtype=np.float32)[:, None]

def repeat_loop(mix, name, start, bars, gain=1.0, fade_in=0.0, fade_out=0.0, tempo=BPM, filt=None, pan=0.0):
    x = loop(name, tempo)
    n = int(round(bars * BAR * SR))
    reps = int(np.ceil(n / len(x)))
    y = np.tile(x, (reps, 1))[:n]
    if filt is not None:
        y = filt(y)
    mix.add(y, start, gain, fade_in, fade_out, pan=pan)

# ---------------------------------------------------------------- filtros
def lowpass(x, fc, order=4):
    b, a = signal.butter(order, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)

def highpass(x, fc, order=4):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)

def sweep_lowpass(x, f0, f1, curve=2.0):
    """Filtro passa-baixas que abre (ou fecha) ao longo do trecho, em blocos de 10 ms."""
    out = np.zeros_like(x)
    blk = SR // 100
    n = len(x)
    zi = None
    for i in range(0, n, blk):
        k = (i / max(1, n - 1)) ** curve
        fc = f0 * (f1 / f0) ** k
        b, a = signal.butter(2, min(0.99, fc / (SR / 2)), "low")
        if zi is None:
            zi = np.zeros((max(len(a), len(b)) - 1, 2))
        y, zi = signal.lfilter(b, a, x[i:i + blk], axis=0, zi=zi)
        out[i:i + blk] = y
    return out.astype(np.float32)

def reverb(x, seconds=2.5, mix=0.3, predelay=0.02, seed=3):
    """Convolução com ruído decaindo exponencialmente — sala grande, escura."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)).astype(np.float32) * np.exp(-t * 6.9 / seconds)[:, None]
    ir = lowpass(ir, 6000, 2)
    ir[: int(predelay * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True)) + 1e-9
    wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x) + n] for c in range(2)], 1)
    m_ = min(len(wet), len(x) + n)
    wet = wet[:m_]
    dry = np.pad(x, ((0, n), (0, 0)))[:m_]
    return (dry * (1 - mix) + wet * mix * 1.0).astype(np.float32)

# ---------------------------------------------------------------- efeitos sintetizados
rng = np.random.default_rng(11)

def _t(sec):
    return np.arange(int(sec * SR)) / SR

def stereo(m, width=0.0):
    if width <= 0:
        return np.stack([m, m], 1).astype(np.float32)
    d = int(width * 0.012 * SR)
    r = np.concatenate([np.zeros(d), m[:-d]]) if d else m
    return np.stack([m, r], 1).astype(np.float32)

def whoosh(sec=0.9, f0=300, f1=5000, peak=0.6, gain=0.5):
    """Ruído filtrado com varredura de banda: o deslocamento de um objeto grande."""
    n = int(sec * SR)
    noise = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    envl = np.where(t < peak, (t / peak) ** 2, ((1 - t) / (1 - peak)) ** 1.5)
    out = np.zeros(n)
    blk = 480
    zi = np.zeros(4)
    for i in range(0, n, blk):
        k = i / n
        fc = f0 * (f1 / f0) ** (np.sin(np.pi * min(1, k / peak) / 2) if k < peak else 1 - 0.5 * (k - peak) / (1 - peak))
        b, a = signal.butter(2, [max(40, fc * 0.5) / (SR / 2), min(0.99, fc * 1.6 / (SR / 2))], "band")
        y, zi = signal.lfilter(b, a, noise[i:i + blk], zi=zi)
        out[i:i + blk] = y
    out *= envl
    out /= np.abs(out).max() + 1e-9
    return stereo(out * gain, 1)

def impact(sec=2.5, gain=0.9):
    """Pancada grave: seno descendente + estalo de ruído + cauda."""
    t = _t(sec)
    f = 30 + 90 * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 2.2)
    click = rng.normal(0, 1, len(t)) * np.exp(-t * 60)
    click = signal.lfilter(*signal.butter(2, 3000 / (SR / 2), "low"), click)
    out = np.tanh((body * 1.2 + click * 0.5) * 1.5)
    out /= np.abs(out).max()
    return reverb(stereo(out * gain, 0.5), 3.0, 0.25)

def sub_drop(sec=1.6, gain=0.8):
    t = _t(sec)
    f = 70 * np.exp(-t * 1.6) + 28
    out = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8) * np.minimum(1, t * 80)
    return stereo(out * gain)

def riser(sec=4.0, gain=0.5, f0=200, f1=8000):
    """Ruído que sobe e acelera — tensão antes de uma virada."""
    n = int(sec * SR)
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    zi = np.zeros(4)
    for i in range(0, n, 480):
        k = (i / n) ** 2
        fc = f0 * (f1 / f0) ** k
        b, a = signal.butter(2, [fc * 0.6 / (SR / 2), min(0.99, fc * 1.4 / (SR / 2))], "band")
        y, zi = signal.lfilter(b, a, noise[i:i + 480], zi=zi)
        out[i:i + 480] = y
    t = np.linspace(0, 1, n)
    # tom que sobe junto
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (t * 3)) / SR) * 0.25
    out = out / (np.abs(out).max() + 1e-9) + tone
    out *= t ** 2.2
    return stereo(out * gain, 1)

def tick(gain=0.25, freq=3800, sec=0.05):
    """Clique de interface: curto, seco, agudo."""
    t = _t(sec)
    out = np.sin(2 * np.pi * freq * t) * np.exp(-t * 180) + rng.normal(0, 1, len(t)) * np.exp(-t * 400) * 0.3
    return stereo(out * gain)

def blip(gain=0.22, f=1320, sec=0.18):
    """Confirmação suave: dois parciais, ataque rápido."""
    t = _t(sec)
    out = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * 28) * np.minimum(1, t * 400)
    return reverb(stereo(out * gain), 1.2, 0.2)

def paper(gain=0.2, sec=0.35):
    """Folha deslizando: ruído rosa em banda média, com rugosidade."""
    n = int(sec * SR)
    x = rng.normal(0, 1, n)
    x = signal.lfilter(*signal.butter(2, [900 / (SR / 2), 6000 / (SR / 2)], "band"), x)
    t = np.linspace(0, 1, n)
    rough = 0.6 + 0.4 * np.abs(np.sin(np.cumsum(rng.uniform(20, 90, n)) / SR * 2 * np.pi))
    out = x * np.sin(np.pi * t) ** 1.2 * rough
    out /= np.abs(out).max() + 1e-9
    return stereo(out * gain, 0.6)

def type_clicks(sec=1.0, rate=11, gain=0.12):
    out = np.zeros((int(sec * SR) + SR // 10, 2), np.float32)
    k = 0.0
    while k < sec:
        c = tick(gain * rng.uniform(0.6, 1.0), rng.uniform(2500, 4200), 0.03)
        i = int(k * SR)
        out[i:i + len(c)] += c
        k += 1 / rate * rng.uniform(0.6, 1.4)
    return out

def heartbeat_tick(gain=0.18):
    """Tique de relógio, para o ato da fragmentação."""
    t = _t(0.08)
    out = rng.normal(0, 1, len(t)) * np.exp(-t * 120)
    out = signal.lfilter(*signal.butter(2, [1800 / (SR / 2), 7000 / (SR / 2)], "band"), out)
    out /= np.abs(out).max()
    return stereo(out * gain)

def glitch(sec=0.25, gain=0.3):
    n = int(sec * SR)
    x = np.zeros(n)
    i = 0
    while i < n:
        L = int(rng.uniform(0.004, 0.03) * SR)
        f = rng.uniform(200, 4000)
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * rng.uniform(0.3, 1)
        x[i:i + L] = seg[: max(0, min(L, n - i))]
        i += L + int(rng.uniform(0, 0.02) * SR)
    x = signal.lfilter(*signal.butter(2, 6000 / (SR / 2), "low"), x)
    return stereo(x * gain, 0.4)

def master(buf, target_lufs=-16.0):
    """Limitador suave e normalização de pico; a sonoridade final sai do loudnorm do ffmpeg."""
    x = buf.copy()
    x = np.tanh(x * 0.9) / 0.9
    peak = np.abs(x).max()
    if peak > 0:
        x *= 0.95 / peak
    return x
