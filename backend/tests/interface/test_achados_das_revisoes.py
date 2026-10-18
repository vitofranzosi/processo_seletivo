"""Os achados das revisões da 077 e da 079 que esta feature corrige (081).

Na Distribuição, a consolidação deixou de pesar o mesmo que a distribuição sobre a mesma seleção;
na Alocação, o aviso diz o ato da tela; e o cenário da presidência deixou de ser importado de um
módulo de teste para outro. Os achados que ficaram como decisão estão na spec, com o motivo. O
desenho em si é provado no navegador e pelo inventário visual refeito (quickstart): aqui fica o que
a marcação garante.
"""

import ast
import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.fixtures.comissao import constituir
from tests.fixtures.mesa import montar_cenario_da_presidencia
from tests.interface.conftest import identificar
from tests.interface.test_telas_de_uso_diario import TEMPLATES, conteudo

TESTES_DA_INTERFACE = Path(__file__).resolve().parent

DISTRIBUIR = '<button type="submit" class="botao">Distribuir as selecionadas</button>'
MARCA = '<span class="marca-irreversivel">irreversível</span>'


@pytest.fixture
def cenario(gestor, api_client, manager_headers, raiz_de_arquivos):
    return montar_cenario_da_presidencia(gestor, api_client, manager_headers)


def distribuicao(client, cenario):
    identificar(client, "maria", [])
    resposta = client.get(
        reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["etapa"]])
    )
    assert resposta.status_code == 200
    return conteudo(resposta.content.decode())


def acoes_sobre_a_selecao(pagina):
    """O parágrafo das ações do formulário das inscrições: o que começa em "Distribuir"."""
    inicio = pagina.rindex('<p class="acoes">', 0, pagina.index(DISTRIBUIR))
    return pagina[inicio : pagina.index("</p>", pagina.index(DISTRIBUIR))]


# ---- o que não se desfaz não pesa como a rotina ----------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_consolidar_as_selecionadas_tem_o_desenho_dos_atos_irreversiveis(
    client, seletor_ligado, cenario
):
    """`FR-1820`, `SC-711`: um botão cheio sobre a seleção, e a marca logo depois do outro."""
    acoes = acoes_sobre_a_selecao(distribuicao(client, cenario))

    assert acoes.count('class="botao"') == 1
    assert DISTRIBUIR in acoes
    consolidar = acoes.split('<button type="submit" class="botao secundario"')[1]
    rotulo, depois = consolidar.split("</button>")
    assert "Consolidar as selecionadas" in rotulo
    # A marca acompanha o botão que qualifica, e é a última coisa da linha.
    assert depois.strip() == MARCA


@pytest.mark.django_db
@pytest.mark.integration
def test_consolidar_as_selecionadas_continua_onde_e_como_estava(client, seletor_ligado, cenario):
    """`FR-1821`: o mesmo destino, nome e valor, depois de "Distribuir", e a frase da `FR-422` da
    030 antes dos dois."""
    pagina = distribuicao(client, cenario)
    acoes = acoes_sobre_a_selecao(pagina)
    destino = reverse(
        "interface:consolidar-resultados", args=[cenario["edital"].id, cenario["etapa"]]
    )

    consolidar = acoes.split('class="botao secundario"')[1].split(">")[0]
    assert f'formaction="{destino}"' in consolidar
    assert 'name="chave_idempotencia"' in consolidar
    assert acoes.index(DISTRIBUIR) < acoes.index("Consolidar as selecionadas")
    assert pagina.index("<dfn>Consolidar</dfn> é transformar") < pagina.index(DISTRIBUIR)
    assert '<button type="submit" class="acao perigoso">Retirar as selecionadas</button>' in pagina


def test_a_marca_nao_estica_na_linha_das_acoes():
    """`FR-1820`: `.acoes` é flexível, e a marca, que tem fundo, esticaria até a altura do botão."""
    folha = (TEMPLATES / "base.html").read_text()
    assert ".acoes .marca-irreversivel{align-self:center}" in folha


# ---- a Alocação diz alocar -------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_alocacao_sem_presidencia_diz_alocar(client, seletor_ligado, gestor, processo_a):
    """`FR-1822`, `SC-712`: o aviso com o ato da tela, no mesmo papel e com o mesmo link."""
    constituir(gestor, processo_a, [("joao", "MEMBRO")])
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:alocacoes", args=[processo_a.id])).content.decode()

    comissao = reverse("interface:comissao", args=[processo_a.id])
    assert (
        '<p class="aviso" role="status"><strong>Designe a presidência antes de alocar.</strong>\n'
        f'  <a href="{comissao}">Ir para a Comissão</a></p>'
    ) in corpo
    assert "antes de distribuir" not in corpo


# ---- o apoio dos testes ----------------------------------------------------------------------


def test_nenhum_modulo_importa_o_cenario_da_presidencia():
    """`FR-1823`, `SC-713`: a montagem mora em `tests/fixtures/mesa.py`, e cada módulo declara a
    fixture dele — importada, ela sombreava o parâmetro e pedia dois `noqa`."""
    importadores = []
    for modulo in TESTES_DA_INTERFACE.glob("test_*.py"):
        for no in ast.walk(ast.parse(modulo.read_text())):
            if isinstance(no, ast.ImportFrom) and no.module == (
                "tests.interface.test_acessibilidade_da_012"
            ):
                if any(nome.name == "cenario" for nome in no.names):
                    importadores.append(modulo.name)
    assert importadores == []


def test_toda_trilha_do_cabecalho_abre_com_a_mesma_navegacao():
    """`FR-1824`: o rótulo e a classe da trilha continuam escritos em cada tela que a sobrescreve
    (D-003 da 081), e este guardião é o que impede uma delas de ficar com a grafia antiga."""

    def sem_espaco(texto):
        # Duas telas da Mesa quebram a linha entre a `nav` e o parcial; o que se compara é a grafia.
        return re.sub(r"\s+", "", texto)

    abertura = sem_espaco(
        '<nav aria-label="Trilha de navegação" class="caminho-da-secao">'
        '{% include "interface/_produto_na_trilha.html" %}'
    )
    inicio, fim = sem_espaco("{% block caminho_do_contexto %}"), sem_espaco("{% endblock %}")
    blocos = {}
    for template in sorted(TEMPLATES.glob("*.html")):
        texto = sem_espaco(template.read_text())
        if template.name != "base.html" and inicio in texto:
            blocos[template.name] = texto.split(inicio)[1].split(fim)[0]
    assert len(blocos) >= 17, "as telas da 077 à 080 sobrescrevem a trilha"
    # Toda `nav` do bloco, e não só a primeira: a auditoria tem uma por ramo.
    fora = [
        nome
        for nome, bloco in blocos.items()
        if "<nav" not in bloco
        or any(not ("<nav" + resto).startswith(abertura) for resto in bloco.split("<nav")[1:])
    ]
    assert fora == []
