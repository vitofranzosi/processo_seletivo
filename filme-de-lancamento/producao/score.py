"""A trilha: arranjo de Apple Loops (Dó menor, 128 BPM) e efeitos sincronizados à imagem."""
import numpy as np
from audiolib import *
import timeline as TL
from timeline import FREEZE, FRASE, DROP, BEAT, BAR
TOTAL = TL.FILM_TOTAL

def b(x):
    """Compasso do arranjo ORIGINAL → segundos do filme com as inserções."""
    return TL.b(TL.S(x))

def span(start_bar, bars):
    """Duração, em compassos do filme, de uma camada que atravessa uma inserção: ela continua tocando."""
    return TL.S(start_bar + bars, end=True) - TL.S(start_bar)

mix = Mix(TOTAL + 4)
fx = Mix(TOTAL + 4)

def L(name, start_bar, bars, gain, fi=0.0, fo=0.0, filt=None, pan=0.0):
    repeat_loop(mix, name, b(start_bar), span(start_bar, bars), gain, fi, fo, tempo=BPM, filt=filt, pan=pan)

def rms_norm(x, target=0.12):
    r = float(np.sqrt((x ** 2).mean()) + 1e-9)
    return x * (target / r)

def free(name, at, length, gain, fi=1.0, fo=1.0, filt=None, tempo=None, target=0.12):
    x = rms_norm(loop(name, tempo), target)
    n = int(length * SR)
    reps = int(np.ceil(n / len(x)))
    y = np.tile(x, (reps, 1))[:n]
    if filt is not None:
        y = filt(y)
    mix.add(y, at, gain, fi, fo)

# alvo de RMS por papel, para que loops de níveis diferentes se equilibrem
def LN(name, start_bar, bars, gain, fi=0.0, fo=0.0, filt=None, target=0.12):
    x = rms_norm(loop(name, BPM), target)
    n = int(round(span(start_bar, bars) * BAR * SR))
    reps = int(np.ceil(n / len(x)))
    y = np.tile(x, (reps, 1))[:n]
    if filt is not None:
        y = filt(y)
    mix.add(y, b(start_bar), gain, fi, fo)

# ======================================================================= I. fragmentação
free("Legend Synth Drone", 0.0, FREEZE + 0.05, 0.42, fi=5.0, fo=0.05, filt=lambda y: highpass(lowpass(y, 1400, 2), 70, 2))
free("Legend Dark Synth Pad", b(4), FREEZE - b(4) + 0.05, 0.35, fi=4.0, fo=0.05, filt=lambda y: lowpass(y, 2200, 2))
# pulso: tique de relógio a cada batida desde o compasso 8, crescendo
for k in range(int((FREEZE - b(8)) / BEAT)):
    t = b(8) + k * BEAT
    g = 0.25 + 0.75 * (k / ((FREEZE - b(8)) / BEAT))
    fx.add(heartbeat_tick(0.16 * g), t)
# chimbal filtrado e bumbo abafado na reta final
LN("Fast Hat Beat", 12, 6, 0.28, fi=3.0, filt=lambda y: highpass(sweep_lowpass(y, 3000, 14000, 1.0), 5000, 2), target=0.10)
LN("Basic Core Beat", 14, 4, 0.55, fi=1.5, filt=lambda y: lowpass(y, 220, 4), target=0.12)
LN("Hard Grinding Bass", 15, 3, 0.30, fi=2.0, filt=lambda y: sweep_lowpass(y, 200, 2500, 1.4), target=0.10)
fx.add(riser(FREEZE - b(14), 0.32), b(14))
# palavras: um toque por palavra; multiplicação em semicolcheias
for i in range(5):
    fx.add(blip(0.14, 880 * 2 ** (i * 3 / 12)), b(4) + i * BEAT * 2)
for j in range(46):
    fx.add(tick(0.05, 2400 + (j * 397) % 2400, 0.03), b(6.5) + j * BEAT / 4)
# ferramentas avulsas surgindo: papel + estalo
for i in range(8):
    fx.add(paper(0.16), b(8 + i) - 0.12)
    fx.add(glitch(0.12, 0.10), b(8 + i) + 0.05)
for k in range(10):
    fx.add(tick(0.07, 3200, 0.04), 24 + k * BEAT * 0.9)  # notificações
# o congelamento: corte seco, pancada e cauda
fx.add(impact(3.5, 0.95), FREEZE)
fx.add(sub_drop(2.0, 0.6), FREEZE)
# a frase
free("Afloat Pad", FRASE - 0.6, b(22) - FRASE + 1.2, 0.5, fi=2.0, fo=1.0, filt=lambda y: lowpass(y, 3000, 2))
fx.add(sub_drop(2.5, 0.35), FRASE + 0.3)

# ======================================================================= II. transformação
LN("Luminosity Synth Layers", 22, 4, 0.55, fi=0.5, filt=lambda y: sweep_lowpass(y, 250, 14000, 1.6), target=0.12)
LN("Melodic Silk Bass", 24, 2, 0.45, fi=1.0, filt=lambda y: sweep_lowpass(y, 150, 3000, 1.2), target=0.11)
LN("Big Snare Roll Topper", 25, 1, 0.45, fi=0.8, target=0.10)
fx.add(riser(b(26) - b(23.5), 0.3), b(23.5))
for i in range(8):
    st = b(22) + 0.35 + i * BEAT * 0.5
    fx.add(whoosh(0.9, 400, 5000, 0.6, 0.20), st + 0.3)
fx.add(whoosh(1.6, 200, 7000, 0.7, 0.35), b(25.5) - 0.2)

# ======================================================================= o título: drop
fx.add(impact(3.0, 1.0), DROP)
fx.add(sub_drop(1.8, 0.7), DROP)
LN("Four Four Beat", 26, 4, 0.75, target=0.13)
LN("Mass Appeal Layers 01", 26, 4, 0.55, target=0.12)
LN("Melodic Silk Bass", 26, 4, 0.5, target=0.11)
fx.add(whoosh(1.0, 300, 6000, 0.7, 0.3), b(29.4))

# ======================================================================= III-a. edital
LN("Chronograph Set Beat 01", 30, 16, 0.7, target=0.13)
LN("Luminosity Synth Layers", 30, 8, 0.48, target=0.11)
LN("Lightspeed Lead Layers", 38, 8, 0.45, target=0.11)
LN("Melodic Silk Bass", 30, 16, 0.48, target=0.11)
# a folha se parte; as faixas pousam
fx.add(paper(0.22), b(31.3))
for i in range(9):
    fx.add(tick(0.08, 2600 + i * 120, 0.04), b(31.3) + 0.2 + i * 0.07)
for t in [b(32.4), b(33.6), b(35.0)]:
    fx.add(whoosh(0.8, 300, 5000, 0.6, 0.22), t - 0.2)
for t in [b(34.5), b(35.4), b(36.6), b(37.4), b(38.2), b(39.0), b(39.5), b(40.0)]:
    fx.add(tick(0.20, 3600, 0.05), t)
# o sistema escreve o Edital; a lei; revisado, publicado, aberto a todos
G0 = TL.seg_start("sc_gera2"); P0 = TL.seg_start("sc_publica2")
fx.add(whoosh(1.0, 250, 4500, 0.6, 0.20), G0 + 0.1)
fx.add(riser(2.4, 0.10, 600, 5000), G0 + 1.2)
fx.add(paper(0.20), G0 + 3.5)
fx.add(whoosh(1.0, 300, 5000, 0.6, 0.22), G0 + 4.6)
for j in range(3):
    fx.add(blip(0.14, 1046 * 2 ** (j * 4 / 12)), G0 + 7.3 + j * 0.7)
fx.add(whoosh(0.8, 300, 5000, 0.6, 0.22), P0 - 0.1)
for j, u in enumerate([2.6, 2.85, 3.1]):
    fx.add(blip(0.10, 988 * 2 ** (j * 3 / 12)), P0 + u)
fx.add(whoosh(0.8, 300, 5000, 0.6, 0.22), P0 + 5.2)
fx.add(tick(0.24, 3600, 0.05), P0 + 7.5)
fx.add(impact(2.0, 0.45), P0 + 7.55)
fx.add(whoosh(1.1, 250, 7000, 0.6, 0.30), P0 + 8.6)
fx.add(whoosh(0.7, 800, 6000, 0.5, 0.18), P0 + 9.6); fx.add(blip(0.16, 1318), P0 + 10.7)
fx.add(tick(0.22, 3600, 0.05), P0 + 14.25)

# ======================================================================= III-b. inscrição
LN("Rocket Fuel Beat 01", 46, 16, 0.7, target=0.13)
LN("Pure Candy Synth Layers", 46, 8, 0.45, target=0.11)
LN("Airy Vox Synth", 54, 8, 0.42, target=0.10)
LN("Melodic Silk Bass", 46, 16, 0.48, target=0.11)
LN("Clap Swing Topper", 61, 1, 0.35, target=0.09)
fx.add(type_clicks(0.4, 26, 0.10), b(48.0))
for t in [b(47.95), b(51.5), b(52.65), b(53.5)]:
    fx.add(tick(0.22, 3400, 0.05), t)
for t in [b(49.0), b(51.85), b(52.25), b(53.9), b(58.6), b(61.4)]:
    fx.add(whoosh(0.8, 300, 5000, 0.6, 0.22), t - 0.1)
fx.add(type_clicks(0.35, 18, 0.09), b(53.15))
for t in [b(55.7), b(56.1), b(56.6), b(57.15)]:
    fx.add(blip(0.13, 1318), t)
fx.add(blip(0.2, 1568), b(57.7)); fx.add(blip(0.16, 2093), b(57.7) + 0.12)

# ======================================================================= V. clímax
LN("Sweeper Beat", 110, 4, 0.55, target=0.12)
LN("Deep Dream Synth", 110, 4, 0.45, fi=1.0, filt=lambda y: sweep_lowpass(y, 400, 12000, 1.2), target=0.11)
fx.add(riser(b(114) - b(111), 0.35), b(111))
fx.add(whoosh(1.8, 200, 6000, 0.6, 0.35), b(112.3))
fx.add(impact(3.0, 1.0), b(114)); fx.add(sub_drop(1.8, 0.7), b(114))
LN("Four Four Beat", 114, 8, 0.78, target=0.13)
LN("Epic Anthem Synth", 114, 8, 0.55, target=0.12)
LN("Thick Gritty Bass", 114, 8, 0.45, target=0.11)
LN("Instant House Topper", 116, 6, 0.30, target=0.09)
for j in range(6):
    fx.add(blip(0.12, 784 * 2 ** (j * 2 / 12)), b(114.5) + j * BEAT)
for k in range(4):
    fx.add(whoosh(0.5, 800, 9000, 0.4, 0.22), b(119.25) + k * BEAT * 3 - 0.15)

# ======================================================================= VI. encerramento
fx.add(impact(4.0, 0.7), b(122))
free("Afloat Pad", b(122) - 0.2, b(133) - b(122) + 0.2, 0.6, fi=0.8, fo=4.0)
free("Longing Piano", b(122.5), b(133) - b(122.5), 0.40, fi=1.5, fo=4.5, filt=lambda y: lowpass(y, 5000, 2))

# ======================================================================= inserções (15/10)
LG0 = TL.seg_start('sc_linguagem'); AS0 = TL.seg_start('sc_assistente2')
# linguagem simples: o groove da elaboração continua; a câmera desce o documento
for u in [0.6, 4.7, 9.0, 12.9]:
    fx.add(whoosh(0.9, 250, 4500, 0.6, 0.20), LG0 + u)
    fx.add(paper(0.14), LG0 + u + 0.2)
for u in [2.1, 5.9, 6.75, 7.6, 10.4]:
    fx.add(blip(0.12, 1046), LG0 + u)

# assistente: arranjo próprio, mais íntimo no começo, que abre quando a resposta chega
def LF(name, at, bars, gain, fi=0.0, fo=0.0, filt=None, target=0.12):
    x = rms_norm(loop(name, BPM), target)
    n = int(round(bars * BAR * SR))
    y = np.tile(x, (int(np.ceil(n / len(x))), 1))[:n]
    if filt is not None:
        y = filt(y)
    mix.add(y, at, gain, fi, fo)
# o pad entra meio segundo antes do corte e o groove da inscrição faz cauda: as camadas se cruzam
LF("Airy Vox Synth", AS0 - 0.5, 14, 0.40, fi=0.9, fo=1.2, target=0.10)
LF("Rocket Fuel Beat 01", AS0, 1, 0.55, fo=0.6 * BAR, target=0.13)
LF("Blueprint Beat 01", AS0, 3, 0.55, fi=0.15, filt=lambda y: sweep_lowpass(y, 500, 9000, 1.5), target=0.12)
LF("Blueprint Beat 01", AS0 + 3 * BAR, 11, 0.60, fo=0.6, target=0.12)
LF("Melodic Silk Bass", AS0, 14, 0.40, fi=0.3, fo=0.8, target=0.11)
LF("Pure Candy Synth Layers", AS0 + 9 * BAR, 5, 0.32, fi=1.5, fo=1.0, target=0.10)
for u in [2.2, 5.9, 7.1, 13.2, 16.5]:
    fx.add(tick(0.22, 3600, 0.05), AS0 + u)
fx.add(whoosh(0.8, 400, 6000, 0.6, 0.24), AS0 + 2.35)
fx.add(type_clicks(2.2, 14, 0.10), AS0 + 13.4)
fx.add(blip(0.16, 1318), AS0 + 7.3); fx.add(blip(0.12, 1760), AS0 + 7.42)
fx.add(riser(1.3, 0.12, 800, 5000), AS0 + 16.6)
fx.add(blip(0.18, 1568), AS0 + 17.9); fx.add(blip(0.14, 2093), AS0 + 18.02)
fx.add(whoosh(0.9, 300, 6000, 0.6, 0.22), AS0 + 25.4)

# ======================================================================= versão simples (15/10)
C0 = TL.seg_start("sc_comissao2"); V0 = TL.seg_start("sc_convocacao2"); D0 = TL.seg_start("sc_diferenciais2")
# comissão → resultado → recurso: groove contínuo, mais calmo que o anterior
LF("Deep Cycles Beat", C0, 15, 0.62, fi=0.3, target=0.13)
LF("Luminosity Synth Layers", C0, 15, 0.40, fi=1.0, target=0.11)
LF("Melodic Silk Bass", C0, 15, 0.44, target=0.11)
LF("Tight House Topper", C0 + 14 * BAR, 1, 0.35, target=0.09)
for i in range(5):
    fx.add(tick(0.10, 2800 + i * 200, 0.04), C0 + 2.3 + i * 0.12)
fx.add(tick(0.22, 3600, 0.05), C0 + 4.35)
for u in [4.8, 11.8, 16.8, 22.425]:
    fx.add(whoosh(0.8, 300, 5000, 0.6, 0.22), C0 + u - 0.1)
# o sorteio: uma confirmação por garantia
for j, u in enumerate([17.7, 19.1, 20.5]):
    fx.add(blip(0.13, 1046 * 2 ** (j * 4 / 12)), C0 + u)
for u in [5.9, 7.8, 9.7]:
    fx.add(whoosh(0.6, 500, 4000, 0.5, 0.12), C0 + u - 0.3)
    fx.add(blip(0.10, 1175), C0 + u + 0.15)
fx.add(blip(0.16, 1175), C0 + 12.8)
# convocação: respiro e retomada
free("Afloat Pad", V0 - 0.3, 9 * BAR + 0.6, 0.45, fi=0.8, fo=0.8)
LF("Blueprint Beat 01", V0, 9, 0.60, fi=0.6, target=0.12)
LF("Mass Appeal Layers 01", V0 + 3 * BAR, 6, 0.40, fi=1.0, target=0.11)
LF("Melodic Silk Bass", V0, 9, 0.42, target=0.11)
for j in range(6):
    fx.add(type_clicks(0.35, 24, 0.06), V0 + 8.6 + j * 0.5)
fx.add(blip(0.18, 1568), V0 + 13.0); fx.add(blip(0.14, 2093), V0 + 13.12)
fx.add(blip(0.18, 1568), V0 + 1.2); fx.add(blip(0.14, 2093), V0 + 1.32)
fx.add(whoosh(0.9, 300, 6000, 0.6, 0.22), V0 + 6.3)
# na prática: três batidas, três ideias
LF("Tight Tech Beat", D0, 8, 0.64, target=0.13)
LF("Spike Riff Synth Layers", D0 + 1 * BAR, 7, 0.38, fi=0.8, target=0.10)
LF("Melodic Silk Bass", D0, 8, 0.44, target=0.11)
LF("Relentless Topper", D0 + 7 * BAR, 1, 0.33, target=0.09)
for j in range(3):
    fx.add(whoosh(0.7, 500, 7000, 0.55, 0.26), D0 + 1.9 + j * (15.0 - 1.9) / 3 - 0.3)

# ======================================================================= mixagem
music = mix.buf
# o corte seco do congelamento: a música para, só a pancada fica
i0, i1 = int(FREEZE * SR), int((FRASE - 0.6) * SR)
music[i0:i1] *= np.linspace(1, 0, i1 - i0, dtype=np.float32)[:, None] ** 8
# compressão lateral leve da música pelos efeitos de impacto (abre espaço)
out = music * 0.85 + fx.buf * 1.0
out = reverb(out, 1.6, 0.12)[: len(out)]
out = master(out)
out = out[: int(TOTAL * SR) + SR]
out.astype(np.float32).tofile("score.f32")
print("trilha:", len(out) / SR, "s, pico", float(np.abs(out).max()))
