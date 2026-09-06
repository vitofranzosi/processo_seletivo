"""A quarta frente de concorrência: publicar e emitir o sucessor, ao mesmo tempo (T-005, FR-003).

**É a que não se resolve revalidando.** `emitir_ordem` pode gravar o ato sucessor entre a aferição
de publicabilidade e a gravação da publicação. A aferição estava correta quando ocorreu, e uma
transação isolada não impede a outra transação de existir: a leitura é consistente com o instante em
que aconteceu, e o problema é o que acontece **depois** dela.

A resposta é o bloqueio. `publicar_resultado` toma `select_for_update` na mesma linha do
`ProcessoSeletivo` que `comando_de_comissao` já toma, **antes** de aferir, e os dois comandos passam
a se serializar. O perdedor encontra o mundo já mudado, e recusa.

**Exige PostgreSQL.** Em SQLite não há duas transações concorrentes de verdade, e este teste
passaria sem verificar nada — que é exatamente o silêncio que o aviso de `tasks.md` nomeia.
"""

import threading

import pytest
from django.db import connection

from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
    publicar_resultado,
)
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import encerrar_conexoes_da_thread
from tests.fixtures.divulgacao import ator_publicador, emitir, montar_ato_publicavel

pytestmark = [
    pytest.mark.integration,
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(
        connection.vendor != "postgresql",
        reason="A serialização é do banco; em sqlite não há duas transações concorrentes.",
    ),
]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=54,
        codigo="0754",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=501,
    )


def test_publicar_espera_a_emissao_concorrente_e_recusa_o_ato_ja_sucedido(cenario, gestor):
    """A prova da serialização, com a interleaving perigosa **forçada** (T-005, FR-003).

    A corrida solta não serve como prova: publicar antes e emitir depois é o ciclo de vida normal —
    a publicação vira histórica e a 015 registra a sucessão —, e um teste que apenas dispara os dois
    e olha o fim aceitaria os dois desfechos sem distinguir qual aconteceu.

    O que interessa é a ordem oposta, e ela é montada aqui: a emissão toma a linha do Processo e a
    segura; publicar parte e **fica esperando**; a emissão grava o sucessor e libera. Sem o
    bloqueio, publicar teria aferido antes, encontrado o ato ainda vigente, e gravado a divulgação
    de um ato que deixou de ser vigente no intervalo — exatamente o caso que revalidar dentro da
    transação não resolve.
    """
    import time

    from django.db import transaction

    from processo_seletivo.processos.models import ProcessoSeletivo

    ato = cenario["ato"]
    confirmacao = assinatura_da_previa(ato=ato, publicacao_anterior=None, projecao=compor(ato))
    desfecho = {}
    comecou = threading.Event()

    def publicar():
        try:
            comecou.set()
            desfecho["publicar"] = publicar_resultado(
                actor=ator_publicador(),
                processo_id=cenario["edital"].processo_id,
                edital_id=cenario["edital"].id,
                marco_id=cenario["marco"],
                ato_id=ato.id,
                natureza="PRELIMINAR",
                autoridade="diretoria-cefor",
                confirmacao_da_previa=confirmacao,
                idempotency_key="publicar-0754-corrida",
                correlation_id="teste",
            )
        except Exception as exc:  # noqa: BLE001 — avaliado no corpo do teste
            desfecho["publicar"] = exc
        finally:
            encerrar_conexoes_da_thread()

    thread = threading.Thread(target=publicar)
    with transaction.atomic():
        # A emissão toma a linha do Processo — a **mesma** que `comando_de_comissao` toma — e a
        # segura até o fim deste bloco.
        ProcessoSeletivo.objects.select_for_update().get(pk=cenario["edital"].processo_id)
        thread.start()
        assert comecou.wait(timeout=10)
        # Enquanto a linha está tomada, publicar não pode ter passado da trava. Se ele tivesse
        # aferido aqui, encontraria o ato ainda vigente — e é essa aferição que precisa acontecer
        # **depois** do commit da emissão.
        time.sleep(1.0)
        assert thread.is_alive(), (
            "publicar não esperou a linha do Processo: sem o bloqueio, ele aferiria o ato como "
            "vigente e gravaria a divulgação de um ato que a emissão está prestes a suceder"
        )
        emitir(cenario, gestor, chave="emitir-0754-corrida", motivo="Resultado tardio.")

    thread.join(timeout=60)
    assert not thread.is_alive(), "publicar ficou preso depois de a emissão liberar a linha"

    recusa = desfecho["publicar"]
    assert isinstance(recusa, DomainError), f"publicar devia recusar, e devolveu {recusa!r}"
    assert recusa.code == "publication_act_superseded"
    assert not PublicacaoResultado.objects.exists(), (
        "nenhuma divulgação pode ter nascido sobre o ato que a emissão sucedeu"
    )


def test_duas_publicacoes_concorrentes_do_mesmo_ato_produzem_uma(cenario):
    """A garantia de banco do cenário das duas abas, sob concorrência real (FR-039, SC-021).

    Duas chaves de idempotência diferentes: a idempotência não vê nada de errado, e quem recusa é
    `uq_publicacao_por_ato_natureza`.
    """
    ato = cenario["ato"]
    confirmacao = assinatura_da_previa(ato=ato, publicacao_anterior=None, projecao=compor(ato))
    barreira = threading.Barrier(2, timeout=30)
    desfechos = []

    def publicar(chave):
        def executar():
            try:
                barreira.wait()
                desfechos.append(
                    publicar_resultado(
                        actor=ator_publicador(),
                        processo_id=cenario["edital"].processo_id,
                        edital_id=cenario["edital"].id,
                        marco_id=cenario["marco"],
                        ato_id=ato.id,
                        natureza="PRELIMINAR",
                        autoridade="diretoria-cefor",
                        confirmacao_da_previa=confirmacao,
                        idempotency_key=chave,
                        correlation_id="teste",
                    )
                )
            except Exception as exc:  # noqa: BLE001 — avaliado no corpo do teste
                desfechos.append(exc)
            finally:
                encerrar_conexoes_da_thread()

        return executar

    threads = [
        threading.Thread(target=publicar("publicar-0754-aba-1")),
        threading.Thread(target=publicar("publicar-0754-aba-2")),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)

    assert PublicacaoResultado.objects.filter(ato=ato).count() == 1
    recusas = [item for item in desfechos if isinstance(item, Exception)]
    assert len(recusas) == 1, f"exatamente uma das duas precisa ser recusada: {desfechos}"
    assert isinstance(recusas[0], DomainError)
    assert recusas[0].code in {"publication_already_exists", "publication_preview_stale"}
