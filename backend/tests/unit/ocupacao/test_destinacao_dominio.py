"""A condição do esgotamento, os impedimentos e a situação, sem banco (155, T019, R-004).

Cada caso é um dos que a US3 nomeia, e os números são escritos à mão: a ordem da reserva é `p1` a
`p4`, e a vaga que sobra é uma.
"""

from datetime import UTC, datetime

from processo_seletivo.ocupacao.domain import destinacao, nomes

ORDEM = [("p1", 1), ("p2", 2), ("p3", 3), ("p4", 4)]


def restantes(**fatos):
    return destinacao.quem_ainda_pode_ocupar(**{"posicoes": ORDEM, **fatos})


class TestQuemAindaPodeOcupar:
    def test_toda_a_ordem_alcancavel_e_livre(self):
        assert restantes() == ["p1", "p2", "p3", "p4"]

    def test_posicao_vazia_nao_conta(self):
        """V-5: eliminado antes da ordem fica sem posição, e não é quem ocupar."""
        assert destinacao.ainda_podem_ocupar(posicoes=[("p1", None), ("p2", None)]) == 0

    def test_excluido_por_desfecho_nao_conta(self):
        """V-1: quem saiu por desfecho tem posição e não ocupa mais nada pela reserva."""
        assert restantes(excluidos={"p1", "p2", "p3", "p4"}) == []

    def test_o_ultimo_efeito_de_cada_pessoa_vence(self):
        efeitos = [
            (nomes.EFEITO_EXCLUSAO, "p1"),
            (nomes.EFEITO_INCLUSAO, "p1"),
            (nomes.EFEITO_EXCLUSAO, "p2"),
        ]
        assert destinacao.excluidos_por_efeito(efeitos) == {"p2"}
        assert destinacao.incluidos_por_efeito(efeitos) == {"p1"}

    def test_ocupante_da_ampla_confirmado_nao_conta(self):
        """V-4: quem confirmou a ocupação pela ampla não ocupa a reserva."""
        assert restantes(ocupam_a_ampla_confirmados={"p1", "p2", "p3", "p4"}) == []

    def test_ocupante_da_ampla_sem_confirmacao_conta(self):
        """US3.2: a ocupação pela ampla ainda pode mudar, e a pessoa continua contando."""
        assert restantes(excluidos={"p2", "p3", "p4"}) == ["p1"]

    def test_inabilitado_nao_conta(self):
        """V-2, tratada como eliminação (155, D-007)."""
        assert restantes(inabilitados={"p1", "p2", "p3", "p4"}) == []

    def test_fora_da_faixa_sem_continuacao_nao_conta(self):
        assert restantes(alcancaveis={"p1", "p2"}, excluidos={"p1", "p2"}) == []

    def test_fora_da_faixa_com_continuacao_conta(self):
        """US3.7: com continuação admitida, a ordem inteira; o caminho é a faixa seguinte."""
        assert restantes(alcancaveis=None, excluidos={"p1", "p2"}) == ["p3", "p4"]

    def test_quem_ja_ocupa_a_reserva_nao_conta_para_a_vaga_que_sobra(self):
        assert restantes(ocupantes={"p1"}, excluidos={"p2", "p3", "p4"}) == []

    def test_identidades_de_tipos_diferentes_comparam_igual(self):
        import uuid

        pessoa = uuid.uuid4()
        assert (
            destinacao.quem_ainda_pode_ocupar(posicoes=[(pessoa, 1)], excluidos={str(pessoa)}) == []
        )


class TestImpedimentos:
    def definitivo(self, **fatos):
        return destinacao.impedimentos({"natureza_do_resultado": "DEFINITIVA", **fatos})

    def test_definitivo_e_nada_pendente_nao_impede(self):
        assert self.definitivo() == []

    def test_resultado_provisorio_impede(self):
        codigos = [
            i.codigo for i in destinacao.impedimentos({"natureza_do_resultado": "PRELIMINAR"})
        ]
        assert codigos == [destinacao.RESULTADO_NAO_DEFINITIVO]

    def test_resultado_nao_divulgado_impede(self):
        (impedimento,) = destinacao.impedimentos({})
        assert impedimento.codigo == destinacao.RESULTADO_NAO_DEFINITIVO
        assert "não foi divulgado" in impedimento.frase

    def test_prazo_recursal_diz_ate_quando(self):
        fecha = datetime(2026, 11, 20, 23, 59, tzinfo=UTC)
        (impedimento,) = self.definitivo(prazo_recursal_ate=fecha)
        assert (impedimento.codigo, impedimento.ate) == (destinacao.PRAZO_RECURSAL_ABERTO, fecha)

    def test_recurso_pendente_impede(self):
        (impedimento,) = self.definitivo(recursos_pendentes=2)
        assert impedimento.codigo == destinacao.RECURSO_PENDENTE
        assert "2 recursos" in impedimento.frase

    def test_prazo_e_recurso_da_eliminacao_impedem(self):
        fecha = datetime(2026, 11, 20, tzinfo=UTC)
        codigos = [
            i.codigo
            for i in self.definitivo(prazo_da_eliminacao_ate=fecha, recursos_da_eliminacao=1)
        ]
        assert codigos == [
            destinacao.PRAZO_DA_ELIMINACAO_ABERTO,
            destinacao.RECURSO_DA_ELIMINACAO_PENDENTE,
        ]

    def test_chamada_em_curso_nomeia_quem(self):
        """US1.4: a tela diz qual chamada impede, e até quando."""
        ate = datetime(2026, 11, 18, tzinfo=UTC)
        (impedimento,) = self.definitivo(chamadas_em_curso=[{"rotulo": "0007 — Ana", "ate": ate}])
        assert impedimento.codigo == destinacao.CHAMADA_EM_CURSO
        assert "0007 — Ana" in impedimento.frase
        assert impedimento.ate == ate

    def test_ampla_sem_confirmacao_impede(self):
        (impedimento,) = self.definitivo(ocupam_a_ampla_sem_confirmacao=1)
        assert impedimento.codigo == destinacao.OCUPACAO_PELA_AMPLA_PODE_MUDAR
        assert "ainda pode mudar" in impedimento.frase

    def test_apuracao_obsoleta_impede(self):
        (impedimento,) = self.definitivo(apuracao_obsoleta=True)
        assert impedimento.codigo == destinacao.APURACAO_OBSOLETA

    def test_a_ordem_e_a_do_caminho(self):
        codigos = [
            i.codigo
            for i in destinacao.impedimentos(
                {
                    "natureza_do_resultado": "PRELIMINAR",
                    "recursos_pendentes": 1,
                    "chamadas_em_curso": [{"rotulo": "x"}],
                    "apuracao_obsoleta": True,
                }
            )
        ]
        assert codigos == [
            destinacao.RESULTADO_NAO_DEFINITIVO,
            destinacao.RECURSO_PENDENTE,
            destinacao.CHAMADA_EM_CURSO,
            destinacao.APURACAO_OBSOLETA,
        ]


class TestQuantidadeDestinavel:
    def test_esgotada_e_sem_impedimento_destina_o_saldo(self):
        assert (
            destinacao.quantidade_destinavel(
                gatilho=nomes.REVERSAO_POR_ESGOTAMENTO, saldo=2, ainda_podem_ocupar=0
            )
            == 2
        )

    def test_com_quem_ocupar_nao_destina(self):
        assert (
            destinacao.quantidade_destinavel(
                gatilho=nomes.REVERSAO_POR_ESGOTAMENTO, saldo=2, ainda_podem_ocupar=1
            )
            == 0
        )

    def test_com_impedimento_nao_destina(self):
        impedimento = destinacao.Impedimento(destinacao.RECURSO_PENDENTE, "", None)
        assert (
            destinacao.quantidade_destinavel(
                gatilho=nomes.REVERSAO_POR_ESGOTAMENTO,
                saldo=1,
                ainda_podem_ocupar=0,
                impedimentos=[impedimento],
            )
            == 0
        )

    def test_por_saldo_nao_ha_conta_nesta_entrega(self):
        """FR-6305 espera a decisão do usuário: zero, e não o saldo inteiro."""
        assert (
            destinacao.quantidade_destinavel(
                gatilho=nomes.REVERSAO_POR_SALDO, saldo=2, ainda_podem_ocupar=0
            )
            == 0
        )

    def test_sem_declaracao_e_passagem_nao_destinam(self):
        for gatilho in (None, nomes.PASSAGEM_ENTRE_COTAS):
            assert (
                destinacao.quantidade_destinavel(gatilho=gatilho, saldo=1, ainda_podem_ocupar=0)
                == 0
            )

    def test_o_saldo_ja_cedido_pelo_movimento_antigo_e_zero(self):
        """FR-6316: o saldo vem das efetivas líquidas; cedidas antes, nada a destinar."""
        assert (
            destinacao.quantidade_destinavel(
                gatilho=nomes.REVERSAO_POR_ESGOTAMENTO, saldo=0, ainda_podem_ocupar=0
            )
            == 0
        )


class TestSituacao:
    def situacao(self, **fatos):
        return destinacao.situacao(
            **{
                "declaracao": nomes.REVERSAO_POR_ESGOTAMENTO,
                "lista_id": "PPI",
                "saldo": 1,
                **fatos,
            }
        )

    def test_esgotada_e_livre_de_impedimento(self):
        estado = self.situacao()
        assert (estado["estado"], estado["quantidade"]) == (destinacao.DESTINACAO_DISPONIVEL, 1)

    def test_sem_saldo(self):
        assert self.situacao(saldo=0)["estado"] == destinacao.SEM_VAGA_A_DESTINAR

    def test_sem_apuracao(self):
        assert self.situacao(saldo=None)["estado"] == destinacao.SEM_VAGA_A_DESTINAR

    def test_movimento_antigo_conta_como_destinada(self):
        """US1.5: a vaga já cedida aparece como destinada, e nada a destina de novo."""
        estado = self.situacao(saldo=0, destinadas=1)
        assert (estado["estado"], estado["destinadas"]) == (destinacao.SEM_VAGA_A_DESTINAR, 1)

    def test_com_alguem_livre_o_caminho_e_chamar(self):
        estado = self.situacao(restantes=["p2"])
        assert (estado["estado"], estado["livres"]) == (destinacao.SEM_VAGA_A_DESTINAR, 1)

    def test_chamada_em_curso_e_impedimento_e_nao_quem_chamar(self):
        """US1.4: a pessoa chamada conta como quem ainda pode ocupar, e a vaga fica impedida."""
        impedimento = destinacao.Impedimento(destinacao.CHAMADA_EM_CURSO, "x", None)
        estado = self.situacao(restantes=["p2"], pendentes=["p2"], impedimentos=[impedimento])
        assert estado["estado"] == destinacao.IMPEDIDA
        assert estado["quantidade"] == 0

    def test_resultado_provisorio_impede(self):
        impedimento = destinacao.Impedimento(destinacao.RESULTADO_NAO_DEFINITIVO, "x", None)
        assert self.situacao(impedimentos=[impedimento])["estado"] == destinacao.IMPEDIDA

    def test_por_saldo_aguarda(self):
        assert self.situacao(declaracao=nomes.REVERSAO_POR_SALDO)["estado"] == (
            destinacao.AGUARDA_D015
        )

    def test_passagem_entre_cotas(self):
        assert self.situacao(declaracao=nomes.PASSAGEM_ENTRE_COTAS)["estado"] == (
            destinacao.PASSAGEM_ENTRE_COTAS
        )

    def test_sem_declaracao_e_a_nao_preenchida(self):
        estado = self.situacao(declaracao=None)
        assert estado["estado"] == destinacao.NAO_PREENCHIDA_DISPONIVEL

    def test_linha_geral_nunca_e_destinada(self):
        estado = self.situacao(lista_id=None)
        assert estado["estado"] == destinacao.NAO_PREENCHIDA_DISPONIVEL
