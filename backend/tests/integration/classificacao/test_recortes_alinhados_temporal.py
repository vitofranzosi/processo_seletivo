"""A Retificação do apontamento da ampla não reabilita nem condena em silêncio (122, US5).

A matriz é a de `research.md`, R-11. T1 a T3 moram aqui, com Retificações reais; T4, T5 e T7 são
propriedades da origem do registro, e moram em `tests/unit/editais/test_papel_do_recorte.py`; T6 é
recusa do comando, em `tests/integration/sorteios/test_recorte_excedente_recusado.py`.

A versão vigente decide o que é operacional; a versão que o registro cita explica de onde ele veio
(FR-3911). Um ato produzido para outro universo nunca volta a valer por obra da Retificação: ele
aparece obsoleto, com a causa `papel_do_recorte`, e o recorte segue por relação, sorteio e ato novos
(FR-3912, D-004).
"""

import pytest

from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.editais.domain.recortes import CODIGO_DA_RECUSA
from processo_seletivo.interface import supervisao
from processo_seletivo.interface.conducao_do_marco import resumo_dos_marcos
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from tests.conftest import ator_institucional
from tests.fixtures.recorte_excedente import (
    LISTA_AC,
    LISTA_OUTRA,
    certame_com_ac,
    divulgar,
    retificar_o_apontamento,
)
from tests.fixtures.sorteio import presidente

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _resumo(certame):
    conteudo = effective_version(edital_id=certame["edital"].id).content
    return resumo_dos_marcos(certame["edital"], conteudo)[str(certame["marco"])]


def _causas(certame, lista):
    estado = estado_do_marco(
        edital=certame["edital"], marco_id=str(certame["marco"]), lista_id=lista
    )
    return estado["obsoleto"], [d["tipo"] for d in estado["divergencias"]]


def _sinais_de(certame, lista_nome):
    ator = ator_institucional("paula.publicadora", "resultado:publicar")
    return [
        sinal
        for sinal in supervisao.sinais(certame["processo"], ator)
        if sinal.edital.id == certame["edital"].id and lista_nome in sinal.alvo
    ]


def test_t1_apontar_a_modalidade_operacional_a_torna_acervo(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, apontada=False, prefixo="t1"
    )
    feita = divulgar(certame, LISTA_AC, chave="t1-divulgar-ac")
    assert _resumo(certame)["recortes"] == 4

    retificar_o_apontamento(api_client, certame["edital"], LISTA_AC, suffix="t1")

    assert _resumo(certame)["recortes"] == 3
    assert _sinais_de(certame, "Ampla Concorrência") == []
    with pytest.raises(DomainError) as erro:
        divulgar(certame, LISTA_AC, chave="t1-divulgar-ac-de-novo")
    assert erro.value.code == CODIGO_DA_RECUSA
    feita.refresh_from_db()
    assert not feita.sucessoras.exists()


def test_t2_retirar_o_apontamento_nao_reabilita_o_ato_nascido_excedente(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="t2"
    )

    retificar_o_apontamento(api_client, certame["edital"], None, suffix="t2")

    assert _resumo(certame)["recortes"] == 4
    obsoleto, causas = _causas(certame, LISTA_AC)
    assert obsoleto
    assert "papel_do_recorte" in causas
    # A divulgação do ato antigo é recusada — pela obsolescência, e não pela recusa do excedente.
    with pytest.raises(DomainError) as erro:
        divulgar(certame, LISTA_AC, chave="t2-divulgar-ac")
    assert erro.value.code != CODIGO_DA_RECUSA
    assert not PublicacaoResultado.objects.filter(
        edital=certame["edital"], lista_id=LISTA_AC
    ).exists()
    # O caminho que segue é a sucessão: relação nova, com motivo, aceita.
    resposta = publicar_relacao(
        actor=presidente(),
        processo_id=certame["edital"].processo_id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=LISTA_AC,
        idempotency_key="t2-relacao-nova",
        correlation_id="teste-122",
        motivo="A Modalidade voltou a ter recorte próprio pela Retificação.",
    )
    assert resposta["relacao"] != certame["relacoes"][LISTA_AC]


def test_t3_trocar_o_apontamento_faz_as_duas_coisas_ao_mesmo_tempo(
    gestor, api_client, manager_headers, process_payload
):
    """AC volta à operação, obsoleta (como T2); a outra reserva vira acervo tornado (como T1)."""
    certame = certame_com_ac(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        acervo=True,
        com_outra=True,
        prefixo="t3",
    )
    assert _resumo(certame)["recortes"] == 4

    retificar_o_apontamento(api_client, certame["edital"], LISTA_OUTRA, suffix="t3")

    obsoleto, causas = _causas(certame, LISTA_AC)
    assert obsoleto and "papel_do_recorte" in causas
    with pytest.raises(DomainError) as erro:
        divulgar(certame, LISTA_OUTRA, chave="t3-divulgar-outra")
    assert erro.value.code == CODIGO_DA_RECUSA
    assert _resumo(certame)["recortes"] == 4
    assert _sinais_de(certame, "Outra reserva") == []


def test_a_ampla_nao_muda_de_papel_e_continua_valendo(
    gestor, api_client, manager_headers, process_payload
):
    """A Retificação do apontamento não condena o ato da ampla, que nunca mudou de papel."""
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="t-amp"
    )

    retificar_o_apontamento(api_client, certame["edital"], None, suffix="t-amp")

    _, causas = _causas(certame, None)
    assert "papel_do_recorte" not in causas
