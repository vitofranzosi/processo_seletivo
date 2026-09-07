"""Enquanto houver pendência reaberta que afete o marco, publicar é recusado.

A reabilitação por recurso devolve alguém ao certame — e ela volta **sem Resultado** nas Etapas que
o marco enumera. Divulgar assim publicaria uma ordem que já se sabe incompleta, e a pessoa
reabilitada apareceria ausente da lista: pior do que não publicar, porque parece decisão.

```text
reabilitada sem Resultado na Etapa do marco  →  publicar recusa, nomeando o caminho
consolidado o Resultado                      →  o impedimento desaparece sozinho
```

**O caminho não é emitir ato sucessor**, e é por isso que a recusa o diz por extenso: emitir antes
de consolidar produziria o mesmo ato incompleto, e a tela mandaria repetir o que não resolve
(FR-079, SC-013).
"""

from decimal import Decimal

import pytest

from processo_seletivo.divulgacao.domain.publicabilidade import (
    IMPEDIMENTO,
    REINGRESSO_PENDENTE,
    aferir,
)
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, publicar_o_ato
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def reabilitada(gestor, api_client, manager_headers, process_payload):
    """Eliminada na Etapa 1, deferida por recurso — e a Etapa 2 já tem ato emitido.

    É o cenário que a auditoria descreveu: quem organiza a Etapa seguinte já a deu por encerrada
    quando o deferimento chega.
    """
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=121,
        codigo="0821",
        pontuacoes=("55.0000", "90.0000"),
        na_primeira_etapa=True,
    )
    cenario = peca["cenario"]
    # A Etapa 2 consolidada só para quem passou, e o ato do marco final emitido.
    outra = cenario["inscricoes"][1]
    contexto = {**cenario, "etapa": cenario["segunda"]}
    distribuir_para(contexto, _gestor(), ["joao"], [outra], chave="lote-0821-segunda")
    concluir_como(contexto, "joao", outra, pontuacao="80.0000")
    _consolidar(cenario, cenario["segunda"], [outra], chave="consolidar-0821-segunda")
    cenario["ato_final"] = emitir(cenario, _gestor(), chave="emitir-0821-final")
    return peca


def deferir(peca):
    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A análise documental não considerou o diploma juntado.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-reingresso",
    )


def afericao(peca):
    cenario = peca["cenario"]
    return aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato_final"])


def test_antes_do_deferimento_o_ato_final_e_publicavel(reabilitada):
    """A prova de que o impedimento abaixo é **do reingresso**, e não do cenário."""
    assert afericao(reabilitada).publicavel is True


def test_com_reingresso_pendente_publicar_e_recusado_com_a_causa(reabilitada):
    deferir(reabilitada)

    resultado = afericao(reabilitada)

    assert resultado.nivel == IMPEDIMENTO
    assert resultado.codigo == REINGRESSO_PENDENTE
    assert "reabilitada por recurso" in resultado.mensagem
    assert "Consolide o resultado" in resultado.mensagem
    # **E não é caminho de sucessor**: emitir outro ato produziria o mesmo ato incompleto.
    assert resultado.admite_sucessor is False


def test_o_comando_de_publicacao_tambem_recusa(reabilitada):
    """A aferição não basta: quem grava é o comando, e é ele que precisa recusar."""
    deferir(reabilitada)

    with pytest.raises(DomainError) as recusa:
        publicar_o_ato(
            reabilitada["cenario"],
            chave="publicar-com-reingresso",
            ato=reabilitada["cenario"]["ato_final"],
        )

    assert recusa.value.code == REINGRESSO_PENDENTE


def test_consolidado_o_resultado_o_impedimento_desaparece(reabilitada):
    """Ele some sozinho, porque é derivado — ninguém precisa dar baixa em nada (D-010)."""
    cenario = reabilitada["cenario"]
    deferir(reabilitada)
    assert afericao(reabilitada).codigo == REINGRESSO_PENDENTE

    contexto = {**cenario, "etapa": cenario["segunda"]}
    distribuir_para(
        contexto, _gestor(), ["joao"], [reabilitada["inscricao"]], chave="lote-0821-reaberta"
    )
    concluir_como(contexto, "joao", reabilitada["inscricao"], pontuacao="70.0000")
    _consolidar(
        cenario, cenario["segunda"], [reabilitada["inscricao"]], chave="consolidar-0821-reaberta"
    )

    resultado = afericao(reabilitada)
    assert resultado.codigo != REINGRESSO_PENDENTE


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


def _consolidar(cenario, etapa_id, inscricoes, *, chave):
    from processo_seletivo.resultados.application.consolidacao import consolidar

    return consolidar(
        actor=_gestor(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa_id,
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=chave,
        correlation_id="reingresso",
    )
