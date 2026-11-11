"""Cenário 5: um barema, configurado uma vez, para as inscrições de três Perfis (146, T027).

O barema mora na Etapa, e a Etapa vale para todos os Perfis (D-001): a mesma ficha pontua a
inscrição de cada um, sem cópia nem modelo. O reaproveitamento do Edital com o barema — a outra
metade de SC-1625 — está em `integration/editais/test_reaproveitamento.py`, desde o incremento A.
"""

import copy
from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.barema import com_barema, concluir_com_ficha, ficha
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import identidade_do_marco, identificador, marco_minimo
from tests.fixtures.mesa import distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.usefixtures("raiz_de_arquivos"),
]

SEED = 151


def _tres_perfis(rascunho):
    base = rascunho["profiles"][0]
    for indice, nome in ((2, "Orientador de TFC — Licenciaturas"), (3, "Orientador — Pedagogia")):
        perfil = copy.deepcopy(base)
        perfil["id"] = identificador(1480 + indice, SEED)
        perfil["code"] = f"P{indice}"
        perfil["name"] = nome
        perfil["classificationMilestones"] = [
            marco_minimo(identidade_do_marco(perfil["id"]), codigo=f"M{indice}")
        ]
        rascunho["profiles"].append(perfil)
    return rascunho


def test_a_mesma_ficha_pontua_os_tres_perfis(gestor, api_client, manager_headers):
    rascunho = _tres_perfis(
        com_barema(
            rascunho_com_etapas(SEED, avaliacoes=1, maxima="100.0000", minima="60.0000"),
            seed=SEED,
        )
    )
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{SEED:04d}"},
        {
            "institutionalCode": "PS-2026-T151",
            "title": "Processo T151",
            "firstEdital": {"number": "T151", "year": 2026, "title": "Edital T151"},
        },
        draft=rascunho,
    )
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="compartilhado",
    )
    etapa = identificador(ETAPA_A1, SEED)
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa)
    cenario = {"edital": edital, "processo": edital.processo, "membros": membros, "etapa": etapa}
    inscricoes = [
        inscrever(edital, 1, primeiro=5100 + indice, perfil=perfil["id"])[0]
        for indice, perfil in enumerate(rascunho["profiles"])
    ]
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="compartilhado")

    for inscricao in inscricoes:
        concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    concluidas = Avaliacao.objects.filter(etapa_id=etapa, estado=Avaliacao.Estado.CONCLUIDA)
    assert {str(i.profile_id) for i in inscricoes} == {p["id"] for p in rascunho["profiles"]}
    assert concluidas.count() == 3
    assert {a.pontuacao for a in concluidas} == {Decimal("70.0000")}
    # O mesmo barema, lido do mesmo lugar: os critérios citados são os mesmos nas três.
    assert len({tuple(linha["criterionId"] for linha in a.criterios) for a in concluidas}) == 1
