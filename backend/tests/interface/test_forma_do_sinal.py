"""A forma única do sinal (`_sinal.html`): o que ela diz da medida e de quem pode agir.

Os testes de sinal conferem a `Medida` como dado, e a unidade fica fora da igualdade dela
(`compare=False`). O que chega ao leitor, porém, é o template — e nenhum caso o renderizava com
unidade. Um `{% if %}` trocado ali apagaria *"recursos"* da tela inteira com a suíte verde.
"""

from django.template.loader import render_to_string

from processo_seletivo.interface import supervisao
from processo_seletivo.interface.conducao import CONDUCAO_DA_RETIFICACAO


def renderizar(**campos):
    sinal = supervisao.Sinal(
        especie=supervisao.UX_064,
        edital=None,
        alvo="Edital 01/2026",
        mensagem="Há recurso aguardando julgamento.",
        **campos,
    )
    return render_to_string("interface/_sinal.html", {"sinal": sinal})


def test_o_template_diz_a_unidade_no_plural_do_denominador():
    """`045`, `FR-743`, `UX-087`: *"1 de 2 recursos"*, e não *"1 de 2"*."""
    corpo = renderizar(
        medida=supervisao.Medida(numerador=1, denominador=2, unidade=supervisao.RECURSO)
    )

    assert '<p class="medida">1 de 2 recursos</p>' in corpo


def test_denominador_um_fica_no_singular():
    corpo = renderizar(
        medida=supervisao.Medida(numerador=1, denominador=1, unidade=supervisao.INSCRICAO)
    )

    assert '<p class="medida">1 de 1 inscrição</p>' in corpo


def test_sem_caminho_o_sinal_diz_a_quem_pedir():
    """`045`, `FR-740`: o ato não é do leitor, e a condução ocupa o lugar do caminho."""
    corpo = renderizar(conducao=CONDUCAO_DA_RETIFICACAO)

    assert '<p class="ajuda">' in corpo
    assert CONDUCAO_DA_RETIFICACAO in corpo
    assert 'class="acao"' not in corpo


def test_com_caminho_nao_ha_frase_de_conducao():
    """A contraprova: com o formulário à frente, *"peça a alguém"* seria falso (037, `FR-544`)."""
    corpo = renderizar(
        destino=supervisao.Destino(rotulo="Julgar recursos", url="/gestao/editais/1/recursos/"),
        conducao=CONDUCAO_DA_RETIFICACAO,
    )

    assert '<a class="acao" href="/gestao/editais/1/recursos/">Julgar recursos</a>' in corpo
    assert 'class="ajuda"' not in corpo
