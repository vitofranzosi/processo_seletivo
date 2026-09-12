"""A prévia e o critério publicado conhecem a Etapa de habilitação (021, R-012, FR-011).

**Os dois defeitos que este arquivo fecha.** A publicação filtrava por `qualifyingStageId` e a
prévia da tela não: a comissão via um número de participantes e congelava outro, sem que nada
explicasse a diferença. E o critério publicado dizia "todas as inscrições submetidas" numa relação
que exclui quem não passou na Etapa anterior — quem ficou de fora não tinha, no texto publicado, o
que explicasse a própria ausência.
"""

import pytest

from processo_seletivo.sorteios.application.previa import recortes_do_marco
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.models import RelacaoDeHabilitados
from tests.fixtures.comissao import constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import MARCO, METODO, marco_com_metodo, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def com_etapa_de_habilitacao(gestor, api_client, manager_headers, process_payload):
    """Um Edital cujo marco declara a Etapa que habilita ao sorteio, e resultados nela."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao

    rascunho = rascunho_com_etapas()
    etapa = rascunho["stages"][1]
    marco_com_metodo(
        rascunho,
        perfil_id=PROFILE_ID,
        etapa_id=etapa["id"],
        metodo={**METODO, "qualifyingStageId": etapa["id"]},
    )
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo="habilitacao")
    inscricoes = inscrever(edital, 4, primeiro=601)
    return edital, etapa["id"], inscricoes


def _habilitar(edital, etapa_id, inscricoes):
    """Resultado vigente favorável para as duas primeiras — as outras ficam de fora."""
    from django.utils import timezone

    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from processo_seletivo.resultados.models import ResultadoEtapa

    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    for inscricao in inscricoes[:2]:
        ResultadoEtapa.objects.create(
            edital=edital,
            inscricao=inscricao,
            etapa_id=etapa_id,
            versao=versao,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            motivo="Habilitada na Etapa anterior ao sorteio.",
            consolidado_em=timezone.now(),
            consolidado_por="cpf:presidente",
        )


def test_a_previa_conta_os_mesmos_que_a_publicacao_congela(com_etapa_de_habilitacao):
    """**Eram números diferentes**, e a tela não explicava a diferença."""
    edital, etapa_id, inscricoes = com_etapa_de_habilitacao
    _habilitar(edital, etapa_id, inscricoes)

    estado = recortes_do_marco(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    ampla = next(r for r in estado["recortes"] if not r["lista_id"])

    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="habilitacao-relacao",
        correlation_id="teste-021",
    )

    assert ampla["projetados"] == 2, "só quem tem resultado favorável na Etapa declarada"
    assert declarado["quantidade"] == ampla["projetados"]


def test_o_criterio_publicado_explica_a_exclusao(com_etapa_de_habilitacao):
    """Quem ficou de fora precisa ler, no texto publicado, o que o deixou de fora (FR-011)."""
    edital, etapa_id, inscricoes = com_etapa_de_habilitacao
    _habilitar(edital, etapa_id, inscricoes)

    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="habilitacao-criterio",
        correlation_id="teste-021",
    )

    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])
    assert "resultado vigente favorável" in relacao.criterio_de_projecao
    assert "Prova didática" in relacao.criterio_de_projecao, "a Etapa é nomeada, e não implícita"


def test_sem_etapa_declarada_o_criterio_nao_inventa_exclusao(
    gestor, api_client, manager_headers, process_payload
):
    """`None` e conjunto vazio continuam sendo coisas diferentes (R-012)."""
    from tests.fixtures.sorteio import certame_de_sorteio

    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)

    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="sem-etapa-criterio",
        correlation_id="teste-021",
    )

    relacao = RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])
    assert "Todas as inscrições submetidas" in relacao.criterio_de_projecao
    assert "favorável" not in relacao.criterio_de_projecao
    assert relacao.quantidade == 3
