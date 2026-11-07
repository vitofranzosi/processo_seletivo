"""O elenco fictício do Edital 900/2026 e as notas de cada Etapa — a fonte única dos números do estudo.

Todos os nomes, datas e notas são inventados para a demonstração. O script de reprodução
(`reproduzir.py`) e a conferência (`conferir.py`) leem daqui; o guia e o estudo citam os
mesmos números.

Legenda das Etapas:
    REQ  Análise dos requisitos  decisória, eliminatória (Deferido / Indeferido)
    CUR  Análise do currículo    0–100, só classificatória, peso 1
    PRO  Prova escrita           0–100, mínima 60, eliminatória e classificatória, peso 3
    ENT  Entrevista              0–100, mínima 60, eliminatória e classificatória, peso 2

`None` numa nota = a pessoa não chega àquela Etapa (eliminada antes, ou fora do corte).
`"AUSENTE"` = ausência registrada pela presidência (Ocorrência), que elimina.
"""

from datetime import date

AC, PCD, PPI = "AC", "PCD", "PPI"

#: código, nome, modalidade, nascimento, REQ, CUR, PRO, ENT
ELENCO = [
    ("C01", "Helena Prado", AC, date(1988, 3, 14), "D", 90, 92, 95),
    ("C02", "Bruno Taveira", AC, date(1990, 7, 2), "D", 80, 85, 88),
    ("C03", "Lívia Montes", AC, date(1985, 11, 23), "D", 95, 55, None),
    ("C04", "Otávio Rangel", AC, date(1993, 1, 9), "D", 70, "AUSENTE", None),
    ("C05", "Marina Couto", AC, date(1991, 5, 30), "I", None, None, None),
    ("C06", "Rafael Quintão", AC, date(1987, 9, 18), "D", 78, 76, 80),
    ("C07", "Sofia Arruda", AC, date(1994, 2, 27), "D", 66, 80, 74),
    ("C08", "Caio Bettencourt", AC, date(1980, 6, 5), "D", 72, 74, 80),
    ("C09", "Diana Ferraz", AC, date(1992, 12, 1), "D", 72, 74, 82),
    ("C10", "Gustavo Lemos", AC, date(1989, 8, 21), "D", 60, 68, 70),
    ("C11", "Patrícia Nogueira", AC, date(1986, 4, 11), "D", 68, 70, None),
    ("C12", "Renato Sales", AC, date(1995, 10, 3), "D", 50, 62, None),
    ("C13", "Elisa Viana", PCD, date(1984, 1, 19), "D", 64, 72, 76),
    ("C14", "Fábio Guerra", PCD, date(1990, 3, 8), "D", 75, 52, None),
    ("C15", "Iara Batista", PCD, date(1997, 7, 25), "D", 58, 66, 55),
    ("C16", "João Benedito", PPI, date(1983, 10, 30), "D", 85, 88, 84),
    ("C17", "Kátia Moura", PPI, date(1996, 2, 14), "D", 62, 70, 72),
    ("C18", "Luan Tavares", PPI, date(1998, 9, 6), "D", 55, 64, "AUSENTE"),
]

#: O recurso contra a classificação preliminar para a entrevista: a banca reconhece erro de soma
#: na Prova escrita de C10, e o julgamento fixa a correção (68 → 76).
RECURSO_DA_PROVA = {"codigo": "C10", "de": 68, "para": 76}

#: Motivo de cada eliminação fora da nota mínima, como a presidência o registra.
MOTIVOS = {
    "C04": "Ausência na Prova escrita, conforme lista de presença.",
    "C05": "Certidão de conclusão sem data de colação de grau: requisito não comprovado.",
    "C18": "Ausência na Entrevista, conforme registro da sala virtual.",
}
