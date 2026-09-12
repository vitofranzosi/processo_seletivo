"""As duas espécies de gatilho da reversão (016, `D-007`).

O caso que as separa tem teste próprio, porque é a razão de elas serem duas: **o mesmo estado do
mundo produz dois resultados legítimos**, e quem decide é o Edital.
"""

from processo_seletivo.ocupacao.domain import nomes, reversao


def reverter(*, especie, publicadas=10, ocupadas=3, ha_quem_ocupar=False):
    return reversao.quantidade_a_reverter(
        especie=especie,
        publicadas=publicadas,
        ocupadas=ocupadas,
        ha_quem_ocupar=ha_quem_ocupar,
    )


class TestSaldo:
    """`ON_BALANCE` reverte o que ficou sem preencher, com ou sem gente na lista."""

    def test_reverte_o_saldo_com_a_lista_esgotada(self):
        assert reverter(especie=nomes.REVERSAO_POR_SALDO) == 7

    def test_reverte_o_saldo_ainda_com_gente_a_ocupar(self):
        assert reverter(especie=nomes.REVERSAO_POR_SALDO, ha_quem_ocupar=True) == 7

    def test_sem_saldo_nao_reverte(self):
        assert reverter(especie=nomes.REVERSAO_POR_SALDO, ocupadas=10) == 0


class TestEsgotamento:
    """`ON_EXHAUSTION` só reverte quando não há mais ninguém a ocupar."""

    def test_reverte_com_a_lista_esgotada(self):
        assert reverter(especie=nomes.REVERSAO_POR_ESGOTAMENTO) == 7

    def test_nao_reverte_havendo_quem_ocupar(self):
        assert reverter(especie=nomes.REVERSAO_POR_ESGOTAMENTO, ha_quem_ocupar=True) == 0


class TestOCasoQueSeparaAsDuasEspecies:
    """**O mesmo estado do mundo, dois resultados legítimos.**

    É a Contraprova 3 do quickstart: 8 de 10 ocupadas, com 4 pessoas ainda por analisar na ordem de
    PPI. Sob saldo reverteriam 2; sob esgotamento, nada. Um gatilho inferido teria de escolher por
    conta própria — e escolher aqui é decidir norma que o Edital escreveu de outro jeito.
    """

    def test_sob_saldo_reverte_dois(self):
        assert reverter(especie=nomes.REVERSAO_POR_SALDO, ocupadas=8, ha_quem_ocupar=True) == 2

    def test_sob_esgotamento_nao_reverte_nada(self):
        assert (
            reverter(especie=nomes.REVERSAO_POR_ESGOTAMENTO, ocupadas=8, ha_quem_ocupar=True) == 0
        )


class TestAusenciaDeDeclaracao:
    """Ausência significa **não reverte** — nunca "reverte do jeito comum" (`D-002`)."""

    def test_especie_nula_nao_reverte(self):
        assert reverter(especie=None) == 0

    def test_especie_desconhecida_nao_reverte(self):
        assert reverter(especie="QUALQUER_COISA") == 0

    def test_perfil_sem_o_objeto_nao_declara(self):
        assert reversao.declarada({}) is None

    def test_objeto_nulo_nao_declara(self):
        assert reversao.declarada({"vacancyReversion": None}) is None

    def test_objeto_com_especie_declara(self):
        perfil = {"vacancyReversion": {"kind": nomes.REVERSAO_POR_SALDO}}
        assert reversao.declarada(perfil) == nomes.REVERSAO_POR_SALDO

    def test_objeto_com_especie_desconhecida_nao_declara(self):
        """A publicação recusa isso (`FR-251`); aqui a leitura não inventa um padrão para o caso
        que não deveria existir.
        """
        assert reversao.declarada({"vacancyReversion": {"kind": "OUTRA"}}) is None
