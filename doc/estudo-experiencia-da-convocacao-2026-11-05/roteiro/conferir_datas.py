"""Confere todo dia da semana escrito nas maquetes contra a data ao lado dele.

A versão 1 das maquetes dizia "segunda-feira, 10/11/2026" e "quarta-feira, 12/11/2026": os dias
foram digitados à mão, e 10/11/2026 é terça-feira. Na implementação o dia sai da data, no fuso da
instalação, por uma função só; aqui, que é texto, a conferência é esta.

Uso: python3 conferir_datas.py <pasta-das-maquetes>
"""

import datetime
import re
import sys
from pathlib import Path

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
DATA = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
DIA = re.compile("|".join(DIAS))
# A data que um dia da semana qualifica está a poucos caracteres dele, antes ou depois.
ALCANCE = 90

erros = conferidos = 0
for arquivo in sorted(Path(sys.argv[1]).glob("*.*")):
    if arquivo.suffix not in {".html", ".txt"}:
        continue
    texto = re.sub(r"<[^>]+>", " ", arquivo.read_text())
    texto = re.sub(r"\s+", " ", texto)
    for achado in DIA.finditer(texto):
        janela_depois = texto[achado.end() : achado.end() + ALCANCE]
        janela_antes = texto[max(0, achado.start() - ALCANCE) : achado.start()]
        # A data mais próxima, de qualquer lado; no empate, a anterior ("10/11/2026 … terça-feira").
        candidatas = [(m.start(), m) for m in DATA.finditer(janela_depois)][:1]
        candidatas += [(len(janela_antes) - m.end(), m) for m in DATA.finditer(janela_antes)][-1:]
        alvo = min(candidatas, key=lambda par: (par[0], par[1].string is janela_depois))[1] if candidatas else None
        if alvo is None:
            print(f"{arquivo.name}: '{achado.group()}' sem data por perto")
            erros += 1
            continue
        d, m, a = map(int, alvo.groups())
        certo = DIAS[datetime.date(a, m, d).weekday()]
        conferidos += 1
        if certo != achado.group():
            erros += 1
            print(f"{arquivo.name}: {alvo.group()} é {certo}, e o texto diz {achado.group()}")
print(f"{conferidos} dias da semana conferidos, {erros} erro(s).")
sys.exit(1 if erros else 0)
