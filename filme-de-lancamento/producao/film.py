"""O filme inteiro como uma função do tempo: as inserções tocam no lugar delas, e o filme original
toca deslocado pelo que já foi inserido antes."""
import importlib
from timeline import SECTIONS, b, FILM_TOTAL

MODS = {"s1_fragmentacao": "sc_abertura", "s2_transformacao": "sc_abertura", "s3a_edital": "sc_edital",
        "s3b_inscricao": "sc_inscricao", "s3c_comissao": "sc_comissao", "s3d_convocacao": "sc_convocacao",
        "s4_diferenciais": "sc_diferenciais", "s5_climax": "sc_final", "s6_encerramento": "sc_final"}
_mods = {}
def mod(name):
    if name not in _mods:
        _mods[name] = importlib.import_module(name)
    return _mods[name]

from timeline import segments
SEGS = segments()

def locate(t):
    """(módulo, tempo local, rótulo) para o instante t do filme."""
    for m, t0, t1, l0 in SEGS:
        if t0 <= t < t1:
            return m, l0 + (t - t0), m
    m, t0, t1, l0 = SEGS[-1]
    return m, l0 + (t - t0), m

def draw(c, t):
    m, tl, _ = locate(t)
    mod(m).draw(c, tl)
