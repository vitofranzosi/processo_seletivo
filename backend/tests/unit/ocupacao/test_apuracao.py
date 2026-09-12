"""A apuração pura: publicadas da linha, ocupadas da interseção, efetivas dos movimentos (016).

Sem banco e sem norma. O que entra é o quadro publicado e dois conjuntos de inscrições; o que sai
são as três quantidades que o ato grava.
"""

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes

AC = "11111111-1111-1111-1111-111111111111"
PPI = "22222222-2222-2222-2222-222222222222"


def perfil(*linhas):
    """`(modalityId, quantidade)` — `None` na linha geral, que é a ampla concorrência."""
    return {
        "vacancyTable": [
            {
                "id": f"aaaaaaaa-0000-0000-0000-00000000000{indice}",
                "modalityId": m,
                "immediateVacancies": q,
            }
            for indice, (m, q) in enumerate(linhas, start=1)
        ]
    }


class TestQuantidadePublicada:
    """A quantidade sai da **linha**, e nunca do total do Perfil (`FR-240`)."""

    def test_a_linha_geral_e_a_ampla_concorrencia(self):
        assert apuracao.quantidade_publicada(perfil((None, 28), (PPI, 10)), lista_id=None) == 28

    def test_a_linha_da_modalidade_e_lida_por_identidade(self):
        assert apuracao.quantidade_publicada(perfil((None, 28), (PPI, 10)), lista_id=PPI) == 10

    def test_recorte_sem_linha_devolve_none_e_nao_zero(self):
        """**A distinção decide.** Linha zerada é declaração legítima do Edital; ausência de linha é
        recorte que o quadro não descreve, e apurar ali afirmaria zero vaga onde nada foi dito.
        """
        assert apuracao.quantidade_publicada(perfil((None, 28)), lista_id=PPI) is None

    def test_linha_zerada_e_zero_de_verdade(self):
        assert apuracao.quantidade_publicada(perfil((None, 28), (PPI, 0)), lista_id=PPI) == 0

    def test_quadro_ausente_devolve_none(self):
        assert apuracao.quantidade_publicada({}, lista_id=None) is None

    def test_a_modalidade_declarada_como_ampla_nao_tem_linha_propria(self):
        """Ela não é recorte próprio: a quantidade dela mora na linha geral (`FR-241`).

        Este teste existe para prender a leitura por **identidade** e não por nome: um Perfil que
        declara `AC` como ampla concorrência não ganha linha `AC`, e procurar por ela devolve nada.
        """
        quadro = perfil((None, 28), (PPI, 10))
        assert apuracao.quantidade_publicada(quadro, lista_id=AC) is None


class TestOcupadas:
    """Ocupada é estar **dentro da faixa** e **habilitada** (`R-001`)."""

    def test_a_intersecao_dos_dois_conjuntos(self):
        _, _, ocupadas = apuracao.apurar(
            publicadas=28, dentro_da_faixa={"a", "b", "c"}, habilitadas={"b", "c", "d"}
        )
        assert ocupadas == 2

    def test_habilitado_fora_da_faixa_nao_ocupa(self):
        """É a advertência da fronteira da `014`, verificada: "quantidade de habilitados" não é
        sinônimo de "vagas ocupadas". Quem passou fora do alvo não ocupou vaga nenhuma.
        """
        _, _, ocupadas = apuracao.apurar(
            publicadas=28, dentro_da_faixa={"a"}, habilitadas={"a", "b", "c", "d", "e"}
        )
        assert ocupadas == 1

    def test_dentro_da_faixa_e_nao_habilitado_nao_ocupa(self):
        _, _, ocupadas = apuracao.apurar(
            publicadas=28, dentro_da_faixa={"a", "b", "c"}, habilitadas=set()
        )
        assert ocupadas == 0


class TestEfetivas:
    """`publicadas + recebidas - cedidas`, contando só os movimentos que a apuração leu."""

    def test_sem_movimento_efetivas_igualam_publicadas(self):
        publicadas, efetivas, _ = apuracao.apurar(
            publicadas=28, dentro_da_faixa=set(), habilitadas=set()
        )
        assert (publicadas, efetivas) == (28, 28)

    def test_a_ampla_que_recebe_sete_fica_com_trinta_e_cinco(self):
        """É a `SC-079`: a efetiva vai a 35 e a **publicada permanece 28** (`FR-239a`)."""
        publicadas, efetivas, _ = apuracao.apurar(
            publicadas=28,
            dentro_da_faixa=set(),
            habilitadas=set(),
            movimentos_lidos=[(nomes.MOVIMENTO_REVERSAO, True, 7)],
        )
        assert (publicadas, efetivas) == (28, 35)

    def test_a_cota_que_cede_sete_fica_com_tres(self):
        publicadas, efetivas, _ = apuracao.apurar(
            publicadas=10,
            dentro_da_faixa=set(),
            habilitadas=set(),
            movimentos_lidos=[(nomes.MOVIMENTO_REVERSAO, False, 7)],
        )
        assert (publicadas, efetivas) == (10, 3)

    def test_movimento_nao_lido_nao_entra_na_conta(self):
        """**É o que torna a reprodução determinística** (`FR-244`): reproduzir é reler os ids que o
        ato congelou, e não "os movimentos de hoje".
        """
        _, efetivas, _ = apuracao.apurar(
            publicadas=28, dentro_da_faixa=set(), habilitadas=set(), movimentos_lidos=[]
        )
        assert efetivas == 28


class TestFaltando:
    def test_efetivas_menos_ocupadas(self):
        assert apuracao.faltando(efetivas=35, ocupadas=13) == 22

    def test_nunca_negativo(self):
        """A fronteira do empate pode fazer a faixa alcançar mais gente que o alvo. Nesse caso não
        faltam vagas negativas — faltam zero.
        """
        assert apuracao.faltando(efetivas=10, ocupadas=12) == 0


class TestReprodutibilidade:
    """A mesma entrada produz a mesma saída (`FR-244`)."""

    @pytest.mark.parametrize("execucao", range(5))
    def test_a_apuracao_e_deterministica(self, execucao):
        assert apuracao.apurar(
            publicadas=28,
            dentro_da_faixa={"a", "b", "c"},
            habilitadas={"b", "c"},
            movimentos_lidos=[(nomes.MOVIMENTO_REVERSAO, True, 7)],
        ) == (28, 35, 2)


class TestEstado:
    """Quatro estados, e dois deles não são erro (contrato, `UX-032`)."""

    def test_sem_quadro_vem_antes_de_tudo(self):
        assert (
            apuracao.estado(tem_quadro=False, tem_apuracao=False, causas_de_obsolescencia=[])
            == nomes.SEM_QUADRO
        )

    def test_sem_quadro_vence_mesmo_com_apuracao(self):
        assert (
            apuracao.estado(tem_quadro=False, tem_apuracao=True, causas_de_obsolescencia=[])
            == nomes.SEM_QUADRO
        )

    def test_com_quadro_e_sem_apuracao_e_nao_apurado(self):
        assert (
            apuracao.estado(tem_quadro=True, tem_apuracao=False, causas_de_obsolescencia=[])
            == nomes.NAO_APURADO
        )

    def test_causa_presente_torna_obsoleto(self):
        assert (
            apuracao.estado(
                tem_quadro=True,
                tem_apuracao=True,
                causas_de_obsolescencia=[nomes.CAUSA_ORDEM_SUCEDIDA],
            )
            == nomes.OBSOLETO
        )

    def test_sem_causa_e_vigente(self):
        assert (
            apuracao.estado(tem_quadro=True, tem_apuracao=True, causas_de_obsolescencia=[])
            == nomes.VIGENTE
        )
