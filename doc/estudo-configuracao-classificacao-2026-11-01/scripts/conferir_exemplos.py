"""Confere a dupla da maquete com funções oficiais, sem acesso ao banco."""

import json
from pathlib import Path
from processo_seletivo.classificacao.domain.combinacao import combinar
from processo_seletivo.classificacao.domain.desempate import ordenar_com_trajetoria

marco = {
    "stages": ["objetiva", "titulos", "documental", "didatica"],
    "operation": "MEDIA_PONDERADA",
    "normalization": "NENHUMA",
    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
}
criterio = {
    "order": 1,
    "type": "MAIOR_PONTUACAO_NA_ETAPA",
    "parameters": {"stageId": "didatica"},
    "whenMissing": "ULTIMO_NO_CRITERIO",
}
notas = {
    "Ana sintética": {"objetiva": 8, "titulos": 6, "didatica": 9},
    "Bruno sintético": {"objetiva": 8, "titulos": 9, "didatica": 8},
}
saida = []
for peso in (1, 2):
    etapas = {
        nome: {"id": nome, "forma": "PONTUADA", "weight": p}
        for nome, p in [("objetiva", 2), ("titulos", peso), ("didatica", 3)]
    }
    etapas["documental"] = {"id": "documental", "forma": "DECISORIA"}
    participantes = [
        {
            "nome": nome,
            "pontuacao": combinar(marco, etapas, valores),
            "pontuacoes": valores,
            "fatos": {},
        }
        for nome, valores in notas.items()
    ]
    ordem = ordenar_com_trajetoria(participantes, [criterio])
    saida.append(
        {
            "peso_titulos": peso,
            "ordem": [
                {
                    "nome": p["nome"],
                    "pontuacao": str(p["pontuacao"]),
                    "posicao": p["posicao"],
                }
                for p in ordem
            ],
        }
    )
assert saida[0]["ordem"][0]["nome"] == "Ana sintética"
assert saida[1]["ordem"][0]["nome"] == "Bruno sintético"
assert [p["pontuacao"] for p in saida[0]["ordem"]] == ["8.17", "8.17"]
assert [p["pontuacao"] for p in saida[1]["ordem"]] == ["8.29", "7.86"]
Path(__file__).resolve().parent.parent.joinpath("exemplos-oficiais.json").write_text(
    json.dumps(saida, ensure_ascii=False, indent=2)
)
print("Dois pesos, duas pontuações e ordem do par conferidos pelo domínio oficial.")
