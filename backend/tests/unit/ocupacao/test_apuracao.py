"""A apuração pura: publicadas da linha, ocupadas da interseção, efetivas dos movimentos (016).

Sem banco e sem norma. O que entra é o quadro publicado e dois conjuntos de inscrições; o que sai
são as três quantidades que o ato grava.
"""

import pytest

from processo_seletivo.classificacao.application.corte import linha_do_quadro
from processo_seletivo.ocupacao.domain import apuracao, nomes

PERFIL = "99999999-9999-9999-9999-999999999999"
AC = "11111111-1111-1111-1111-111111111111"
PPI = "22222222-2222-2222-2222-222222222222"


def conteudo(*linhas, ampla=None):
    """O conteúdo publicado com um Perfil e o quadro dado. `(modalityId, quantidade)` por linha."""
    return {
        "profiles": [
            {
                "id": PERFIL,
                "generalCompetitionModalityId": ampla,
                "vacancyTable": [
                    {
                        "id": f"aaaaaaaa-0000-0000-0000-00000000000{indice}",
                        "modalityId": m,
                        "immediateVacancies": q,
                    }
                    for indice, (m, q) in enumerate(linhas, start=1)
                ],
            }
        ]
    }


class TestALinhaDoQuadroEReusada:
    """A leitura da linha vem da `014`, e não de um segundo leitor (016, `FR-240`, `FR-241`).

    **Este arquivo é de unidade e importa de `classificacao.application`** de propósito: a função é
    pura — recebe o conteúdo publicado e devolve a linha — e o que os testes prendem é que a
    apuração usa **aquela** regra, e não uma cópia dela. Um segundo leitor erraria o caso do Edital
    que declara "Ampla concorrência" como Modalidade, e o alvo derivado do corte discordaria da
    apuração no mesmo recorte.
    """

    def test_a_linha_geral_e_a_ampla_concorrencia(self):
        linha = linha_do_quadro(conteudo((None, 28), (PPI, 10)), perfil_id=PERFIL, lista_id=None)
        assert linha["immediateVacancies"] == 28

    def test_a_linha_da_modalidade_e_lida_por_identidade(self):
        linha = linha_do_quadro(conteudo((None, 28), (PPI, 10)), perfil_id=PERFIL, lista_id=PPI)
        assert linha["immediateVacancies"] == 10

    def test_recorte_sem_linha_devolve_none_e_nao_zero(self):
        """**A distinção decide.** Linha zerada é declaração legítima do Edital; ausência de linha é
        recorte que o quadro não descreve, e apurar ali afirmaria zero vaga onde nada foi dito.
        """
        assert linha_do_quadro(conteudo((None, 28)), perfil_id=PERFIL, lista_id=PPI) is None

    def test_linha_zerada_e_zero_de_verdade(self):
        linha = linha_do_quadro(conteudo((None, 28), (PPI, 0)), perfil_id=PERFIL, lista_id=PPI)
        assert linha["immediateVacancies"] == 0

    def test_a_modalidade_declarada_como_ampla_le_a_linha_geral(self):
        """**É o caso que um leitor próprio erraria.**

        O Perfil declara `AC` como ampla concorrência, e `AC` não tem linha reservada — a quantidade
        dela mora na linha geral. Pedir a linha de `AC` devolve a **geral**, com 28, e não nada.
        Uma segunda implementação que só casasse `modalityId` devolveria `None` aqui, e a apuração
        passaria a discordar do alvo derivado do corte no mesmo recorte.
        """
        quadro = conteudo((None, 28), (PPI, 10), ampla=AC)
        linha = linha_do_quadro(quadro, perfil_id=PERFIL, lista_id=AC)
        assert linha["immediateVacancies"] == 28
        assert linha["modalityId"] is None


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


class TestOTetoDaOcupacao:
    """**Suplente não ocupa vaga**, e o teto é o que impede um número falso.

    A faixa pode ser maior que o quadro: no 77/2026 são 40 vagas com 30 suplentes alcançados na
    mesma faixa (`D-011` da `014`). Se todos habilitarem, a interseção dá 70 — e ocupar 70 de 40
    não é um número grande, é um número falso. A constraint `ocupadas <= efetivas` recusaria o ato,
    de modo que sem o teto a apuração daquele Edital simplesmente não sairia.
    """

    def test_a_faixa_maior_que_o_quadro_nao_ocupa_mais_que_as_vagas(self):
        faixa = {f"i{n}" for n in range(70)}

        _, efetivas, ocupadas = apuracao.apurar(
            publicadas=40, dentro_da_faixa=faixa, habilitadas=faixa
        )

        assert (efetivas, ocupadas) == (40, 40)

    def test_o_excedente_e_suplente_e_nao_ocupante(self):
        """Trinta habilitados além das vagas continuam sendo trinta — eles só não ocupam."""
        faixa = {f"i{n}" for n in range(70)}

        _, _, ocupadas = apuracao.apurar(publicadas=40, dentro_da_faixa=faixa, habilitadas=faixa)

        assert ocupadas == 40, "e os outros 30 esperam que uma vaga vague — é a 019 que os chama"

    def test_o_teto_acompanha_as_efetivas_e_nao_as_publicadas(self):
        """Recebida a reversão, o teto sobe com ela."""
        faixa = {f"i{n}" for n in range(10)}

        _, efetivas, ocupadas = apuracao.apurar(
            publicadas=2,
            dentro_da_faixa=faixa,
            habilitadas=faixa,
            movimentos_lidos=[(nomes.MOVIMENTO_REVERSAO, True, 3)],
        )

        assert (efetivas, ocupadas) == (5, 5)


class TestAExclusaoDaConcomitancia:
    """`FR-252`: quem ocupou pela ampla não é computado na reservada.

    **Exclusão, e não transferência** — quantidade nenhuma muda de lista.
    """

    def test_o_ocupante_da_ampla_sai_da_contagem_da_reservada(self):
        _, efetivas, ocupadas = apuracao.apurar(
            publicadas=1,
            dentro_da_faixa={"cotista"},
            habilitadas={"cotista"},
            ocupantes_da_ampla={"cotista"},
        )

        assert (efetivas, ocupadas) == (1, 0), "a vaga reservada segue aberta, e não migra"

    def test_quem_nao_ocupou_pela_ampla_continua_contando(self):
        _, _, ocupadas = apuracao.apurar(
            publicadas=1,
            dentro_da_faixa={"outro"},
            habilitadas={"outro"},
            ocupantes_da_ampla={"cotista"},
        )

        assert ocupadas == 1
