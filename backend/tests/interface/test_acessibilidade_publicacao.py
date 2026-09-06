"""As três telas da 017 pelo teclado, e sem depender de cor (FR-052, FR-053, FR-054).

O que dá para prender sem navegador é a **marcação**: controle nativo, rótulo ligado ao campo,
nenhuma reordenação de tabulação, e nenhuma informação que exista só como cor. O anúncio pelo leitor
de tela e o movimento real do foco continuam no quickstart, como verificação manual — um teste de
fonte é uma aproximação, e tratá-lo como o navegador seria a confusão que a rubrica do portal já
evita.
"""

import re

import pytest
from django.test import Client
from django.urls import reverse

from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

NAO_NATIVOS = re.compile(
    r"<(?!a\b|button\b|input\b|select\b|textarea\b|main\b|form\b)"
    r"[a-z]+[^>]*\s(?:onclick|hx-get|hx-post)=",
    re.IGNORECASE,
)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=83,
        codigo="0783",
        pontuacoes=("90.0000", "80.0000", "80.0000"),
        primeiro=1801,
    )


@pytest.fixture
def telas(client, seletor_ligado, cenario):
    """As três: a prévia, o histórico e a página pública — cada uma pelo canal do seu ator."""
    identificar(client, "paula.publicadora", ["publicador"])
    previa = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
        )
    ).content.decode()
    publicacao = publicar_o_ato(cenario, chave="publicar-0783")
    historico = client.get(
        reverse("interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]])
    ).content.decode()
    publica = Client().get(reverse("portal:resultado", args=[publicacao.id])).content.decode()
    return {"prévia": previa, "histórico": historico, "página pública": publica}


def test_os_controles_sao_nativos_e_alcancaveis_pelo_teclado(telas):
    """Um `div` com `onclick` é invisível para quem navega por tabulação."""
    for nome, corpo in telas.items():
        assert not NAO_NATIVOS.search(corpo), f"controle fora de elemento nativo em {nome}"
        assert not re.search(r"<a(?=[\s>])(?![^>]*\bhref=)[^>]*>", corpo), (
            f"âncora sem href não recebe foco, em {nome}"
        )
        assert not re.search(r'tabindex="[1-9]', corpo), (
            f"tabindex positivo reordena a navegação e quebra a ordem visual, em {nome}"
        )


def test_a_confirmacao_e_um_formulario_que_funciona_sem_javascript(telas):
    """O ato mais consequente da feature não pode depender de script para acontecer."""
    previa = telas["prévia"]

    formulario = re.search(r"<form[^>]*>", previa).group(0)
    assert 'method="post"' in formulario and "action=" in formulario
    assert '<button type="submit"' in previa
    assert "csrfmiddlewaretoken" in previa


def test_cada_campo_da_previa_tem_rotulo_ligado_por_id(telas):
    """Natureza e autoridade são escolhas do operador, e escolha sem rótulo não se lê."""
    previa = telas["prévia"]
    identificadores = set(re.findall(r'<(?:input|select|textarea)[^>]*\sid="([^"]+)"', previa))
    ocultos = set(re.findall(r'<input[^>]*type="hidden"[^>]*\sname="([^"]+)"', previa))
    rotulados = set(re.findall(r'<label[^>]*\sfor="([^"]+)"', previa))

    assert {"natureza", "autoridade"} <= identificadores
    assert (identificadores - ocultos) <= rotulados


def test_a_situacao_vigente_ou_sucedida_nao_depende_de_cor(telas):
    """FR-052 nos dois canais: a palavra está escrita, e não apenas pintada."""
    sem_marcacao = re.sub(r"<[^>]+>", " ", telas["histórico"])
    assert "Vigente" in sem_marcacao

    publica = re.sub(r"<[^>]+>", " ", telas["página pública"])
    assert "Resultado preliminar" in publica


def test_o_empate_e_dito_em_texto_nas_duas_telas(telas):
    """Uma linha destacada só por cor não informa quem não distingue a cor (FR-014, FR-052)."""
    for nome in ("prévia", "página pública"):
        assert "posição compartilhada" in telas[nome], f"o empate precisa estar escrito em {nome}"


def test_as_tabelas_tem_cabecalho_de_coluna_associado(telas):
    """FR-054: sem `scope`, quem ouve a tabela recebe valores sem saber de que coluna são."""
    for nome, corpo in telas.items():
        if "<table" not in corpo:
            continue
        # `\b` depois de `th`: sem ele, `<thead>` casa como um cabeçalho sem `scope`.
        cabecalhos = re.findall(r"<th\b([^>]*)>", corpo)
        assert cabecalhos, f"tabela sem cabeçalho em {nome}"
        assert all('scope="col"' in atributos for atributos in cabecalhos), (
            f"cabeçalho de coluna sem scope em {nome}"
        )


def test_a_previa_anuncia_a_recusa_como_alerta(client, seletor_ligado, cenario, gestor):
    """Uma recusa que não é anunciada some para quem não está olhando o alto da tela."""
    from tests.fixtures.divulgacao import emitir

    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0783-b", motivo="Resultado tardio.")
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], antigo.id],
        )
    ).content.decode()

    assert 'role="alert"' in corpo
