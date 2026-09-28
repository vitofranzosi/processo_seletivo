"""RC-112 da auditoria de consolidação (`A-1` da `046`) — a Ocorrência que trava a Etapa seguinte.

**Este arquivo prende o comportamento de hoje, e não o desejado.** O desejado não está decidido:
o `FR-004` da `013` manda exatamente o que acontece aqui — basta um Resultado na Etapa anterior
para exigir habilitação nela —, e a `D-003` justifica o gate com o caso que ele não cobre ("sem
ele, Etapa anterior de leitura múltipla [...] deixaria a Etapa seguinte permanentemente sem
participantes").
Os dois textos se contradizem só quando a Ocorrência entra, e a escolha entre eles é do usuário
(`doc/achado-ocorrencia-trava-a-etapa-seguinte.md`). Decidida, este arquivo muda junto.

A cadeia, nos dois cenários: a Etapa anterior não se consolida — a regra a recusa por inteiro —, a
Ocorrência passa mesmo assim (`013`, `D-1`, item 6: "Uma Etapa impedida de consolidar continua
podendo registrar que alguém não compareceu") e produz `ELIMINADA`; o primeiro Resultado acorda a
exigência de habilitação, e ninguém mais pode obter `HABILITADA` ali, porque o único outro caminho
é a consolidação, que continua recusando.
"""

import pytest

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.resultados.application.prontidao import participacao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import ETAPA_A1, ETAPA_A2, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import publish_original
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def presidente():
    return ator_institucional("maria")


def edital_com_decisoria_nao_eliminatoria(gestor, api_client, manager_headers, *, seed):
    """O caso que a `046` ainda publica: decisória e não eliminatória, sem marco que a cite.

    A consolidação a recusa por inteiro, e a publicação só avisa (`FR-748`): nada no fluxo publicado
    exige o Resultado dela. É por isso que o achado não ficou restrito ao acervo.
    """
    rascunho = rascunho_com_etapas(seed, avaliacoes=1, decisoria=True)
    rascunho["stages"][0]["eliminatory"] = False
    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{seed:04d}"},
        {
            "institutionalCode": f"PS-2026-{seed}",
            "title": f"Processo {seed}",
            "firstEdital": {"number": str(seed), "year": 2026, "title": f"Edital {seed}"},
        },
        draft=rascunho,
    )
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=f"rc112-{seed}")
    return {
        "edital": edital,
        "processo": edital.processo,
        "primeira": identificador(ETAPA_A1, seed),
        "segunda": identificador(ETAPA_A2, seed),
    }


def percorrer(cenario, presidente, *, codigo_da_recusa):
    edital = cenario["edital"]
    faltante, *demais = inscrever(edital, 3, primeiro=1)

    # Antes da Ocorrência, o gate está dormente e a Etapa seguinte recebe todos (`FR-004`).
    participantes, _, aguardando = participacao(edital=edital, etapa_id=cenario["segunda"])
    assert {i.id for i in demais} <= participantes
    assert aguardando == set()

    # A anterior não se consolida para ninguém — nem para quem compareceu.
    with pytest.raises(DomainError) as recusa:
        consolidar(
            actor=presidente,
            processo_id=cenario["processo"].id,
            edital_id=edital.id,
            etapa_id=cenario["primeira"],
            inscricao_ids=[demais[0].id],
            idempotency_key=f"c-{edital.id}",
            correlation_id="rc-112",
        )
    assert recusa.value.code == codigo_da_recusa

    # Mas a Ocorrência passa, e elimina.
    desfecho = registrar_ocorrencia(
        actor=presidente,
        processo_id=cenario["processo"].id,
        edital_id=edital.id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[faltante.id],
        motivo="não compareceu",
        idempotency_key=f"o-{edital.id}",
        correlation_id="rc-112",
    )
    assert desfecho["feitas"] == 1

    # O primeiro Resultado acordou a exigência de habilitação, e quem compareceu fica esperando uma
    # habilitação que a Etapa anterior não tem como produzir.
    participantes, eliminadas, aguardando = participacao(edital=edital, etapa_id=cenario["segunda"])
    assert faltante.id in eliminadas
    assert aguardando == {i.id for i in demais}
    assert participantes == set()


def test_edital_novo_decisoria_nao_eliminatoria_trava_a_seguinte(
    gestor, api_client, manager_headers, presidente
):
    cenario = edital_com_decisoria_nao_eliminatoria(gestor, api_client, manager_headers, seed=1120)
    percorrer(cenario, presidente, codigo_da_recusa="regra_insuficiente")


def test_acervo_de_leitura_multipla_trava_a_seguinte(
    gestor, api_client, manager_headers, presidente
):
    """O caso que a `D-003` nomeia: o gate existe para este Edital, e a Ocorrência o desarma."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1121, codigo="1121", avaliacoes=2
    )
    percorrer(cenario, presidente, codigo_da_recusa="regra_de_combinacao_ausente")
