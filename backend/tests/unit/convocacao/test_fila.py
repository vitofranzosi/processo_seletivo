"""A fila de chamada: quem é titular, quem é suplente, e em que ordem cada um é chamado (019).

**Sem banco e sem norma.** O que entra é a sequência da faixa e os conjuntos de quem já respondeu;
o que sai é uma lista na ordem de chamada. É o que permite testar o 77/2026 inteiro sem migrar nada.

**A fila não é coluna.** Ela é derivada da ordem vigente a cada leitura, como a faixa da `014` e a
vigência da `016`: guardar "posição na fila" exigiria `UPDATE` em tabela append-only, e faria a
reclassificação reescrever o passado em vez de acrescentar um ato.
"""

from processo_seletivo.convocacao.domain import fila

# O recorte do 77/2026 em miniatura: duas vagas, faixa de quatro.
FAIXA = ["p1", "p2", "p3", "p4"]
HABILITADAS = set(FAIXA)
VAGAS = 2


class TestTitularESuplente:
    def test_os_primeiros_efetivas_sao_titulares_e_o_resto_e_suplente(self):
        alcancados = fila.alcancados(progrediram_em_ordem=FAIXA, habilitadas=HABILITADAS)

        assert fila.titulares(alcancados_em_ordem=alcancados, efetivas=VAGAS) == ["p1", "p2"]
        assert fila.suplentes(alcancados_em_ordem=alcancados, efetivas=VAGAS) == ["p3", "p4"]

    def test_quem_nao_habilitou_nao_e_alcancado(self):
        """Eliminado na Etapa governada não segura vaga nenhuma, e quem vem depois **sobe**."""
        alcancados = fila.alcancados(progrediram_em_ordem=FAIXA, habilitadas=HABILITADAS - {"p2"})

        assert alcancados == ["p1", "p3", "p4"]
        assert fila.titulares(alcancados_em_ordem=alcancados, efetivas=VAGAS) == ["p1", "p3"]

    def test_o_teto_e_a_faixa_e_nao_o_quadro(self):
        """**Quem está fora da faixa não é suplente**: é quem a `014` não selecionou.

        Chamá-lo seria selecionar, e ampliar a faixa é ato do corte — pela `016`, e não daqui.
        """
        alcancados = fila.alcancados(progrediram_em_ordem=FAIXA, habilitadas=HABILITADAS | {"p9"})

        assert "p9" not in alcancados


class TestASuplenciaNaoAtravessaRecorte:
    """`SC-086`: a vaga liberada é chamada para o próximo do **mesmo** recorte.

    **O recorte é `(perfil, marco, lista)`**, e a fila é montada sobre a faixa daquele recorte. Uma
    vaga reservada que vagasse e fosse chamada na ampla moveria quantidade entre listas sem ato de
    reversão — que é exatamente o que a `FR-270` proíbe, e o que a `016` só admite como movimento
    declarado.
    """

    def test_a_fila_so_contem_quem_a_faixa_daquele_recorte_alcancou(self):
        """De outra lista ninguém entra, porque a sequência de entrada é a daquele recorte."""
        de_outra_lista = ["r1", "r2"]

        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA)

        assert set(chamaveis).isdisjoint(de_outra_lista)
        assert chamaveis == FAIXA

    def test_quem_ocupa_pela_ampla_sai_antes_da_janela(self):
        """A concorrência concomitante é exclusão, e quem vem depois **sobe** (`FR-252`).

        O item 8.9 do 28/2026 diz *"abrindo vaga para o próximo suplente autodeclarado"* — filtrar
        depois de recortar a janela deixaria o buraco no lugar.
        """
        alcancados = fila.alcancados(
            progrediram_em_ordem=FAIXA, habilitadas=HABILITADAS, ocupantes_da_ampla={"p1"}
        )

        assert alcancados == ["p2", "p3", "p4"]
        assert fila.titulares(alcancados_em_ordem=alcancados, efetivas=VAGAS) == ["p2", "p3"]


class TestOEsgotamentoDaListaAlcancada:
    """`lista_alcancada_esgotada`: não há mais quem chamar dentro do teto publicado."""

    def test_com_todos_servidos_a_fila_esgota(self):
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, servidos=set(FAIXA))

        assert chamaveis == []
        assert fila.esgotou(chamaveis) is True
        assert fila.proximo(chamaveis) is None

    def test_chamada_em_aberto_tira_da_fila_sem_esgotar(self):
        """A pessoa está dentro do prazo dela: não é chamável de novo, e não encerrou nada."""
        chamaveis = fila.ordem_de_chamada(
            alcancados_em_ordem=FAIXA, com_chamada_em_aberto={"p1", "p2"}
        )

        assert chamaveis == ["p3", "p4"]
        assert fila.esgotou(chamaveis) is False

    def test_quem_encerrou_nao_volta_a_ser_chamavel(self):
        """Os quatro desfechos que põem fim à participação no recorte."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, encerrados={"p1", "p3"})

        assert chamaveis == ["p2", "p4"]

    def test_a_reclassificacao_nao_esta_entre_os_que_encerram(self):
        """`D-008`: o reclassificado não perdeu habilitação — ele abriu mão da vez."""
        from processo_seletivo.convocacao.domain import nomes

        assert nomes.RECLASSIFICACAO not in fila.DESFECHOS_QUE_ENCERRAM
        assert set(fila.DESFECHOS_QUE_ENCERRAM) == {
            nomes.INDEFERIMENTO,
            nomes.DESISTENCIA_EXPRESSA,
            nomes.NAO_ATENDIMENTO,
            nomes.INERCIA,
        }


class TestOReabilitadoPorDeferimento:
    """`FR-292b`: a decisão recursal devolveu a vez, e não só a habilitação.

    Chamá-lo depois de quem passou à frente enquanto o recurso corria seria executar a decisão pela
    metade — ele receberia o direito e ficaria no fim da fila.
    """

    def test_o_reabilitado_vai_para_o_topo(self):
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reabilitados={"p3"})

        assert chamaveis[0] == "p3"

    def test_o_reabilitado_bloqueia_quem_esta_abaixo(self):
        """A precedência dele é a de todos os outros, e não só a de quem estava atrás na ordem."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reabilitados={"p4"})

        assert fila.precedencia(chamaveis, "p1") == ["p4"]
        assert fila.precedencia(chamaveis, "p4") == []

    def test_dois_reabilitados_mantem_a_ordem_entre_si(self):
        """Entre eles vale a ordem do ato de ordenação, e não a de julgamento dos recursos."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA, reabilitados={"p4", "p2"})

        assert chamaveis[:2] == ["p2", "p4"]


class TestAPrecedencia:
    def test_a_precedencia_nomeia_quem_esta_antes(self):
        """**É a lista, e não um booleano**: *"há alguém antes"* não diz o que fazer."""
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA)

        assert fila.precedencia(chamaveis, "p3") == ["p1", "p2"]

    def test_quem_nao_esta_na_fila_e_precedido_por_todos(self):
        """Perguntar pela vez de quem não está na fila devolve a fila inteira — e não vazio.

        Devolver vazio diria "ela é a próxima", que é falso e autorizaria a chamada.
        """
        chamaveis = fila.ordem_de_chamada(alcancados_em_ordem=FAIXA)

        assert fila.precedencia(chamaveis, "estranho") == FAIXA

    def test_esta_na_faixa_distingue_quem_a_014_alcancou(self):
        alcancados = fila.alcancados(progrediram_em_ordem=FAIXA, habilitadas=HABILITADAS)

        assert fila.esta_na_faixa(alcancados, "p4") is True
        assert fila.esta_na_faixa(alcancados, "p9") is False
