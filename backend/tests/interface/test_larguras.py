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

pytestmark = [pytest.mark.django_db]


def folha(cliente, url):
    corpo = cliente.get(url).content.decode()
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


@pytest.fixture
def da_gestao(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return folha(client, reverse("interface:lista"))


@pytest.fixture
def do_portal(client):
    return folha(client, reverse("portal:vitrine"))


@pytest.fixture
def da_visao_geral(client, seletor_ligado):
    """A folha **renderizada** da Visão Geral — base mais o estilo próprio da página (040).

    Existe porque a `040` moveu o estilo de uma tela para um bloco que só ela preenche, e sem este
    caso a regra do pixel cravado deixaria de alcançá-lo: a folha da lista não o contém mais.
    É a mesma disciplina da varredura de vocabulário — tela que sai do alcance de um guardião entra
    nele por outro lugar, **no mesmo commit**.
    """
    identificar(client, "carlos", ["gestor"])
    return folha(client, reverse("interface:visao-geral"))


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


@pytest.mark.parametrize("base", ["gestao", "portal"])
def test_o_texto_corrido_tem_medida_propria(base, da_gestao, do_portal):
    """Sem isto, alargar a página levaria as linhas de 147 para mais de 200 caracteres."""
    css = da_gestao if base == "gestao" else do_portal

    assert re.search(r"main>p[^{]*\{[^}]*max-width:var\(--leitura\)", css)


def test_o_que_se_escreve_acompanha_o_que_se_le(da_gestao):
    """O parecer de uma avaliação se esticava por 1.052 px, e ninguém redige assim."""
    assert re.search(r"\.campo>textarea[^{]*\{[^}]*max-width:var\(--leitura\)", da_gestao)


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

    larguras = re.findall(r"\.tabela-de-perfis \.c-[\w-]+\{width:(\d+)%\}", da_visao_geral)

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


def test_a_consulta_estreita_nao_alcanca_a_tabela_aninhada(da_visao_geral):
    """`FR-627` — seletor descendente atravessa `<table>` dentro de `<table>`.

    A consulta estreita esconde a terceira, a sexta e a sétima coluna da tabela principal. Escrita
    como descendente, ela alcançava também a tabela **aninhada** na expansão — onde a terceira e a
    sexta são *Submetidas* e *Atenção*. No telefone a região filha ficava com **três** colunas onde
    a `FR-627` exige cinco, e perdia justamente a de atenção.

    Nada acusava, e nada poderia: `display:none` não muda o HTML, de modo que toda asserção sobre a
    marcação continuava verde. Por isso o guardião é sobre a **forma do seletor**.
    """
    estreita = re.search(r"@media \(max-width:40rem\)\{(.*?)\n\}", da_visao_geral, re.S).group(1)

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
    do_edital = float(re.search(r"\n\.marca\{[^}]*font-size:([\d.]+)rem", da_visao_geral).group(1))
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


def test_o_painel_do_documento_respeita_o_atributo_hidden(da_gestao):
    """`display` de autor vence o `display:none` que o `hidden` traz do navegador.

    Sem a guarda, o painel aparecia vazio no alto de **toda** inscrição, com o botão de fechar,
    antes de qualquer documento ser aberto — e empurrava a avaliação para fora da primeira tela.
    """
    assert re.search(r"\.painel-documento:not\(\[hidden\]\)\{[^}]*display:flex", da_gestao)
    assert not re.search(r"\.painel-documento\{[^}]*display:flex", da_gestao)


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
    for alvo in ("?cobertura=sem_nenhum", "?cobertura=incompleta", "?cobertura=avaliacao_pendente"):
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
