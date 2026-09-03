"""O cenário da 013: uma Etapa de leitura única, eliminatória, com nota mínima publicada.

Separado de `mesa.py` porque a 012 monta o cenário oposto — **duas** avaliações por inscrição, que
é justamente o que a V1 da 013 se recusa a consolidar. Repetir a montagem em cada arquivo faria os
dois divergirem, e o valor de `avaliacoes` é a diferença que importa.

Duas Etapas em ordem, porque a progressão só existe a partir da segunda, e as duas primeiras regras
de D-003 não são demonstráveis com uma Etapa só.
"""

from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import (
    ETAPA_A1,
    ETAPA_A2,
    alocar_em,
    constituir,
    publicar_processo_com_etapas,
)
from tests.fixtures.edital import identificador

NOTA_MINIMA = "60.0000"


def montar_etapa_de_leitura_unica(
    gestor, api_client, manager_headers, *, seed, codigo, avaliadores=("joao",), avaliacoes=1
):
    """Edital publicado com Etapa de leitura única, comissão constituída e banca alocada.

    `avaliacoes` fica parametrizável porque um cenário precisa do contrário: o Edital de leitura
    múltipla, que a V1 não consolida e cuja Etapa seguinte **não pode** ficar travada por isso.
    """
    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        seed=seed,
        avaliacoes=avaliacoes,
        maxima="100.0000",
        minima=NOTA_MINIMA,
    )
    processo = edital.processo
    pessoas = [("maria", Funcao.PRESIDENTE)] + [(nome, Funcao.MEMBRO) for nome in avaliadores]
    membros = constituir(gestor, processo, pessoas, prefixo=f"resultado-{seed}")
    primeira = identificador(ETAPA_A1, seed)
    segunda = identificador(ETAPA_A2, seed)
    for nome in avaliadores:
        for etapa in (primeira, segunda):
            alocar_em(
                gestor, processo, membros[nome], edital, etapa, chave=f"aloc-{seed}-{nome}-{etapa}"
            )
    return {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": primeira,
        "primeira": primeira,
        "segunda": segunda,
    }
