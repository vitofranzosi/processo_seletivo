"""O invariante da soma: reverter redistribui, e não cria nem destrói vaga (016, `FR-247`).

**Teste de propriedade, e não de exemplo, porque é a composição que erra.** Cada movimento sozinho é
trivialmente correto; o que quebra é a sequência — reverter 3 e depois liberar 1 pode manter a soma
certa e pôr a vaga no recorte errado. Por isso são duas asserções a cada passo: a soma **e** o
recorte.
"""

import random

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes

AMPLA = None
PPI = "22222222-2222-2222-2222-222222222222"
PCD = "33333333-3333-3333-3333-333333333333"


class Mundo:
    """As quantidades publicadas por recorte e os movimentos que aconteceram sobre elas.

    Modela o que o banco guarda: `publicadas` **nunca muda** (`FR-239a`), e o que se acumula são os
    movimentos. As efetivas são derivadas — como são no código de verdade.
    """

    def __init__(self, publicadas):
        self.publicadas = dict(publicadas)
        self.movimentos = []

    def mover(self, *, origem, destino, quantidade, especie):
        self.movimentos.append((especie, origem, destino, quantidade))

    def efetivas(self, recorte):
        lidos = [
            (especie, destino == recorte, q)
            for especie, origem, destino, q in self.movimentos
            if recorte in (origem, destino)
        ]
        _, efetivas, _ = apuracao.apurar(
            publicadas=self.publicadas[recorte],
            dentro_da_faixa=set(),
            habilitadas=set(),
            movimentos_lidos=lidos,
        )
        return efetivas

    @property
    def soma_publicada(self):
        return sum(self.publicadas.values())

    @property
    def soma_efetiva(self):
        return sum(self.efetivas(r) for r in self.publicadas)


@pytest.fixture
def mundo():
    """O Perfil da `SC-079`: 28 na ampla, 10 em PPI, 2 em PcD — o 28/2026 por polo."""
    return Mundo({AMPLA: 28, PPI: 10, PCD: 2})


def test_a_reversao_preserva_a_soma(mundo):
    mundo.mover(origem=PPI, destino=AMPLA, quantidade=7, especie=nomes.MOVIMENTO_REVERSAO)

    assert mundo.soma_efetiva == mundo.soma_publicada == 40
    assert mundo.efetivas(AMPLA) == 35
    assert mundo.efetivas(PPI) == 3


def test_a_liberacao_preserva_a_soma_e_vai_para_a_reservada(mundo):
    """**O sentido oposto.** A vaga volta para a lista reservada, e nunca para a linha geral."""
    mundo.mover(origem=AMPLA, destino=PPI, quantidade=1, especie=nomes.MOVIMENTO_LIBERACAO)

    assert mundo.soma_efetiva == 40
    assert mundo.efetivas(PPI) == 11
    assert mundo.efetivas(AMPLA) == 27


def test_a_publicada_nunca_muda_por_movimento(mundo):
    """`FR-239a`: o que a reversão move é a efetiva, e o publicado é intocável."""
    antes = dict(mundo.publicadas)

    mundo.mover(origem=PPI, destino=AMPLA, quantidade=7, especie=nomes.MOVIMENTO_REVERSAO)
    mundo.mover(origem=AMPLA, destino=PCD, quantidade=1, especie=nomes.MOVIMENTO_LIBERACAO)

    assert mundo.publicadas == antes


@pytest.mark.parametrize("semente", range(25))
def test_a_soma_e_constante_sob_sequencia_aleatoria(semente, mundo):
    """**A propriedade.** Vinte e cinco sequências, e a soma fecha em todas.

    O gerador só produz movimentos legítimos — reversão da cota para a geral, liberação da geral
    para uma cota —, porque o que se testa é o invariante da composição, e não a validação de
    entrada, que mora nas constraints.
    """
    sorteio = random.Random(semente)
    for _ in range(sorteio.randint(1, 12)):
        if sorteio.random() < 0.5:
            cota = sorteio.choice([PPI, PCD])
            mundo.mover(
                origem=cota,
                destino=AMPLA,
                quantidade=sorteio.randint(1, 3),
                especie=nomes.MOVIMENTO_REVERSAO,
            )
        else:
            mundo.mover(
                origem=AMPLA,
                destino=sorteio.choice([PPI, PCD]),
                quantidade=1,
                especie=nomes.MOVIMENTO_LIBERACAO,
            )
        assert mundo.soma_efetiva == mundo.soma_publicada == 40


@pytest.mark.parametrize("semente", range(25))
def test_nenhum_movimento_leva_vaga_para_recorte_que_nao_e_o_declarado(semente, mundo):
    """**A asserção que a soma não faz.** Reversão vai para a geral; liberação, para a reservada.

    Trocar os dois sentidos mantém a soma certa e põe a vaga no recorte errado — o defeito mais
    provável desta feature, e o único que soma nenhuma denuncia.
    """
    sorteio = random.Random(semente)
    for _ in range(sorteio.randint(1, 12)):
        reversao = sorteio.random() < 0.5
        cota = sorteio.choice([PPI, PCD])
        mundo.mover(
            origem=cota if reversao else AMPLA,
            destino=AMPLA if reversao else cota,
            quantidade=sorteio.randint(1, 2),
            especie=nomes.MOVIMENTO_REVERSAO if reversao else nomes.MOVIMENTO_LIBERACAO,
        )
    for especie, origem, destino, _ in mundo.movimentos:
        if especie == nomes.MOVIMENTO_REVERSAO:
            assert destino is AMPLA and origem is not AMPLA
        else:
            assert origem is AMPLA and destino is not AMPLA
