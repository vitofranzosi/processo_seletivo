"""A leitura de um recorte antes e depois de haver apuração (016, `UX-031`, `UX-032`, `UX-032a`).

**O que este arquivo protege é a ausência.** Três dos quatro números não existem antes de um ato os
produzir, e devolvê-los como zero seria afirmar "não há vaga a ocupar" sem que ninguém o tenha
afirmado — "ler ocupa" pela porta dos fundos, contra a `FR-261` e contra a `FR-259`.
"""

import pytest

from processo_seletivo.ocupacao.application import selectors
from processo_seletivo.ocupacao.domain import nomes
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.integration.ocupacao.test_emissao import apurar

pytestmark = pytest.mark.django_db(transaction=True)


def ler(edital, *, lista_id=None):
    return selectors.ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )


class TestAntesDeApurar:
    """`NOT_APPRAISED` **não** é colapsado em zero."""

    def test_as_tres_quantidades_de_apuracao_vem_nulas(self, cenario):
        edital, _, _ = cenario

        leitura = ler(edital)

        assert leitura["estado"] == nomes.NAO_APURADO
        assert leitura["efetivas"] is None
        assert leitura["ocupadas"] is None
        assert leitura["faltando"] is None

    def test_publicadas_vem_do_quadro_porque_nao_depende_de_apuracao(self, cenario):
        """**A exceção, e ela é justificada.**

        `publicadas` sai da linha do quadro publicado — fato normativo do Edital, rastreável a
        ele, e verdadeiro antes de qualquer apuração. Dizer "o Edital publicou 3 vagas neste
        recorte, e a ocupação ainda não foi apurada" é verdadeiro nas duas metades; dizer
        "faltam 0" não seria.
        """
        edital, _, _ = cenario

        assert ler(edital)["publicadas"] == 3

    def test_nenhuma_leitura_emite_apuracao(self, cenario):
        """**Ler não ocupa** (`FR-261`), como ler não corta."""
        from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao

        edital, _, _ = cenario

        for _ in range(3):
            ler(edital)

        assert ApuracaoDeOcupacao.objects.count() == 0


class TestDepoisDeApurar:
    def test_os_quatro_numeros_aparecem(self, cenario, gestor):
        """As **quatro** quantidades do recorte, e não três (`FR-239`)."""
        edital, _, _ = cenario
        apurar(edital, gestor)

        leitura = ler(edital)

        assert leitura["estado"] == nomes.VIGENTE
        assert leitura["publicadas"] == 3
        assert leitura["efetivas"] == 3
        assert leitura["ocupadas"] == 0
        assert leitura["faltando"] == 3

    def test_ocupadas_zero_apurado_e_diferente_de_ocupadas_ausente(self, cenario, gestor):
        """**A distinção que a correção existe para preservar.**

        Depois de apurar, `ocupadas = 0` é afirmação: um ato contou e não encontrou ninguém
        ocupando. Antes de apurar, é ausência. O mesmo número com sentidos opostos, e é por isso
        que o estado viaja junto.
        """
        edital, _, _ = cenario
        antes = ler(edital)
        apurar(edital, gestor)
        depois = ler(edital)

        assert antes["ocupadas"] is None and antes["estado"] == nomes.NAO_APURADO
        assert depois["ocupadas"] == 0 and depois["estado"] == nomes.VIGENTE


class TestSemQuadroPublicado:
    """`NO_VACANCY_TABLE`: nem `publicadas` existe — o Edital não declarou linha (`UX-032`)."""

    def test_as_quatro_quantidades_vem_nulas(
        self, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
    ):
        from tests.fixtures.corte import montar_cenario_do_corte

        edital, _, _ = montar_cenario_do_corte(
            gestor, api_client, manager_headers, process_payload, prefixo="ocupacao-016-leitura"
        )

        leitura = ler(edital)

        assert leitura["estado"] == nomes.SEM_QUADRO
        assert leitura["publicadas"] is None
        assert leitura["efetivas"] is None
        assert leitura["ocupadas"] is None
        assert leitura["faltando"] is None
