"""058 — os resíduos do polish: o que já foi decidido para uma tela, na tela vizinha.

As medidas de tela — a largura a 375 px, o x dos valores da Revisão, a posição da nota da Matrículas
— estão em `specs/058-polish-residuos/verificacao.md`, tiradas na página renderizada. O que fica
aqui é o que as produz: a marcação no template, a regra na folha e o valor que o formulário recebe.
As provas da 2ª decisão (destinos por papel, envio e rascunho gravado) estão no mesmo diretório.
"""

import re
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.urls import reverse

from processo_seletivo.interface import forms
from tests.interface.conftest import identificar
from tests.interface.test_acessibilidade import sem_prosa
from tests.interface.test_exportacao_de_matriculas import (
    _primeira,
    cenario,  # noqa: F401 — fixture
    entrar,
    tela,
)
from tests.interface.test_polish_da_057 import FOLHA, GESTAO, da_pagina, regra
from tests.interface.test_processo import ato, sem_publicacao  # noqa: F401 — fixture

ATO_DO_PROCESSO = re.compile(r'<a class="([^"]*)" href="[^"]*/atos/(\w+)"')


def _atos(corpo):
    """`{chave: classe}` dos links de ato do Processo, e o trecho do grupo das terminais."""
    cartao = corpo.split('id="acoes-processo"', 1)[1].split("</section>", 1)[0]
    terminais = cartao.split('class="lista-acoes em-linha terminais"', 1)
    return (
        {chave: classe for classe, chave in ATO_DO_PROCESSO.findall(cartao)},
        terminais[1].split("</ul>", 1)[0] if len(terminais) == 2 else "",
    )


# ---- R1: o Processo -----------------------------------------------------------------------------


def test_as_terminais_moram_num_parcial_das_duas_telas():
    """FR-1069, D-002: as regras saem do Detalhe do Edital para um parcial que as duas incluem."""
    for pagina in ("detalhe.html", "processo_detalhe.html"):
        folha = da_pagina(pagina)
        assert "flex-direction:row" in regra(".lista-acoes.em-linha", folha), pagina
        assert "border-top:1px" in regra(".lista-acoes+.terminais", folha), pagina
        contorno = regra(".terminais .botao", folha)
        assert "background:var(--branco)" in contorno and "color:var(--vermelho)" in contorno
    for seletor in (".lista-acoes.em-linha", ".lista-acoes+.terminais", ".terminais .botao"):
        assert regra(seletor) is None, f"{seletor} não é da folha comum"
    assert regra(".colunas.ao-topo", da_pagina("detalhe.html"))
    assert regra(".colunas.ao-topo", da_pagina("processo_detalhe.html")) is None


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_processo_em_elaboracao_tem_ativar_secundario_e_cancelar_a_parte(
    client,
    seletor_ligado,
    sem_publicacao,  # noqa: F811
):
    """FR-1069, FR-1070: Ativar secundário; Cancelar no grupo de baixo, contornado, marcado."""
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[sem_publicacao.id])
    ).content.decode()

    classes, terminais = _atos(corpo)
    assert classes == {"ativar": "botao secundario", "cancelar": "botao perigoso"}
    # A ordem dos grupos não depende da ordem em que `ATOS` declara os atos.
    fonte = (GESTAO / "processo_detalhe.html").read_text()
    assert '{% regroup atos|dictsort:"irreversivel" by irreversivel as grupos %}' in fonte
    assert "/atos/cancelar" in terminais and "irreversível" in terminais
    assert "/atos/ativar" not in terminais
    assert corpo.index("/atos/ativar") < corpo.index("/atos/cancelar")
    assert "Publicar o primeiro Edital deste Processo já o ativa" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_processo_ativo_nao_tem_ato_cheio_fora_do_grupo(client, seletor_ligado, sem_publicacao):  # noqa: F811
    """SC-411: Encerrar e Cancelar só no grupo das terminais, cada um com o marcador; o aviso
    de impedimento continua depois deles, e os destinos são os de antes."""
    identificar(client, "marcia.gestora", ["gestor"])
    assert ato(client, sem_publicacao, "ativar", "Abertura formal").status_code == 302
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[sem_publicacao.id])
    ).content.decode()

    classes, terminais = _atos(corpo)
    # Encerrar `secundario`, como no Edital: discreto mesmo fora do grupo que o contorna.
    assert classes == {"encerrar": "botao secundario", "cancelar": "botao perigoso"}
    assert terminais.count("irreversível") == 2
    assert "/atos/encerrar" in terminais and "/atos/cancelar" in terminais
    # Sem ato comum acima, não há primeira lista — e o filete, que é de irmão, não se desenha.
    assert (
        'class="lista-acoes em-linha">'
        not in corpo.split('id="acoes-processo"', 1)[1].split("</section>", 1)[0]
    )
    assert corpo.index("/atos/cancelar") < corpo.index("estão impedidos")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_ato_o_cartao_diz_que_nao_ha(client, seletor_ligado, sem_publicacao):  # noqa: F811
    """FR-1070: a frase de ausência, e nenhum grupo vazio."""
    identificar(client, "leitora", ["auditor"])
    corpo = client.get(
        reverse("interface:processo-detalhe", args=[sem_publicacao.id])
    ).content.decode()

    assert "Nenhum ato disponível para seus papéis nesta situação." in corpo
    assert "terminais" not in corpo.split('id="acoes-processo"', 1)[1].split("</section>", 1)[0]


# ---- R2: 375 px ---------------------------------------------------------------------------------


def test_a_moldura_rola_so_abaixo_de_60_rem_na_mesma_regra_da_alocacao():
    """FR-1071, FR-1072, D-003: o mesmo limiar e a mesma declaração da matriz de Alocação; acima
    dele a moldura não é contêiner de rolagem, e o cabeçalho fixo da Alocação não muda."""
    # A folha tem mais de um bloco de 60 rem; o que importa é o da Alocação, onde quer que esteja.
    blocos = re.findall(r"@media \(max-width:60rem\)\{(.*?)\n\}", FOLHA, re.S)
    com_moldura = [bloco for bloco in blocos if ".rolavel-no-estreito" in bloco]
    assert len(com_moldura) == 1
    assert ".distribuicao-moldura,.rolavel-no-estreito{overflow-x:auto}" in com_moldura[0]
    fora = FOLHA
    for bloco in blocos:
        fora = fora.replace(bloco, "")
    assert ".rolavel-no-estreito" not in fora, "em tela larga a moldura é bloco comum"
    assert regra(".distribuicao-moldura", fora) == "overflow-x:visible"


@pytest.mark.parametrize(
    ("tela", "antes_da_tabela"),
    [("lista.html", "{% if processo.editais.all %}"), ("marco.html", "Recortes deste marco</h2>")],
)
def test_a_tabela_mora_na_moldura(tela, antes_da_tabela):
    """FR-1071, FR-1073: a tabela dentro da moldura, e não solta no cartão ou na seção."""
    fonte = (GESTAO / tela).read_text()
    trecho = fonte.split(antes_da_tabela, 1)[1]
    moldura = re.search(r'<div class="rolavel-no-estreito"[^>]*>', trecho)
    assert moldura and moldura.start() < trecho.index("<table>")
    assert re.search(r"</table>\s*</div>", trecho), "a moldura fecha logo depois da tabela"


# ---- R3, R4, R5: a mesma decisão na tela vizinha ---------------------------------------------


def test_a_secao_das_matriculas_nao_e_fileira_de_numeros():
    """FR-1074: `.resumo` é a classe dos blocos de números; numa `section`, punha o título e a nota
    lado a lado. Tirada, como a 055 fez na Ocupação."""
    fonte = (GESTAO / "matriculas.html").read_text()
    assert '<section aria-labelledby="lacunas">' in fonte
    assert 'class="resumo"' not in fonte


def test_nos_resultados_so_a_nota_vai_a_direita():
    """FR-1075, D-009: a tabela alcança `.tabela td.numero`, e só a nota pontuada leva `numero`."""
    fonte = (GESTAO / "resultados.html").read_text()
    assert '<table class="tabela">' in fonte
    assert '<td{% if resultado.forma == "PONTUADA" %} class="numero"{% endif %}>' in fonte
    assert 'class="numero">{% if resultado.forma == "DECISORIA"' not in fonte
    assert "text-align:right" in regra(".tabela td.numero,.tabela th.numero")


#: O texto que **grava** e por isso fica (D-004; o achado do F8): a frase anuncia o motivo do ato.
FICA = {
    "ocupacao.html": ["O déficit apurado de {{ recorte.faltando }} vaga(s) será a causa do ato"]
}


@pytest.mark.parametrize(
    "tela_",
    [
        "distribuicao.html",
        "matriculas.html",
        "recurso.html",
        "ocupacao.html",
        "ocupacao_historico.html",
        "compor_base.html",
    ],
)
def test_os_plurais_da_tela_concordam_com_o_numero(tela_):
    """FR-1076, FR-1077: nenhum "(s)" no texto que o template compõe, salvo o que grava ato."""
    texto = sem_prosa((GESTAO / tela_).read_text())
    for frase in FICA.get(tela_, []):
        assert frase in texto, "o texto que grava ato não muda"
        texto = texto.replace(frase, "")
    assert not re.findall(r"\w\((s|es|ões)\)", texto)


@pytest.mark.django_db
def test_a_previa_das_matriculas_escreve_linha_no_numero_dela(client, seletor_ligado, cenario):  # noqa: F811
    """FR-1076 na tela: "2 linhas", e nunca "linha(s)"."""
    edital, _ = cenario
    entrar(client)
    corpo = " ".join(client.get(tela(edital, populacao=_primeira(edital))).content.decode().split())
    assert "(s)" not in corpo
    assert re.search(r"<strong>2</strong> linhas\.", corpo)


# ---- R6: o valor das Etapas ----------------------------------------------------------------------


def _etapa(**numeros):
    campos = dict(
        id="e1",
        name="Prova",
        order=1,
        eliminatory=False,
        classificatory=True,
        evaluations_per_registration=None,
        forma="PONTUADA",
        rotulo_favoravel="",
        rotulo_desfavoravel="",
        evento_id=None,
        weight=None,
        minimum_score=None,
        maximum_score=None,
    )
    return SimpleNamespace(**{**campos, **numeros})


def test_os_numeros_das_etapas_chegam_ao_campo_sem_zeros_a_direita():
    """FR-1078, D-005: "2", "6", "87.5" — com ponto, que é o que o `value` de um campo numérico
    aceita; quem mostra a vírgula é o navegador. Nada é arredondado, e vazio continua vazio."""
    etapas = [
        _etapa(weight=Decimal("2.0000"), minimum_score=Decimal("6.0000")),
        _etapa(maximum_score=Decimal("87.5000"), weight=Decimal("100.0000")),
        _etapa(minimum_score=Decimal("60.0050"), weight=Decimal("0.0001")),
    ]
    edital = SimpleNamespace(etapas=SimpleNamespace(order_by=lambda *_: etapas))

    linhas = forms.etapas_do_edital(edital)

    assert [(e["weight"], e["minimumScore"], e["maximumScore"]) for e in linhas] == [
        ("2", "6", ""),
        ("100", "", "87.5"),
        ("0.0001", "60.005", ""),
    ]
    for linha, etapa in zip(linhas, etapas, strict=True):
        for chave, campo in (("weight", "weight"), ("minimumScore", "minimum_score")):
            if linha[chave]:
                assert Decimal(linha[chave]) == getattr(etapa, campo), "o mesmo número"


# ---- R7, R8: os dois desalinhamentos -------------------------------------------------------------


def test_a_coluna_de_rotulos_da_revisao_tem_uma_largura_so():
    """FR-1080, FR-1081, D-006: o teto de 16 rem virou a largura, igual em todo bloco; o `min`
    só age em tela estreita."""
    grade = regra(".conferencia .dados-da-inscricao", da_pagina("compor_revisao.html"))
    assert "grid-template-columns:min(16rem,40%)1fr" in grade
    assert "fit-content" not in grade


MOTIVO_EM_AREA = re.compile(
    r'<p class="campo">\s*<label for="(motivo[^"]*)">[^<]*(?:<span[^>]*>\*</span>)?</label>\s*'
    r"(?:\{% comment %\}.*?\{% endcomment %\}\s*)?"
    r'<textarea id="\1" name="motivo" rows="3" required',
    re.S,
)


@pytest.mark.parametrize(
    ("pagina", "rotulo"),
    [
        ("ordenacao.html", "Motivo da sucessão"),
        ("corte.html", "Motivo da sucessão"),
        ("ocupacao.html", "Motivo da nova apuração"),
        ("sorteio.html", "Motivo da sucessão"),
    ],
)
def test_o_motivo_de_sucessao_tem_o_mesmo_controle_nas_quatro_telas(pagina, rotulo):
    """FR-1082, D-007: área de texto de três linhas em `p.campo`, que é o que dá a largura de
    leitura (`.campo>textarea`). O nome do campo não muda."""
    fonte = (GESTAO / pagina).read_text()
    assert MOTIVO_EM_AREA.search(fonte), pagina
    assert f">{rotulo}" in fonte
    assert "max-width:var(--leitura)" in regra(
        ".campo>textarea,.campo>input[type=text],.campo>input[type=search],.campo>input[type=email]"
    )


def test_o_motivo_da_anulacao_fica_como_esta():
    """FR-1083, D-008: a anulação não sucede ato, e não é o motivo de que a reavaliação fala."""
    fonte = (GESTAO / "sorteio.html").read_text()
    assert re.search(
        r'<input type="text" id="anulacao-\{\{ forloop.counter \}\}" name="motivo"', fonte
    )


def test_a_moldura_da_conducao_e_focavel_e_nomeada():
    """FR-1073: há células sem link, e sem foco a moldura não rolaria pelo teclado."""
    fonte = (GESTAO / "marco.html").read_text()
    assert (
        '<div class="rolavel-no-estreito" tabindex="0" role="region"'
        ' aria-labelledby="indicador-titulo">' in fonte
    )
