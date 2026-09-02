"""Acessibilidade verificável sem navegador: contraste, marcação nativa e link de salto.

A spec da 002 exige eMAG 3.1 e WCAG 2.1 AA, valendo a mais restritiva. O que um verificador
automatizado encontra em execução — e o que ele não encontra — está em `accessibility.md`;
aqui ficam as regras que dá para prender no repositório.
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar

BASE = (
    Path(__file__).resolve().parents[2]
    / "processo_seletivo/interface/templates/interface/base.html"
)
FONTE = BASE.read_text()
# Os tokens saíram da base para uma parcial compartilhada quando o canal público nasceu (009,
# T008). A rubrica de contraste segue a paleta para onde ela foi — e passa a valer para os dois
# canais de uma vez, que é o ganho de tê-la num lugar só.
TOKENS = (
    Path(__file__).resolve().parents[2]
    / "processo_seletivo/shared/templates/shared/_tokens.css.html"
).read_text()
MINIMO_AA = 4.5


def _controle(corpo, identificador):
    """A tag do controle daquele `id` — para afirmar sobre os atributos dele, e não sobre o HTML."""
    achado = re.search(
        r"<(?:input|textarea|select)[^>]*?id=\"" + re.escape(identificador) + r"\"[^>]*?>", corpo
    )
    assert achado, f"controle {identificador} não encontrado"
    return achado.group(0)


def _descrito_por(controle):
    achado = re.search(r'aria-describedby="([^"]*)"', controle)
    return achado.group(1) if achado else ""


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def tokens():
    """Cada `--nome:#rrggbb` declarado no :root, hoje na parcial compartilhada."""
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{3,6})", TOKENS))


def luminancia(cor):
    cor = cor.lstrip("#")
    if len(cor) == 3:
        cor = "".join(c * 2 for c in cor)
    canais = []
    for i in (0, 2, 4):
        v = int(cor[i : i + 2], 16) / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def contraste(frente, fundo):
    a, b = luminancia(frente), luminancia(fundo)
    claro, escuro = max(a, b), min(a, b)
    return (claro + 0.05) / (escuro + 0.05)


# Combinações que as telas realmente produzem. Manter explícito é o ponto: foi conflar dois
# papéis num token só que fez o rótulo da etapa e os links reprovarem.
PARES = [
    ("--verde-texto", "--branco", "links e rótulos sobre cartão"),
    ("--verde-texto", "--fundo", "links sobre o fundo da página"),
    ("--verde-texto", "--verde-claro", "rótulo da etapa atual e .acao no hover"),
    ("--verde-texto", "--vermelho-fundo", "link do Edital pendente dentro da recusa"),
    ("--verde-texto", "--amarelo-fundo", "links dentro de aviso"),
    ("--branco", "--verde", "texto do botão primário"),
    ("--branco", "--verde-escuro", "cabeçalho e botão no hover"),
    ("--branco", "--vermelho", "botão perigoso"),
    ("--verde-escuro", "--verde-claro", "chip de situação publicada"),
    ("--sucesso", "--verde-claro", "etapa concluída no assistente"),
    ("--amarelo", "--amarelo-fundo", "aviso"),
    ("--vermelho", "--vermelho-fundo", "erro e marcador irreversível"),
    ("#333", "--cinza-fundo", "chip de Edital em elaboração"),
    ("--texto-fraco", "--cinza-fundo", "chip encerrado e passo futuro do assistente"),
    ("--texto", "--fundo", "corpo do texto"),
    ("--texto-fraco", "--branco", "texto de apoio"),
    ("--texto-fraco", "--fundo", "texto de apoio sobre a página"),
]


def resolver(valor, declarados):
    """Aceita tanto `--token` quanto a cor literal que a folha usa direto."""
    if valor.startswith("#"):
        return valor
    assert valor in declarados, f"{valor} saiu da paleta"
    return declarados[valor]


@pytest.mark.parametrize(("frente", "fundo", "onde"), PARES)
def test_contraste_atende_wcag_aa(frente, fundo, onde):
    declarados = tokens()
    razao = contraste(resolver(frente, declarados), resolver(fundo, declarados))
    assert razao >= MINIMO_AA, (
        f"{onde}: {frente} sobre {fundo} dá {razao:.2f}:1, abaixo de {MINIMO_AA}:1"
    )


def test_link_de_salto_move_o_foco_e_nao_so_a_rolagem():
    """Sem tabindex, ativar o link rola a página e deixa o foco no BODY — a próxima tabulação
    volta ao cabeçalho, que é justamente o que o link existe para pular (WCAG 2.4.1)."""
    destino = re.search(r'<a class="pular" href="#([\w-]+)"', FONTE)
    assert destino, "o primeiro foco da página precisa ser o link de salto"
    alvo = destino.group(1)
    assert re.search(rf'<main id="{alvo}" tabindex="-1">', FONTE), (
        "o alvo do link de salto precisa poder receber foco"
    )


TELAS_CRITICAS = [
    ("interface:lista", None),
    ("interface:identificar", None),
]
NAO_NATIVOS = re.compile(
    r"<(?!a\b|button\b|input\b|select\b|textarea\b|main\b)[a-z]+[^>]*\s(?:onclick|hx-get|hx-post)=",
    re.IGNORECASE,
)


@pytest.mark.parametrize(
    "template",
    sorted(p.name for p in BASE.parent.glob("*.html")),
)
def test_controles_sao_nativos(template):
    """Enter e Espaço ativam `<button>` e `<a href>` por conta do navegador.

    Um `<div>` com onclick não é alcançável nem acionável por teclado, e nenhum verificador
    automatizado de contraste pega isso — é a marcação que decide.
    """
    corpo = (BASE.parent / template).read_text()

    assert not NAO_NATIVOS.search(corpo), "controle interativo fora de elemento nativo"
    # `<a(?=[\s>])` e não `<a`: sem isso, <article> casa e o teste acusa o que não existe.
    assert not re.search(r"<a(?=[\s>])(?![^>]*\bhref=)[^>]*>", corpo), (
        "âncora sem href não recebe foco"
    )
    assert not re.search(r'tabindex="[1-9]', corpo), (
        "tabindex positivo reordena a navegação e quebra a ordem visual"
    )


# ---------------------------------------------------------------------------
# 007 — os atritos que a auditoria mediu (FR-032, FR-033, FR-040, FR-041, FR-042)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ("etapa", "obrigatorios"),
    [("identificacao", 1), ("perfis", 0), ("cronograma", 0)],
)
def test_campos_obrigatorios_sao_marcados_na_etiqueta(
    client, seletor_ligado, edital, etapa, obrigatorios
):
    """T070/FR-032: nada separava o campo exigido do opcional em todo o produto.

    Nem asterisco, nem etiqueta, nem marca visual: descobria-se falhando. Em formulários longos,
    falhar significa rolar de volta procurando qual campo o servidor recusou.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:compor-etapa", args=[edital.id, etapa])).content.decode()

    if obrigatorios:
        assert corpo.count('class="obrigatorio"') >= obrigatorios
    # A marca visual é `aria-hidden`; quem usa leitor de tela recebe por `aria-required`.
    assert corpo.count('class="obrigatorio"') == corpo.count('aria-hidden="true">*</span>')


@pytest.mark.django_db(transaction=True)
def test_o_controle_obrigatorio_declara_aria_required(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "identificacao"])
    ).content.decode()

    assert 'aria-required="true"' in corpo


@pytest.mark.django_db(transaction=True)
def test_a_recusa_recebe_foco_para_nao_passar_despercebida(client, seletor_ligado, edital):
    """T070/FR-033: sem foco, quem envia um formulário longo e é recusado não vê a mensagem."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "perfis"]),
        {
            "perfil-0-id": "aaaaaaaa-0000-4000-8000-0000000000f1",
            "perfil-0-code": "P",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "LIMITED",  # limitada sem limite: o domínio recusa
        },
    )
    corpo = resposta.content.decode()

    assert 'role="alert"' in corpo
    assert 'tabindex="-1"' in corpo, "o resumo precisa poder receber o foco"
    assert "autofocus" in corpo


@pytest.mark.django_db(transaction=True)
def test_a_recusa_ancora_no_campo_e_aparece_junto_dele(client, seletor_ligado, edital):
    """FR-033 por inteiro: âncora no resumo **e** mensagem junto do campo.

    Ficou de fora da primeira entrega porque as exceções de domínio carregavam mensagem e nada
    mais. Agora carregam `campo` e `identidade` — opcionais —, e a interface as resolve para o `id`
    do controle daquela linha.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = "aaaaaaaa-0000-4000-8000-0000000000c1"

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "perfis"]),
        {
            "perfil-0-id": perfil,
            "perfil-0-code": "P",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "LIMITED",  # limitada sem limite: o domínio nomeia reserveLimit
        },
    )
    corpo = resposta.content.decode()

    # O resumo aponta para o campo.
    assert 'href="#perfil-0-reserveLimit"' in corpo, "o item do resumo precisa ancorar no campo"
    # E a mensagem aparece junto dele.
    assert 'id="recusa-perfil-0-reserveLimit"' in corpo, "falta a marca junto do campo"
    assert resposta.context["recusas"] == {
        "perfil-0-reserveLimit": "Cadastro Reserva limitado exige limite não negativo."
    }

    # **O vínculo programático**, que é o que FR-033 pede e o que `role="alert"` não dá: o alerta
    # anuncia a mensagem quando ela aparece, mas quem volta ao controle depois não tem como saber
    # que aquela mensagem lhe pertence.
    controle = _controle(corpo, "perfil-0-reserveLimit")
    assert 'aria-invalid="true"' in controle, controle
    assert "recusa-perfil-0-reserveLimit" in _descrito_por(controle), controle
    # E a ajuda que já existia não pode ter sido substituída pela recusa.
    assert "ajuda-reserva-0" in _descrito_por(controle), controle


@pytest.mark.django_db(transaction=True)
def test_recusa_que_nao_pertence_a_campo_nenhum_fica_em_texto(client, seletor_ligado, edital):
    """ "O Edital deve possuir ao menos um Perfil" não é de campo nenhum.

    Apontar um campo qualquer seria pior do que não apontar — e é por isso que `campo` é opcional.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(reverse("interface:compor-etapa", args=[edital.id, "perfis"]), {})
    corpo = resposta.content.decode()

    assert "ao menos um Perfil" in corpo
    assert resposta.context["recusas"] == {}
    assert 'href="#perfil-' not in corpo


@pytest.mark.django_db(transaction=True)
def test_a_etapa_de_conteudo_nasce_pronta_para_revisar_e_nao_concluida(
    client, seletor_ligado, edital
):
    """T088/FR-040: o passo 5 se declarava concluído sem ter sido aberto.

    As seções nascem com o texto do catálogo e, tecnicamente, nada falta — mas o sistema afirmava
    que a pessoa fez algo que ela não fez.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))

    conteudo = next(p for p in resposta.context["progresso"] if p["chave"] == "conteudo")
    assert conteudo["estado"] == "pronta"
    assert conteudo["rotulo_estado"] == "pronta para revisar"
    assert not conteudo["concluida"]
    # A distinção não pode depender só de cor.
    assert "pronta para revisar" in resposta.content.decode()


@pytest.mark.django_db(transaction=True)
def test_gravar_a_etapa_de_conteudo_a_torna_concluida(client, seletor_ligado, edital):
    from processo_seletivo.editais.domain import secoes as catalogo

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client,
        edital,
        perfis={
            "perfil-0-id": "aaaaaaaa-0000-4000-8000-0000000000f2",
            "perfil-0-code": "P",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
        },
    )
    campos = {
        f"secao-{s.key}": ("Texto revisto." if s.key == "apresentacao" else s.default_text)
        for s in catalogo.CATALOGO
        if not s.gerada
    }
    client.post(reverse("interface:compor-etapa", args=[edital.id, "conteudo"]), campos)

    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))
    conteudo = next(p for p in resposta.context["progresso"] if p["chave"] == "conteudo")
    assert conteudo["estado"] == "concluida"


@pytest.mark.django_db(transaction=True)
def test_a_faixa_do_ato_usa_o_rotulo_humano_e_nao_a_chave(client, seletor_ligado, edital):
    """T090/FR-041: "Ato registrado: submeter" saía assim porque a chave passava pelo filtro de
    *situações*, que não a conhece — e um filtro devolve o que não reconhece.

    O rótulo é o que `atos.ATOS` declara e a tela de confirmação já exibe no título: "Submeter para
    revisão". Existia, e não era consultado.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:detalhe", args=[edital.id]) + "?ato=submeter"
    ).content.decode()

    assert "Ato registrado: Submeter para revisão." in corpo
    assert "Ato registrado: submeter." not in corpo


@pytest.mark.django_db(transaction=True)
def test_a_auditoria_diz_qual_area_do_rascunho_mudou(client, seletor_ligado, edital):
    """T092/FR-042: quatro gravações produziam quatro registros idênticos.

    A trilha existe para responder questionamento, e "alguém mexeu no rascunho quatro vezes" não
    responde nenhum.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client,
        edital,
        perfis={
            "perfil-0-id": "aaaaaaaa-0000-4000-8000-0000000000f3",
            "perfil-0-code": "P",
            "perfil-0-name": "Perfil",
            "perfil-0-immediateVacancies": "1",
            "perfil-0-reserveType": "NONE",
        },
        eventos={
            "evento-0-id": "aaaaaaaa-0000-4000-8000-0000000000e3",
            "evento-0-type": "Inscrições",
            "evento-0-description": "Inscrições",
            "evento-0-startAt": "2027-03-01T10:00",
            "evento-0-order": "1",
        },
    )

    areas = list(
        RegistroAuditoria.objects.filter(
            aggregate_id=edital.id, operation="ALTERAR_RASCUNHO"
        ).values_list("reason", flat=True)
    )
    assert "Perfis de Vaga" in areas
    assert "Cronograma" in areas
    assert len(set(areas)) == len(areas), "registros de etapas diferentes não podem ser idênticos"


ALOCACOES = BASE.parent / "alocacoes.html"


def test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem():
    """`position:sticky` se prende ao ancestral que rola, e não à janela.

    A moldura da matriz nasceu com a classe `.rolagem` (`overflow-x:auto`), que faz o
    `overflow-y` computar para `auto` junto. Com isso o cabeçalho passava a ser fixado contra a
    moldura — que tem a altura do conteúdo e nunca rola por dentro — e sumia da tela na primeira
    rolagem. Numa comissão de cinquenta, sobravam colunas de caixas sem o nome da Etapa.

    Em tela estreita a rolagem horizontal é necessária; ali quem fixa é a coluna de nomes.
    """
    moldura = re.search(
        r'<div class="([\w-]+)">\s*<table class="distribuicao">', ALOCACOES.read_text()
    )
    assert moldura, "a matriz precisa estar dentro de uma moldura identificável"
    classe = moldura.group(1)

    fora_de_media = re.sub(r"@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}", "", FONTE)
    regra = re.search(rf"\.{classe}\{{([^}}]*)\}}", fora_de_media)
    assert regra, f".{classe} precisa declarar seu overflow fora de qualquer @media"
    assert "overflow-x:visible" in regra.group(1).replace(" ", ""), (
        f".{classe} rola em tela larga: o cabeçalho da matriz deixa de ser fixado pela janela"
    )


TELAS = sorted(BASE.parent.glob("*.html"))


@pytest.mark.parametrize("template", [p for p in TELAS], ids=lambda p: p.name)
def test_todo_botao_de_envio_declara_o_seu_peso(template):
    """Botão sem classe cai no desenho do navegador, e sai cinza no meio de uma tela verde.

    Não é só estética: `.botao`, `.acao` e `.perigoso` são o vocabulário com que estas telas
    dizem **o que é principal, o que é secundário e o que não se desfaz**. Nove envios estavam
    sem nenhum dos três — "Propor distribuição", "Confirmar esta distribuição", "Registrar
    impedimento", "Concluir avaliação" —, isto é, todas as ações principais da 012, e cada uma
    ao lado de um "Cancelar" que **tinha** classe. O contraste dizia o contrário do que valia.
    """
    corpo = template.read_text()

    sem_classe = re.findall(r'<button(?![^>]*\bclass=)[^>]*type="submit"[^>]*>', corpo)
    assert sem_classe == [], sem_classe


@pytest.mark.parametrize("template", [p for p in TELAS], ids=lambda p: p.name)
def test_nenhuma_classe_citada_deixa_de_existir_na_folha(template):
    """`.s-PRESIDENTE` e `.oculto` foram escritas nos templates e nunca definidas.

    Uma classe sem regra não quebra nada em execução — ela some. A pastilha de função ficava com
    a forma e sem a cor; `.oculto` prometia esconder e não escondia, e cinco legendas de tabela
    escritas para quem ouve a tela apareciam impressas para quem a vê, repetindo o título logo
    acima. É defeito silencioso por natureza, e por isso vira teste.

    O que se dispensa é o que a folha não decide: classe de gancho para JavaScript ou para
    consulta em teste, declarada aqui de propósito.
    """
    from tests.interface.conftest import CLASSES_SEM_DESENHO

    definidas = set(re.findall(r"\.([A-Za-z][\w-]*)", FONTE))
    citadas = set()
    for valor in re.findall(r'class="([^"]*)"', template.read_text()):
        # `s-{{ ... }}` monta o nome no render; o sufixo é conferido por quem o escreve.
        if "{{" in valor or "{%" in valor:
            continue
        citadas.update(valor.split())

    orfas = sorted(citadas - definidas - CLASSES_SEM_DESENHO)
    assert orfas == [], f"classes citadas e sem regra na folha: {orfas}"
