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
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, semear_prontas
from tests.interface.conftest import identificar
from tests.interface.test_telas_de_uso_diario import TEMPLATES, conteudo

TESTES_DA_INTERFACE = Path(__file__).resolve().parent

DISTRIBUIR = '<button type="submit" class="botao">Distribuir as selecionadas</button>'


def marca(identificador):
    return f'<span class="marca-irreversivel" id="{identificador}">irreversível</span>'


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
    assert depois.strip() == marca("consolidar-selecionadas-irreversivel")


@pytest.mark.django_db
@pytest.mark.integration
def test_a_marca_descreve_o_botao_para_quem_nao_a_ve(client, seletor_ligado, cenario):
    """`FR-1827`: o leitor de tela anuncia "irreversível" junto do botão, no foco, e não só quem
    percorre a página linha a linha."""
    acoes = acoes_sobre_a_selecao(distribuicao(client, cenario))

    abertura = acoes.split('class="botao secundario"')[1].split(">")[0]
    alvo = re.search(r'aria-describedby="([^"]+)"', abertura).group(1)
    assert f'id="{alvo}">irreversível</span>' in acoes


@pytest.mark.django_db
@pytest.mark.integration
def test_consolidar_as_prontas_tem_o_mesmo_desenho(
    client, seletor_ligado, gestor, api_client, manager_headers
):
    """`FR-1828`: o mesmo ato com o mesmo desenho nos dois lugares da página — nenhum botão cheio
    leva à consolidação, e as duas marcas descrevem os seus botões."""
    etapa = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1811, codigo="1811"
    )
    semear_prontas(etapa, 2, primeiro=1)
    identificar(client, "maria", ["gestor"])
    pagina = conteudo(
        client.get(
            reverse("interface:distribuicao", args=[etapa["edital"].id, etapa["primeira"]])
        ).content.decode()
    )

    linha = pagina.split('<input type="hidden" name="alcance" value="prontas">')[1]
    linha = linha[
        linha.index('<p class="acoes">') : linha.index("</p>", linha.index('<p class="acoes">'))
    ]
    assert '<button type="submit" class="botao secundario"' in linha
    assert 'aria-describedby="consolidar-prontas-irreversivel"' in linha
    assert "Consolidar as 2 prontas</button>" in linha
    assert marca("consolidar-prontas-irreversivel") in linha
    cheios = re.findall(r'<button type="submit" class="botao"[^>]*>\s*([^<]*)', pagina)
    assert not [rotulo for rotulo in cheios if "Consolidar" in rotulo]


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


def test_a_marca_nao_estica_em_linha_flexivel():
    """`FR-1820`: em linha flexível a marca, que tem fundo, esticaria até a altura do botão; a
    regra mora na própria marca, e não num contêiner (R-002)."""
    folha = (TEMPLATES / "base.html").read_text()
    regra = re.search(r"^\.marca-irreversivel\s*\{([^}]*)\}", folha, re.M)
    assert regra, "a marca perdeu a regra própria"
    assert re.search(r"align-self\s*:\s*center", regra.group(1))
    # E nenhum seletor de contêiner em volta dela (`.acoes .marca-irreversivel`), que era a primeira
    # versão: valia numa linha flexível só.
    assert not re.search(r"^[^\n{}]*\S[ \t]+\.marca-irreversivel\s*\{", folha, re.M)


# ---- a Alocação diz alocar -------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_alocacao_sem_presidencia_diz_alocar(client, seletor_ligado, gestor, processo_a):
    """`FR-1822`, `SC-712`: o aviso com o ato da tela, no mesmo papel e com o mesmo link."""
    constituir(gestor, processo_a, [("joao", "MEMBRO")])
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:alocacoes", args=[processo_a.id])).content.decode()

    aviso = corpo.split('<p class="aviso" role="status">')[1].split("</p>")[0]
    assert "<strong>Designe a presidência antes de alocar.</strong>" in aviso
    comissao = reverse("interface:comissao", args=[processo_a.id])
    assert f'<a href="{comissao}">Ir para a Comissão</a>' in aviso
    assert "antes de distribuir" not in corpo


# ---- o apoio dos testes ----------------------------------------------------------------------


def declara_o_cenario_da_presidencia(arvore):
    """O módulo declara uma fixture `cenario` que chama `montar_cenario_da_presidencia`."""
    for no in arvore.body:
        if isinstance(no, ast.FunctionDef) and no.name == "cenario":
            # Pelo nome importado ou pelo módulo (`mesa.montar_cenario_da_presidencia`).
            chamadas = {
                getattr(chamada.func, "id", None) or getattr(chamada.func, "attr", None)
                for chamada in ast.walk(no)
                if isinstance(chamada, ast.Call)
            }
            if "montar_cenario_da_presidencia" in chamadas:
                return True
    return False


def test_nenhum_modulo_importa_o_cenario_da_presidencia():
    """`FR-1823`, `SC-713`: a montagem mora em `tests/fixtures/mesa.py`, e cada módulo declara a
    fixture dele — importada, ela sombreava o parâmetro e pedia dois `noqa`. Vale para todo módulo
    que a declara, e não só para o da `012`, de onde ela saiu: os da 077, da 079 e da 080 também
    são lidos por outros, que importam deles os auxiliares."""
    arvores = {
        f"tests.interface.{modulo.stem}": ast.parse(modulo.read_text())
        for modulo in TESTES_DA_INTERFACE.glob("test_*.py")
    }
    donos = {nome for nome, arvore in arvores.items() if declara_o_cenario_da_presidencia(arvore)}
    assert "tests.interface.test_acessibilidade_da_012" in donos
    importadores = [
        nome
        for nome, arvore in arvores.items()
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom)
        and no.module in donos
        and any(apelido.name == "cenario" for apelido in no.names)
    ]
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
    inicio = sem_espaco("{% block caminho_do_contexto %}")
    # `{% endblock %}` ou `{% endblock caminho_do_contexto %}`: o bloco termina no primeiro dos
    # dois, e não no `endblock` do conteúdo, que tem trilhas próprias.
    fim = re.compile(r"\{%endblock(?:caminho_do_contexto)?%\}")
    blocos = {}
    for template in sorted(TEMPLATES.glob("*.html")):
        texto = sem_espaco(template.read_text())
        if template.name != "base.html" and inicio in texto:
            blocos[template.name] = fim.split(texto.split(inicio)[1])[0]
    # A lista da 077 é a primeira tela a sobrescrever: se ela sumir daqui, a leitura falhou.
    assert "lista.html" in blocos
    # Toda `nav` do bloco, e não só a primeira: a auditoria tem uma por ramo. Um bloco sem `nav` —
    # o cabeçalho da 076 refeito, ou só o `block.super` — não é trilha, e não é desta regra.
    fora = [
        nome
        for nome, bloco in blocos.items()
        if any(not ("<nav" + resto).startswith(abertura) for resto in bloco.split("<nav")[1:])
    ]
    assert fora == []
