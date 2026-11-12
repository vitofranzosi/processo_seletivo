"""Os desfazimentos da destinação e da declaração de não preenchida (155, T035, US6, R-005).

Sem chamada dependente, o ato contrário fica ao lado do original e a soma volta; com ela, o pedido
é recusado com 409 **e fica na trilha**, com as chamadas nomeadas, e nada é desfeito (FR-6335). As
chamadas chegam por *callable*, como no ato: a composição pela condução tem o caso dela na tela.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.destinacao import (
    desfazer_destinacao,
    desfazer_nao_preenchida,
    previa_do_desfazimento_da_destinacao,
    previa_do_desfazimento_da_nao_preenchida,
)
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga, VagaNaoPreenchida
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_concomitancia import apurar
from tests.integration.ocupacao.test_destinacao import destinar, esgotado
from tests.integration.ocupacao.test_nao_preenchida import declarar

pytestmark = pytest.mark.django_db(transaction=True)

CHAMADA = {
    "id": "00000000-0000-4000-8000-00000000c155",
    "rotulo": "P-0701 — Fulana",
    "ocupa": False,
}


def nenhuma(**_):
    return []


def com_chamada(**_):
    return [CHAMADA]


@pytest.fixture
def destinada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    certame = esgotado(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "desf-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    destinar(certame, gestor, chave="desf-155-destinar")
    return certame


@pytest.fixture
def declarada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    certame = esgotado(
        gestor, api_client, manager_headers, process_payload, "desf-np-155", reversao=None
    )
    declarar(certame, gestor, chave="desf-np-155-declarar")
    return certame


def vigente(certame, lista_id):
    return selectors.apuracao_vigente(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )


def desfazer(certame, gestor, *, chamadas=nenhuma, chave="desf-155-ato", motivo="Engano"):
    movimento = MovimentoDeVaga.objects.get(especie=nomes.MOVIMENTO_REVERSAO)
    assinatura = previa_do_desfazimento_da_destinacao(
        edital=certame["edital"], movimento_id=movimento.id, chamadas_dependentes=chamadas
    )["assinatura"]
    return desfazer_destinacao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        movimento_id=movimento.id,
        motivo=motivo,
        assinatura=assinatura,
        chamadas_dependentes=chamadas,
        idempotency_key=chave,
        correlation_id="teste-155-desf",
    )


def desfazer_a_declaracao(
    certame, gestor, *, chamadas=nenhuma, chave="desf-np-155-ato", motivo="Engano"
):
    declaracao = VagaNaoPreenchida.objects.get(especie=nomes.NAO_PREENCHIDA_DECLARACAO)
    assinatura = previa_do_desfazimento_da_nao_preenchida(
        edital=certame["edital"], declaracao_id=declaracao.id, chamadas_dependentes=chamadas
    )["assinatura"]
    return desfazer_nao_preenchida(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        declaracao_id=declaracao.id,
        motivo=motivo,
        assinatura=assinatura,
        chamadas_dependentes=chamadas,
        idempotency_key=chave,
        correlation_id="teste-155-desf",
    )


def recusa(funcao, *args, **kwargs):
    with pytest.raises(DomainError) as erro:
        funcao(*args, **kwargs)
    return erro.value


class TestDesfazerADestinacao:
    def test_os_dois_registros_ficam_e_a_soma_volta(self, destinada, gestor):
        """FR-6334, FR-6336, SC-2106: o contrário cita o original, e as efetivas voltam."""
        original = MovimentoDeVaga.objects.get()

        declarado = desfazer(destinada, gestor)

        contrario = MovimentoDeVaga.objects.get(especie=nomes.MOVIMENTO_DESFAZIMENTO)
        assert MovimentoDeVaga.objects.count() == 2
        assert contrario.desfaz_id == original.id
        assert (contrario.origem_lista_id, str(contrario.destino_lista_id)) == (None, LISTA_PPI)
        assert contrario.quantidade == original.quantidade == declarado["quantidade"]
        assert contrario.fundamento == "Engano"
        assert declarado["apuracaoSeguinte"] is not None, declarado["apuracaoPendente"]
        reserva = vigente(destinada, LISTA_PPI)
        assert (reserva.efetivas, reserva.faltando) == (1, 1), "a origem volta a ter a vaga"
        apurar(destinada, gestor, chave="desf-155-ampla-depois", motivo="Destinação desfeita")
        assert vigente(destinada, None).efetivas + reserva.efetivas == 2

    def test_a_trilha_registra_o_desfazimento(self, destinada, gestor):
        desfazer(destinada, gestor)

        registro = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZER_DESTINACAO")
        assert registro.correlation_id == "teste-155-desf"
        assert "Motivo: Engano" in registro.reason

    def test_sem_motivo_recusa(self, destinada, gestor):
        erro = recusa(desfazer, destinada, gestor, motivo="  ")
        assert (erro.code, erro.status) == (nomes.MOTIVO_OBRIGATORIO, 422)
        assert MovimentoDeVaga.objects.count() == 1

    def test_o_desfeito_nao_se_desfaz_de_novo(self, destinada, gestor):
        desfazer(destinada, gestor)

        erro = recusa(desfazer, destinada, gestor, chave="desf-155-ato-2")

        assert erro.code == nomes.ATO_JA_DESFEITO
        assert MovimentoDeVaga.objects.count() == 2

    def test_com_chamada_dependente_recusa_registra_e_nada_desfaz(self, destinada, gestor):
        """FR-6335: 409, o evento com as chamadas, e nenhum movimento contrário."""
        erro = recusa(desfazer, destinada, gestor, chamadas=com_chamada)

        assert (erro.code, erro.status) == (nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE, 409)
        assert "P-0701 — Fulana" in erro.detail and "precisa do seu desfecho antes" in erro.detail
        assert MovimentoDeVaga.objects.count() == 1
        evento = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZIMENTO_IMPEDIDO")
        assert evento.detalhe["chamadas"] == [CHAMADA]
        assert "P-0701 — Fulana" in evento.reason
        assert evento.correlation_id == "teste-155-desf"

    def test_a_repeticao_da_recusa_nao_grava_outro_evento(self, destinada, gestor):
        recusa(desfazer, destinada, gestor, chamadas=com_chamada)

        erro = recusa(desfazer, destinada, gestor, chamadas=com_chamada)

        assert erro.code == nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE
        assert (
            RegistroAuditoria.objects.filter(operation="OCUPACAO_DESFAZIMENTO_IMPEDIDO").count()
            == 1
        )

    def test_a_ampla_que_declarou_a_vaga_recebida_nao_a_devolve(self, destinada, gestor):
        """A declaração na ampla leu o movimento: desfazê-lo passaria das vagas dela."""
        from tests.integration.ocupacao.test_nao_preenchida import sem_ninguem_na_ampla

        sem_ninguem_na_ampla(destinada, gestor, "desf-ampla")
        declarar(destinada, gestor, lista_id=None, chave="desf-ampla-declarar")

        erro = recusa(desfazer, destinada, gestor)

        assert erro.code == nomes.DESTINACAO_COM_DECLARACAO_DEPENDENTE
        assert MovimentoDeVaga.objects.count() == 1


class TestDesfazerANaoPreenchida:
    def test_os_dois_registros_ficam_e_a_vaga_volta_a_ocupar(self, declarada, gestor):
        original = VagaNaoPreenchida.objects.get()

        declarado = desfazer_a_declaracao(declarada, gestor)

        contrario = VagaNaoPreenchida.objects.get(especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO)
        assert VagaNaoPreenchida.objects.count() == 2
        assert (contrario.desfaz_id, contrario.quantidade) == (original.id, original.quantidade)
        assert declarado["apuracaoSeguinte"] is not None, declarado["apuracaoPendente"]
        reserva = vigente(declarada, LISTA_PPI)
        assert (reserva.nao_preenchidas, reserva.faltando) == (0, 1)
        assert RegistroAuditoria.objects.filter(
            operation="OCUPACAO_DESFAZER_NAO_PREENCHIDA"
        ).exists()

    def test_o_desfeito_nao_se_desfaz_de_novo(self, declarada, gestor):
        desfazer_a_declaracao(declarada, gestor)

        erro = recusa(desfazer_a_declaracao, declarada, gestor, chave="desf-np-155-ato-2")

        assert erro.code == nomes.ATO_JA_DESFEITO

    def test_com_chamada_dependente_recusa_registra_e_nada_desfaz(self, declarada, gestor):
        erro = recusa(desfazer_a_declaracao, declarada, gestor, chamadas=com_chamada)

        assert (erro.code, erro.status) == (nomes.DESTINACAO_COM_CHAMADA_DEPENDENTE, 409)
        assert VagaNaoPreenchida.objects.count() == 1
        evento = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZIMENTO_IMPEDIDO")
        assert evento.detalhe["chamadas"] == [CHAMADA]

    def test_a_pergunta_e_a_do_proprio_recorte_pela_declaracao(self, declarada, gestor):
        """R-005: a chamada dependente é a do recorte da declaração, que leu a declaração."""
        perguntas = []

        def registrar(**pergunta):
            perguntas.append(pergunta)
            return []

        desfazer_a_declaracao(declarada, gestor, chamadas=registrar)

        declaracao = VagaNaoPreenchida.objects.get(especie=nomes.NAO_PREENCHIDA_DECLARACAO)
        assert {str(p["lista_id"]) for p in perguntas} == {LISTA_PPI}
        assert {p["nao_preenchida_id"] for p in perguntas} == {declaracao.id}
        assert {p["movimento_id"] for p in perguntas} == {None}
