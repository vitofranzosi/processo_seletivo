"""T047 — o que a 012 fazia continua sendo feito.

Duas afirmações, e a segunda é a que a revisão do plano acrescentou: a primeira Etapa não muda
nada, e a Atribuição criada enquanto a exigência estava dormente **volta a autorizar** quando o
Resultado habilitador aparece — ela não é destruída, é preservada como histórico.
"""

from uuid import UUID

import pytest

from processo_seletivo.avaliacoes.application.selectors import mesa
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def linhas_da_mesa(cenario, etapa):
    linhas, _, _ = mesa(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=UUID(str(etapa)),
        vigentes=etapas_vigentes(cenario["edital"]),
    )
    return {linha["atribuicao"].inscricao_id for linha in linhas}


def test_a_primeira_etapa_conserva_o_comportamento_da_012(gestor, api_client, manager_headers):
    """Sem Etapa anterior não há progressão a aplicar, e nada muda para ninguém."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1420, codigo="1420"
    )
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    desfecho = distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1420")

    assert desfecho["feitas"] == 3
    assert linhas_da_mesa(cenario, cenario["primeira"]) == {i.id for i in inscricoes}


def test_a_atribuicao_antecipada_e_preservada_e_volta_a_autorizar(
    gestor, api_client, manager_headers
):
    """Criada enquanto a exigência dormia; inerte enquanto falta o Resultado; viva depois dele."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1421, codigo="1421"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1421")
    # Antes de qualquer Resultado: a Etapa 2 aceita as duas, como na 012.
    distribuir_para(
        {**cenario, "etapa": cenario["segunda"]}, gestor, ["joao"], inscricoes, chave="lote2-1421"
    )
    assert linhas_da_mesa(cenario, cenario["segunda"]) == {i.id for i in inscricoes}

    # Consolidando **uma** delas, a exigência passa a vigorar: a outra fica aguardando.
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="k-1421",
        correlation_id="teste",
    )
    assert linhas_da_mesa(cenario, cenario["segunda"]) == {inscricoes[0].id}
    # E o registro antecipado da outra **continua lá**, para investigação.
    assert Atribuicao.objects.filter(
        etapa_id=cenario["segunda"], inscricao=inscricoes[1], ativo=True
    ).exists()

    # Habilitada depois, ela volta a autorizar — sem nova distribuição.
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="80")
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[1].id],
        idempotency_key="k2-1421",
        correlation_id="teste",
    )
    assert linhas_da_mesa(cenario, cenario["segunda"]) == {i.id for i in inscricoes}
