"""O que o servidor entrega à vista do conjunto da etapa Classificação (053).

A tabela e o Perfil à vista são montados pelo `classificacao.js`, sobre o `vista-do-
conjunto.js`, e o que eles fazem no navegador — foco, `hidden`, `details`, a validação nativa —
se verifica no preview (quickstart.md) e, nas regras puras, em
`tests/javascript/classificacao.test.js`. Aqui fica o que o script não tem como saber sozinho, e
a promessa que torna a vista inofensiva: **o formulário é o mesmo**.

- o cartão do Perfil se identifica, também sem script (FR-960);
- a etapa vem na ordem pendências → tabela → método comum → cartões (UX-127, FR-966, FR-974);
- as frases da linha moram no template, sem ajuda visível nova no cartão (R-003, UX-129);
- a origem do marco é a da Revisão (FR-964);
- as pendências da etapa vão à linha do Perfil que elas nomeiam (FR-965);
- a devolução sem mudança não acusa Perfil nenhum, e a com mudança acusa só o mudado (FR-967);
- a recusa do servidor aponta um elemento que existe na tela devolvida (FR-973, SC-357);
- a etapa declara o rascunho local das demais (FR-979).
"""

import html
import re
import uuid
from html.parser import HTMLParser

import pytest

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from tests.interface.conftest import ETAPA_CLASSIFICATORIA
from tests.interface.test_aplicar_a_todos import (
    MARCO,
    P1,
    P2,
    P3,
    _classificacao,
    _impressao,
    _url,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class _Formulario(HTMLParser):
    """Os campos que o navegador enviaria em `#formulario`, com o `select` múltiplo das Etapas."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dentro = False
        self.campos = []
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
        elif tag == "select" and a.get("name"):
            self._escolha = [a["name"], [], None, "multiple" in a]
        elif tag == "option" and self._escolha is not None:
            valor = a.get("value", "")
            if self._escolha[2] is None:
                self._escolha[2] = valor
            if "selected" in a:
                self._escolha[1].append(valor)

    def handle_endtag(self, tag):
        if tag == "form":
            self.dentro = False
        elif tag == "select" and self._escolha is not None:
            nome, escolhidos, primeiro, multiplo = self._escolha
            if multiplo:
                self.campos.extend((nome, valor) for valor in escolhidos)
            else:
                self.campos.append((nome, escolhidos[-1] if escolhidos else primeiro))
            self._escolha = None


def _devolver(client, edital, corpo, *, fora=(), **mudancas):
    """Devolve o formulário que a tela mostrou pedindo a prévia do gesto — um envio que não grava.

    `fora` tira do envio os campos com esses prefixos; `mudancas` troca ou acrescenta valores.
    """
    leitor = _Formulario()
    leitor.feed(corpo)
    envio = {}
    for nome, valor in leitor.campos:
        if any(nome.startswith(prefixo) for prefixo in fora):
            continue
        envio.setdefault(nome, []).append(mudancas.pop(nome, valor))
    for nome, valor in mudancas.items():
        envio[nome] = [valor]
    envio["aplicar"] = [f"marco:{P1}:0"]
    return client.post(_url(edital), envio)


def _cartao(corpo, perfil):
    return re.search(rf'<fieldset class="linha perfil" id="cartao-{perfil}"[^>]*>', corpo).group(0)


def _gravar_o_marco_do_lp01(client, edital, **extra):
    resposta = client.post(_url(edital), _classificacao(**extra))
    assert resposta.status_code == 302, resposta.content
    return client.get(_url(edital)).content.decode()


# --- O cartão e a etapa ----------------------------------------------------------------------


def test_o_cartao_do_perfil_se_identifica_e_carrega_o_que_a_linha_le(client, tres_perfis):
    corpo = client.get(_url(tres_perfis)).content.decode()

    assert "<legend>Perfil LP01 — Professor</legend>" in corpo
    cartao = _cartao(corpo, P1)
    assert 'data-codigo="LP01"' in cartao
    assert 'data-denominacao="Professor"' in cartao
    # O Perfil sem marco não classifica ninguém, e a publicação o diz: é a pendência dele.
    assert 'data-pendencias="1"' in cartao
    # Sem envio que não gravou, nada é "alterado", e nada é devolvido.
    assert "data-nao-salvo" not in corpo
    assert "data-devolvido" not in corpo


def test_a_etapa_vem_na_ordem_pendencias_tabela_metodo_cartoes(client, tres_perfis):
    corpo = client.get(_url(tres_perfis)).content.decode()

    posicoes = [
        corpo.index('id="titulo-classificacao"'),
        corpo.index('id="visao-da-classificacao"'),
        corpo.index("Método do sorteio comum a este Edital"),
        corpo.index('id="classificacao-perfis"'),
    ]
    assert posicoes == sorted(posicoes)
    assert corpo.index("interface/vista-do-conjunto.js") < corpo.index("interface/classificacao.js")


def test_sem_script_a_etapa_e_a_de_sempre(client, tres_perfis):
    """FR-974: o servidor não esconde nada; a vista só existe onde o script existe."""
    corpo = client.get(_url(tres_perfis)).content.decode()

    assert re.search(
        r'<div id="visao-da-classificacao" class="visao-dos-perfis" hidden></div>', corpo
    )
    for perfil in (P1, P2, P3):
        assert " hidden" not in _cartao(corpo, perfil)
    assert ".visao-dos-perfis .tabela-rolavel{position:relative}" in corpo


def test_as_frases_curtas_da_linha_moram_no_template(client, tres_perfis):
    corpo = html.unescape(_gravar_o_marco_do_lp01(client, tres_perfis))

    for atributo in (
        'data-resumo-por_pontuacao="pela pontuação"',
        'data-resumo-por_sorteio="por sorteio"',
        'data-resumo-fixed="quantidade fixa"',
        'data-resumo-from_vacancy_table="o que o quadro de vagas publicar"',
        'data-resumo-nenhuma="este marco não corta"',
        'data-resumo="admite"',
        'data-resumo="não admite por esta via"',
        'data-resumo="nada declarado"',
        'data-resumo-maior_pontuacao_na_etapa="maior nota em"',
    ):
        assert atributo in corpo, atributo


def test_o_bloco_do_metodo_do_marco_de_sorteio_diz_as_tres_frases(client, tres_perfis):
    corpo = html.unescape(
        _gravar_o_marco_do_lp01(
            client, tres_perfis, **{f"marco-{P1}-0-orderProduction": "POR_SORTEIO"}
        )
    )

    assert re.search(r"<fieldset class=\"campos\" data-metodo-do-marco", corpo)
    assert 'data-resumo-proprio="método próprio"' in corpo
    assert 'data-resumo-comum="método comum"' in corpo


# --- A origem (FR-964) -----------------------------------------------------------------------


def _aplicar_o_lp01(client, edital):
    previa = client.post(_url(edital), _classificacao(aplicar=f"marco:{P1}:0"))
    resposta = client.post(
        _url(edital),
        _classificacao(
            confirmar_aplicacao=f"marco:{P1}:0",
            aplicar_destino=[P2],
            aplicar_impressao=_impressao(previa.content.decode()),
        ),
    )
    assert resposta.status_code == 302, resposta.content
    return html.unescape(client.get(resposta["Location"]).content.decode())


def test_o_marco_aplicado_diz_de_onde_veio_com_a_frase_da_revisao(client, tres_perfis):
    corpo = _aplicar_o_lp01(client, tres_perfis)

    assert re.search(
        r'data-origem="aplicado a partir do Perfil LP01, por ana\.elaboradora, em [\d/]+ [\d:]+"',
        _cartao(corpo, P2),
    )
    # A origem gravou, e não recebeu; o que ficou fora do alcance não foi tocado.
    assert "data-origem" not in _cartao(corpo, P1)
    assert "data-origem" not in _cartao(corpo, P3)


def test_editado_e_gravado_depois_o_marco_deixa_de_ser_do_gesto(client, tres_perfis):
    """FR-935 da 051, lida pela linha: a origem vale enquanto o gravado for o que o gesto gravou."""
    corpo = _aplicar_o_lp01(client, tres_perfis)
    leitor = _Formulario()
    leitor.feed(corpo)
    envio = {}
    for nome, valor in leitor.campos:
        envio.setdefault(nome, []).append(valor)
    sub = re.search(rf'name="marco-{P2}-(\d+)-scale"', corpo).group(1)
    envio[f"marco-{P2}-{sub}-scale"] = ["3"]

    resposta = client.post(_url(tres_perfis), envio)
    assert resposta.status_code == 302, resposta.content

    corpo = client.get(_url(tres_perfis)).content.decode()
    assert "data-origem" not in _cartao(corpo, P2)


# --- As pendências (FR-965, FR-966) ----------------------------------------------------------


def test_a_pendencia_do_marco_vai_ao_bloco_da_etapa_e_a_linha_do_perfil(client, tres_perfis):
    """O corte sem o desfecho do empate não publica — é pendência do marco, e o marco é do LP01.

    O caminho do achado é `/profiles/id=LP01/classificationMilestones/id=…/cutRule/tieOutcome`: ele
    nomeia o Perfil antes do marco, e é ao Perfil que a pendência vai (D-003 da spec).
    """
    completo = _gravar_o_marco_do_lp01(client, tres_perfis)
    assert 'data-pendencias="0"' in _cartao(completo, P1)

    corpo = _gravar_o_marco_do_lp01(client, tres_perfis, **{f"marco-{P1}-0-cutTieOutcome": ""})

    assert 'class="pendencias"' in corpo
    assert "não declara o que acontece com o empate" in html.unescape(corpo)
    assert 'data-pendencias="1"' in _cartao(corpo, P1)
    # A do LP02 é outra: ele não tem marco.
    assert 'data-pendencias="1"' in _cartao(corpo, P2)


# --- "Difere do gravado" (FR-967) ------------------------------------------------------------


def test_a_devolucao_sem_mudanca_nao_acusa_perfil_nenhum(client, tres_perfis):
    """O guardião da normalização: a tela devolvida como veio não difere do gravado."""
    corpo = _gravar_o_marco_do_lp01(client, tres_perfis)

    resposta = _devolver(client, tres_perfis, corpo)

    assert resposta.status_code == 200
    devolvido = resposta.content.decode()
    assert "data-devolvido" in devolvido
    assert "data-nao-salvo" not in devolvido


def test_a_devolucao_acusa_so_o_perfil_mudado(client, tres_perfis):
    corpo = _gravar_o_marco_do_lp01(client, tres_perfis)

    devolvido = _devolver(
        client, tres_perfis, corpo, **{f"marco-{P1}-0-name": "Classificação final revista"}
    ).content.decode()

    assert "data-nao-salvo" in _cartao(devolvido, P1)
    assert "data-nao-salvo" not in _cartao(devolvido, P2)


def test_criterio_mudado_e_marco_novo_acusam_o_perfil_deles(client, tres_perfis):
    corpo = _gravar_o_marco_do_lp01(client, tres_perfis)
    novo = f"marco-{P2}-0"

    devolvido = _devolver(
        client,
        tres_perfis,
        corpo,
        **{
            f"criterio-{P1}-0-0-whenMissing": "CRITERIO_NAO_SE_APLICA",
            f"{novo}-id": str(uuid.uuid4()),
            f"{novo}-code": "LP02",
            f"{novo}-name": "Classificação final — Professor",
            f"{novo}-orderProduction": "POR_SORTEIO",
            f"{novo}-scale": "2",
            f"{novo}-mode": "MEIO_PARA_CIMA",
        },
    ).content.decode()

    assert "data-nao-salvo" in _cartao(devolvido, P1)
    assert "data-nao-salvo" in _cartao(devolvido, P2)
    assert "data-nao-salvo" not in _cartao(devolvido, P3)


def test_marco_removido_na_tela_acusa_o_perfil(client, tres_perfis):
    """A restauração devolve sem gravar; o marco que o guardado não tem saiu na tela."""
    _gravar_o_marco_do_lp01(client, tres_perfis)

    resposta = client.post(_url(tres_perfis), {"perfil_id": [P1, P2, P3], "restaurar": "1"})
    devolvido = resposta.content.decode()

    assert "data-nao-salvo" in _cartao(devolvido, P1)
    assert "data-nao-salvo" not in _cartao(devolvido, P2)
    assert MarcoClassificatorio.objects.filter(pk=MARCO).exists()


# --- A recusa aponta o que existe (FR-973, SC-357) ------------------------------------------


def _ancoras(corpo):
    resumo = corpo.split('class="erro"', 1)[1].split("</div>", 1)[0]
    return re.findall(r'<a href="#([^"]+)">', resumo)


@pytest.mark.parametrize(
    ("mudancas", "esperada"),
    [
        ({f"criterio-{P1}-0-0-target": ""}, f"criterio-{P1}-0-0-target"),
        ({f"criterio-{P1}-0-0-whenMissing": ""}, f"criterio-{P1}-0-0-whenMissing"),
        # A forma exige Etapa, e o seletor de Etapas é campo que a tela pode não desenhar: a
        # recusa recua para o cartão do marco, que sempre está.
        ({f"marco-{P1}-0-stages": []}, f"marco-{P1}-0"),
    ],
    ids=["critério sem alvo", "critério sem ausência", "marco sem Etapa"],
)
def test_a_recusa_do_marco_aponta_um_elemento_da_tela_devolvida(
    client, tres_perfis, mudancas, esperada
):
    resposta = client.post(_url(tres_perfis), _classificacao(**mudancas))

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert _ancoras(corpo) == [esperada]
    assert f'id="{esperada}"' in corpo
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()


def test_a_ordem_repetida_aponta_o_segundo_criterio(client, tres_perfis):
    segundo = f"criterio-{P1}-0-1"
    resposta = client.post(
        _url(tres_perfis),
        _classificacao(
            **{
                f"{segundo}-id": str(uuid.uuid4()),
                f"{segundo}-order": "1",
                f"{segundo}-type": "MAIOR_PONTUACAO_NA_ETAPA",
                f"{segundo}-target": ETAPA_CLASSIFICATORIA,
                f"{segundo}-whenMissing": "ULTIMO_NO_CRITERIO",
            }
        ),
    )

    corpo = resposta.content.decode()
    assert _ancoras(corpo) == [f"{segundo}-order"]
    assert f'id="{segundo}-order"' in corpo


# --- O rascunho local (FR-979) ---------------------------------------------------------------


def test_a_restauracao_devolve_os_marcos_e_diz_que_nao_foram_salvos(client, tres_perfis):
    """A metade do servidor já existia: restaurar é devolver o digitado sem gravar."""
    resposta = client.post(_url(tres_perfis), {**_classificacao(), "restaurar": "1"})

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "data-rascunho-restaurado" in corpo
    assert f'name="marco-{P1}-0-id" value="{MARCO}"' in corpo
    assert "data-nao-salvo" in _cartao(corpo, P1)
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()
