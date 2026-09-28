"""O alcance dos gestos da `050`: o começo da fila, os vencidos, os pendentes e a assinatura."""

from types import SimpleNamespace

from processo_seletivo.convocacao.domain import alcance, nomes


class TestTitularesDoComecoDaFila:
    def test_alcanca_os_titulares_e_para_no_primeiro_suplente(self):
        resultado = alcance.titulares_do_comeco_da_fila(
            ["t1", "t2", "s1", "s2"], ocupando={"t1", "t2"}
        )

        assert resultado.pessoas == ("t1", "t2")
        assert resultado.parada == "s1"
        assert resultado.motivo_da_parada == alcance.PARADA_SUPLENTE

    def test_nunca_pula_ninguem(self):
        """`D-001`: um titular depois de um suplente fica de fora, e não é alcançado por cima."""
        resultado = alcance.titulares_do_comeco_da_fila(["t1", "s1", "t2"], ocupando={"t1", "t2"})

        assert resultado.pessoas == ("t1",)

    def test_o_reabilitado_que_nao_ocupa_para_o_gesto_com_a_razao_dele(self):
        resultado = alcance.titulares_do_comeco_da_fila(
            ["r1", "t1"], ocupando={"t1"}, reabilitados={"r1"}
        )

        assert resultado.pessoas == ()
        assert resultado.motivo_da_parada == alcance.PARADA_REABILITADO

    def test_fila_so_de_titulares_alcanca_todos_sem_parada(self):
        resultado = alcance.titulares_do_comeco_da_fila(["t1", "t2"], ocupando={"t1", "t2"})

        assert resultado.pessoas == ("t1", "t2")
        assert resultado.parada is None


def linha(estado, *, desfecho=None, vencimento="v", enviada="e"):
    return {
        "estado": estado,
        "desfecho": desfecho,
        "convocacao": SimpleNamespace(vencimento=vencimento),
        "enviadaEm": enviada,
    }


class TestVencidas:
    def test_so_o_vencimento_decorrido_entra_e_as_outras_sao_contadas(self):
        linhas = [
            linha(nomes.CONVOCADO_VENCIMENTO_DECORRIDO),
            linha(nomes.CONVOCADO_VENCIMENTO_DECORRIDO),
            linha(nomes.CONVOCADO_PRAZO_EM_CURSO),
            linha(nomes.CONVOCADO_PRAZO_EM_CURSO, vencimento=None),
            linha(nomes.CONVOCADO_PRAZO_NAO_INICIADO, enviada=None),
            linha(nomes.DESFECHADO, desfecho="aceite"),
        ]

        particao = alcance.vencidas(linhas)

        assert len(particao.alcancadas) == 2
        assert particao.fora == {"emCurso": 1, "naoIniciado": 1, "semVencimento": 1}


class TestPendentes:
    def test_pendente_e_sem_desfecho_e_sem_envio(self):
        linhas = [
            linha(nomes.CONVOCADO_PRAZO_NAO_INICIADO, enviada=None),
            linha(nomes.CONVOCADO_PRAZO_EM_CURSO),
            linha(nomes.DESFECHADO, desfecho="x", enviada=None),
        ]

        assert len(alcance.pendentes(linhas).alcancadas) == 1


class TestAssinatura:
    BASE = {"gesto": "titulares", "apuracao_id": "a", "versao_id": "v", "forma": "F"}

    def test_mesma_declaracao_mesma_assinatura(self):
        assert alcance.assinatura(**self.BASE, identidades=["1", "2"]) == alcance.assinatura(
            **self.BASE, identidades=["1", "2"]
        )

    def test_a_ordem_entra_na_assinatura(self):
        assert alcance.assinatura(**self.BASE, identidades=["1", "2"]) != alcance.assinatura(
            **self.BASE, identidades=["2", "1"]
        )

    def test_apuracao_nova_muda_a_assinatura(self):
        outra = {**self.BASE, "apuracao_id": "b"}
        assert alcance.assinatura(**self.BASE, identidades=["1"]) != alcance.assinatura(
            **outra, identidades=["1"]
        )
