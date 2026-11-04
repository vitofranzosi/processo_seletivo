"""A jornada consolidada do convocado num navegador de verdade (118, SC-1119, SC-1121, SC-1122).

Os cenários são os da revisão de UX de 04/11/2026 e os de controle do plano, montados pelas
*fixtures* (`tests/fixtures/jornada_do_convocado.py`). Cada um se lê como a pessoa o lê: o
acompanhamento, a convocação e, quando há, o Requerimento, a 375 × 812 e a 1280 × 900.

Em toda página: nenhuma rolagem horizontal e nenhuma violação da política de conteúdo no console
(a `Tela` da `115` vigia o console). Na convocação: nenhum nome acessível de botão de envio ou de
escolha de arquivo se repete. Nos cenários em que há o que fazer, o bloco *O que fazer agora*
termina dentro da primeira tela a 375 px, com a contagem e o primeiro link de tarefa.

`NAVEGADOR_CAPTURAS=<pasta>` grava, por cenário, as telas inteiras e o texto visível de cada uma —
é de onde saem as capturas e as citações literais da `verificacao.md`.
"""

import json
import os
import re
from pathlib import Path

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from django.urls import reverse  # noqa: E402

from tests.fixtures import jornada_do_convocado as jornada  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import (  # noqa: E402
    CELULAR,
    DESKTOP,
    Tela,
    sem_rolagem_horizontal,
)

pytestmark = pytest.mark.django_db(transaction=True)

COM_REQUERIMENTO = {"B", "B2", "C1", "C2", "F", "G", "H", "I1", "K", "M", "M0", "N", "N0", "G0"}
PRIMEIRA_TELA = {"A", "C1", "C2", "F", "J"}
CENARIOS = list(jornada.CENARIOS)


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def fx(gestor, api_client, manager_headers, process_payload):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def _saida(letra):
    pasta = os.getenv("NAVEGADOR_CAPTURAS")
    if not pasta:
        return None
    destino = Path(pasta) / letra
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def _nomes_repetidos(pagina):
    """Os nomes acessíveis dos botões de envio e dos rótulos de escolher arquivo que se repetem."""
    nomes = pagina.evaluate(
        """() => [...document.querySelectorAll(
                'main button[type=submit], main label.botao-arquivo')]
              .map(e => e.textContent.replace(/\\s+/g, ' ').trim())"""
    )
    return sorted({n for n in nomes if nomes.count(n) > 1})


@pytest.mark.parametrize("letra", CENARIOS)
def test_cada_cenario_nas_duas_larguras(tela, fx, letra):
    cenario = jornada.montar(letra, fx)
    telas = ["acompanhamento", "convocacao"]
    if letra in COM_REQUERIMENTO:
        telas.append("requerimento")
    destino = _saida(letra)
    textos = {}

    with cenario.relogio():
        for nome_da_largura, largura in (("375", CELULAR), ("desktop", DESKTOP)):
            pagina = tela.candidato(cenario.pessoa, viewport=largura)
            for nome in telas:
                pagina.goto(tela.servidor.url + reverse(f"portal:{nome}", args=[cenario.pessoa.id]))
                pagina.wait_for_load_state()
                expect(pagina.locator("main h1")).to_be_visible()
                sem_rolagem_horizontal(pagina)
                if nome == "convocacao":
                    assert _nomes_repetidos(pagina) == [], "nome acessível repetido (SC-1122)"
                if destino is not None:
                    pagina.screenshot(
                        path=str(destino / f"{nome}-{nome_da_largura}.png"), full_page=True
                    )
                    textos[f"{nome}-{nome_da_largura}"] = pagina.locator("main").inner_text()
            if letra in PRIMEIRA_TELA and largura is CELULAR:
                _o_que_fazer_na_primeira_tela(tela, pagina, cenario)

    if destino is not None:
        (destino / "textos.json").write_text(json.dumps(textos, ensure_ascii=False, indent=2))


def _o_que_fazer_na_primeira_tela(tela, pagina, cenario):
    """SC-1119: a contagem e o primeiro link de tarefa terminam dentro de 812 px."""
    pagina.goto(tela.servidor.url + reverse("portal:convocacao", args=[cenario.pessoa.id]))
    bloco = pagina.locator("#o-que-fazer-agora")
    expect(bloco).to_be_visible()
    frase = bloco.locator(".acao-principal").bounding_box()
    primeira = bloco.locator(".tarefas a").first.bounding_box()
    assert frase["y"] + frase["height"] <= CELULAR["height"], frase
    assert primeira["y"] + primeira["height"] <= CELULAR["height"], primeira


def test_f_pelo_teclado_a_ordem_e_a_visual_e_o_foco_se_ve(tela, fx):
    """SC-1122 e o roteiro de teclado do quickstart, a 375 px, no cenário F."""
    cenario = jornada.montar("F", fx)
    pagina = tela.candidato(cenario.pessoa, viewport=CELULAR)
    pagina.goto(tela.servidor.url + reverse("portal:convocacao", args=[cenario.pessoa.id]))

    passos = []
    for _ in range(40):
        pagina.keyboard.press("Tab")
        passos.append(
            pagina.evaluate(
                """() => { const e = document.activeElement; const s = getComputedStyle(e);
                  const alvo = e.matches('input[type=file]') ? e.nextElementSibling : e;
                  const r = alvo.getBoundingClientRect(); const a = getComputedStyle(alvo);
                  return {tag: e.tagName, texto: (e.textContent || e.getAttribute('aria-label')
                            || e.id || '').replace(/\\s+/g, ' ').trim().slice(0, 60),
                          y: r.top + window.scrollY, x: r.left,
                          contorno: s.outlineStyle !== 'none' || a.outlineStyle !== 'none'}; }"""
            )
        )
    no_main = [p for p in passos if p["tag"] != "BODY"]
    assert all(p["contorno"] for p in no_main), [p for p in no_main if not p["contorno"]]
    # A ordem do Tab segue a de leitura: no conteúdo, cada foco está abaixo do anterior, até o fim
    # da página voltar ao cabeçalho, que tem dois controles na mesma linha e fica de fora.
    conteudo = []
    for passo in no_main:
        if passo["y"] < 200:
            if conteudo:
                break
            continue
        conteudo.append(passo)
    assert len(conteudo) >= 10, conteudo
    alturas = [p["y"] for p in conteudo]
    assert alturas == sorted(alturas), conteudo
    rotulos = [p["texto"] for p in no_main]
    assert "Histórico escolar do ensino médio" in rotulos
    assert "Ver e corrigir os documentos pendentes" in rotulos
    assert any(r.startswith("Enviar: ") for r in rotulos), rotulos

    # Ativar a âncora do pendente leva o foco ao cartão dele (quickstart).
    pagina.goto(tela.servidor.url + reverse("portal:convocacao", args=[cenario.pessoa.id]))
    pagina.locator("#o-que-fazer-agora .tarefas a").first.click()
    alvo = pagina.evaluate("() => document.activeElement.id")
    assert re.match(r"item-[0-9a-f-]{36}$", alvo), alvo
    assert pagina.locator(f"#{alvo} .selo", has_text="Precisa de correção").count() == 1
