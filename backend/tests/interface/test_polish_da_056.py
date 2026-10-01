"""056 — o polish do assistente de composição.

As medidas de tela — 80 px de stepper, o h2 de Perfis em y ≤ 440, a página do Conteúdo — estão em
`specs/056-polish-assistente-de-composicao/verificacao.md`, tiradas na página renderizada. O que
fica aqui é o que as produz: a regra na folha e a marcação no template. Nada disso muda
comportamento, e por isso nenhum outro teste perceberia se voltasse ao que era.
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.interface.test_acessibilidade import FONTE, sem_prosa
from tests.interface.test_conteudo_da_054 import composto  # noqa: F401

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
GESTAO = RAIZ / "interface/templates/interface"
FOLHA = sem_prosa(FONTE)


def regra(seletor, folha=FOLHA):
    """O corpo da regra cujo seletor é exatamente `seletor`, sem espaços, ou `None`."""
    achado = re.search(rf"(?:^|[}}\n])[ \t]*{re.escape(seletor)}\{{([^}}]*)\}}", folha)
    return achado.group(1).replace("\n", "").replace(" ", "") if achado else None


# --- F1 — o stepper numa linha (FR-1020 a FR-1022) ---------------------------------------------


def test_o_stepper_e_grade_de_colunas_iguais():
    """`flex:1 1 160px` com quebra fazia 7 + 2, com as duas últimas esticadas a 613 px.

    A grade quebra em colunas do mesmo tamanho em todas as linhas (FR-1021), e a 1280 px cabe as
    nove numa só (FR-1020): 7,5 rem por coluna, contra 131 px disponíveis.
    """
    corpo = regra(".assistente")
    assert corpo and "display:grid" in corpo
    assert "repeat(auto-fit,minmax(7.5rem,1fr))" in corpo
    assert "flex-wrap" not in corpo
    assert "flex:" not in (regra(".assistente li") or ""), "a base de 160 px volta a quebrar 7 + 2"


def test_a_situacao_da_etapa_continua_em_texto():
    """FR-1022: a situação é escrita, e não só cor. Sai a caixa-alta, e não a palavra."""
    compor = (GESTAO / "compor_base.html").read_text()
    assert '<span class="estado">etapa atual</span>' in compor
    assert '<span class="estado">{{ passo.rotulo_estado }}</span>' in compor
    assert 'aria-current="step"' in compor
    assert "text-transform" not in (regra(".assistente .estado") or "")
    # A marca vazada da etapa pronta para revisar continua: a distinção não pode ser só de cor.
    assert "border:2px" in (regra(".assistente .a-pronta .numero") or "")


# --- F3 — o Conteúdo do Edital (FR-1029 a FR-1032) ---------------------------------------------


@pytest.fixture
def conteudo(client, composto):  # noqa: F811
    """A etapa com três seções escritas e as demais vazias."""
    return client.get(
        reverse("interface:compor-etapa", args=[composto.id, "conteudo"])
    ).content.decode()


def _secao(html, chave):
    achado = re.search(rf'<fieldset[^>]*data-secao="{chave}".*?</fieldset>', html, re.S)
    assert achado, chave
    return achado.group(0)


@pytest.mark.django_db
@pytest.mark.integration
def test_a_secao_vazia_nasce_com_duas_linhas_e_a_escrita_com_cinco(conteudo):
    """FR-1030: a vazia do tamanho da preenchida era a maior parte dos 4.876 px da página."""
    assert re.search(r'name="secao-certificado" rows="2"', _secao(conteudo, "certificado"))
    assert re.search(r'name="secao-publico-alvo" rows="5"', _secao(conteudo, "publico-alvo"))


@pytest.mark.django_db
@pytest.mark.integration
def test_a_marca_de_secao_vazia_continua_no_nome_do_campo(conteudo):
    """FR-1031 e D-008: muda o desenho, e não o texto — ela fecha o nome acessível do campo."""
    secao = _secao(conteudo, "certificado")
    assert "(vazia — não sai no documento)</span></legend>" in secao
    assert 'aria-labelledby="titulo-certificado"' in secao
    regras = (GESTAO / "compor_conteudo.html").read_text()
    assert ".secao>legend [data-estado-texto]{text-transform:none" in regras


@pytest.mark.django_db
@pytest.mark.integration
def test_a_secao_gerada_nao_tem_caixa_e_o_caminho_fica_na_frase(conteudo):
    """FR-1032: sem moldura de campo, e o link no fim da frase, e não num parágrafo só dele."""
    secao = _secao(conteudo, "cronograma")
    assert "Não há texto a redigir: alterar aquele conteúdo altera esta seção." in secao
    paragrafo = re.search(r'<p class="ajuda">(.*?)</p>', secao, re.S).group(1)
    assert "Ir para Cronograma</a>" in paragrafo
    regras = (GESTAO / "compor_conteudo.html").read_text()
    assert "fieldset.secao.gerada{border:0;" in regras
    assert "fieldset.secao{max-width:calc(var(--leitura)" in regras


# --- F2 — os cartões de coleção (FR-1023 a FR-1028) --------------------------------------------

CARTOES = {
    "_evento.html": ("Evento do Cronograma", True),
    "_etapa.html": ("Etapa de Avaliação", True),
    "_documento.html": ("Documento exigido", True),
    "_modalidade.html": ("Modalidade de Concorrência", False),
}


@pytest.mark.parametrize("template", CARTOES)
def test_as_acoes_moram_na_linha_da_legenda(template):
    """FR-1023: o grupo é o filho seguinte à `legend`, e a folha o leva para a borda de cima.

    Antes ele era a última coluna da faixa de campos, ou uma faixa só dele — a linha de ações que a
    auditoria mediu em Etapa, Documento e Modalidade.
    """
    corpo = sem_prosa((GESTAO / template).read_text())
    depois_da_legenda = corpo[corpo.index("</legend>") :]
    campos = depois_da_legenda.index('<div class="campos">')
    grupo = re.compile(r"acoes[-_]da[-_]linha")  # a classe, ou o parcial que a desenha
    assert grupo.search(depois_da_legenda[:campos]), f"{template}: as ações não seguem a legenda"
    assert not grupo.search(depois_da_legenda[campos:]), f"{template}: o grupo ficou nos campos"


@pytest.mark.parametrize("template", CARTOES)
def test_a_legenda_nomeia_o_item_sem_mudar_a_confirmacao(template):
    """FR-1024 e FR-1027: categoria, posição e nome; `data-rotulo` é só a categoria.

    `remocao.js` monta "Remover <data-rotulo>? …" — com a categoria, a pergunta é a de antes. E a
    legenda não leva botão: ela é o nome do grupo de campos.
    """
    categoria, ordenavel = CARTOES[template]
    corpo = (GESTAO / template).read_text()
    legenda = re.search(r"<legend([^>]*)>(.*?)</legend>", corpo, re.S)
    assert f'data-rotulo="{categoria}"' in legenda.group(1)
    assert f'<span class="categoria">{categoria}' in legenda.group(2)
    assert ("<span data-ordem></span>" in legenda.group(2)) is ordenavel
    assert '<span class="nome">' in legenda.group(2)
    assert "{% if" in legenda.group(2), "sem identificador, o nome não é desenhado vazio"
    assert "<button" not in legenda.group(2)


def test_a_folha_leva_o_grupo_para_a_borda_e_o_devolve_em_tela_estreita():
    """FR-1023 e FR-1026: posicionado ao lado da legenda; abaixo de 60 rem, no fluxo."""
    assert "position:relative" in regra("fieldset.linha")
    corpo = regra("fieldset.linha>.acoes-da-linha")
    assert "position:absolute" in corpo and "right:1rem" in corpo
    assert re.search(
        r"@media \(max-width:60rem\)\{\s*fieldset\.linha>\.acoes-da-linha\{position:static", FOLHA
    )
    # No fluxo o grupo quebra: o `fieldset` cresce até o conteúdo mínimo, e as duas ações em texto
    # da Modalidade numa fileira só alargavam o cartão do Perfil para 481 px numa janela de 375.
    assert re.search(r"fieldset\.linha>\.acoes-da-linha \.grupo\{flex-wrap:wrap", FOLHA), (
        "o grupo no fluxo precisa quebrar"
    )
    # O que a mudança tornou morto sai junto: a reserva de rótulo e a coluna dentro da faixa.
    assert ".campos>.acoes-da-linha" not in FOLHA
    assert "rotulo-vazio" not in FOLHA
    assert "rotulo-vazio" not in (GESTAO / "_acoes_da_linha.html").read_text()


@pytest.mark.django_db
@pytest.mark.integration
def test_o_evento_novo_tem_legenda_sem_nome_e_o_gravado_com_o_tipo(client, composto):  # noqa: F811
    """FR-1024: o Evento recém-acrescentado diz a categoria; o gravado diz também qual é."""
    novo = client.get(reverse("interface:fragmento-evento"), {"indice": "7"}).content.decode()
    legenda = re.search(r"<legend[^>]*>(.*?)</legend>", novo, re.S).group(1)
    assert 'class="nome"' not in legenda

    pagina = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "cronograma"])
    ).content.decode()
    nomes = re.findall(
        r'<legend data-rotulo="Evento do Cronograma">.*?<span class="nome">(.*?)</span>', pagina
    )
    assert nomes, "o Evento gravado não diz qual é"


def test_a_faixa_do_evento_poe_as_datas_juntas_e_o_local_no_fim():
    """FR-1028 e D-006: Tipo, Descrição, Início, Término — e "Onde acontece" depois, curto.

    Uma faixa só (`test_o_evento_cabe_numa_linha`); a quebra de "Onde acontece" para a linha de
    baixo a 1280 px é da largura, e não de marcação.
    """
    corpo = (GESTAO / "_evento.html").read_text()
    ordem = [
        corpo.index(f'name="evento-{{{{ indice }}}}-{campo}"')
        for campo in (
            "type",
            "description",
            "startAt",
            "endAt",
            "location",
        )
    ]
    assert ordem == sorted(ordem)
    assert '<p class="campo largo">\n      <label for="evento-{{ indice }}-description">' in corpo
    assert '<p class="campo local">' in corpo
    cronograma = (GESTAO / "compor_cronograma.html").read_text()
    assert ".campo.local{flex:0 1 20rem}" in cronograma


# --- F4 — a Revisão em grade de rótulo e valor (FR-1033, FR-1034) ------------------------------


def test_a_linha_rotulada_e_a_mesma_cadeia():
    """FR-1034: o texto da linha não muda — é por isso que os testes da Revisão seguem valendo."""
    from processo_seletivo.interface.origens import Rotulada, com_origem

    linha = Rotulada("Peso", "2.0000")
    assert linha == "Peso: 2.0000"
    assert (linha.rotulo, linha.valor) == ("Peso", "2.0000")

    com = com_origem(Rotulada("Caráter", "eliminatória"), "o padrão da Etapa decisória")
    assert com == "Caráter: eliminatória (o padrão da Etapa decisória)"
    assert com.rotulo == "Caráter", "a origem vai para o valor, e o rótulo continua"
    assert com_origem(linha, "") is linha


def test_os_trechos_juntam_vizinhos_e_nao_partem_texto_de_quem_elabora():
    """FR-1033: o dois-pontos da descrição de um Evento não é rótulo; a ordem não muda."""
    from processo_seletivo.interface.origens import Rotulada
    from processo_seletivo.interface.templatetags.interface_extras import em_trechos

    linhas = [
        "Inscrições: pelo sistema, das 9h às 18h",
        Rotulada("Início", "01/10/2026 09:00"),
        Rotulada("Onde acontece", "Sala 3"),
        "",
        "É o período de inscrições deste Edital",
    ]
    trechos = em_trechos(linhas)

    assert [trecho["pares"] for trecho in trechos] == [False, True, False]
    assert trechos[0]["linhas"] == ["Inscrições: pelo sistema, das 9h às 18h"]
    assert [linha.rotulo for linha in trechos[1]["linhas"]] == ["Início", "Onde acontece"]
    assert [linha for trecho in trechos for linha in trecho["linhas"]] == [
        linha for linha in linhas if linha
    ]


@pytest.mark.django_db
@pytest.mark.integration
def test_a_revisao_poe_os_rotulos_numa_coluna(client, composto):  # noqa: F811
    """FR-1033: a linha rotulada vira `dt`/`dd`; nenhuma sai em `span` corrido."""
    corpo = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "revisao"])
    ).content.decode()

    assert '<dl class="dados-da-inscricao"><dt>Início:</dt> <dd>' in corpo
    corridas = re.findall(r'<span class="detalhe">([^<]*)</span>', corpo)
    for rotulo in ("Início", "Cadastro Reserva", "Exigência", "Caráter", "Por que não se corrige"):
        assert not any(linha.startswith(f"{rotulo}: ") for linha in corridas), rotulo
    revisao = (GESTAO / "compor_revisao.html").read_text()
    assert (
        ".conferencia .dados-da-inscricao{grid-template-columns:fit-content(16rem) 1fr" in revisao
    )


# --- F5 — texto longo em área de texto (FR-1035, FR-1036) --------------------------------------


@pytest.mark.parametrize(
    ("template", "nome"),
    [
        ("_perfil.html", "perfil-{{ indice }}-description"),
        ("_documento.html", "documento-{{ indice }}-instructions"),
    ],
)
def test_o_texto_longo_do_compor_e_area_de_texto_com_o_mesmo_nome(template, nome):
    """FR-1035: muda o controle, e não o nome — o envio é o mesmo."""
    corpo = (GESTAO / template).read_text()
    assert re.search(rf'<textarea id="[^"]+"\s+name="{re.escape(nome)}"[^>]*rows="2"', corpo)
    assert not re.search(rf'<input[^>]*name="{re.escape(nome)}"', corpo)


def test_os_tres_campos_longos_do_retificar_sao_texto_longo():
    """FR-1036 e D-011: o tipo muda o controle; a conversão dos dois tipos é a mesma."""
    from processo_seletivo.interface import retificacao

    tipos = {caminho: tipo for caminho, _, tipo in retificacao.CAMPOS_RAIZ}
    for caminho in ("title", "description", "matriculationRequest/declarationText"):
        assert tipos[caminho] == retificacao.TEXTO_LONGO, caminho
        for bruto in ("  Edital de seleção  ", ""):
            assert retificacao._converter(bruto, retificacao.TEXTO_LONGO, "x") == (
                retificacao._converter(bruto, retificacao.TEXTO, "x")
            )
    linha = (GESTAO / "_retificacao_linha.html").read_text()
    assert "campo.chave == 'title' or campo.chave == 'description' %}2" in linha
    assert "campo.chave == 'matriculationRequest/declarationText' %}4" in linha


# --- D4 — Anexos com as larguras das outras etapas (FR-1037) -----------------------------------


def test_a_navegacao_da_etapa_nao_herda_a_medida_de_leitura():
    """Em Anexos a barra é filha de `main`, e `main>p` a prendia em 685 px: "Avançar" no meio."""
    assert "max-width:none" in regra(".navegacao-etapa")
    anexos = (GESTAO / "compor_anexos.html").read_text()
    assert "#anexos-lista>.vazio{max-width:none}" in anexos


# --- F6 — o Perfil no Retificar na ordem do Compor (FR-1038) -----------------------------------


def test_o_perfil_se_desenha_na_ordem_do_compor_sem_renomear_campo():
    """D-013: a referência é a posição em `CAMPOS_PERFIL`; só a apresentação reordena."""
    from processo_seletivo.interface.retificacao import CAMPOS_PERFIL, na_ordem_do_compor

    campos = [
        {"chave": chave, "referencia": f"g2c{indice}"}
        for indice, (chave, _, _) in enumerate(CAMPOS_PERFIL, 1)
    ]
    desenhados = na_ordem_do_compor({"tipo": "Perfil", "campos": campos})

    chaves = [campo["chave"] for campo in desenhados]
    assert chaves[0] == "name"
    assert chaves.index("name") < chaves.index("requirements")
    assert sorted(c["referencia"] for c in desenhados) == sorted(c["referencia"] for c in campos)
    assert {c["chave"]: c["referencia"] for c in desenhados} == {
        c["chave"]: c["referencia"] for c in campos
    }, "nenhum campo troca de nome"
    assert na_ordem_do_compor({"tipo": "Evento", "campos": campos}) == campos
