"""T016 — as duas perguntas de autorização, e o que cada uma recusa."""

import pytest

from processo_seletivo.comissoes.domain.autorizacao import (
    BASE_PRESIDENCIA,
    PERMISSAO_SISTEMICA,
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em

pytestmark = pytest.mark.django_db


def test_permissao_sistemica_autoriza_gerir(gestor, processo_a):
    base = pode_gerir_comissao(gestor, processo_a)

    assert base is not None and base.permissao == PERMISSAO_SISTEMICA


def test_presidencia_autoriza_gerir_sem_o_papel_de_gestor(processo_a, comissao_de_a):
    """SC-020: as duas bases são independentes, e cada uma basta sozinha."""
    maria = ator_institucional("maria")

    base = pode_gerir_comissao(maria, processo_a)

    assert base is not None and base.permissao == BASE_PRESIDENCIA


def test_membro_comum_nao_gere(processo_a, comissao_de_a):
    assert pode_gerir_comissao(ator_institucional("joao"), processo_a) is None


def test_presidencia_vale_so_no_processo_dela(processo_a, edital_b, comissao_de_a):
    """SC-011: presidir não é papel global — se fosse, valeria em todo Processo."""
    maria = ator_institucional("maria")

    assert pode_gerir_comissao(maria, edital_b.processo) is None


def test_presidente_nao_alocado_nao_atua(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    """FR-012: presidir não concede atuação. Para atuar, tem de estar alocado como qualquer um."""
    maria = ator_institucional("maria")

    assert pode_gerir_comissao(maria, processo_a) is not None
    assert pode_atuar_na_etapa(maria, edital_a, etapa_a1) is False


def test_alocado_atua_na_etapa_dele_e_nao_na_outra(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    joao = ator_institucional("joao")
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    assert pode_atuar_na_etapa(joao, edital_a, etapa_a1) is True
    # SC-010: alocação numa Etapa não alcança a vizinha, nem no mesmo Edital.
    assert pode_atuar_na_etapa(joao, edital_a, etapa_a2) is False


def test_escopo_divergente_nao_autoriza(processo_a, edital_a, comissao_de_a, etapa_a1):
    de_fora = ator_institucional("maria", PERMISSAO_SISTEMICA, escopo="outra-unidade")

    assert pode_gerir_comissao(de_fora, processo_a) is None
    assert pode_atuar_na_etapa(de_fora, edital_a, etapa_a1) is False


def test_minhas_etapas_ordena_o_numero_do_edital_como_numero(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """`number` é texto: sem conversão, o Edital 11 apareceria antes do 2."""
    from processo_seletivo.comissoes.application.selectors import _numero

    assert _numero("2") < _numero("11")
    assert _numero("07") < _numero("11")
    # Número não numérico não pode quebrar a ordenação — vai para o fim, em ordem alfabética.
    assert _numero("11") < _numero("11-A")


def test_a_chave_de_leitura_e_uma_so_para_toda_a_feature(gestor, processo_a, comissao_de_a):
    """Duas ordenações por nome no mesmo arquivo foi o que reintroduziu o defeito do acento.

    A lista da Comissão e o filtro da trilha ordenam pela mesma função — se alguém criar uma
    terceira ordenação por nome, este teste não a pega, mas a ausência de `casefold()` solto
    no módulo, sim.
    """
    import inspect

    from processo_seletivo.comissoes.application import selectors

    fonte = inspect.getsource(selectors)
    assert fonte.count(".casefold()") == 1, "a normalização de nome vive em `chave_de_leitura`"
    assert "unicodedata" in fonte


def test_o_filtro_da_trilha_ordena_ignorando_acento(gestor, processo_a):
    """“Íris” não pode cair depois de “Léo” num seletor que alguém vai percorrer com os olhos."""
    from processo_seletivo.comissoes.application.comissao import adicionar_varios
    from processo_seletivo.comissoes.application.selectors import pessoas_da_trilha

    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[("iri", "Íris Melo"), ("leo", "Léo Braga"), ("ana", "Ana Costa")],
        funcao="MEMBRO",
        idempotency_key="acento-na-trilha-0001",
        correlation_id="c",
    )

    lidos = [p["rotulo"] for p in pessoas_da_trilha(processo_a) if p["rotulo"]]

    assert lidos == ["Ana Costa", "Íris Melo", "Léo Braga"]


def test_o_filtro_da_trilha_mostra_o_rotulo_mais_recente(gestor, processo_a):
    """Quem saiu e voltou com outro nome é procurado pelo nome de agora."""
    from processo_seletivo.comissoes.application.comissao import (
        adicionar_varios,
        remover_membro,
    )
    from processo_seletivo.comissoes.application.selectors import pessoas_da_trilha
    from processo_seletivo.comissoes.models import MembroComissao

    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[("joao.souza", "João S.")],
        funcao="MEMBRO",
        idempotency_key="rotulo-antigo",
        correlation_id="c",
    )
    antigo = MembroComissao.objects.get(identity_subject="joao.souza")
    remover_membro(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=antigo.id,
        idempotency_key="rotulo-saida",
        correlation_id="c",
    )
    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=[("joao.souza", "João Souza Neto")],
        funcao="MEMBRO",
        idempotency_key="rotulo-novo",
        correlation_id="c",
    )

    pessoas = {p["subject"]: p["rotulo"] for p in pessoas_da_trilha(processo_a)}

    assert pessoas["joao.souza"] == "João Souza Neto"
    assert len([p for p in pessoas_da_trilha(processo_a) if p["subject"] == "joao.souza"]) == 1
