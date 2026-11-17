"""A data de nascimento não sai para onde não foi pedida (180, FR-8311, SC-2903).

Uma jornada inteira com uma data que não se confunde com nenhuma outra da tela — informada em "Seus
dados", congelada no envio, conferida pela gestão —, e depois a pergunta: onde ela ficou? Nas duas
colunas e na página da conferência, e em mais nada. Nem página pública, nem comprovante, nem trilha,
nem registro técnico.

**O que este arquivo não percorre são as publicações do certame** (resultado, convocados, inscrições
publicadas): montá-las aqui custaria o cenário de três features para provar uma ausência. Quem as
cobre é `tests/unit/identidade/test_data_nao_decide_identidade.py`, pela lista de quem lê a coluna —
nenhum módulo de publicação está nela, e um que entrar reprova lá.
"""

import logging
from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import CPF_MARIA, MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL
from tests.interface.conftest import identificar as identificar_na_gestao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: Uma data que nenhum outro dado do cenário produz: o Edital é de 2026, e as fixtures nascem em
#: 2000.
NASCIMENTO = date(1987, 3, 9)
#: As formas em que ela poderia escapar: como a pessoa digitou, como o banco guarda, e por extenso.
FORMAS = ("09/03/1987", "1987-03-09", "9 de março de 1987", "09 de março de 1987", "09.03.1987")


def _sem_a_data(texto):
    return not any(forma in texto for forma in FORMAS)


@pytest.fixture
def registro_tecnico():
    """O que os loggers da aplicação emitiram — `caplog` não serve: `propagate` é falso."""

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__()
            self.linhas = []

        def emit(self, registro):
            self.linhas.append(self.format(registro))

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo")
    anterior = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(coletor)
    yield coletor
    logger.removeHandler(coletor)
    logger.setLevel(anterior)


@pytest.fixture
def jornada(client, settings, selecao, inscricao_de_maria, registro_tecnico):
    """Do cadastro à conferência, pelas telas: é por elas que um vazamento aconteceria."""
    identificar(client, MARIA)
    gravada = client.post(
        reverse("portal:meus-dados"),
        {"nome": MARIA.nome, "cpf": CPF_MARIA, "data_nascimento": "09/03/1987"},
    )
    assert gravada.status_code == 302, gravada.content
    assert CandidateIdentity.objects.get(subject=MARIA.subject).data_nascimento == NASCIMENTO

    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    enviada = client.post(
        reverse("portal:revisao", args=[inscricao.id]), {"veracidade": "on", "ciencia": "on"}
    )
    assert enviada.status_code == 302, enviada.content
    inscricao.refresh_from_db()
    assert inscricao.status == Inscricao.Status.SUBMETIDA
    assert inscricao.data_nascimento == NASCIMENTO

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    gestao = Client()
    identificar_na_gestao(gestao, "bruno.gestor", ["gestor"])
    conferencia = gestao.post(
        reverse("interface:conferir-identidade", args=[inscricao.id]),
        {"motivo": "Dúvida sobre o titular, a pedido da comissão."},
    )
    assert "09/03/1987" in conferencia.content.decode(), "a conferência é o lugar onde ela aparece"
    return {
        "edital": selecao,
        "inscricao": inscricao,
        "candidato": client,
        "gestao": gestao,
        "registro_tecnico": registro_tecnico,
    }


def test_nenhuma_pagina_publica_mostra_a_data(jornada):
    """SC-2903: quem não se identificou não encontra a data em lugar nenhum."""
    anonimo = Client()

    for endereco in (
        reverse("portal:vitrine"),
        reverse("portal:selecao", args=[jornada["edital"].id]),
    ):
        resposta = anonimo.get(endereco)
        assert resposta.status_code == 200, endereco
        assert _sem_a_data(resposta.content.decode()), endereco


def test_o_que_o_candidato_leva_consigo_nao_mostra_a_data(jornada):
    """O comprovante e a lista das inscrições circulam: identificam por nome e CPF, e basta."""
    inscricao = jornada["inscricao"]

    for endereco in (
        reverse("portal:comprovante", args=[inscricao.id]),
        reverse("portal:inscricoes"),
        reverse("portal:acompanhamento", args=[inscricao.id]),
    ):
        resposta = jornada["candidato"].get(endereco)
        assert resposta.status_code == 200, endereco
        assert _sem_a_data(resposta.content.decode()), endereco


def test_as_telas_da_gestao_nao_mostram_a_data_fora_da_conferencia(jornada):
    """FR-8312: a lista e o dossiê continuam sem ela; só o ato com motivo a revela."""
    inscricao = jornada["inscricao"]

    for endereco in (
        reverse("interface:inscricoes", args=[jornada["edital"].id]),
        reverse("interface:inscricao-recebida", args=[inscricao.id]),
    ):
        resposta = jornada["gestao"].get(endereco)
        assert resposta.status_code == 200, endereco
        assert _sem_a_data(resposta.content.decode()), endereco


def test_nenhum_registro_de_auditoria_da_jornada_guarda_a_data(jornada):
    """FR-8311 e FR-8316: a trilha referencia o ato, e não copia o dado."""
    registros = list(RegistroAuditoria.objects.all())

    assert registros, "a jornada não deixou trilha nenhuma — o teste não estaria medindo nada"
    assert {"CONFERIR_IDENTIDADE"} <= {registro.operation for registro in registros}
    for registro in registros:
        tudo = " ".join(
            str(valor)
            for valor in (
                registro.reason,
                registro.detalhe,
                registro.previous_state,
                registro.new_state,
                registro.idempotency_key,
                registro.correlation_id,
            )
        )
        assert _sem_a_data(tudo), registro.operation


def test_o_registro_tecnico_da_jornada_nao_guarda_a_data(jornada):
    """O log de aplicação é registro técnico como a trilha, e vai para mais mãos do que ela."""
    emitido = "\n".join(jornada["registro_tecnico"].linhas)

    assert _sem_a_data(emitido)
