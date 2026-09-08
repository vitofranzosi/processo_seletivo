"""Aberta e encerrada precisam parecer coisas diferentes — e a diferença estava suprimida.

Na vitrine, o cartão da seleção aberta e o da encerrada tinham a **mesma** superfície branca, a
mesma borda e o mesmo título verde. A distinção existia, mas nos dois lugares mais quietos: um
título de seção em cinza acima, e uma frase no rodapé do cartão.

Pior que isso: a frase da aberta também era cinza. `.selecao .situacao{color:var(--texto-fraco)}`
foi escrita para **a lista de inscrições do candidato**, onde o cinza é a situação da inscrição — e
as duas telas usam `ul.selecoes > li.selecao` para coisas diferentes. Solta, a regra vencia
`.situacao.aberto` por ordem na folha e deixava "Inscrições abertas" do mesmo tom de "Inscrições
encerradas".

O que estes testes prendem é a cor de estado voltar à vitrine, e a regra da outra tela ficar na
outra tela. O que eles **não** prendem é a superfície: um Edital encerrado continua sendo ato
normativo publicado, e apagá-lo visualmente diria "descartado" onde o certo é "não recebe mais
inscrição".
"""

import re

import pytest
from django.urls import reverse

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def folha(client):
    corpo = client.get(reverse("portal:vitrine")).content.decode()
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


def regra(folha, seletor):
    achado = re.search(re.escape(seletor) + r"\{([^}]*)\}", folha)
    return achado.group(1) if achado else None


def test_a_situacao_da_vitrine_nao_e_pintada_pela_regra_da_outra_tela(folha):
    """A regra do cinza fica onde ela foi escrita para valer."""
    da_vitrine = regra(folha, ".selecao .situacao")
    assert da_vitrine is not None, "a folha não desenha a situação do cartão"
    assert "color" not in da_vitrine, (
        f"a vitrine volta a pintar a situação por cima do estado: {da_vitrine}"
    )


def test_a_lista_de_inscricoes_conserva_o_cinza_que_e_dela(folha):
    """Escopar não pode virar apagar: lá o cinza é a situação **da inscrição**."""
    assert "--texto-fraco" in (regra(folha, ".minhas-inscricoes .situacao") or "")
    assert "--sucesso" in (regra(folha, ".minhas-inscricoes .situacao.enviada") or "")


def test_a_lista_de_inscricoes_se_declara_pelo_nome():
    """Sem a classe no template, a regra escopada não alcança nada e o cinza de lá some calado.

    A guarda de classes órfãs cobre o sentido oposto — classe citada sem regra. Esta cobre o que
    escopar introduz: regra sem quem a cite. Lê o template, como a guarda irmã já faz, porque a
    página exige sessão de candidato **e** inscrição criada para renderizar a lista.
    """
    from pathlib import Path

    template = (
        Path(__file__).resolve().parents[1]
        / "../processo_seletivo/portal/templates/portal/inscricoes.html"
    ).resolve()

    assert "minhas-inscricoes" in template.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("estado", "esperado"),
    [("aberto", "--sucesso"), ("encerrado", "--texto-fraco")],
)
def test_cada_estado_do_periodo_tem_a_sua_cor(folha, estado, esperado):
    """É a única cor que separa os dois cartões, já que a superfície é a mesma de propósito."""
    assert esperado in (regra(folha, f".situacao.{estado}") or "")
