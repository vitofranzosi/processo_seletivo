"""A tela de condução fala a língua do canal (125, US3, FR-4000, D-007).

Na publicação, quem conduz **registra** onde publicou, e é esse registro que mostra a convocação ao
candidato. A tela dizia *"Sem comunicação enviada"*, *"Emitir a comunicação"* e *"Enviada em"* — e
nada sobre o candidato ainda não ver. A mensagem continua com as frases de sempre (FR-4002).
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

REFERENCIA = "site do certame, 06/11/2026"
DO_ENVIO = (
    "Sem comunicação enviada",
    "Emitir a comunicação",
    "Comunicações que ainda não saíram",
    "contado do envio da comunicação",
    "a comunicação ainda não foi enviada com sucesso",
    "A comunicação sai no mesmo ato.",
)


@pytest.fixture
def por_publicacao(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    certame = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="gestao-125",
        forma=FORMA_POR_PUBLICACAO,
    )
    pessoa, convocacao = cenarios.convocar_primeira(
        certame, gestor, chave="gestao-125", vencimento=timezone.now() + timedelta(days=5)
    )
    return certame[0], pessoa, convocacao


def _abrir(client, edital):
    return client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()


def test_sem_registro_a_tela_diz_publicacao_e_que_o_candidato_nao_ve(
    client, seletor_ligado, por_publicacao
):
    edital, _, _ = por_publicacao
    identificar(client, "carlos", ["gestor"])

    pagina = _abrir(client, edital)

    assert "Publicação não registrada" in pagina
    assert "o candidato ainda não vê esta convocação" in pagina
    assert "Publicações a registrar" in pagina
    assert "Registrar a publicação" in pagina
    for frase in DO_ENVIO:
        assert frase not in pagina, frase


def test_registrada_a_tela_diz_onde_e_nao_enviada_em(client, seletor_ligado, por_publicacao):
    edital, _, convocacao = por_publicacao
    identificar(client, "carlos", ["gestor"])
    resposta = client.post(
        reverse("interface:comunicar-convocacao", args=[edital.id, MARCO, convocacao.id]),
        {"chave": "gestao-125-pub", "referencia_da_publicacao": REFERENCIA},
    )
    pagina = client.get(resposta["Location"]).content.decode()

    assert f"Publicação registrada: {REFERENCIA}" in pagina
    assert "o candidato já vê a convocação no portal" in pagina
    assert "Publicação registrada em" in pagina and f"— {REFERENCIA}" in pagina
    assert "contado do registro da publicação" in pagina
    assert "Comunicação enviada." not in pagina
    assert "<dt>Enviada em</dt>" not in pagina


def test_o_historico_diz_publicada(client, seletor_ligado, por_publicacao, gestor):
    from processo_seletivo.convocacao.application.comunicar import comunicar

    edital, _, convocacao = por_publicacao
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key="gestao-125-hist",
        correlation_id="teste-125",
        referencia_da_publicacao=REFERENCIA,
    )
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(
        reverse("interface:convocacao-historico", args=[edital.id, MARCO])
    ).content.decode()

    assert f"publicada em {REFERENCIA}" in pagina
    assert "não enviada" not in pagina
