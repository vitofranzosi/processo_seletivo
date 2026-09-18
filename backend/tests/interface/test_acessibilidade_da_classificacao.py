"""A tabela larga rola dentro de si; a página continua cabendo em 375 px."""

import re
from pathlib import Path

import pytest


def test_toda_tabela_da_classificacao_tem_conteiner_rolavel():
    templates = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo"
        / "interface"
        / "templates"
        / "interface"
    )
    for nome in ("ordenacao.html", "ato_ordenacao.html"):
        corpo = (templates / nome).read_text()
        assert corpo.count("<table") == corpo.count('class="tabela-rolavel"')


def test_o_conteiner_limita_a_rolagem_horizontal():
    base = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo"
        / "interface"
        / "templates"
        / "interface"
        / "base.html"
    )
    assert ".tabela-rolavel{overflow-x:auto}" in base.read_text()


# --- Nenhum campo obrigatório fora da tela (030, FR-414 a FR-418) ----------------------------
#
# A regra está escrita no alto de `_marco.html` e custou caro: campo `required` invisível é
# submissão que o navegador recusa **sem conseguir mostrar o que falta**. A revelação progressiva
# multiplicou os estados do cartão — a forma da ordem, a quantidade de Etapas —, e cada um deles é
# uma chance de o `required` ficar para trás junto com o campo que saiu.
#
# Os campos impertinentes viajam como `<input type="hidden">`, e é justamente por isso que o
# cuidado é necessário: `hidden` com `required` é a mesma submissão travada, agora sem nem o
# recurso de abrir um bloco.

ESTADOS_DO_CARTAO = {
    "sem forma declarada": {},
    "ordena por sorteio": {"orderProduction": "POR_SORTEIO"},
    "ordena por pontuação": {"orderProduction": "POR_PONTUACAO"},
    "uma Etapa só": {
        "orderProduction": "POR_PONTUACAO",
        "etapas": ["11111111-1111-1111-1111-111111111111"],
    },
    "método guardado e impertinente": {
        "orderProduction": "POR_PONTUACAO",
        "drawAlgorithm": "IFES-SORTEIO-SHA256-v1",
    },
}

_DETALHE_FECHADO = re.compile(r"<details(?![^>]*\bopen\b)[^>]*>.*?</details>", re.I | re.S)
_OBRIGATORIO = re.compile(r"<(input|select|textarea)\b[^>]*\brequired\b[^>]*>", re.I)


def _cartao(**marco):
    from django.template.loader import render_to_string

    return render_to_string(
        "interface/_marco.html",
        {
            "marco": {"id": "11111111-1111-1111-1111-111111111111", **marco},
            "indice": "p0",
            "sub": 0,
            "etapas_classificatorias": [
                {"id": "11111111-1111-1111-1111-111111111111", "rotulo": "Prova"},
                {"id": "22222222-2222-2222-2222-222222222222", "rotulo": "Títulos"},
            ],
            "etapas_governaveis": [],
            "fatos_declarados": [],
        },
    )


@pytest.mark.parametrize("estado", sorted(ESTADOS_DO_CARTAO), ids=lambda nome: nome)
def test_nenhum_campo_obrigatorio_e_renderizado_fora_da_tela(estado):
    cartao = _cartao(**ESTADOS_DO_CARTAO[estado])

    ocultos = [
        achado.group(0)
        for achado in _OBRIGATORIO.finditer(cartao)
        if 'type="hidden"' in achado.group(0)
    ]
    assert ocultos == [], f"campo oculto e obrigatório em «{estado}»: {ocultos}"

    dentro_de_bloco_fechado = _OBRIGATORIO.findall(cartao) != _OBRIGATORIO.findall(
        _DETALHE_FECHADO.sub(" ", cartao)
    )
    assert not dentro_de_bloco_fechado, f"campo obrigatório dentro de bloco fechado em «{estado}»"


def test_o_marco_de_sorteio_nao_exige_etapa_na_tela():
    """FR-432 na folha: a exigência sai junto com a regra que deixou de valer."""
    seletor = re.search(
        r'<select[^>]*name="marco-p0-0-stages"[^>]*>', _cartao(orderProduction="POR_SORTEIO")
    )

    assert seletor is not None
    assert "required" not in seletor.group(0)


# --- Nenhuma ajuda visível dentro dos cartões de composição (030, FR-428) --------------------
#
# A decisão é do projeto, e é anterior a esta feature: explicação que não muda de um Perfil para o
# outro não se imprime uma vez por Perfil — num Edital de sete polos ela apareceria sete vezes, e
# vinte e uma quando o cartão é o da Modalidade. O que a `030` faz é mantê-la enquanto acrescenta
# microcópia: toda definição nova foi para o `como-preencher` da etapa, nunca para o cartão.
#
# **E o equivalente para tecnologia assistiva permanece.** Sair de vista não pode virar sair do
# produto: cada campo continua apontando, por `aria-describedby`, para a descrição que o explica.

CARTOES = ("_marco.html", "_perfil.html", "_modalidade.html")

#: As classes que desenham texto de ajuda **visível**. `oculto` não está aqui de propósito: ela é o
#: equivalente para tecnologia assistiva, e é o que precisa continuar existindo.
#:
#: `declaracao-derivada` também não: ela não é ajuda. Ajuda explica como preencher um campo; aquela
#: frase declara o que o sistema faz **no lugar** de um campo que deixou de existir (FR-416), e
#: esconder o que se afirma sobre a norma seria o oposto do que a feature promete.
CLASSES_DE_AJUDA_VISIVEL = ("ajuda", "explicacao", "definicoes", "como-preencher")

_COMENTARIO_DO_DJANGO = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)


def _sem_comentario(nome):
    caminho = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/templates/interface"
        / nome
    )
    return _COMENTARIO_DO_DJANGO.sub(" ", caminho.read_text())


@pytest.mark.parametrize("cartao", CARTOES)
def test_nenhum_cartao_de_composicao_traz_ajuda_visivel(cartao):
    corpo = _sem_comentario(cartao)
    encontradas = [classe for classe in CLASSES_DE_AJUDA_VISIVEL if f'class="{classe}"' in corpo]

    assert encontradas == [], (
        f"{cartao} voltou a trazer ajuda visível ({encontradas}): microcópia nova vai para o "
        "`como-preencher` da etapa, e não para dentro do cartão (FR-428)"
    )


@pytest.mark.parametrize("cartao", CARTOES)
def test_o_equivalente_para_tecnologia_assistiva_permanece(cartao):
    """Sair de vista não é sair do produto: cada descrição tem `id`, e algum campo a aponta."""
    corpo = _sem_comentario(cartao)
    # **Por conteúdo do atributo, e não por partição dele.** Aqui os valores são template —
    # `ajuda-perc-{{ indice }}-{{ sub }}`, e um deles ainda tem um `{% if %}` dentro —, de modo
    # que `split()` os quebraria no meio das chaves. O que importa é que a descrição seja
    # apontada; um atributo que a contenha é exatamente isso.
    descricoes = set(re.findall(r'class="oculto" id="([^"]+)"', corpo))
    apontadas = re.findall(r'aria-describedby="([^"]+)"', corpo)

    assert descricoes, f"{cartao} não descreve campo nenhum a leitor de tela"
    orfas = sorted(
        descricao
        for descricao in descricoes
        if not any(descricao in atributo for atributo in apontadas)
    )
    assert orfas == [], f"{cartao} tem descrição que nenhum campo aponta: {orfas}"
