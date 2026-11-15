"""Duas larguras, porque são dois trabalhos — e nenhuma delas em pixel cravado.

Um limite só em `main` fazia três coisas ao mesmo tempo: medida de texto, largura de tabela e
largura de painel. Fazia as três mal, e ao mesmo tempo — media-se **84 caracteres por linha no
portal e 147 na gestão**, contra os 65 a 75 confortáveis, enquanto sobravam **412 px de tela** ao
lado de um PDF renderizado a 69% do tamanho.

O que estes testes prendem é a separação: `--pagina` para a estrutura, `--leitura` para o texto. Não
substituem olhar a tela — o que se pode conferir aqui é que a regra existe e que ninguém voltou a
cravar um limite em pixel.
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar
from tests.interface.folha import folha_da_pagina

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def da_gestao(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return folha_da_pagina(client, reverse("interface:lista"))


@pytest.fixture
def do_portal(client):
    return folha_da_pagina(client, reverse("portal:vitrine"))


@pytest.fixture
def da_visao_geral(client, seletor_ligado):
    """A folha **renderizada** da Visão Geral — base mais o estilo próprio da página (040).

    Existe porque a `040` moveu o estilo de uma tela para um bloco que só ela preenche, e sem este
    caso a regra do pixel cravado deixaria de alcançá-lo: a folha da lista não o contém mais.
    É a mesma disciplina da varredura de vocabulário — tela que sai do alcance de um guardião entra
    nele por outro lugar, **no mesmo commit**.
    """
    identificar(client, "carlos", ["gestor"])
    return folha_da_pagina(client, reverse("interface:visao-geral"))


# Tipos que o navegador desenha como caixa de texto. Os demais — `hidden`, `checkbox`, `radio`,
# `file`, `submit` — têm aparência própria e não entram na regra de campo.
NAO_SAO_CAIXA_DE_TEXTO = {
    "hidden",
    "checkbox",
    "radio",
    "file",
    "submit",
    "button",
    "image",
    "reset",
}
TEMPLATES = Path(__file__).resolve().parents[2] / "processo_seletivo"


def test_todo_campo_de_texto_dos_templates_esta_na_regra_de_campo(da_gestao):
    """Uma lista que enumera tipos esquece o tipo seguinte. Duas vezes, aqui.

    A regra cobria só `input[type=text]`, e `Ano` — que é `number` — ficava com a aparência padrão
    do navegador. Estenderam a lista, e anos depois a busca da Visão Geral entrou como `search`:
    22 px de altura e fonte de 13,33 px ao lado de selects de 41 px e 16 px, com borda `2px inset`.
    E como a barra de filtros alinha por `flex-end`, o rótulo *Buscar* descia os mesmos 19 px de
    diferença — o campo parecia "menor", e o rótulo, "torto". Um `tel` estava na mesma situação.

    Por isso este guardião **varre os templates** em vez de conferir a lista contra si mesma: o
    tipo que ninguém lembrou é exatamente o que uma lista escrita à mão não acusa.
    """
    usados = set()
    for template in TEMPLATES.rglob("*.html"):
        for campo in re.findall(r"<input[^>]*>", template.read_text(encoding="utf-8")):
            tipo = re.search(r'type="([a-z-]+)"', campo)
            if tipo and tipo.group(1) not in NAO_SAO_CAIXA_DE_TEXTO:
                usados.add(tipo.group(1))

    # **Sem os comentários.** A prosa desta folha cita `input[type=text]` ao explicar a regra, e um
    # seletor casado com o comentário junto devolve a regra errada — foi o que aconteceu aqui.
    sem_comentario = re.sub(r"/\*.*?\*/", "", da_gestao, flags=re.S)
    regras = [
        seletores
        for seletores, corpo in re.findall(r"([^{}]*)\{([^{}]*)\}", sem_comentario)
        if "input[type=" in seletores and "select" in seletores and "textarea" in seletores
    ]
    assert regras, "a regra de campo sumiu da folha"

    coberto = " ".join(regras)
    faltando = sorted(t for t in usados if f"input[type={t}]" not in coberto)
    assert faltando == [], faltando


def test_as_duas_larguras_vivem_nos_tokens(da_gestao, do_portal):
    """Num lugar só, como as cores: é o que impede as duas bases de divergirem."""
    for css in (da_gestao, do_portal):
        assert "--leitura:" in css
        assert "--pagina:" in css


@pytest.mark.parametrize("base", ["gestao", "portal"])
def test_a_pagina_serve_a_estrutura(base, da_gestao, do_portal):
    """`main` deixa de ser o limite do texto e passa a ser o limite da página."""
    css = da_gestao if base == "gestao" else do_portal

    assert re.search(r"main\{max-width:var\(--pagina\)", css), css[:0]
    assert not re.search(r"main\{max-width:\d+px", css)


def test_o_texto_corrido_do_portal_tem_medida_propria(do_portal):
    """Sem isto, alargar a página levaria as linhas de 147 para mais de 200 caracteres. A migração
    do design system é da gestão: o portal continua com a medida."""
    assert re.search(r"main>p[^{]*\{[^}]*max-width:var\(--leitura\)", do_portal)


def test_o_texto_da_gestao_ocupa_a_largura_do_conteudo(da_gestao):
    """Migração do design system (15/11, D-012 da `172`): o usuário viu as duas composições e
    preferiu o texto na largura do conteúdo. A medida de 68ch não volta por nenhuma regra comum."""
    assert "var(--leitura)" not in da_gestao


def test_o_campo_de_texto_ocupa_a_largura_do_formulario(da_gestao):
    """Pedido do usuário no piloto da `172`: o campo do fundamento cobria metade da área. O número
    e a data continuam do tamanho do que recebem (`.campo.curto>input`, `input[type=date]`)."""
    assert not re.search(r"\.campo>(?:textarea|select|input)[^{]*\{[^}]*max-width", da_gestao)
    assert re.search(r"\.campo\.curto>input\{max-width:10rem\}", da_gestao)


def test_a_vitrine_usa_a_tela_em_duas_colunas(do_portal):
    """Cinco seleções ocupavam 1,8 tela com 346 px vazios de cada lado."""
    assert re.search(r"\.selecoes\{[^}]*grid-template-columns:repeat\(auto-fill", do_portal)


def test_nenhuma_das_bases_crava_largura_em_pixel(da_gestao, do_portal):
    """`max-width` em pixel volta a ser um número decidindo por todas as telas."""
    for css in (da_gestao, do_portal):
        cravadas = re.findall(r"(?<!min-)max-width:(\d+)px", css)
        assert cravadas == [], cravadas


def test_o_estilo_de_pagina_tambem_nao_crava_largura_em_pixel(da_visao_geral):
    """A regra vale onde o estilo estiver, e não onde ele costumava estar."""
    cravadas = re.findall(r"(?<!min-)max-width:(\d+)px", da_visao_geral)

    assert cravadas == [], cravadas


def test_a_grade_da_tabela_filha_e_declarada_e_fecha_em_cem(da_visao_geral):
    """`FR-632` — sem `table-layout:fixed`, cada expansão negocia largura com o próprio conteúdo.

    Medido antes: duas expansões do mesmo recorte não coincidiam em **coluna nenhuma**, e
    `Inscr./vaga` saía com `192 px` num Edital e `78 px` no seguinte — porque num deles a frase
    *"não se aplica: este Perfil não publica vaga imediata"* caía naquela célula e a dilatava.
    Rolando a página, a mesma coluna saltava.

    A soma é conferida porque uma proporção que não fecha não dá erro: ela só reparte a sobra em
    silêncio, e a grade volta a depender do conteúdo sem nada acusar.
    """
    assert re.search(r"\.tabela-de-perfis\{[^}]*table-layout:fixed", da_visao_geral)

    # O `;` antes da chave é da 091 (a varredura de sintaxe de modelo nas folhas estáticas).
    larguras = re.findall(r"\.tabela-de-perfis \.c-[\w-]+\{width:(\d+)%;?\}", da_visao_geral)

    assert len(larguras) == 6, larguras
    assert sum(int(n) for n in larguras) == 100, larguras


def test_cabecalho_e_numero_dividem_a_borda_nas_duas_tabelas(da_visao_geral):
    """`FR-627` — a convenção já era da casa, e esta tela cobria só o `td`.

    `base.html` alinha à direita `td.numero` **e** `th.numero`. A Visão Geral escreveu a regra só
    para o `td`, e o resultado era o rótulo colado à esquerda da coluna com o número colado à
    direita: medido, `Em preenchimento` punha `137 px` entre o começo de um e o fim do outro, e o
    número acabava mais perto do rótulo da coluna **seguinte** que do seu.

    Não se centraliza: centralizado, `2`, `40` e `105` deixam de empilhar pela casa das unidades.
    Por isso a asserção é sobre `right`, e não sobre "ter alinhamento".
    """
    # Varre **todas** as regras que falam de `th.numero`, e não a primeira: a folha da página vem
    # depois da base, e a base tem a sua própria — que não é a desta tela.
    regras = [
        (seletores, corpo)
        for seletores, corpo in re.findall(r"([^{}]*)\{([^{}]*)\}", da_visao_geral)
        if "th.numero" in seletores
    ]
    cobre = [
        seletores
        for seletores, corpo in regras
        if "text-align:right" in corpo
        and ".tabela-da-visao th.numero" in seletores
        and ".tabela-de-perfis th.numero" in seletores
    ]

    assert cobre, [s for s, _ in regras]


def test_a_folha_da_visao_geral_so_usa_cor_de_token():
    """P0 do estudo de design system (14/11): a Visão Geral tinha paleta própria, e era a única
    tela da gestão com texto abaixo de 4,5:1 — 155 trechos, quase todos `#9aa3ad` sobre `#f8f8f8`,
    a 2,41:1.

    `test_contraste_atende_wcag_aa` confere os pares de `tokens.css`, e por isso não via cor
    literal. Este fecha a porta por onde ela entrou: cor nesta folha é `var(--…)`.
    """
    folha = (TEMPLATES / "interface/static/interface/telas/visao-geral.css").read_text()
    sem_comentario = re.sub(r"/\*.*?\*/", "", folha, flags=re.S)

    assert re.findall(r"#[0-9a-fA-F]{3,8}\b", sem_comentario) == []
    assert re.findall(r"\b(?:rgba?|hsla?)\(", sem_comentario, flags=re.I) == []
    # O nome de cor (`gray`, `white`, `darkslategray`…) é o terceiro caminho, e a lista dos nomes
    # tem 148: em vez dela, a propriedade de cor só admite `var(--…)`, medida e as palavras que
    # não são cor. Uma palavra nova fora desta lista reprova até alguém decidir que não é cor.
    nao_sao_cor = {
        "transparent", "currentcolor", "inherit", "initial", "unset", "none",
        "solid", "dashed", "dotted", "double", "hidden", "thin", "medium", "thick", "underline",
    }  # fmt: skip
    declaracoes = re.findall(r"(?<![\w-])([a-z-]+)\s*:\s*([^;{}]+)(?=[;}])", sem_comentario)
    de_cor = [
        (propriedade, valor)
        for propriedade, valor in declaracoes
        if re.fullmatch(
            r"color|background(-color)?|border(-(top|right|bottom|left))?(-color)?"
            r"|outline(-color)?|box-shadow|text-decoration(-color)?|fill|stroke",
            propriedade,
        )
    ]
    assert de_cor, "a leitura das declarações deixou de achar a cor da folha"
    fora = [
        (propriedade, valor)
        for propriedade, valor in de_cor
        for palavra in re.findall(r"[a-z][a-z-]*", re.sub(r"var\([^)]*\)", "", valor), re.I)
        if palavra.lower() not in nao_sao_cor and not re.fullmatch(r"px|rem|em|%", palavra)
    ]
    assert fora == []


def test_a_tabela_da_visao_geral_rola_na_moldura_comum():
    """P0: a moldura própria só rolava abaixo de 40 rem, e a 768 px o documento media 880 px. A
    comum, `.tabela-rolavel`, rola em toda largura.

    A conferência é pela árvore, e não pelo texto: a tabela é filha direta da moldura, com o
    espaço que for entre as duas."""
    from html.parser import HTMLParser

    class Pais(HTMLParser):
        def __init__(self):
            super().__init__()
            self.pilha, self.pai_da_tabela = [], None

        def handle_starttag(self, tag, attrs):
            classes = (dict(attrs).get("class") or "").split()
            if tag == "table" and "tabela-da-visao" in classes:
                self.pai_da_tabela = self.pilha[-1] if self.pilha else None
            if tag not in {"br", "img", "input", "meta", "link", "hr", "wbr", "col", "source"}:
                self.pilha.append((tag, classes))

        def handle_endtag(self, tag):
            while self.pilha and self.pilha.pop()[0] != tag:
                pass

    modelo = (GESTAO / "visao_geral.html").read_text()
    leitor = Pais()
    leitor.feed(re.sub(r"{%.*?%}|{{.*?}}", "", modelo, flags=re.S))

    assert leitor.pai_da_tabela is not None, "a tabela da Visão Geral saiu do modelo"
    assert leitor.pai_da_tabela[0] == "div"
    assert "tabela-rolavel" in leitor.pai_da_tabela[1]
    assert "rolagem-da-tabela" not in modelo


def test_a_consulta_estreita_nao_alcanca_a_tabela_aninhada(da_visao_geral):
    """`FR-627` — seletor descendente atravessa `<table>` dentro de `<table>`.

    A consulta estreita esconde a terceira, a sexta e a sétima coluna da tabela principal. Escrita
    como descendente, ela alcançava também a tabela **aninhada** na expansão — onde a terceira e a
    sexta são *Submetidas* e *Atenção*. No telefone a região filha ficava com **três** colunas onde
    a `FR-627` exige cinco, e perdia justamente a de atenção.

    Nada acusava, e nada poderia: `display:none` não muda o HTML, de modo que toda asserção sobre a
    marcação continuava verde. Por isso o guardião é sobre a **forma do seletor**.
    """
    # O bloco da Visão Geral, e não o primeiro de 40rem da folha: a folha comum também tem um.
    blocos = re.findall(r"@media \(max-width:40rem\)\{(.*?)\n\}", da_visao_geral, re.S)
    estreita = next(b for b in blocos if ".tabela-da-visao" in b)

    assert ".tabela-da-visao th:nth-child(" not in estreita
    assert ".tabela-da-visao td:nth-child(" not in estreita
    assert estreita.count(".tabela-da-visao>thead>tr>*:nth-child(") == 3
    assert estreita.count(".tabela-da-visao>tbody>tr>*:nth-child(") == 3


def test_a_marca_do_perfil_e_menor_que_a_do_edital(da_visao_geral):
    """`FR-633`. A `FR-624` obrigou só o **cabeçalho**, e a marca escapou do rebaixamento.

    Denominação, número e cabeçalho foram todos reduzidos na região filha; a marca ficou idêntica à
    do Edital — mesma fonte, mesmo peso, mesma borda —, de modo que o elemento mais gritante da
    expansão era justamente o que menos deveria competir com a linha acima.

    A comparação é **numérica**, e não a presença da regra: quem aumentar a marca do Edital sem
    olhar para esta passa a ter as duas iguais de novo, e uma asserção de existência não veria.
    """
    do_edital = float(
        re.search(r"\nmain \.marca\{[^}]*font-size:([\d.]+)rem", da_visao_geral).group(1)
    )
    do_perfil = float(
        re.search(r"\.tabela-de-perfis \.marca\{[^}]*font-size:([\d.]+)rem", da_visao_geral).group(
            1
        )
    )

    assert do_perfil < do_edital, (do_perfil, do_edital)


def test_a_consulta_estreita_vence_a_regra_de_mesa_do_recuo(da_visao_geral):
    """`@media` **não acrescenta especificidade** — quem vier por último vence.

    O recuo da expansão tem duas redações: `2.5rem` em mesa e `.6rem` em viewport estreito. Elas
    têm o mesmo seletor e a mesma especificidade, e a consulta estreita nasceu **acima** da regra
    de mesa, junto das outras consultas da folha. Resultado: o `padding` de mesa a sobrescrevia em
    toda largura, e o recuo ficava em 40 px no telefone — sem erro de sintaxe, sem aviso, e sem
    nenhum teste falhando. Foi medido no navegador, e é por isso que virou guardião.
    """
    de_mesa = da_visao_geral.index(".expansao-do-edital>td{padding:")
    estreita = da_visao_geral.index(".expansao-do-edital>td{padding-left:.6rem}")

    assert estreita > de_mesa, "a sobrescrita estreita precisa vir **depois** da regra de mesa"


def test_o_painel_do_documento_respeita_o_atributo_hidden():
    """`display` de autor vence o `display:none` que o `hidden` traz do navegador.

    Sem a guarda, o painel aparecia vazio no alto de **toda** inscrição, com o botão de fechar,
    antes de qualquer documento ser aberto — e empurrava a avaliação para fora da primeira tela.
    """
    # A regra mora na folha do visualizador desde a 157, carregada pela Mesa e pela conferência.
    folha = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/static/interface/grupos/visualizador.css"
    ).read_text(encoding="utf-8")
    assert re.search(r"\.painel-documento:not\(\[hidden\]\)\{[^}]*display:flex", folha)
    assert not re.search(r"\.painel-documento\{[^}]*display:flex", folha)


def test_os_numeros_da_distribuicao_sao_o_filtro(
    client, seletor_ligado, gestor, edital_a, etapa_a1
):
    """Ler a contagem num cartão para depois procurá-la num `select` é pedir duas vezes o mesmo.

    "Sem avaliador suficiente" é onde a presidência quer chegar; o número é o caminho.
    """
    from tests.fixtures.comissao import inscrever

    inscrever(edital_a, 2, primeiro=800)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(
        reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])
    ).content.decode()

    # Dentro do controle, e não em qualquer lugar da página: o que se prende é que o número
    # **seja** o filtro, e não que o endereço exista em algum canto.
    controle = re.search(r'<nav class="filtros-da-mesa"[^>]*>(.*?)</nav>', corpo, re.S)
    assert controle, "a distribuição tem o controle de cobertura"
    for alvo in ("?cobertura=sem_nenhum", "?cobertura=carente", "?cobertura=avaliacao_pendente"):
        assert alvo in controle.group(1), alvo


def test_nenhuma_tela_anuncia_um_estado_como_sucesso(client, seletor_ligado, gestor, processo_a):
    """Faixa verde é para ato recém-praticado, e não para fato permanente.

    "Você integra a comissão", "Você está alocado nesta Etapa" e "Avaliação concluída em…"
    reapareciam a cada visita dizendo "deu certo" sobre coisas que a pessoa já sabia.
    """
    from tests.fixtures.comissao import constituir

    constituir(gestor, processo_a, [("carlos", "MEMBRO")], prefixo="estado")
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Você integra a comissão de" in corpo
    assert 'class="sucesso"' not in corpo


def test_a_marca_de_atencao_nao_alcanca_a_marca_do_cabecalho(da_visao_geral):
    """A marca de atenção e a marca do cabeçalho dividem a classe `.marca`.

    Escrita sem escopo, a regra da Visão Geral pintava também o `Cefor/Ifes · Processos Seletivos`
    do topo: fundo creme e borda âmbar sob texto branco, e o nome do sistema sumia — só nesta tela,
    que é a única a declarar a regra. Nenhuma asserção sobre a marcação via, porque o HTML do
    cabeçalho é o mesmo em toda tela; por isso o guardião é, de novo, sobre a forma do seletor.
    """
    soltas = re.findall(r"(?:^|[\n,}])\.marca(?=[{.,:\s])", da_visao_geral)

    assert not soltas, soltas


# ---- 375 px: as duas telas do percurso de 15/10 ------------------------------------------------
#
# A auditoria de consolidação de 15/10 mediu, por `scrollWidth` numa moldura de 375 px, duas telas
# que nenhum guardião alcançava: a verificação pública do sorteio, a 673 px (PV-03), e o detalhe do
# Edital na gestão, a 440 px (PV-04). Depois da correção as duas fecham em 375. A medida mora no
# PR; o que fica aqui é o que a produz — a classe no elemento que transbordava e a regra na folha —,
# como no resto deste arquivo.

PORTAL = TEMPLATES / "portal" / "templates" / "portal"
GESTAO = TEMPLATES / "interface" / "templates" / "interface"


def _corpo_da_regra(seletor, css):
    achado = re.search(rf"(?:^|[}}\n]){re.escape(seletor)}\{{([^}}]*)\}}", css)
    return achado.group(1) if achado else ""


def test_a_linha_de_comando_do_verificador_quebra_a_375_px(do_portal):
    """PV-03: o `<code>` com o resumo de 64 caracteres sem espaço não pode ditar a largura.

    Os resumos da seção Integridade já quebravam pela regra de `.resumos dd`; a linha de comando,
    numa lista comum, não tinha regra nenhuma. Todo `<code>` fora daquela lista leva `.comando`.
    """
    fonte = (PORTAL / "verificacao_de_sorteio.html").read_text(encoding="utf-8")
    fora_dos_resumos = fonte.split('<dl class="resumos">', 1)[0]

    codigos = re.findall(r"<code[^>]*>", fora_dos_resumos)
    assert codigos, "a linha de comando do verificador sumiu da tela"
    assert all('class="comando"' in codigo for codigo in codigos), codigos
    assert "overflow-wrap:anywhere" in _corpo_da_regra(".comando", do_portal)


def test_a_acao_de_rotulo_longo_do_detalhe_quebra_a_375_px(da_gestao):
    """PV-04: o rótulo da validação do assistente (070) é fixado pelo contrato, e por isso quebra.

    A `.acao` é `nowrap` de propósito — na linha de tabela, partir o rótulo desalinha a linha —, e a
    exceção é declarada por classe, e não tirando o `nowrap` de todas.
    """
    fonte = (GESTAO / "detalhe.html").read_text(encoding="utf-8")
    link = re.search(r'<a class="([^"]*)"[^>]*>Ver as respostas do assistente', fonte)

    assert link and "longa" in link.group(1).split()
    regra = _corpo_da_regra(".acao.longa", da_gestao)
    assert "white-space:normal" in regra
    assert "max-width:100%" in regra
