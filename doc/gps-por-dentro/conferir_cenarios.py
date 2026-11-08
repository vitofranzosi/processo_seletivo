"""Gera estados didáticos pelas funções oficiais; não toca banco nem emite atos.

A saída embutida no HTML evita um motor paralelo no navegador. As asserções fixam o
exemplo pedagógico: se o contrato mudar, a publicação do guia precisa ser revista.
"""


# O checkout local fornece as funções oficiais sem instalar outro motor.
# ruff: noqa: E402

import json
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from processo_seletivo.classificacao.domain import combinacao, desempate, faixa
from processo_seletivo.ocupacao.domain import apuracao
from processo_seletivo.resultados.domain.regra import consequencia
from processo_seletivo.sorteios.domain import chave
from processo_seletivo.shared.canonical import canonical_sha256

ELENCO = [
    {
        "id": "ana",
        "nome": "Ana",
        "sigla": "AN",
        "reserva": True,
        "prova": 90,
        "entrevista": 60,
        "nascimento": "1992-03-01",
    },
    {
        "id": "bruno",
        "nome": "Bruno",
        "sigla": "BR",
        "reserva": False,
        "prova": 85,
        "entrevista": 90,
        "nascimento": "1986-06-20",
    },
    {
        "id": "carla",
        "nome": "Carla",
        "sigla": "CA",
        "reserva": True,
        "prova": 80,
        "entrevista": 92,
        "nascimento": "1990-02-10",
    },
    {
        "id": "davi",
        "nome": "Davi",
        "sigla": "DA",
        "reserva": False,
        "prova": 80,
        "entrevista": 100,
        "nascimento": "1988-07-12",
    },
    {
        "id": "elisa",
        "nome": "Elisa",
        "sigla": "EL",
        "reserva": True,
        "prova": 65,
        "entrevista": 90,
        "nascimento": "1994-01-15",
    },
    {
        "id": "fabio",
        "nome": "Fábio",
        "sigla": "FA",
        "reserva": False,
        "prova": 60,
        "entrevista": None,
        "nascimento": "1989-08-14",
    },
    {
        "id": "gabi",
        "nome": "Gabi",
        "sigla": "GA",
        "reserva": False,
        "prova": 55,
        "entrevista": None,
        "nascimento": "1996-09-11",
    },
    {
        "id": "hugo",
        "nome": "Hugo",
        "sigla": "HU",
        "reserva": False,
        "prova": 70,
        "entrevista": None,
        "nascimento": "1991-04-07",
    },
]
ETAPAS = {
    "prova": {
        "forma": "PONTUADA",
        "weight": 3,
        "eliminatory": True,
        "classificatory": True,
        "minimumScore": 60,
        "maximumScore": 100,
    },
    "entrevista": {
        "forma": "PONTUADA",
        "weight": 1,
        "eliminatory": True,
        "classificatory": True,
        "minimumScore": 50,
        "maximumScore": 100,
    },
}
CRITERIOS = [
    {
        "order": 1,
        "type": desempate.MENOR_VALOR_DE_FATO,
        "parameters": {"factId": "nascimento"},
        "whenMissing": desempate.ULTIMO_NO_CRITERIO,
    }
]
MARCO = {
    "stages": ["prova"],
    "operation": "MEDIA_PONDERADA",
    "normalization": "NENHUMA",
    "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
}


class Conclusao:
    def __init__(self, valor):
        self.pontuacao = Decimal(str(valor))


def ordem(lista, *, corrigida=False, final=False):
    participantes = []
    for p in lista:
        if consequencia(ETAPAS["prova"], Conclusao(p["prova"]))[0] != "HABILITADA":
            continue
        notas = {
            "prova": Decimal(88 if corrigida and p["id"] == "carla" else p["prova"])
        }
        marco = {**MARCO}
        if final:
            if p["entrevista"] is None:
                continue
            assert (
                consequencia(ETAPAS["entrevista"], Conclusao(p["entrevista"]))[0]
                == "HABILITADA"
            )
            notas["entrevista"] = Decimal(p["entrevista"])
            marco["stages"] = ["prova", "entrevista"]
        participantes.append(
            {
                "id": p["id"],
                "pontuacao": combinacao.combinar(marco, ETAPAS, notas),
                "pontuacoes": notas,
                "fatos": {"nascimento": date.fromisoformat(p["nascimento"])},
            }
        )
    resultado = desempate.ordenar(participantes, CRITERIOS)
    return [
        {
            "id": p["id"],
            "posicao": p["posicao"],
            "nota": str(p["pontuacao"]),
            "desempate": p["separado_por"] is not None,
        }
        for p in resultado
    ]


def ids(itens):
    return [p["id"] for p in itens]


def cortar(itens, alvo, excedente=0, regra=faixa.EMPATE_ADMITE_EXCEDENTE):
    return faixa.calcular(
        [(p["id"], p["posicao"]) for p in itens],
        alvo=alvo,
        excedente=excedente,
        desfecho=regra,
    )[0]


def gerar():
    reserva = [p for p in ELENCO if p["reserva"]]
    inicial, corrigida = ordem(ELENCO), ordem(ELENCO, corrigida=True)
    reservada = ordem(reserva, corrigida=True)
    ac, pcd = cortar(corrigida, 4), cortar(reservada, 4)
    avancam = list(dict.fromkeys(ac + pcd))
    assert ids(inicial) == ["ana", "bruno", "davi", "carla", "hugo", "elisa", "fabio"]
    assert ids(corrigida) == ["ana", "carla", "bruno", "davi", "hugo", "elisa", "fabio"]
    assert set(avancam) == {"ana", "bruno", "carla", "davi", "elisa"}
    final = ordem([p for p in ELENCO if p["id"] in avancam], corrigida=True, final=True)
    final_pcd = [
        dict(p, posicao=i + 1)
        for i, p in enumerate(p for p in final if p["id"] in ids(reservada))
    ]
    assert ids(final) == ["carla", "bruno", "davi", "ana", "elisa"]
    assert [p["nota"] for p in final] == ["89.00", "86.25", "85.00", "82.50", "71.25"]
    faixa_ac, faixa_pcd = cortar(final, 2, 3), cortar(final_pcd, 1, 3)
    titulares_ac = apuracao.titulares_iniciais(
        progrediram_em_ordem=faixa_ac, efetivas=2
    )
    titulares_pcd = apuracao.titulares_iniciais(
        progrediram_em_ordem=faixa_pcd, efetivas=1, ocupantes_da_ampla=titulares_ac
    )
    assert titulares_ac == ["carla", "bruno"] and titulares_pcd == ["ana"]
    kwargs = {"publicadas": 2, "progrediram_em_ordem": faixa_ac, "habilitadas": avancam}
    ap0 = apuracao.apurar(**kwargs)
    ap1 = apuracao.apurar(**kwargs, efeitos_lidos=[("EXCLUSAO", "bruno")])
    ap2 = apuracao.apurar(
        **kwargs, efeitos_lidos=[("EXCLUSAO", "bruno"), ("INCLUSAO", "davi")]
    )
    assert ap0 == (2, 2, 2) and ap1 == (2, 2, 1) and ap2 == (2, 2, 2)
    assert consequencia(ETAPAS["prova"], Conclusao(60))[0] == "HABILITADA"
    assert consequencia(ETAPAS["prova"], Conclusao(55))[0] == "ELIMINADA"
    assert combinacao.combinar(MARCO, ETAPAS, {}) is combinacao.SEM_PONTUACAO
    empate = [("ana", 1), ("bruno", 2), ("carla", 2), ("davi", 4)]
    assert faixa.calcular(empate, alvo=2, desfecho="ADMITS_SURPLUS")[0] == [
        "ana",
        "bruno",
        "carla",
    ]
    try:
        faixa.calcular(empate, alvo=2, desfecho="STRICT")
    except faixa.EmpateAtravessaOCorte:
        pass
    else:
        raise AssertionError("A emissão deveria ser recusada no empate estrito")
    relacao = {
        "demo": "gps-por-dentro",
        "publicNumbers": list(range(1, 9)),
        "candidatos": [p["id"] for p in ELENCO],
    }
    resumo = canonical_sha256(relacao)
    entradas = {
        "relation_hash": resumo,
        "draw_scope_id": "guia-ficticio:ampla",
        "seed": "DEMONSTRACAO-FIXA-2026",
        "public_numbers": list(range(1, 9)),
    }
    sorteio = chave.ordem(**entradas)
    assert sorteio == chave.ordem(**entradas) and sorted(sorteio) == list(range(1, 9))
    return {
        "base": "da566ff2",
        "elenco": ELENCO,
        "inicial": inicial,
        "corrigida": corrigida,
        "reservada": reservada,
        "corteAC": ac,
        "cortePCD": pcd,
        "avancam": avancam,
        "final": final,
        "finalPCD": final_pcd,
        "titularesAC": titulares_ac,
        "titularesPCD": titulares_pcd,
        "apuracoes": [ap0, ap1, ap2],
        "sorteio": [
            {"id": ELENCO[n - 1]["id"], "numero": n, "posicao": i + 1}
            for i, n in enumerate(sorteio)
        ],
        "sorteioEntradas": entradas,
        "empate": {
            "posicoes": empate,
            "admite": ["ana", "bruno", "carla"],
            "estrito": "EMISSAO_RECUSADA",
        },
    }


if __name__ == "__main__":
    resultado = json.loads(json.dumps(gerar(), ensure_ascii=False))
    saida = json.dumps(resultado, ensure_ascii=False, indent=2)
    pasta = Path(__file__).resolve().parent
    if "--conferir" in sys.argv:
        assert json.loads((pasta / "cenarios.json").read_text()) == resultado, (
            "Regere os estados: o domínio mudou."
        )
        html = (pasta / "index.html").read_text()
        embutido = re.search(
            r'<script type="application/json" id="dados">(.*?)</script>', html, re.S
        )
        assert embutido and json.loads(embutido[1]) == resultado, (
            "O HTML não contém os estados conferidos."
        )
        print(
            "Conferidos: mínimo/ausência, duas ordens, desempate, corte por lista, união de 5, média, reserva, 3 apurações, empate estrito/excedente e sorteio. HTML = cenarios.json = domínio."
        )
    else:
        (pasta / "cenarios.json").write_text(saida + "\n")
        arquivo = pasta / "index.html"
        if arquivo.exists():
            html = arquivo.read_text()
            html = re.sub(
                r'(<script type="application/json" id="dados">).*?(</script>)',
                lambda m: m[1] + saida + m[2],
                html,
                flags=re.S,
            )
            arquivo.write_text(html)
        print(
            "Estados gerados pelas funções oficiais; nenhuma conexão ou operação real."
        )
