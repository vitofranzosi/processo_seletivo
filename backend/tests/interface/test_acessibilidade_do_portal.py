"""A rubrica de acessibilidade, estendida ao canal do candidato (T111, FR-079, FR-080).

O que se prende aqui é o que dá para prender: marcação nativa, rótulo ligado ao campo, link de
salto com alvo focável, nenhuma reordenação de tabulação, e ausência de largura fixa — que é o que
sustenta 375 px sem rolagem horizontal.

O que continua fora, e está no quickstart como verificação manual: o anúncio pelo leitor de tela,
o movimento real do foco e o comportamento do seletor de arquivo no celular. Um teste de fonte é
uma aproximação; tratá-lo como o navegador seria a mesma confusão que o shim de DOM evita.
"""

import re
from pathlib import Path

import pytest

PORTAL = (
    Path(__file__).resolve().parents[2] / "processo_seletivo" / "portal" / "templates" / "portal"
)
TEMPLATES = sorted(PORTAL.glob("*.html"))
# `form` entra na lista de elementos admitidos, e a rubrica administrativa não o admite porque lá
# ninguém o usa assim. Um `<form hx-post>` com `method`, `action` e um `<button type=submit>` é
# acessível por construção — e é o que faz o envio de documento funcionar **sem** JavaScript, com o
# htmx apenas melhorando a experiência. O que a regra proíbe continua proibido: `hx-*` pendurado em
# `div` ou `span`, que nenhum teclado alcança.
NAO_NATIVOS = re.compile(
    r"<(?!a\b|button\b|input\b|select\b|textarea\b|main\b|form\b)"
    r"[a-z]+[^>]*\s(?:onclick|hx-get|hx-post)=",
    re.IGNORECASE,
)


def test_a_rubrica_cobre_o_portal_inteiro():
    """Sem isto, renomear a pasta transformaria a garantia em silêncio aprovado."""
    assert len(TEMPLATES) >= 7


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_controles_sao_nativos(template):
    corpo = template.read_text()

    assert not NAO_NATIVOS.search(corpo), "controle interativo fora de elemento nativo"
    for formulario in re.findall(r"<form[^>]*hx-post[^>]*>", corpo):
        assert "method=" in formulario and "action=" in formulario, (
            "formulário com htmx precisa funcionar sem JavaScript: sem `method` e `action`, "
            "quem tiver o script bloqueado fica sem envio nenhum"
        )
    assert not re.search(r"<a(?=[\s>])(?![^>]*\bhref=)[^>]*>", corpo), (
        "âncora sem href não recebe foco"
    )
    assert not re.search(r'tabindex="[1-9]', corpo), (
        "tabindex positivo reordena a navegação e quebra a ordem visual"
    )


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_todo_campo_tem_rotulo_ligado_por_id(template):
    corpo = template.read_text()
    identificadores = set(re.findall(r'<(?:input|select|textarea)[^>]*\sid="([^"]+)"', corpo))
    rotulados = set(re.findall(r'<label[^>]*\sfor="([^"]+)"', corpo))
    # `csrfmiddlewaretoken` e os campos ocultos não são controles que alguém preenche.
    ocultos = set(re.findall(r'<input[^>]*type="hidden"[^>]*\sid="([^"]+)"', corpo))

    assert (identificadores - ocultos) <= rotulados, (
        f"campo sem rótulo associado em {template.name}: "
        f"{sorted(identificadores - ocultos - rotulados)}"
    )


def test_a_base_do_portal_leva_o_foco_ao_conteudo():
    corpo = (PORTAL / "base.html").read_text()

    destino = re.search(r'<a class="pular" href="#([\w-]+)"', corpo)
    assert destino, "o primeiro foco da página precisa ser o link de salto"
    assert re.search(rf'<main id="{destino.group(1)}" tabindex="-1">', corpo), (
        "o alvo do link de salto precisa poder receber foco"
    )


def test_nada_no_portal_fixa_largura_em_pixel():
    """Largura fixa é o que produz rolagem horizontal em 375 px (FR-079)."""
    corpo = (PORTAL / "base.html").read_text()
    regras = re.findall(r"(?<!max-)(?<!min-)width:\s*(\d+)px", corpo)

    assert regras == [], f"largura fixa em pixel: {regras}"


def test_o_estado_nao_depende_so_de_cor():
    """WCAG 1.4.1: quem não distingue as cores lê o mesmo estado no símbolo e no texto."""
    documentos = (PORTAL / "_documentos.html").read_text()

    assert "✓" in documentos and "○" in documentos
    assert "de {{ documentos.total }}" in documentos, "a contagem diz em texto o que a cor mostra"
