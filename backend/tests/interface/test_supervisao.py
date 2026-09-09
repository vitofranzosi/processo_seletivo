"""A página da supervisão: o que ela apresenta, o que ela recusa apresentar, e para onde encaminha.

Os testes de derivação vivem em `tests/integration/supervisao/`; aqui ficam os que só existem no
canal — a região anunciada, o equivalente textual da série, e as proibições de apresentação.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.supervisao import rascunhar, submeter
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:supervisao", args=[processo.id])


def abrir(client, processo, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(url(processo))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def regiao(corpo, ancora):
    """O trecho de uma das duas regiões, delimitado pelo `<section>` que a anuncia.

    Procurar no documento inteiro faria uma asserção sobre o Pulso passar ou falhar por causa de
    algo escrito na Atenção — e as duas regiões existem justamente porque são coisas diferentes.

    O fechamento é contado, e não procurado: a região do Pulso tem um bloco por Edital, e um
    recorte que parasse no primeiro `</section>` devolveria o cabeçalho e mais nada — passando
    silenciosamente em toda asserção de ausência.
    """
    abertura = re.search(rf'<section[^>]*aria-labelledby="{ancora}"[^>]*>', corpo)
    assert abertura is not None, f"a região {ancora} não foi anunciada como região"
    profundidade, posicao = 0, abertura.start()
    for marca in re.finditer(r"<section\b|</section>", corpo[abertura.start() :]):
        profundidade += 1 if marca.group(0) != "</section>" else -1
        if profundidade == 0:
            return corpo[posicao : posicao + marca.end()]
    raise AssertionError(f"a região {ancora} não foi fechada")


def texto(trecho):
    """O que a região **apresenta**, sem marcação.

    A asserção de "nenhum percentual" precisa disto: a altura de uma barra é `style="height:40%"`,
    e um `%` dentro de atributo é unidade de desenho, não informação. Procurar no HTML cru faria o
    teste falhar por causa da folha de estilo e passar quando o número aparecesse escrito.
    """
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def sem_espacos(trecho):
    """O trecho sem espaço em branco algum — para comparar marcação sem depender de indentação."""
    return re.sub(r"\s+", "", trecho)


def test_as_duas_regioes_sao_anunciadas_com_titulo_proprio(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-006`: quem navega por marcos salta de uma para a outra sem varrer a página."""
    corpo = abrir(client, processo_a)

    assert 'id="pulso-titulo"' in corpo
    assert 'id="atencao-titulo"' in corpo


def test_nenhum_percentual_e_apresentado_sobre_inscricao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-017` e `SC-005`: não há denominador normativo para inscrição.

    Um percentual de avanço aqui responderia "quanto falta" a uma pergunta que ninguém pode
    responder — não existe o número de inscrições que o Edital espera receber.
    """
    submeter(edital_a, 7)
    rascunhar(edital_a, 2)
    # Com submissões no Edital que tem período, a série é desenhada — e é justamente aí que um `%`
    # aparece na marcação, como altura de barra. O que a região não pode é **apresentar** um.
    submeter(edital_c, 3, seed=2)

    corpo = abrir(client, processo_a)

    pulso = regiao(corpo, "pulso-titulo")
    assert "barra" in pulso, "sem série desenhada o teste não exercita o caso que ele protege"
    assert "%" not in texto(pulso)


def test_o_pulso_nomeia_o_edital_de_cada_contagem(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-011`, `FR-020` e `UX-007`: nenhuma linha do Edital aparece sem dizer de qual Edital é."""
    submeter(edital_a, 3)
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert f"{edital_a.number}/{edital_a.year}" in pulso
    assert f"{edital_c.number}/{edital_c.year}" in pulso


def test_o_rascunho_usa_o_termo_que_a_tela_de_inscricoes_ja_usa(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`Princípio I`: dois termos para o mesmo conceito é o que a linguagem ubíqua recusa.

    A tela da `009` chama o rascunho de **em preenchimento**. Enquanto não houver decisão de
    vocabulário que valha para as duas telas, a supervisão adota o termo vigente — e não inventa
    um segundo.
    """
    rascunhar(edital_a, 2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "preenchimento" in pulso.lower()


def test_a_serie_tem_equivalente_textual_com_os_mesmos_valores(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-016`, `UX-008` e `SC-015`: o gráfico é desenho; os números vivem na tabela.

    A asserção compara **os mesmos valores** que a derivação produziu, e não uma amostra: um
    equivalente que perdesse um dia seria pior do que nenhum, porque pareceria completo.
    """
    from datetime import timedelta

    from django.utils import timezone

    from processo_seletivo.interface import supervisao as leitura

    agora = timezone.now()
    submeter(edital_c, 2, quando=agora - timedelta(days=2), seed=2)
    submeter(edital_c, 5, primeiro=40, quando=agora - timedelta(days=1), seed=2)

    corpo = abrir(client, processo_a)

    serie = next(
        item.serie for item in leitura.pulso(processo_a).por_edital if item.edital.id == edital_c.id
    )
    assert serie, "o Edital com período declarado precisa ter série"
    pulso = sem_espacos(regiao(corpo, "pulso-titulo"))
    for ponto in serie:
        linha = sem_espacos(
            f'<tr><th scope="row">{ponto.dia.strftime("%d/%m/%Y")}</th>'
            f"<td>{ponto.quantidade}</td></tr>"
        )
        assert linha in pulso, f"o dia {ponto.dia} não aparece no equivalente textual"


def test_as_barras_da_serie_nao_sao_lidas_como_conteudo(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-008`: o desenho não pode ser anunciado duas vezes a quem ouve a tela."""
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert '<ul class="barras" aria-hidden="true">' in pulso


def test_a_ausencia_de_periodo_em_curso_e_declarada(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a
):
    """`FR-018`: dito, e não deixado como um zero sem qualificação."""
    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "Nenhum Edital com período de inscrições em curso" in texto(pulso)
    assert "últimas 24 horas" not in texto(pulso)
