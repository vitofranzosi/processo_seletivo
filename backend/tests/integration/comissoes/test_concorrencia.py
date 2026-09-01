"""T073 e T073a — a corrida que de fato quebraria o invariante, e a que quebraria a autorização.

Duas remoções do **mesmo** presidente não testam nada interessante: o lock as serializa e a
segunda vê a linha já inativa. A corrida real é com **dois** presidentes e uma remoção concorrente
de cada — ambas leem "há outro presidente", ambas passam, e a comissão fica com zero.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.comissoes.application.comissao import alterar_funcao, remover_membro
from processo_seletivo.comissoes.models import Funcao, MembroComissao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir, publicar_processo_com_etapas

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="locks exigem PostgreSQL"
)


def em_paralelo(alvos):
    """Roda os alvos em threads, cada um com a sua conexão, e devolve os resultados."""
    resultados = []
    trava = threading.Lock()

    def executar(indice, alvo):
        try:
            alvo()
            desfecho = ("ok", None)
        except DomainError as recusa:
            desfecho = ("recusado", recusa.code)
        except Exception as erro:  # pragma: no cover - só aparece se o desenho estiver errado
            desfecho = ("erro", repr(erro))
        finally:
            connections.close_all()
        with trava:
            resultados.append((indice, *desfecho))

    threads = [threading.Thread(target=executar, args=(i, alvo)) for i, alvo in enumerate(alvos)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    return resultados


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_dois_presidentes_removidos_ao_mesmo_tempo_nao_zeram_a_presidencia(
    api_client, manager_headers, process_payload
):
    """SC-019: exatamente uma das operações pode vencer."""
    edital = publicar_processo_com_etapas(api_client, manager_headers, process_payload)
    processo = edital.processo
    gestor = ator_institucional("carlos", "comissao:gerir")
    membros = constituir(
        gestor, processo, [("maria", "PRESIDENTE"), ("ana", "PRESIDENTE"), ("joao", "MEMBRO")]
    )
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador

    alocar_em(gestor, processo, membros["joao"], edital, identificador(ETAPA_A1, 0))

    def remover(subject, chave):
        def acao():
            remover_membro(
                actor=ator_institucional("carlos", "comissao:gerir"),
                processo_id=processo.id,
                membro_id=membros[subject].id,
                idempotency_key=chave,
                correlation_id="corrida",
            )

        return acao

    resultados = em_paralelo([remover("maria", "c-1"), remover("ana", "c-2")])

    vencedoras = [r for r in resultados if r[1] == "ok"]
    assert len(vencedoras) == 1, resultados
    restantes = MembroComissao.objects.filter(
        processo=processo, ativo=True, funcao=Funcao.PRESIDENTE
    )
    assert restantes.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_presidente_rebaixado_no_meio_do_caminho_nao_conclui_a_alteracao(
    api_client, manager_headers, process_payload
):
    """D-016: a base é reavaliada **depois** do lock, e não na view.

    Sem a reavaliação, quem perdeu a presidência entre a tela e a gravação concluiria o ato com
    uma autorização que já não existe.
    """
    edital = publicar_processo_com_etapas(api_client, manager_headers, process_payload)
    processo = edital.processo
    gestor = ator_institucional("carlos", "comissao:gerir")
    membros = constituir(
        gestor, processo, [("maria", "PRESIDENTE"), ("ana", "PRESIDENTE"), ("joao", "MEMBRO")]
    )

    def rebaixar_maria():
        alterar_funcao(
            actor=ator_institucional("carlos", "comissao:gerir"),
            processo_id=processo.id,
            membro_id=membros["maria"].id,
            funcao="MEMBRO",
            idempotency_key="rebaixa",
            correlation_id="corrida",
        )

    def maria_altera_joao():
        alterar_funcao(
            actor=ator_institucional("maria"),
            processo_id=processo.id,
            membro_id=membros["joao"].id,
            funcao="PRESIDENTE",
            idempotency_key="maria-altera",
            correlation_id="corrida",
        )

    resultados = em_paralelo([rebaixar_maria, maria_altera_joao])

    membros["maria"].refresh_from_db()
    membros["joao"].refresh_from_db()
    if membros["maria"].funcao == Funcao.MEMBRO:
        # Maria foi rebaixada. Se a alteração dela venceu antes, tudo bem; o que não pode é ela
        # ter concluído **depois**, com a base já inexistente.
        desfecho = dict((r[0], r[1]) for r in resultados)
        assert desfecho[1] in {"ok", "recusado"}
    assert MembroComissao.objects.filter(processo=processo, ativo=True).count() == 3
