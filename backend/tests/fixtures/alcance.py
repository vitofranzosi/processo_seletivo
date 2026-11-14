"""O Edital da spec 163: três Etapas, e a do meio só para quem se inscreveu em `PPI`.

```text
1  Análise documental   pontuada, eliminatória, nota mínima 60   todas as inscrições
2  Heteroidentificação  decisória, eliminatória                   só PPI
3  Prova didática       pontuada, classificatória                 todas as inscrições
```

Um Perfil com `PPI` e `PCD`, e a ampla na grafia sem Modalidade. O marco é o mínimo da fixture:
sorteio, sem Etapa enumerada e sem corte que governe — a Etapa restrita não pode ser governada nem
medida (FR-6964), e o que se quer ver aqui é a participação.

Função, e não fixture, pela regra de `tests/fixtures/corte.py`: cada módulo declara a sua.
"""

from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import (
    ETAPA_A1,
    ETAPA_A2,
    alocar_em,
    constituir,
    etapas,
    rascunho_com_etapas,
)
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import publish_original
from tests.fixtures.resultado import ETAPA_A3, NOTA_MINIMA

MODALIDADE_PPI = "00000000-0000-4000-8000-000000001631"
MODALIDADE_PCD = "00000000-0000-4000-8000-000000001632"
LINHA_GERAL = "00000000-0000-4000-8000-000000001633"
LINHA_PPI = "00000000-0000-4000-8000-000000001634"
LINHA_PCD = "00000000-0000-4000-8000-000000001635"


def rascunho_com_alcance(seed, *, alcance=("PPI",)):
    """O rascunho do Edital acima. `alcance=None` publica a mesma Etapa para todas."""
    rascunho = rascunho_com_etapas(seed, avaliacoes=1, maxima="100.0000", minima=NOTA_MINIMA)
    analise, prova = etapas(seed, avaliacoes=1, maxima="100.0000", minima=NOTA_MINIMA)
    rascunho["stages"] = [
        {**analise, "order": 1},
        {
            "id": identificador(ETAPA_A3, seed),
            "name": "Heteroidentificação",
            "order": 2,
            "eliminatory": True,
            "classificatory": False,
            "evaluationsPerRegistration": 1,
            "forma": "DECISORIA",
            "rotuloFavoravel": "Confirmada",
            "rotuloDesfavoravel": "Não confirmada",
            "modalityCodes": None if alcance is None else list(alcance),
        },
        {**prova, "order": 3},
    ]
    perfil = rascunho["profiles"][0]
    perfil["competitionModalities"] = [
        {"id": MODALIDADE_PPI, "code": "PPI", "name": "Pretos e pardos", "vacancies": 0},
        {"id": MODALIDADE_PCD, "code": "PCD", "name": "Pessoas com deficiência", "vacancies": 0},
    ]
    perfil["vacancyTable"] = [
        {"id": LINHA_GERAL, "modalityId": None, "immediateVacancies": 1},
        {"id": LINHA_PPI, "modalityId": MODALIDADE_PPI, "immediateVacancies": 1},
        {"id": LINHA_PCD, "modalityId": MODALIDADE_PCD, "immediateVacancies": 1},
    ]
    perfil["immediateVacancies"] = 3
    return rascunho


def montar_com_alcance(
    gestor, api_client, manager_headers, *, seed, codigo, alcance=("PPI",), avaliador="joao"
):
    """Publica, constitui a comissão e aloca o avaliador nas três Etapas."""
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"alcance-163-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        draft=rascunho_com_alcance(seed, alcance=alcance),
    )
    processo = edital.processo
    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), (avaliador, Funcao.MEMBRO)],
        prefixo=f"alcance-{seed}",
    )
    analise = identificador(ETAPA_A1, seed)
    hetero = identificador(ETAPA_A3, seed)
    prova = identificador(ETAPA_A2, seed)
    for etapa in (analise, hetero, prova):
        alocar_em(
            gestor, processo, membros[avaliador], edital, etapa, chave=f"aloc-163-{seed}-{etapa}"
        )
    return {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": analise,
        "analise": analise,
        "hetero": hetero,
        "prova": prova,
        # O Perfil é derivado do `seed`: a inscrição precisa nascer nele, ou o universo da ordem —
        # que filtra pelo Perfil — não a encontra.
        "perfil": identificador(401, seed),
    }
