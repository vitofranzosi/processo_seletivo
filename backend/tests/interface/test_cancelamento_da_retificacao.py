"""O cancelamento da Retificação, que a decisão de governança fechou e ninguém alcançava (E2E-021).

**Por que existe.** A auditoria de 02/09/2026 encontrou o ato declarado em `atos_retificacao` com
a permissão `retificacao:cancelar`, e essa permissão **sem dono em `PAPEIS`** — o ato existia e
nenhum papel o alcançava. A decisão tomada ali fecha duas coisas: cancelar é do **Gestor**, pelo
mesmo espelho de `edital:cancelar`, e parte **apenas da elaboração**.

**A separação que sustenta o conjunto de uma situação só.** Cancelar abandona um ato em
preparação; devolver desfaz o avanço no fluxo de aprovação. Deixar o cancelamento atravessar a
revisão e a homologação faria uma pessoa só desfazer a aprovação de outra, e a trilha registraria
um ato onde houve dois.

```
EM_REVISAO ──devolver──▶ EM_ELABORACAO ──cancelar──▶ CANCELADA
HOMOLOGADA ──devolver──▶ EM_ELABORACAO ──cancelar──▶ CANCELADA
```
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

VAGAS = caminho_perfil("immediateVacancies")
MOTIVO = "A Diretoria desistiu da ampliação antes de submeter."


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def em_elaboracao(client, seletor_ligado, edital):
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**campos(vigente, **{VAGAS: "9"}), "justificativa": "Ampliação", "confirmar": "1"},
    )
    retificacao = Retificacao.objects.get()
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    return retificacao


def ato(client, retificacao, acao, **campos_extra):
    url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
    chave = client.get(url).context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, **campos_extra})


def detalhe(client, retificacao):
    url = reverse("interface:retificacao-detalhe", args=[retificacao.id])
    return client.get(url).content.decode()


def test_o_gestor_encontra_o_ato_que_a_permissao_sem_dono_escondia(client, em_elaboracao):
    identificar(client, "gestora", ["gestor"])

    assert "Cancelar Retificação" in detalhe(client, em_elaboracao)


def test_o_gestor_cancela_e_o_registro_permanece_no_historico(client, em_elaboracao):
    identificar(client, "gestora", ["gestor"])

    resposta = ato(client, em_elaboracao, "cancelar", motivo=MOTIVO)

    assert resposta.status_code == 302
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status == Retificacao.Status.CANCELADA
    assert Retificacao.objects.filter(pk=em_elaboracao.pk).exists()


def test_quem_elabora_nao_ganha_o_poder_de_eliminar_o_ato(client, em_elaboracao):
    """A segregação é o ponto da decisão, e não detalhe de tela."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    assert "Cancelar Retificação" not in detalhe(client, em_elaboracao)

    resposta = ato(client, em_elaboracao, "cancelar", motivo=MOTIVO)

    assert resposta.status_code in (403, 404)
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status == Retificacao.Status.EM_ELABORACAO


def test_submetida_deixa_de_oferecer_o_cancelamento_e_passa_a_exigir_a_devolucao(
    client, em_elaboracao
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    ato(client, em_elaboracao, "submeter")
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status == Retificacao.Status.EM_REVISAO

    identificar(client, "gestora", ["gestor"])

    assert "Cancelar Retificação" not in detalhe(client, em_elaboracao)
