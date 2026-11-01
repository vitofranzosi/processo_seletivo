"""O cenário do A-10 de ponta a ponta: reaproveitar, publicar, convocar, requerer e exportar.

**Por que de ponta a ponta.** O defeito não aparecia na cópia — aparecia meses depois, na matrícula:
o Edital reaproveitado publicava sem exigir o Requerimento, a convocada abria `/requerimento` e
recebia 404, e a exportadora não tinha ato nenhum. Um teste que conferisse só as colunas do destino
provaria a cópia e deixaria de fora a pergunta que importa: *a pessoa convocada no Edital novo
consegue requerer a matrícula?* (auditoria de prontidão de 31/10/2026, A-10.)

**Como o cenário da convocação serve ao Edital reaproveitado.** `montar_cenario_da_convocacao`
conduz o certame pelas identidades fixas do rascunho dele — Perfil, marco, Etapa pontuada. A
origem publica o mesmo rascunho com identidades **trocadas**, e a cópia é guiada de volta às do
cenário pelo mapa de identidades, que é o único ponto da cópia que as escolhe. O destino continua
sem identidade em comum com a origem (FR-009); só passa a ter as que o cenário sabe conduzir.
"""

import json
import uuid
from unittest import mock

import pytest
from django.urls import reverse

from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.editais.application import reaproveitamento as servico
from processo_seletivo.editais.domain import reaproveitamento as dominio
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.matriculas.domain import nomes as nomes_da_matricula
from processo_seletivo.matriculas.models import GeracaoDeArquivo
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.conftest import ator_institucional
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.matriculas import (
    montar_cenario_da_exportacao,
    publicar_coletando_requerimento,
)
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import levar_a_publicacao, publish_original
from tests.fixtures.requerimento import DECLARACAO, UUID_NO_TEXTO
from tests.fixtures.requerimento import declarar as declarar_requerimento
from tests.integration.matriculas.test_geracao import gerar_do_cenario
from tests.interface.test_portal_caminho_da_convocacao import entrar_como, primeira_da_fila

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def com_identidades_trocadas(rascunho):
    """O rascunho com toda identidade trocada, e o caminho de volta de cada uma."""
    texto = json.dumps(rascunho)
    novas = {antiga: str(uuid.uuid4()) for antiga in set(UUID_NO_TEXTO.findall(texto))}
    for antiga, nova in novas.items():
        texto = texto.replace(antiga, nova)
    return json.loads(texto), {nova: antiga for antiga, nova in novas.items()}


def publicar_reaproveitando(como_producao, guardados):  # noqa: F811
    """O `publicar` do cenário, trocado por *publicar a origem, reaproveitar e publicar o destino*.

    `guardados` recebe a origem e o destino, para que o teste os compare depois.
    """

    def publicar(api_client, manager_headers, process_payload, *, draft=None):
        rascunho_da_origem, de_volta = com_identidades_trocadas(draft)
        origem = publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=rascunho_da_origem,
            antes_de_submeter=declarar_requerimento(nomes.NA_CONVOCACAO),
        )
        criado = api_client.post(
            "/api/v1/admin/processos",
            {
                "institutionalCode": "PS-2027-080",
                "title": "Processo Seletivo 2027",
                "firstEdital": {"number": "80", "year": 2027, "title": "Edital reaproveitado"},
            },
            format="json",
            **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "a10-destino-0001"},
        )
        assert criado.status_code == 201, criado.content
        destino = Edital.objects.get(processo_id=criado.json()["id"])

        def mapa_guiado(conteudo):
            mapa = dominio.mapa_de_identidades(conteudo)
            return {daqui: de_volta.get(daqui, para) for daqui, para in mapa.items()}

        with mock.patch.object(servico, "mapa_de_identidades", mapa_guiado), como_producao():
            servico.reaproveitar_edital(
                actor=ator_institucional("preparadora", "edital:elaborar"),
                edital_id=destino.id,
                origem_id=origem.id,
                expected_revision=destino.revision,
                idempotency_key="a10-reaproveitar-0001",
                correlation_id="correlacao-a10",
            )
        # **Sem regravar o rascunho**: o `PUT` do ajudante poria o rascunho mínimo por cima da
        # cópia, e o Edital publicado seria outro.
        publicado = levar_a_publicacao(
            api_client, destino, chave="a10-publicacao-destino", regravar_rascunho=False
        )
        guardados.update(origem=origem, destino=publicado)
        return publicado

    return publicar


@pytest.fixture
def guardados():
    return {}


@pytest.fixture
def certame_reaproveitado(
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
    como_producao,  # noqa: F811
    guardados,
):
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="a10-convocacao",
        publicar=publicar_reaproveitando(como_producao, guardados),
    )


def test_o_edital_reaproveitado_publica_o_requerimento_da_origem(certame_reaproveitado, guardados):
    edital, _, _ = certame_reaproveitado
    origem, destino = guardados["origem"], guardados["destino"]
    assert edital.pk == destino.pk != origem.pk

    publicado = effective_version(edital_id=destino.id).content

    assert publicado["matriculationRequest"] == {
        "moment": nomes.NA_CONVOCACAO,
        "declarationText": DECLARACAO,
    }
    assert publicado["number"] == "80" and publicado["year"] == 2027


def test_a_convocada_recebe_o_requerimento_no_momento_declarado(
    certame_reaproveitado, gestor, client
):
    """Antes da chamada, ainda indisponível; chamada, a tela abre — onde antes respondia 404."""
    edital, _, inscricoes = certame_reaproveitado
    conteudo = effective_version(edital_id=edital.id).content
    pessoa = primeira_da_fila(edital, inscricoes)

    antes = preencher.apurar(pessoa, conteudo)
    assert (antes.exigido, antes.momento, antes.disponivel) == (True, nomes.NA_CONVOCACAO, False)

    convocar(edital, gestor, pessoa.id, idempotency_key="a10-convocar")
    depois = preencher.apurar(pessoa, conteudo)
    assert depois.disponivel is True

    entrar_como(client, pessoa)
    resposta = client.get(reverse("portal:requerimento", args=[pessoa.id]))
    assert resposta.status_code == 200
    assert DECLARACAO in resposta.content.decode()


@pytest.fixture
def exportacao_reaproveitada(
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
    como_producao,  # noqa: F811
    guardados,
):
    return montar_cenario_da_exportacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="a10-exportacao",
        publicar=publicar_reaproveitando(como_producao, guardados),
    )


def test_a_exportacao_de_matricula_identifica_o_novo_edital(exportacao_reaproveitada, guardados):
    edital, convocadas = exportacao_reaproveitada
    origem, destino = guardados["origem"], guardados["destino"]
    quem_exporta = ator_institucional("exportadora", nomes_da_matricula.EXPORTAR)

    arquivo = gerar_do_cenario(quem_exporta, edital)

    registro = GeracaoDeArquivo.objects.get(pk=arquivo.geracao.pk)
    assert registro.edital_id == destino.id
    assert registro.quantidade_de_linhas == len(convocadas)
    assert arquivo.nome.startswith(f"matriculas-{destino.number}-{destino.year}-")
    assert not GeracaoDeArquivo.objects.filter(edital=origem).exists()


# ---------------------------------------------------------------------------
# O lado de lá: o certame da origem não atravessa
# ---------------------------------------------------------------------------


@pytest.fixture
def certame_anterior(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Uma origem com convocados e Requerimentos enviados — o certame que já aconteceu."""
    return montar_cenario_da_exportacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="a10-anterior",
        publicar=publicar_coletando_requerimento,
    )


def test_nenhuma_inscricao_convocacao_ou_requerimento_da_origem_e_copiado(
    certame_anterior,
    api_client,
    manager_headers,
    como_producao,  # noqa: F811
):
    origem, convocadas = certame_anterior
    assert Convocacao.objects.filter(edital=origem).count() == len(convocadas)
    assert RequerimentoDeMatricula.objects.filter(inscricao__edital=origem).exists()
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-081",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "81", "year": 2027, "title": "Nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "a10-destino-0002"},
    )
    destino = Edital.objects.get(processo_id=criado.json()["id"])

    with como_producao():
        copiado = servico.reaproveitar_edital(
            actor=ator_institucional("preparadora", "edital:elaborar"),
            edital_id=destino.id,
            origem_id=origem.id,
            expected_revision=destino.revision,
            idempotency_key="a10-reaproveitar-0002",
        )

    assert copiado.requerimento_momento == nomes.NA_CONVOCACAO
    assert Inscricao.objects.filter(edital=copiado).count() == 0
    assert Convocacao.objects.filter(edital=copiado).count() == 0
    assert RequerimentoDeMatricula.objects.filter(inscricao__edital=copiado).count() == 0
