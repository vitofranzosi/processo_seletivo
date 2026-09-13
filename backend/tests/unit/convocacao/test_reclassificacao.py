"""A reclassificação: o ausente vai para o fim da fila, e volta depois (019, `US4`, `FR-291`).

**É o 69/2026, e hoje ele precisa de planilha paralela.** O Edital manda que quem não comparece à
chamada seja reclassificado para o fim da lista e possa ser convocado de novo depois — e nenhum
sistema guarda essa posição nova. Quem a guarda é uma coluna à parte, num arquivo que alguém mantém.

**E a reclassificação NÃO afirma perda de habilitação** (`D-008`). A pessoa continua habilitada:
o que ela perdeu foi a vez. Tratá-la como eliminação seria decidir, por conta própria, uma
consequência que o Edital não escreveu — e que tiraria dela a chance que ele lhe dá.
"""

import pytest

from processo_seletivo.convocacao.domain import fila, nomes

FAIXA = ["p1", "p2", "p3", "p4"]


class TestOReclassificadoVaiParaOFim:
    def test_passa_a_constar_depois_do_ultimo_suplente(self):
        """`T072`: o fim da fila, e não a posição seguinte à dele."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reclassificados={"p1"})

        assert chamaveis == ["p2", "p3", "p4", "p1"]

    def test_dois_reclassificados_mantem_a_ordem_entre_si(self):
        """Entre eles vale a ordem de classificação: reclassificar não reordena o certame."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reclassificados={"p1", "p2"})

        assert chamaveis == ["p3", "p4", "p1", "p2"]

    def test_o_reclassificado_continua_na_fila(self):
        """**Ele não sai**, e é o que o distingue dos quatro desfechos que encerram.

        Sair seria perda de habilitação por outro nome — e a `D-008` a proíbe.
        """
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reclassificados={"p1"})

        assert "p1" in chamaveis

    def test_esgotada_a_fila_ele_e_o_proximo(self):
        """É a promessa do Edital cumprida: depois do último suplente, ele volta."""
        chamaveis = fila.ordem_de_chamada(
            alcancados_em_ordem=FAIXA, reclassificados={"p1"}, servidos={"p2", "p3", "p4"}
        )

        assert fila.proximo(chamaveis) == "p1"


class TestAReclassificacaoNaoAfirmaPerdaDeHabilitacao:
    """`T074`, `D-008`: a pessoa continua habilitada — o que ela perdeu foi a vez."""

    def test_nao_esta_entre_os_desfechos_que_encerram(self):
        assert nomes.RECLASSIFICACAO not in fila.DESFECHOS_QUE_ENCERRAM

    def test_o_efeito_dela_na_contagem_e_exclusao_e_nao_eliminacao(self):
        """**Exclusão do conjunto de ocupantes, e nada além disso.**

        Ela deixa de ocupar a vaga — porque não compareceu para ocupá-la —, e o Resultado da Etapa
        dela não é tocado. Produzir um Resultado `ELIMINADA` aqui seria a `019` decidindo
        habilitação, que é da `013`.
        """
        from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

        assert nomes.EFEITO_POR_DESFECHO[nomes.RECLASSIFICACAO] == nomes_da_ocupacao.EFEITO_EXCLUSAO

    def test_o_desfecho_de_reclassificacao_nao_exige_atestado_nem_sucessor(self):
        """As duas constraints de forma alcançam a inércia e a regularização — não esta.

        Exigir atestado aqui confundiria não comparecer com fato externo atestado por terceiro; e
        exigir Resultado sucessor faria a reclassificação mexer na habilitação.
        """
        from processo_seletivo.convocacao.models import DesfechoDaConvocacao

        formas = {c.name: str(c.condition) for c in DesfechoDaConvocacao._meta.constraints}

        assert nomes.INERCIA in formas["ck_desfecho_inercia_exige_atestado"]
        assert nomes.REGULARIZACAO in formas["ck_desfecho_regularizacao_exige_sucessor"]
        assert nomes.RECLASSIFICACAO not in formas["ck_desfecho_inercia_exige_atestado"]
        assert nomes.RECLASSIFICACAO not in formas["ck_desfecho_regularizacao_exige_sucessor"]


class TestARecusaAntesDoEsgotamento:
    """`T073`, `reclassificado_antes_do_esgotamento`.

    Chamá-lo antes de quem nunca foi chamado inverteria a consequência da reclassificação: quem não
    compareceu passaria à frente de quem estava esperando, e ela viraria vantagem.
    """

    def recusar(self, *, inscricao, fila_atual, reclassificados):
        from processo_seletivo.convocacao.application.convocar import (
            _recusar_reclassificado_antes_do_esgotamento,
        )

        _recusar_reclassificado_antes_do_esgotamento(
            {"fila": fila_atual, "reclassificados": reclassificados}, inscricao=inscricao
        )

    def test_com_gente_ainda_nao_chamada_a_recusa_dispara(self):
        from processo_seletivo.shared.api.problems import DomainError

        with pytest.raises(DomainError) as erro:
            self.recusar(inscricao="p1", fila_atual=["p2", "p3", "p1"], reclassificados={"p1"})

        assert erro.value.code == nomes.RECLASSIFICADO_ANTES_DO_ESGOTAMENTO
        assert "2 Inscrição" in erro.value.detail

    def test_esgotados_os_demais_ele_passa(self):
        self.recusar(inscricao="p1", fila_atual=["p1"], reclassificados={"p1"})

    def test_quem_nao_foi_reclassificado_nao_passa_por_esta_recusa(self):
        self.recusar(inscricao="p2", fila_atual=["p2", "p3", "p1"], reclassificados={"p1"})

    def test_entre_dois_reclassificados_a_recusa_nao_impede_o_primeiro(self):
        """Esgotados os não reclassificados, a fila deles corre na ordem de classificação."""
        self.recusar(inscricao="p1", fila_atual=["p1", "p2"], reclassificados={"p1", "p2"})
