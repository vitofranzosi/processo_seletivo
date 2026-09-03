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
    etapas,
    publicar_processo_com_etapas,
    rascunho_com_etapas,
)
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import publish_original

# A terceira Etapa não existe nos cenários da 011 e da 012, e ela é a única forma de demonstrar a
# transitividade: eliminada na primeira, com a segunda ainda não consolidada, a inscrição não pode
# reaparecer na terceira. Fica aqui, e não em `comissao.py`, para não mexer no cenário
# compartilhado da 011 e da 012.
ETAPA_A3 = 412

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


def montar_tres_etapas(gestor, api_client, manager_headers, *, seed, codigo, avaliador="joao"):
    """Um Edital com **três** Etapas em ordem — o cenário da transitividade.

    A terceira é acrescentada ao rascunho que `rascunho_com_etapas` produz, em vez de a fixture
    compartilhada ganhar uma Etapa que a 011 e a 012 não pediram.
    """
    rascunho = rascunho_com_etapas(seed, avaliacoes=1, maxima="100.0000", minima=NOTA_MINIMA)
    rascunho["stages"] = [
        *etapas(seed, avaliacoes=1, maxima="100.0000", minima=NOTA_MINIMA),
        {
            "id": identificador(ETAPA_A3, seed),
            "name": "Entrevista",
            "order": 3,
            "eliminatory": False,
            "classificatory": True,
        },
    ]
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{codigo}",
            "title": f"Processo {codigo}",
            "firstEdital": {"number": codigo, "year": 2026, "title": f"Edital {codigo}"},
        },
        draft=rascunho,
    )
    processo = edital.processo
    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), (avaliador, Funcao.MEMBRO)],
        prefixo=f"tres-{seed}",
    )
    etapas_do_edital = [
        identificador(ETAPA_A1, seed),
        identificador(ETAPA_A2, seed),
        identificador(ETAPA_A3, seed),
    ]
    for etapa in etapas_do_edital:
        alocar_em(
            gestor, processo, membros[avaliador], edital, etapa, chave=f"aloc3-{seed}-{etapa}"
        )
    return {
        "edital": edital,
        "processo": processo,
        "membros": membros,
        "etapa": etapas_do_edital[0],
        "primeira": etapas_do_edital[0],
        "segunda": etapas_do_edital[1],
        "terceira": etapas_do_edital[2],
    }
