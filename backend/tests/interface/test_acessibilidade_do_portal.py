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


# ---------------------------------------------------------------------------
# As telas que a 010 acrescentou (T096). A varredura por `TEMPLATES` acima já as alcança; o que
# vem abaixo prende o que é específico delas.
# ---------------------------------------------------------------------------

TELAS_DA_010 = (
    "acesso_email.html",
    "acesso_codigo.html",
    "acesso_reconciliar.html",
    "meus_dados.html",
    "inscricoes.html",
    "inscricao_enviada.html",
    "acompanhamento.html",
    "conta.html",
)


@pytest.mark.parametrize("nome", TELAS_DA_010)
def test_as_telas_da_010_existem_e_estendem_a_base(nome):
    corpo = (PORTAL / nome).read_text()
    assert '{% extends "portal/base.html" %}' in corpo, nome


@pytest.mark.parametrize("nome", TELAS_DA_010)
def test_todo_campo_da_010_tem_rotulo_ligado(nome):
    """Rótulo solto é rótulo que o leitor de tela não associa a campo nenhum."""
    corpo = (PORTAL / nome).read_text()

    for identificador in re.findall(r'<input[^>]*\sid="([\w-]+)"', corpo):
        assert f'<label for="{identificador}"' in corpo, f"{nome}: {identificador}"


def test_o_campo_do_codigo_e_um_so_e_aceita_colagem():
    """Seis campos independentes obrigariam a navegar entre eles.

    E quebrariam a colagem, que é o que a `UX-005` pede.
    """
    corpo = (PORTAL / "acesso_codigo.html").read_text()

    assert len(re.findall(r'<input[^>]*name="codigo"', corpo)) == 1
    assert 'inputmode="numeric"' in corpo
    assert 'autocomplete="one-time-code"' in corpo


def test_a_situacao_da_inscricao_nao_depende_so_de_cor():
    corpo = (PORTAL / "inscricoes.html").read_text()

    assert "✓ Inscrição enviada" in corpo
    assert "Inscrição não enviada" in corpo, "o texto diz o que a cor mostra"


def test_o_acompanhamento_distingue_os_blocos_por_texto():
    """A distinção entre o que é seu e o que é do processo precisa sobreviver ao preto e branco."""
    corpo = (PORTAL / "acompanhamento.html").read_text()

    assert "Sua participação" in corpo and "Cronograma do processo" in corpo
    assert "✓" in corpo


def test_a_integridade_fica_recolhida_em_elemento_nativo():
    """`<details>` abre por teclado sem uma linha de script (FR-073, UX-010)."""
    corpo = (PORTAL / "inscricao_enviada.html").read_text()

    assert "<details" in corpo and "<summary>" in corpo
    assert "onclick" not in corpo


def test_nenhuma_acao_da_010_depende_de_script():
    """Toda ação é `form` com `method` e `button` — teclado alcança tudo, sem JavaScript."""
    for nome in TELAS_DA_010:
        corpo = (PORTAL / nome).read_text()
        assert "onclick" not in corpo, nome
        for acao in re.findall(r"<form([^>]*)>", corpo):
            if "method" in acao:
                assert 'method="post"' in acao, f"{nome}: {acao}"
