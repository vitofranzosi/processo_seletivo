"""O que o servidor entrega à vista do conjunto dos Perfis (052).

A tabela e o cartão à vista são montados pelo `perfis.js`, e o que ele faz no navegador — foco,
`hidden`, a validação nativa — se verifica no preview (quickstart.md) e, nas regras puras, em
`tests/javascript/perfis.test.js`. Aqui fica o que o script não tem como saber sozinho, e a promessa
que torna a vista inofensiva: **o formulário é o mesmo**.

- a legenda identifica o Perfil, também sem script (FR-944);
- o cartão diz quantas pendências da etapa o têm por objeto (FR-948) e se o que o servidor devolveu
  difere do gravado (FR-949) — e a devolução sem mudança não acusa nada;
- a etapa vem na ordem tabela → conjunto → cartões, com nenhum cartão escondido pelo servidor
  (UX-120, FR-955);
- o script não cria, remove nem renomeia campo (FR-950, SC-350).
"""

import html
import re
import uuid
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.interface import forms
from processo_seletivo.interface.templatetags.interface_extras import legenda_do_perfil
from processo_seletivo.interface.views import _pendencias_por_perfil
from tests.interface.test_aplicar_a_todos import P1, P2, P3, _perfis_no_formulario, _url

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ESTATICOS = Path(__file__).resolve().parents[2] / "processo_seletivo" / "interface" / "static"
# A vista saiu do `perfis.js` para o script comum quando a Classificação entrou (053, R-001): a
# garantia de que ela não mexe no envio vale para os três, e varrer só o `perfis.js` a teria
# deixado passar em silêncio pelo arquivo onde a montagem agora mora.
SCRIPTS = [
    ESTATICOS / "interface" / nome
    for nome in ("vista-do-conjunto.js", "perfis.js", "classificacao.js")
]


class _Formulario(HTMLParser):
    """Os campos que o navegador enviaria em `#formulario`: nome e valor, como a tela os tem.

    Os do *Duplicar* ficam de fora — moram noutro formulário (`form=`) — e os botões também: o que
    se quer é o envio de um *Preencher pelo percentual*, que acrescenta só o próprio botão.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dentro = False
        self.campos = []
        self._area = None
        self._escolha = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.dentro = a.get("id") == "formulario"
            return
        if not self.dentro or "form" in a:
            return
        if tag == "input" and a.get("name"):
            tipo = a.get("type", "text")
            if tipo in ("submit", "button"):
                return
            if tipo in ("radio", "checkbox") and "checked" not in a:
                return
            self.campos.append((a["name"], a.get("value", "")))
        elif tag == "textarea" and a.get("name"):
            self._area = [a["name"], ""]
        elif tag == "select" and a.get("name"):
            self._escolha = [a["name"], None, None]
        elif tag == "option" and self._escolha is not None:
            valor = a.get("value", "")
            if self._escolha[2] is None:
                self._escolha[2] = valor
            if "selected" in a:
                self._escolha[1] = valor

    def handle_data(self, dados):
        if self._area is not None:
            self._area[1] += dados

    def handle_endtag(self, tag):
        if tag == "form":
            self.dentro = False
        elif tag == "textarea" and self._area is not None:
            self.campos.append(tuple(self._area))
            self._area = None
        elif tag == "select" and self._escolha is not None:
            nome, escolhido, primeiro = self._escolha
            self.campos.append((nome, escolhido if escolhido is not None else primeiro))
            self._escolha = None


def _campos(corpo):
    leitor = _Formulario()
    leitor.feed(corpo)
    return leitor.campos


def _enviar_de_volta(client, edital, corpo, **mudancas):
    """Devolve o formulário que a tela mostrou, trocando só `mudancas`, sem gravar nada."""
    envio = {}
    for nome, valor in _campos(corpo):
        envio.setdefault(nome, []).append(mudancas.pop(nome, valor))
    for nome, valor in mudancas.items():
        envio[nome] = [valor]
    envio["preencher_quadro"] = ["1"]
    return client.post(_url(edital, "perfis"), envio)


def _cartao(corpo, perfil):
    return re.search(rf'<fieldset class="linha perfil" id="cartao-{perfil}"[^>]*>', corpo).group(0)


def _indice_de(corpo, perfil):
    return re.search(rf'name="perfil-(\d+)-id" value="{perfil}"', corpo).group(1)


# --- A legenda (FR-944) -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("perfil", "esperada"),
    [
        ({"code": "P03", "locality": "Vitória", "name": "Professor"}, "Perfil P03 — Vitória"),
        ({"code": "P03", "locality": "", "name": "Professor"}, "Perfil P03 — Professor"),
        ({"code": "P03", "locality": " ", "name": ""}, "Perfil P03"),
        ({"code": "", "locality": "Vitória", "name": "Professor"}, "Perfil novo"),
        ({}, "Perfil novo"),
    ],
)
def test_a_legenda_identifica_o_perfil(perfil, esperada):
    assert legenda_do_perfil(perfil) == esperada


def test_a_etapa_identifica_cada_cartao_pela_legenda(client, tres_perfis):
    corpo = html.unescape(client.get(_url(tres_perfis, "perfis")).content.decode())

    for codigo in ("LP01", "LP02", "LP03"):
        assert f"<legend>Perfil {codigo} — Professor</legend>" in corpo
    assert "<legend>Perfil de Vaga</legend>" not in corpo


def test_o_perfil_acrescentado_nasce_como_perfil_novo(client, tres_perfis):
    resposta = client.get(reverse("interface:fragmento-perfil"), {"edital": tres_perfis.id})

    assert "<legend>Perfil novo</legend>" in html.unescape(resposta.content.decode())


# --- A ordem da etapa e o que o servidor não esconde (UX-120, FR-955) -------------------------


def test_a_etapa_vem_na_ordem_tabela_conjunto_cartoes(client, tres_perfis):
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    posicoes = [
        corpo.index('id="visao-dos-perfis"'),
        corpo.index('hx-target="#perfis"'),
        corpo.index('id="declarado-uma-vez"'),
        corpo.index('name="preencher_quadro"'),
        corpo.index('<div id="perfis">'),
    ]
    assert posicoes == sorted(posicoes)
    assert "interface/perfis.js" in corpo


def test_sem_script_a_etapa_e_a_de_sempre(client, tres_perfis):
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    # O lugar da tabela chega vazio e oculto: sem script, não há tabela.
    assert re.search(r'<div id="visao-dos-perfis" class="visao-dos-perfis" hidden></div>', corpo)
    # E nenhum cartão sai escondido do servidor.
    for perfil in (P1, P2, P3):
        assert " hidden" not in _cartao(corpo, perfil)


def test_as_frases_curtas_da_linha_moram_no_template(client, tres_perfis):
    corpo = html.unescape(client.get(_url(tres_perfis, "perfis")).content.decode())

    for frase in ("não há", "limitado", "ilimitado"):
        assert f'data-resumo="{frase}"' in corpo
    assert 'data-resumo-nenhuma="não declarada"' in corpo
    assert 'data-resumo-publication="por publicação"' in corpo
    assert 'data-resumo-individual_message="por mensagem individual"' in corpo


# --- As pendências de cada Perfil (FR-948, R-003) ---------------------------------------------


def test_so_a_pendencia_que_nomeia_um_perfil_vai_para_a_linha():
    pendencias = [
        {"campo": f"/profiles/id={P1}/vacancyTable"},
        {"campo": f"/profiles/id={P1}/callForm"},
        {"campo": f"/profiles/id={P2}/name"},
        {"campo": "profiles"},
        {"campo": ""},
    ]

    assert _pendencias_por_perfil(pendencias) == {P1: 2, P2: 1}


def test_o_cartao_diz_quantas_pendencias_da_etapa_o_tem_por_objeto(client, tres_perfis):
    modalidade = str(uuid.uuid4())
    # Os três cortam: sem forma de convocação, cada um teria a pendência da `FR-943`. Declarada a
    # forma, só o LP02 fica pendente — ele reparte 2 vagas num quadro que soma 1 + 3.
    resposta = client.post(
        _url(tres_perfis, "perfis"),
        _perfis_no_formulario(
            **{
                **{f"perfil-{i}-callForm": "PUBLICATION" for i in range(3)},
                "modalidade-1-0-id": modalidade,
                "modalidade-1-0-ruleId": str(uuid.uuid4()),
                "modalidade-1-0-code": "PPI",
                "modalidade-1-0-name": "Pessoas pretas, pardas e indígenas",
                "modalidade-1-0-percentage": "25",
                "modalidade-1-0-foundation": "Lei nº 12.711/2012",
                "modalidade-1-0-version": "2012-08-29",
                "linha-1-0-id": str(uuid.uuid4()),
                "linha-1-0-modalityId": "",
                "linha-1-0-immediateVacancies": "1",
                "linha-1-1-id": str(uuid.uuid4()),
                "linha-1-1-modalityId": modalidade,
                "linha-1-1-immediateVacancies": "3",
            }
        ),
    )
    assert resposta.status_code == 302, resposta.content

    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    assert 'data-pendencias="0"' in _cartao(corpo, P1)
    assert re.search(r'data-pendencias="[1-9]\d*"', _cartao(corpo, P2))
    assert 'data-pendencias="0"' in _cartao(corpo, P3)


# --- "Difere do gravado" (FR-949, R-004) ------------------------------------------------------


def test_a_devolucao_sem_mudanca_nao_acusa_perfil_nenhum(client, tres_perfis):
    """O guardião da normalização: se ele reprovar, a linha diria "alterado" em todo Perfil."""
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    resposta = _enviar_de_volta(client, tres_perfis, corpo)

    assert resposta.status_code == 200
    devolvido = resposta.content.decode()
    assert "data-nao-salvo" not in devolvido
    assert "data-devolvido" in devolvido


def test_a_devolucao_acusa_so_o_perfil_mudado(client, tres_perfis):
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    resposta = _enviar_de_volta(
        client,
        tres_perfis,
        corpo,
        **{
            f"perfil-{_indice_de(corpo, P2)}-locality": "Viana",
            f"fato-{_indice_de(corpo, P1)}-0-label": "Anos de experiência",
        },
    )

    devolvido = resposta.content.decode()
    assert "data-nao-salvo" in _cartao(devolvido, P1)
    assert "data-nao-salvo" in _cartao(devolvido, P2)
    assert "data-nao-salvo" not in _cartao(devolvido, P3)


def test_perfil_que_so_existe_na_tela_e_alterado():
    gravado = {"id": P1, "code": "LP01", "reserveType": "NONE", "immediateVacancies": 2}

    assert forms.perfis_alterados(
        [gravado, {"id": P2, "code": "LP02", "reserveType": "NONE"}], [gravado]
    ) == {P2}


def test_a_comparacao_ignora_o_que_o_cartao_nao_mostra():
    """Os marcos e os textos que só o contrato escreve não são da tela, e não acusam alteração."""
    gravado = {
        "id": P1,
        "code": "LP01",
        "reserveType": "NONE",
        "immediateVacancies": 2,
        "classificationMilestones": [{"id": "x"}],
        "classificationInformation": "texto do contrato",
        "competitionModalities": [
            {
                "id": "m",
                "code": "PPI",
                "name": "PPI",
                "description": "descrição que a tela não desenha",
                "normativeRule": {"percentage": "25.0000", "rounding": {}},
            }
        ],
    }
    digitado = {
        "id": P1,
        "code": "LP01",
        "reserveType": "NONE",
        "immediateVacancies": 2,
        "requirements": [],
        "vacancyReversion": None,
        "competitionModalities": [
            {"id": "m", "code": "PPI", "name": "PPI", "normativeRule": {"percentage": "25"}}
        ],
    }

    assert forms.perfis_alterados([digitado], [gravado]) == set()


def test_a_etapa_aberta_do_banco_nao_diz_que_devolveu(client, tres_perfis):
    """Sem envio, o valor inicial de cada campo é o gravado, e a tela compara sozinha."""
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    assert "data-devolvido" not in corpo
    assert "data-nao-salvo" not in corpo


# --- O formulário é o mesmo (FR-950, SC-350) --------------------------------------------------


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda caminho: caminho.name)
def test_o_script_nao_cria_remove_nem_renomeia_campo(script):
    """A vista esconde; ela nunca mexe no que o formulário envia.

    Varredura do fonte, e não execução: o que se prende é a ausência de toda operação que mudaria
    o envio — criar controle, dar nome, clonar, remover ou mover cartão.
    """
    fonte = script.read_text()
    codigo = re.sub(r"/\*.*?\*/|//[^\n]*", "", fonte, flags=re.S)

    assert not re.search(r'createElement\(\s*"(input|select|textarea|form|option)"', codigo)
    assert not re.search(r"\.name\s*=", codigo)
    assert 'setAttribute("name"' not in codigo
    assert "cloneNode" not in codigo
    assert not re.search(r"\.remove\(\)", codigo)
    assert "removeChild" not in codigo
    # Os botões da vista são `type=button`: nenhum deles envia. Só o script comum cria botão.
    if re.search(r'(createElement|elemento)\(\s*"button"', codigo):
        assert codigo.count('.type = "button"') >= 2


def test_a_tabela_rola_dentro_do_proprio_conteiner(client, tres_perfis):
    """UX-121. O texto oculto das células é `position:absolute`, e sem um contêiner posicionado ele
    tem a página por referência: medido a 375 px, a página inteira alargava para 817."""
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()

    assert ".visao-dos-perfis .tabela-rolavel{position:relative}" in corpo
