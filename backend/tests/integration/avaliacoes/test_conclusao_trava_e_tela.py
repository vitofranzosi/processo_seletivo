"""RC-62, o que a revisão do PR 221 encontrou depois do #220: a corrida e a tela.

A recusa em si — concluir avaliação de quem já tem Resultado na Etapa — está em
`test_conclusao_depois_do_resultado.py`. Aqui ficam as duas lacunas dela:

- **a corrida**: concluir travava só a Atribuição, e a Ocorrência grava sob o `FOR UPDATE` do
  Processo; as duas transações liam "sem Resultado" uma da outra e comitavam, e o par contraditório
  que o RC-62 existe para impedir voltava à trilha;
- **a tela**: a Mesa oferecia "Concluir avaliação" e só recusava depois do POST, com o parecer
  inteiro escrito.
"""

import threading
import time

import pytest
from django.db import connection, connections, transaction
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1620, codigo="1620"
    )
    montado["inscricoes"] = inscrever(montado["edital"], 2, primeiro=1)
    distribuir_para(montado, gestor, ["joao"], montado["inscricoes"], chave="rc62-tela")
    return montado


def _ocorrencia(cenario, inscricao):
    registrar_ocorrencia(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        motivo="não compareceu",
        idempotency_key=f"rc62-tela-{inscricao.id}",
        correlation_id="teste",
    )


def test_a_mesa_diz_a_recusa_antes_do_clique_e_nao_oferece_concluir(
    client, seletor_ligado, cenario
):
    """A frase é a do comando, e o rascunho continua oferecido. Quem não tem Resultado vê a tela
    de sempre."""
    faltou, compareceu = cenario["inscricoes"]
    _ocorrencia(cenario, faltou)
    identificar(client, "joao", [])

    def tela(inscricao):
        return client.get(
            reverse(
                "interface:mesa-inscricao",
                args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
            )
        ).content.decode()

    impedida = tela(faltou)
    assert 'id="impedimento-de-concluir"' in impedida
    assert "já tem Resultado na Etapa" in impedida
    assert "Concluir avaliação</button>" not in impedida
    assert "Salvar sem concluir" in impedida

    livre = tela(compareceu)
    assert 'id="impedimento-de-concluir"' not in livre
    assert "Concluir avaliação</button>" in livre


@pytest.mark.skipif(connection.vendor != "postgresql", reason="a trava exige PostgreSQL")
def test_a_conclusao_espera_o_ato_da_presidencia_e_le_o_resultado_dele(cenario):
    """A presidência segura o Processo — como `comando_de_comissao` segura — e registra a Ocorrência
    dentro da mesma transação. A conclusão, disparada no meio, precisa esperar e ler o Resultado
    que nasceu."""
    faltou, _ = cenario["inscricoes"]
    segurando = threading.Event()
    falhas = []

    def presidencia():
        try:
            with transaction.atomic():
                ProcessoSeletivo.objects.select_for_update().get(pk=cenario["processo"].id)
                segurando.set()
                time.sleep(0.5)
                _ocorrencia(cenario, faltou)
        except Exception as exc:  # noqa: BLE001 — repassado para o corpo do teste
            falhas.append(exc)
        finally:
            connections.close_all()

    thread = threading.Thread(target=presidencia)
    thread.start()
    assert segurando.wait(timeout=5)

    inicio = time.monotonic()
    with pytest.raises(DomainError) as recusa:
        concluir_como(cenario, "joao", faltou, pontuacao="75")
    esperou = time.monotonic() - inicio

    thread.join(timeout=10)
    assert not falhas, falhas
    assert esperou >= 0.2, "a conclusão não esperou o ato da presidência"
    assert recusa.value.code == "inscricao_ja_tem_resultado"
    assert not Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).exists()
