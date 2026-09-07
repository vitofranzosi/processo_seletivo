"""Removida a eliminação, a inscrição volta — **em todas as Etapas seguintes**.

É o efeito que a auditoria da 017 registrou como descoberto por acaso: deferir um recurso na Etapa 1
não é só corrigir a Etapa 1. A pessoa passa a participar da Etapa 2, da Etapa 3, e de tudo o que a
eliminação a excluía — e o sistema precisa dizer isso, porque quem organiza a Etapa seguinte já a
deu por encerrada.

```text
eliminação vigente na Etapa 1  →  fora da Etapa 2 e das seguintes
sucessor habilitante na Etapa 1 →  pendente na Etapa 2, distribuível, avaliável, consolidável
```

**A participação é derivada da eliminação vigente**, e é por isso que ela volta sozinha: nenhuma
operação de reintegração existe, e nenhuma precisa existir (FR-075, FR-076, D-010).
"""

from decimal import Decimal

import pytest

from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.prontidao import panorama_da_etapa
from processo_seletivo.resultados.application.selectors import (
    reabilitacao_da_inscricao,
    reabilitadas_por_recurso,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def eliminada_na_primeira(gestor, api_client, manager_headers, process_payload):
    """Eliminada na **Etapa 1**, com a Etapa 2 já consolidada para as demais.

    A ordem é a real, e é o que torna o caso difícil: quando o recurso é deferido, a Etapa seguinte
    já foi dada por encerrada por quem a organizou.
    """
    return cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=119,
        codigo="0819",
        pontuacoes=("55.0000", "90.0000"),
        na_primeira_etapa=True,
    )


def panorama(cenario, etapa_id):
    edital = cenario["edital"]
    vigentes = etapas_vigentes(edital)
    return panorama_da_etapa(
        edital=edital, etapa=vigentes[identificador(etapa_id)], etapas_vigentes=vigentes
    )


def deferir(peca, pontuacao=Decimal("82.0000")):
    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=pontuacao,
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-retroativa",
    )


def test_a_reabilitacao_e_derivada_e_nomeia_a_decisao(eliminada_na_primeira):
    """Sem estado de reintegração: reabilitada é quem tem sucessor vigente que habilita (D-010)."""
    peca = eliminada_na_primeira
    edital = peca["cenario"]["edital"]

    assert reabilitadas_por_recurso(edital=edital) == {}

    _decisao, sucessor = deferir(peca)

    reabilitadas = reabilitadas_por_recurso(edital=edital)
    assert set(reabilitadas) == {peca["inscricao"].id}
    linha = reabilitacao_da_inscricao(reabilitadas[peca["inscricao"].id])
    assert linha["recurso"] == peca["recurso"].protocolo
    assert linha["consequencia_anterior"] == ResultadoEtapa.Consequencia.ELIMINADA
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.HABILITADA


def test_corrigir_quem_ja_seguia_nao_e_reabilitacao(
    gestor, api_client, manager_headers, process_payload
):
    """A distinção que impede a tela de avisar sobre quem nunca saiu.

    Corrigir a nota de quem já estava habilitada é superação, e não reingresso. Chamá-la de
    reabilitação encheria a Mesa de avisos sobre gente que nunca deixou o certame — e o aviso que
    aparece sempre é o aviso que ninguém lê.
    """
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=120,
        codigo="0820",
        pontuacoes=("70.0000", "90.0000"),
    )

    deferir(peca, pontuacao=Decimal("88.0000"))

    assert reabilitadas_por_recurso(edital=peca["cenario"]["edital"]) == {}


def test_a_inscricao_reaparece_como_pendente_na_etapa_seguinte(eliminada_na_primeira):
    """A participação volta sozinha, porque ela é derivada da eliminação vigente (FR-075)."""
    peca = eliminada_na_primeira
    cenario = peca["cenario"]
    seguinte = cenario["segunda"]

    antes = panorama(cenario, seguinte)
    assert peca["inscricao"].id not in antes["participantes"]

    deferir(peca)

    depois = panorama(cenario, seguinte)
    assert peca["inscricao"].id in depois["participantes"]


def test_a_inscricao_reaberta_e_distribuivel_avaliavel_e_consolidavel(eliminada_na_primeira):
    """As operações que já existem bastam — nenhuma de reintegração foi criada (SC-012)."""
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.conftest import ator_institucional

    peca = eliminada_na_primeira
    cenario = peca["cenario"]
    seguinte = cenario["segunda"]
    deferir(peca)

    contexto = {**cenario, "etapa": seguinte}
    declarado = distribuir_para(
        contexto, _gestor(), ["joao"], [peca["inscricao"]], chave="lote-retroativa"
    )
    assert declarado["recusadas"] == 0, declarado["motivos"]
    concluir_como(contexto, "joao", peca["inscricao"], pontuacao="77.0000")

    resultado = consolidar(
        actor=ator_institucional("carlos", "comissao:gerir"),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=seguinte,
        inscricao_ids=[peca["inscricao"].id],
        idempotency_key="consolidar-retroativa",
        correlation_id="retroativa",
    )

    assert resultado["feitas"] == 1
    novo = ResultadoEtapa.vigentes.get(inscricao=peca["inscricao"], etapa_id=seguinte)
    assert novo.pontuacao == Decimal("77.0000")
    # E ele é um Resultado **raiz** da Etapa seguinte: não sucede coisa alguma, porque ali não
    # havia Resultado a superar.
    assert novo.resultado_anterior_id is None


def _gestor():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")
