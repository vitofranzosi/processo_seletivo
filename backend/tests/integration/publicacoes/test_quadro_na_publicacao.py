"""O quadro de vagas no conteúdo publicado (025, US2).

O que a publicação promete: o quadro viaja **no conteúdo**, legível por máquina e com identidade
por linha — e não como anexo binário. Publicado como binário, ele ficaria assim para sempre, porque
publicação é ato imutável: não seria migração adiada, e sim bifurcação permanente do acervo entre
Editais com quadro legível e Editais sem (D-001).
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_sha256
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MODALIDADE = {
    "PCD": "00000000-0000-0000-0000-0000002501cd",
    "PPI": "00000000-0000-0000-0000-0000002501p1".replace("p", "b"),
    "Q": "00000000-0000-0000-0000-0000002501aa",
}
LINHA = {
    "GERAL": "00000000-0000-0000-0000-000000252001",
    "PCD": "00000000-0000-0000-0000-000000252002",
    "PPI": "00000000-0000-0000-0000-000000252003",
    "Q": "00000000-0000-0000-0000-000000252004",
}


def _modalidade(identificador, code, name):
    return {"id": identificador, "code": code, "name": name}


def rascunho_com_quadro(*, total=80, linhas=None, modalidades=None):
    """O quadro do `57/2026`, na forma que o rascunho aceita: `AC 56`, `PcD 4`, `PPI 20`."""
    rascunho = complete_draft()
    perfil = rascunho["profiles"][0]
    perfil["immediateVacancies"] = total
    perfil["competitionModalities"] = (
        [
            _modalidade(MODALIDADE["PCD"], "PCD", "Pessoa com deficiência"),
            _modalidade(MODALIDADE["PPI"], "PPI", "Pretos, pardos e indígenas"),
        ]
        if modalidades is None
        else modalidades
    )
    perfil["vacancyTable"] = (
        [
            {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
            {"id": LINHA["PCD"], "modalityId": MODALIDADE["PCD"], "immediateVacancies": 4},
            {"id": LINHA["PPI"], "modalityId": MODALIDADE["PPI"], "immediateVacancies": 20},
        ]
        if linhas is None
        else linhas
    )
    return rascunho


def conteudo_publicado(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content


# --- T043/T050 · a coleção sai no dicionário do Perfil (FR-164) ------------------------------


def test_o_quadro_sai_no_conteudo_publicado_com_identidade_por_linha(
    api_client, manager_headers, process_payload
):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_quadro()
    )

    perfil = conteudo_publicado(edital)["profiles"][0]
    assert perfil["vacancyTable"] == [
        {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
        {"id": LINHA["PCD"], "modalityId": MODALIDADE["PCD"], "immediateVacancies": 4},
        {"id": LINHA["PPI"], "modalityId": MODALIDADE["PPI"], "immediateVacancies": 20},
    ]
    assert conteudo_publicado(edital)["schemaVersion"] == SCHEMA_VERSION


def test_a_ordem_publicada_e_a_declarada_e_nao_e_alfabetizada(
    api_client, manager_headers, process_payload
):
    """D-009: a ordem é declarada e preservada, e não recalculada nem alfabetizada."""
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_com_quadro(
            linhas=[
                {"id": LINHA["PPI"], "modalityId": MODALIDADE["PPI"], "immediateVacancies": 20},
                {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
                {"id": LINHA["PCD"], "modalityId": MODALIDADE["PCD"], "immediateVacancies": 4},
            ]
        ),
    )

    perfil = conteudo_publicado(edital)["profiles"][0]
    assert [linha["id"] for linha in perfil["vacancyTable"]] == [
        LINHA["PPI"],
        LINHA["GERAL"],
        LINHA["PCD"],
    ]
    # A ordem **não** é publicada como campo: publicá-la faria o quadro afirmar uma precedência
    # entre listas que é de outra feature (D-009, R-003).
    assert all("order" not in linha for linha in perfil["vacancyTable"])


# --- T044 · o resumo canônico inclui o quadro (FR-168) ---------------------------------------


def test_dois_conteudos_identicos_produzem_o_mesmo_resumo_canonico(
    api_client, manager_headers, process_payload
):
    """A determinização é do emissor, e não do resumo: `sort_keys` ordena chaves, não listas."""
    conteudo = conteudo_publicado(
        publish_original(api_client, manager_headers, process_payload, draft=rascunho_com_quadro())
    )

    assert canonical_sha256(conteudo) == canonical_sha256({**conteudo})
    trocado = {
        **conteudo,
        "profiles": [
            {
                **conteudo["profiles"][0],
                "vacancyTable": list(reversed(conteudo["profiles"][0]["vacancyTable"])),
            }
        ],
    }
    assert canonical_sha256(trocado) != canonical_sha256(conteudo), (
        "o quadro entra no resumo: mudar a ordem das linhas muda o resumo"
    )


# --- T046 · o que percentual nenhum gera sai como entrou (SC-051) ----------------------------


def test_o_quadro_que_percentual_nenhum_gera_e_publicado_identico(
    api_client, manager_headers, process_payload
):
    """`Q 1` e `PCD 1` saem de arredondamento sobre censo, e não são geráveis por percentual.

    É a prova de que percentual não substitui quadro publicado e não o gera (FR-157, SC-051).
    """
    modalidades = [
        _modalidade(MODALIDADE["PPI"], "PPI", "Pretos, pardos e indígenas"),
        _modalidade(MODALIDADE["Q"], "Q", "Quilombola"),
        _modalidade(MODALIDADE["PCD"], "PCD", "Pessoa com deficiência"),
    ]
    linhas = [
        {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 18},
        {"id": LINHA["PPI"], "modalityId": MODALIDADE["PPI"], "immediateVacancies": 6},
        {"id": LINHA["Q"], "modalityId": MODALIDADE["Q"], "immediateVacancies": 1},
        {"id": LINHA["PCD"], "modalityId": MODALIDADE["PCD"], "immediateVacancies": 1},
    ]
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_com_quadro(total=26, linhas=linhas, modalidades=modalidades),
    )

    assert conteudo_publicado(edital)["profiles"][0]["vacancyTable"] == linhas


# --- T048 · a publicação recusa linha que aponte Modalidade inexistente (FR-166) -------------


def test_a_publicacao_recusa_linha_que_aponta_modalidade_que_nao_existe_no_perfil(
    api_client, manager_headers, process_payload
):
    """A elaboração já recusa; aqui a mesma regra vale sobre o conteúdo que passa a vigorar.

    Uma Retificação alcança tanto a linha quanto a Modalidade que ela aponta: sem esta verificação,
    remover a Modalidade deixaria para trás uma quantidade apontando o nada (FR-166, FR-172).
    """
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_quadro()
    )
    conteudo = conteudo_publicado(edital)
    perfil = conteudo["profiles"][0]
    mutilado = {
        **conteudo,
        "profiles": [
            {
                **perfil,
                "competitionModalities": [
                    modalidade
                    for modalidade in perfil["competitionModalities"]
                    if modalidade["id"] != MODALIDADE["PPI"]
                ],
            }
        ],
    }

    achados = [
        item
        for item in blocking_findings(validate_for_publication(mutilado))
        if item.code.startswith("vacancy_")
    ]
    assert [item.code for item in achados] == ["vacancy_row_modality_missing"]
    assert LINHA["PPI"] in achados[0].path, "o achado nomeia a linha que impede"


# --- T047 · Edital publicado antes do degrau (SC-050) ----------------------------------------


def test_edital_publicado_antes_do_degrau_le_com_a_colecao_vazia(
    api_client, manager_headers, process_payload
):
    """Coleção vazia significa "não publicou quadro", e nunca "zero vaga" (D-005, SC-050)."""
    from processo_seletivo.publicacoes.domain.elevacao import elevar
    from tests.fixtures.legado import publicar_na_versao_anterior

    edital = publicar_na_versao_anterior(api_client, manager_headers, process_payload, versao=11)
    guardado = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content

    assert "vacancyTable" not in guardado["profiles"][0], "o gravado não é reescrito"
    lido = elevar(guardado)
    assert lido["profiles"][0]["vacancyTable"] == []
    assert lido["profiles"][0]["immediateVacancies"] == 1, "o total continua o que era"


# --- T049 · o reaproveitamento entre Editais (R-012) -----------------------------------------


def test_a_linha_copiada_aponta_a_modalidade_do_edital_novo():
    """Esquecer o segundo passo é o defeito silencioso da feature (025, R-012).

    Sem a troca do `modalityId`, a linha copiada continuaria apontando a Modalidade do Edital
    **anterior**, e nada acusaria — a quantidade publicada passaria a repartir a cota de outro
    certame.
    """
    from processo_seletivo.editais.domain.reaproveitamento import mapa_de_identidades, remapear

    conteudo = {
        "profiles": [
            {
                "id": "00000000-0000-0000-0000-000000250100",
                "competitionModalities": [
                    _modalidade(MODALIDADE["PPI"], "PPI", "Pretos, pardos e indígenas")
                ],
                "declaredFacts": [],
                "classificationMilestones": [],
                "vacancyTable": [
                    {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
                    {"id": LINHA["PPI"], "modalityId": MODALIDADE["PPI"], "immediateVacancies": 20},
                ],
            }
        ],
        "schedule": [],
        "stages": [],
        "documentRequirements": [],
        "attachments": [],
    }

    mapa = mapa_de_identidades(conteudo)
    copiado = remapear(conteudo, mapa)

    linhas = copiado["profiles"][0]["vacancyTable"]
    nova_modalidade = copiado["profiles"][0]["competitionModalities"][0]["id"]
    assert linhas[1]["modalityId"] == nova_modalidade
    assert linhas[1]["modalityId"] != MODALIDADE["PPI"], "a Modalidade do Edital anterior sai"
    assert {linha["id"] for linha in linhas}.isdisjoint({LINHA["GERAL"], LINHA["PPI"]})
    # A linha geral não referencia nada, e `None` atravessa intocado.
    assert linhas[0]["modalityId"] is None
    assert [linha["immediateVacancies"] for linha in linhas] == [56, 20]


# --- T079 · o quadro entra no prefetch, e não acrescenta consulta por Perfil -----------------


def test_a_emissao_de_sete_perfis_nao_acrescenta_consulta_por_perfil(
    api_client, manager_headers, process_payload
):
    """O maior caso do alvo é o `28/2026`: 7 polos × 3 Modalidades.

    A emissão já faz `prefetch_related` sobre as coleções do Perfil, e o quadro entra no mesmo.
    Sem isso, cada Perfil custaria uma consulta a mais — e o que hoje é uma medida num teste
    voltaria a ser impressão de quem olha a página.
    """
    from processo_seletivo.editais.models.perfis import (
        LinhaDoQuadroDeVagas,
        ModalidadeConcorrencia,
        PerfilVaga,
    )
    from processo_seletivo.processos.models import Edital
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    def montar(quantos):
        # As linhas saem antes: `modalidade` é `PROTECT` — a D-008 escrita no banco —, e a cascata
        # do Perfil tropeçaria nela, como tropeçava em `replace_draft` antes da mesma correção.
        LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).delete()
        PerfilVaga.objects.filter(edital=edital).delete()
        for indice in range(quantos):
            perfil = PerfilVaga.objects.create(
                edital=edital, code=f"P{indice}", name=f"Polo {indice}", immediate_vacancies=40
            )
            for sigla in ("PCD", "PPI", "Q"):
                modalidade = ModalidadeConcorrencia.objects.create(
                    perfil=perfil, code=sigla, name=sigla
                )
                LinhaDoQuadroDeVagas.objects.create(
                    perfil=perfil, modalidade=modalidade, vagas_imediatas=2, ordem=1
                )
            LinhaDoQuadroDeVagas.objects.create(perfil=perfil, vagas_imediatas=28, ordem=0)

    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    def consultas_do_quadro(quantos):
        montar(quantos)
        with CaptureQueriesContext(connection) as capturadas:
            snapshot = edital_snapshot(edital)
        do_quadro = [
            consulta
            for consulta in capturadas.captured_queries
            if "linhadoquadrodevagas" in consulta["sql"].lower()
        ]
        return do_quadro, snapshot

    de_um, _ = consultas_do_quadro(1)
    de_sete, snapshot = consultas_do_quadro(7)

    assert len(de_um) == 1, "uma consulta, e não uma por Perfil"
    assert len(de_sete) == len(de_um), (
        "o quadro entra no `prefetch_related` que a emissão já faz: sete Perfis custam a mesma "
        "consulta que um"
    )
    assert [len(perfil["vacancyTable"]) for perfil in snapshot["profiles"]] == [4] * 7
