"""A Retificação do acervo diz o que a Etapa não terá, e não é recusada por isso (046, `FR-751`).

**O Edital do acervo com dupla leitura existe**: foi publicado antes da `046`, e a consolidação o
recusa por inteiro. A Retificação é a saída dele — `evaluationsPerRegistration` é retificável —, e
por isso a família nova é advertência nela, e nunca impeditiva (032, `FR-460`).

**E a advertência precisa chegar à tela.** A confirmação da Retificação subtrai da lista os códigos
que impediriam a publicação (`advertencias_do_ato`, a issue #117). Com um código só nas duas
severidades, a advertência desta Etapa — que é exigida, e portanto impeditiva na publicação —
sumiria ali, em silêncio. São dois códigos (`R-3`), e este arquivo prende o efeito, e não o
desenho: a frase aparece na confirmação, pela tela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
from tests.fixtures.comissao import ETAPA_A1, publicar_processo_com_etapas
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import create_retification
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

COMBINAR = "não declara como combiná-las"


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    """A *Análise documental* eliminatória com duas avaliações — publicada antes da `046`."""
    return publicar_processo_com_etapas(
        api_client, manager_headers, process_payload, avaliacoes=2, como_acervo=True
    )


def test_a_retificacao_que_nao_toca_a_etapa_e_aceita_e_adverte_na_confirmacao(
    client, seletor_ligado, api_client, do_acervo
):
    em_elaboracao = create_retification(
        api_client,
        do_acervo,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Corrigida"}],
        suffix="046-descricao",
    )

    advertencias = advertencias_do_ato(em_elaboracao)
    assert [item.code for item in advertencias if COMBINAR in item.message] == [
        "stage_without_result"
    ], "a advertência sobrevive à subtração dos impeditivos"

    identificar(client, "ana.elaboradora", ["elaborador"])
    confirmacao = client.get(
        reverse("interface:retificacao-ato", args=[em_elaboracao.id, "submeter"])
    ).content.decode()
    assert COMBINAR in confirmacao, "e chega à tela de confirmação"


def test_a_retificacao_que_volta_a_uma_avaliacao_faz_a_advertencia_sumir(api_client, do_acervo):
    etapa = identificador(ETAPA_A1, 0)
    corrige = create_retification(
        api_client,
        do_acervo,
        [
            {
                "operation": "REPLACE",
                "targetPath": f"/stages/id={etapa}/evaluationsPerRegistration",
                "newValue": 1,
            }
        ],
        suffix="046-uma-leitura",
    )

    assert not [item for item in advertencias_do_ato(corrige) if COMBINAR in item.message]
