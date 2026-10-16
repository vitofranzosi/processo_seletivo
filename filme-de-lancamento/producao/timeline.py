"""A grade do filme. Imagem e som leem os mesmos instantes daqui."""
BPM = 128.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT          # 1,875 s

def b(n):
    """Compasso n (pode ser fracionário) em segundos."""
    return n * BAR

# seções: (nome, início em compassos, fim em compassos)
SECTIONS = [
    ("s1_fragmentacao", 0, 22),      # 0:00 – 0:41.25 (congela em 18, frase em 19)
    ("s2_transformacao", 22, 30),    # 0:41.25 – 0:56.25 (drop em 26)
    ("s3a_edital", 30, 46),          # 0:56.25 – 1:26.25
    ("s3b_inscricao", 46, 62),       # 1:26.25 – 1:56.25
    ("s3c_comissao", 62, 78),        # 1:56.25 – 2:26.25
    ("s3d_convocacao", 78, 94),      # 2:26.25 – 2:56.25
    ("s4_diferenciais", 94, 110),    # 2:56.25 – 3:26.25
    ("s5_climax", 110, 122),         # 3:26.25 – 3:48.75
    ("s6_encerramento", 122, 133),   # 3:48.75 – 4:09.4
]

FREEZE = b(18)          # congelamento
FRASE = b(19)           # "Mas nenhum deveria precisar começar do zero."
DROP = b(26)            # entrada do título
TOTAL = b(133)

def section(name):
    for n, a, z in SECTIONS:
        if n == name:
            return b(a), b(z)
    raise KeyError(name)

# ---------------------------------------------------------------- o filme como lista de trechos (15/10)
# (módulo, instante LOCAL de início em s, duração em compassos). Os módulos do corte original
# (abertura, edital, inscrição, final) usam o tempo original como relógio local; os novos começam em 0.
# A partir da avaliação, o corte original (compassos 62–110) foi substituído por três cenas mais
# curtas, em linguagem simples, para o público geral do Cefor.
PLAYLIST = [
    ("sc_abertura", b(0), 30),
    ("sc_edital", b(30), 10.4),       # composição do Edital (até a Revisão)
    ("sc_gera2", 0.0, 7),             # o sistema escreve o Edital, em linguagem simples (Lei 15.263/2025)
    ("sc_linguagem", 0.0, 8),         # o Edital gerado, em linguagem simples
    ("sc_publica2", 0.0, 8),          # revisado, publicado, aberto a todos → inscrições
    ("sc_inscricao", b(46), 16),
    ("sc_assistente2", 0.0, 14),      # o assistente: pergunta sugerida × pergunta livre à IA
    ("sc_comissao2", 0.0, 11),
    ("sc_convocacao2", 0.0, 9),       # convocação e a planilha para o sistema acadêmico
    ("sc_diferenciais2", 0.0, 8),
    ("sc_final", b(110), 23),
]
ORIGINAIS = {"sc_abertura", "sc_edital", "sc_inscricao", "sc_final"}
FILM_BARS = sum(n for _, _, n in PLAYLIST)
FILM_TOTAL = b(FILM_BARS)

def segments():
    """[(módulo, início no filme em s, fim em s, início local em s)]"""
    out, t = [], 0.0
    for m, l0, n in PLAYLIST:
        out.append((m, t, t + b(n), l0)); t += b(n)
    return out

def seg_start(module):
    return next(t0 for m, t0, _, _ in segments() if m == module)

def S(x, end=False):
    """Compasso do corte ORIGINAL → compasso do filme. Num trecho cortado, vai para o início do
    trecho original seguinte que continua no filme: uma camada da trilha que atravessava o corte
    continua tocando por cima das cenas novas, até ali."""
    orig = [(l0 / BAR, l0 / BAR + (t1 - t0) / BAR, t0 / BAR) for m, t0, t1, l0 in segments() if m in ORIGINAIS]
    for a, z, f in orig:
        if (a < x <= z) if end else (a <= x < z):
            return f + (x - a)
    nxt = [f for a, z, f in orig if a >= x]
    if nxt:
        return min(nxt)
    a, z, f = orig[-1]
    return f + (z - a)

def insert_spans():
    """Compatibilidade: [(início, fim, módulo)] das cenas novas."""
    return [(t0, t1, m) for m, t0, t1, _ in segments() if m not in ORIGINAIS]
