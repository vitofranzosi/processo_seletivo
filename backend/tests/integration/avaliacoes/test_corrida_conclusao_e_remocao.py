"""Concluir e remover atribuição disputam a **mesma linha** — e é isso que FR-092 exige.

Sem trava comum, a sequência é esta: a remoção lê "pendente", inativa a Atribuição, e a conclusão
concorrente grava depois. O resultado é uma avaliação **concluída e inelegível pela via comum** —
o efeito sem o ato nomeado, que é exatamente o que a fase inteira existe para impedir.

O invariante que este arquivo protege cabe numa linha:

> nunca existe Avaliação concluída sob Atribuição inativada por remoção comum.

Duas threads reais, com `transaction=True` para que cada uma tenha a sua conexão e o seu commit.
Sem isso a corrida não acontece — as duas operações rodariam sequencialmente no mesmo snapshot.
"""

import threading

import pytest
from django.db import connections

from processo_seletivo.avaliacoes.application.avaliacao import concluir
from processo_seletivo.avaliacoes.application.distribuicao import remover_atribuicao
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.mesa import distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=13, codigo="D1")


@pytest.fixture
def disputada(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1300)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="corrida")
    return inscricao


def test_concluir_e_remover_nunca_produzem_concluida_inelegivel(cenario, gestor, disputada):
    """Uma das duas vence, e as duas saídas são íntegras.

    Se a remoção vier primeiro, a conclusão é recusada — a Atribuição já não autoriza. Se a
    conclusão vier primeiro, a remoção recusa com o motivo de FR-092. O que não pode acontecer é
    a Atribuição ficar inativa **e** a Avaliação concluída.
    """
    atribuicao = Atribuicao.objects.get(inscricao=disputada)
    versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    partida = threading.Barrier(2)
    desfechos = {}

    def concluir_avaliacao():
        partida.wait(timeout=5)
        try:
            concluir(
                ator=ator_institucional("joao"),
                edital=cenario["edital"],
                etapa_id=cenario["etapa"],
                inscricao_id=disputada.id,
                pontuacao="90",
                parecer="Atende",
                expected_revision=1,
                versao_reconhecida=versao.id,
                correlation_id="teste",
            )
            desfechos["conclusao"] = "ok"
        except DomainError as recusa:
            desfechos["conclusao"] = f"recusa:{recusa.status}"
        except Exception as erro:  # noqa: BLE001 — é o que não pode acontecer
            desfechos["conclusao"] = f"erro:{type(erro).__name__}"
        finally:
            connections.close_all()

    def remover():
        partida.wait(timeout=5)
        try:
            resultado = remover_atribuicao(
                actor=gestor,
                processo_id=cenario["processo"].id,
                atribuicao_ids=[atribuicao.id],
                idempotency_key="corrida-remocao",
                correlation_id="teste",
            )
            desfechos["remocao"] = "removida" if resultado["feitas"] else "recusada"
        except DomainError as recusa:
            desfechos["remocao"] = f"recusa:{recusa.status}"
        except Exception as erro:  # noqa: BLE001
            desfechos["remocao"] = f"erro:{type(erro).__name__}"
        finally:
            connections.close_all()

    fios = [threading.Thread(target=concluir_avaliacao), threading.Thread(target=remover)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=15)

    assert not any(str(d).startswith("erro:") for d in desfechos.values()), desfechos
    atribuicao.refresh_from_db()
    concluida = Avaliacao.objects.filter(
        atribuicao=atribuicao, estado=Avaliacao.Estado.CONCLUIDA
    ).exists()

    # **O invariante.** As duas saídas legítimas, e nenhuma terceira.
    if desfechos["remocao"] == "removida":
        assert not atribuicao.ativo
        assert not concluida, "conclusão gravada depois da remoção comum — FR-092 furado"
        assert desfechos["conclusao"].startswith("recusa"), desfechos
    else:
        assert atribuicao.ativo
        assert concluida
        assert desfechos["conclusao"] == "ok", desfechos


def test_o_estado_final_e_sempre_coerente_sob_repeticao(cenario, gestor):
    """A corrida repetida, para que um resultado feliz por acaso não passe por garantia."""
    for rodada in range(4):
        inscricao = inscricoes_de(cenario, 1, primeiro=1400 + rodada)[0]
        distribuir_para(cenario, gestor, ["joao"], [inscricao], chave=f"r{rodada}")
        atribuicao = Atribuicao.objects.get(inscricao=inscricao)
        versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
        partida = threading.Barrier(2)

        def concluir_avaliacao(alvo=inscricao, v=versao, largada=partida):
            largada.wait(timeout=5)
            try:
                concluir(
                    ator=ator_institucional("joao"),
                    edital=cenario["edital"],
                    etapa_id=cenario["etapa"],
                    inscricao_id=alvo.id,
                    pontuacao="90",
                    parecer="Atende",
                    expected_revision=1,
                    versao_reconhecida=v.id,
                    correlation_id="teste",
                )
            except DomainError:
                pass
            finally:
                connections.close_all()

        def remover(alvo=atribuicao, chave=rodada, largada=partida):
            largada.wait(timeout=5)
            try:
                remover_atribuicao(
                    actor=gestor,
                    processo_id=cenario["processo"].id,
                    atribuicao_ids=[alvo.id],
                    idempotency_key=f"corrida-{chave}",
                    correlation_id="teste",
                )
            except DomainError:
                pass
            finally:
                connections.close_all()

        fios = [threading.Thread(target=concluir_avaliacao), threading.Thread(target=remover)]
        for fio in fios:
            fio.start()
        for fio in fios:
            fio.join(timeout=15)

        atribuicao.refresh_from_db()
        concluida = Avaliacao.objects.filter(
            atribuicao=atribuicao, estado=Avaliacao.Estado.CONCLUIDA
        ).exists()
        assert not (concluida and not atribuicao.ativo), f"rodada {rodada}: concluída e inelegível"
