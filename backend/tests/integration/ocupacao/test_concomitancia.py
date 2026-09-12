"""Quem concorre em duas listas ao mesmo tempo (016, US4, `FR-252`).

**O item 8.9 do 28/2026 é exclusão, e não transferência**, e é o achado que reescreveu este arquivo.
O texto do Edital é literal: o autodeclarado sorteado dentro das vagas de ampla *"não será computado
para efeito do preenchimento das vagas reservadas, isto é, não constará na lista de classificados
como autodeclarados, abrindo vaga para o próximo suplente autodeclarado"*.

Quantidade nenhuma muda de lista. Com 2 vagas amplas e 1 reservada, o efeito correto é 2 efetivas na
ampla com 1 ocupada, e 1 efetiva na reservada com **zero** ocupada — a vaga dela segue aberta ao
próximo autodeclarado. A primeira implementação modelava isso como movimento de quantidade e
produzia 1 e 2. O erro não era de conta: era de leitura.

**Estes testes percorrem o caminho positivo pelo serviço**, e não chamando o domínio direto — que é
o que faltava quando a US4 foi marcada como concluída pela primeira vez.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
from tests.fixtures.sorteio import MARCO

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def sorteado(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Certame de sorteio `2 / 1 / 1`, com **regra de corte e Etapa governada**.

    A Etapa governada é o que faltava: sem ela não há Resultado a ler, e ninguém consta ocupando —
    que era o único caso que a versão anterior deste arquivo provava.
    """
    # **Quatro sorteados e quatro vagas amplas**, de propósito: assim a faixa da ampla alcança
    # todos, e quem declarou cota está dentro dela de forma determinística — a ordem vem da chave
    # sorteada, e não se escolhe quem cai onde.
    return certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="conc-016",
        com_corte=True,
        quantos=4,
        geral=4,
    )


def apurar(certame, gestor, *, lista_id=None, chave="conc-016", motivo=""):
    return emitir_apuracao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-ocupacao-016",
        motivo=motivo,
    )


def habilitar(certame, inscricoes):
    """Consolida `HABILITADA` na Etapa governada — o fato que torna a vaga ocupada (`R-001`)."""
    from processo_seletivo.publicacoes.application.selectors import effective_version

    # **A versão consolidada é exigida pelo gatilho** `check_stage_result_source`: um Resultado
    # tem de citar a versão do próprio Edital, e a recusa é do banco, não da aplicação.
    versao = effective_version(edital_id=certame["edital"].id)
    for inscricao in inscricoes:
        ResultadoEtapa.objects.create(
            inscricao=inscricao,
            edital=certame["edital"],
            versao=versao,
            etapa_id=certame["etapa_governada"],
            # `OCORRENCIA`, e não `AVALIACAO`: a análise documental do sorteio não é avaliação
            # de banca — é fato observado sobre a documentação, que é o que aquela origem nomeia.
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="Documentação deferida",
            consolidado_em=timezone.now(),
            consolidado_por="teste",
        )


def emitir_cortes(certame, gestor):
    """Emite o corte de cada recorte, que é o que define a faixa de cada lista."""
    from processo_seletivo.classificacao.application.corte import calcular_corte
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )

    for indice, lista in enumerate((None, LISTA_PPI)):
        proposta = calcular_corte(
            edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
        )
        emitir_corte(
            actor=gestor,
            processo_id=certame["processo"].id,
            edital_id=certame["edital"].id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"conc-016-corte-{indice}",
            correlation_id="teste-ocupacao-016",
            confirmacao_do_calculo=assinatura_da_proposta(proposta),
        )


class TestOCaminhoPositivo:
    def test_o_cotista_ocupa_pela_ampla_e_nao_conta_na_reservada(self, sorteado, gestor):
        """**`FR-252` no caminho de verdade**, e é o número que o Edital manda.

        A ampla fica com 1 ocupada de 2; a reservada, com **0** de 1 — e a vaga dela segue aberta ao
        próximo autodeclarado, que é literalmente o que o item 8.9 diz.
        """
        emitir_cortes(sorteado, gestor)
        habilitar(sorteado, [sorteado["cotista_ppi"]])

        ampla = apurar(sorteado, gestor, chave="conc-016-ampla")
        cota = apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")

        assert (ampla["publicadas"], ampla["efetivas"], ampla["ocupadas"]) == (4, 4, 1)
        assert (cota["publicadas"], cota["efetivas"], cota["ocupadas"]) == (1, 1, 0)
        assert cota["faltando"] == 1, "a vaga reservada segue aberta ao próximo autodeclarado"

    def test_a_concomitancia_nao_cria_movimento_de_vaga(self, sorteado, gestor):
        """**Ela não move quantidade nenhuma**, e é o que a distingue da reversão.

        Um movimento aqui reduziria as efetivas da ampla e aumentaria as da reservada — 1 e 2 onde o
        Edital manda 2 e 1.
        """
        emitir_cortes(sorteado, gestor)
        habilitar(sorteado, [sorteado["cotista_ppi"]])

        apurar(sorteado, gestor, chave="conc-016-ampla")
        apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")

        assert MovimentoDeVaga.objects.count() == 0

    def test_quem_nao_declarou_cota_conta_normalmente_na_ampla(self, sorteado, gestor):
        """A exclusão alcança **só** quem concorre nas duas listas."""
        emitir_cortes(sorteado, gestor)
        habilitar(sorteado, [sorteado["inscricoes"][2]])

        ampla = apurar(sorteado, gestor, chave="conc-016-ampla")

        assert ampla["ocupadas"] == 1

    def test_reapurar_nao_duplica_nem_muda_o_numero(self, sorteado, gestor):
        """**Reemitir é idempotente no efeito.**

        A exclusão é recalculada do zero sobre o mesmo estado — não acumula. E como ela não cria
        movimento, não há o que duplicar.
        """
        emitir_cortes(sorteado, gestor)
        habilitar(sorteado, [sorteado["cotista_ppi"]])
        apurar(sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi")

        segunda = apurar(
            sorteado, gestor, lista_id=LISTA_PPI, chave="conc-016-ppi-2", motivo="Reanálise"
        )

        assert (segunda["efetivas"], segunda["ocupadas"]) == (1, 0)
        assert MovimentoDeVaga.objects.count() == 0
        assert ApuracaoDeOcupacao.objects.filter(lista_id=uuid.UUID(LISTA_PPI)).count() == 2


class TestEsgotamentoDaReserva:
    """`T053`: esgotada a reserva, é a **reversão** que decide o saldo — não a concomitância."""

    @pytest.fixture
    def com_reversao(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        return certame_sorteado_com_quadro(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            prefixo="esgot-016",
            com_corte=True,
            quantos=4,
            geral=4,
            reversao=nomes.REVERSAO_POR_SALDO,
        )

    def test_a_reserva_esgotada_pela_concomitancia_cede_o_saldo(self, com_reversao, gestor):
        """**As duas regras compostas, e é o cenário que a `T053` pede.**

        O único autodeclarado de PPI ocupa pela ampla, logo não conta na reservada: a reserva fica
        com 1 publicada e 0 ocupada. Declarada a reversão por saldo, essa vaga é cedida à ampla.

        A ordem é a do Edital: primeiro a concomitância decide que ele não ocupou a reservada;
        depois a reversão decide o que fazer com a vaga que sobrou.
        """
        emitir_cortes(com_reversao, gestor)
        habilitar(com_reversao, [com_reversao["cotista_ppi"]])
        apurar(com_reversao, gestor, chave="esgot-016-ampla")

        cota = apurar(com_reversao, gestor, lista_id=LISTA_PPI, chave="esgot-016-ppi")

        assert cota["ocupadas"] == 0, "ele ocupou pela ampla, não aqui"
        assert cota["reverteu"] == 1, "e o saldo foi cedido"
        # **A apuração da origem nasce com a efetiva líquida.**
        assert cota["efetivas"] == 0
        depois = apurar(com_reversao, gestor, chave="esgot-016-ampla-2", motivo="Reversão recebida")
        assert (depois["publicadas"], depois["efetivas"]) == (4, 5)

    def test_a_apuracao_de_origem_nao_nasce_obsoleta(self, com_reversao, gestor):
        """**O defeito que o id gerado antes da apuração corrige.**

        O movimento que a apuração causa entra nos **próprios** `movimentosLidos`. Sem isso,
        `_movimento_posterior` via um movimento fora da lista lida e declarava obsoleta a apuração
        que acabara de ser emitida.
        """
        emitir_cortes(com_reversao, gestor)
        apurar(com_reversao, gestor, lista_id=LISTA_PPI, chave="esgot-016-ppi")

        leitura = selectors.ocupacao_do_recorte(
            edital=com_reversao["edital"],
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=LISTA_PPI,
        )

        assert leitura["estado"] == nomes.VIGENTE, leitura["causasDeObsolescencia"]

    def test_reapurar_a_cota_nao_reverte_de_novo(self, com_reversao, gestor):
        """**A guarda contra duplicação, e ela é aritmética.**

        O saldo sai das **efetivas**, não das publicadas. Cedidas todas, a apuração seguinte lê o
        movimento, chega com efetiva zero, e o saldo dá zero. Partir de `publicadas` faria cada nova
        apuração ceder a mesma vaga outra vez.
        """
        emitir_cortes(com_reversao, gestor)
        primeira = apurar(com_reversao, gestor, lista_id=LISTA_PPI, chave="esgot-016-ppi")
        assert primeira["reverteu"] == 1

        segunda = apurar(
            com_reversao, gestor, lista_id=LISTA_PPI, chave="esgot-016-ppi-2", motivo="Reanálise"
        )

        assert segunda["reverteu"] == 0
        assert MovimentoDeVaga.objects.count() == 1
