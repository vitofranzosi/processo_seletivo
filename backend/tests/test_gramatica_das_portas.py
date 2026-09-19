"""A gramática das portas de autorização, afirmada por varredura (033, SC-165, SC-166, FR-481).

**Por que não basta testar caso a caso.** Os casos de `tests/authorization/` prendem o que existe
hoje: cada um nomeia uma porta, um ator e um status. Uma porta escrita **amanhã**, com a gramática
antiga, não quebra nenhum deles — e o critério passa a valer para o dia em que foi conferido, e não
para os seguintes. Foi exatamente assim que quatro portas improvisaram o mesmo `raise Http404` sem
que nada acusasse.

**A âncora é o inventário**, e não uma lista escrita aqui. Isso é o **inverso** da escolha de
`test_vocabulario_da_composicao.py`, que usa lista literal e diz por quê no próprio comentário —
*"uma lista calculada passaria a ignorar a tela que deixasse de usar o termo"*. Para o problema
daquele teste, lista literal está certa: o risco é a tela **sumir** da lista. Aqui o risco é o
oposto — o que precisa ser detectado é a porta que **aparece depois**, e lista literal nunca a vê.

O custo é real, e é o ponto: todo `raise Http404` novo em `interface/views.py` passa a exigir uma
linha no inventário. Quem o escrever tem de dizer se é objeto inexistente, escopo institucional ou
recusa de autorização — que é a decisão que esta feature existe para tornar consciente.
"""

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VIEWS = RAIZ / "processo_seletivo/interface/views.py"
INVENTARIO = RAIZ.parent / "specs/033-navegacao-por-capacidade/inventario-das-negativas.md"

#: As seis portas de autorização da gestão. Literal **e** verificada: o detector abaixo cobre a
#: porta que nascer depois, e esta lista é o que dá nome às que já existem.
PORTAS = (
    "_edital_para_classificar",
    "_edital_para_publicar",
    "_etapa_para_auditar",
    "_etapa_para_distribuir",
    "_peca_para_julgar",
    "_processo_para_gerir",
)

#: O que um `if` que guarda um `raise` menciona quando decide **autorização**, e não existência.
SINAIS_DE_AUTORIZACAO = ("pode_gerir_comissao", "pode_auditar", "pode_ver_a_classificacao", ".can(")

_FONTE = VIEWS.read_text()
_ARVORE = ast.parse(_FONTE)
_LINHAS = _FONTE.splitlines()


def _funcoes():
    return {
        no.name: no
        for no in ast.walk(_ARVORE)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _pais():
    pais = {}
    for no in ast.walk(_ARVORE):
        for filho in ast.iter_child_nodes(no):
            pais[filho] = no
    return pais


def _e_http404(no):
    return (
        isinstance(no, ast.Raise)
        and no.exc is not None
        and (
            (isinstance(no.exc, ast.Name) and no.exc.id == "Http404")
            or (isinstance(no.exc, ast.Call) and getattr(no.exc.func, "id", "") == "Http404")
        )
    )


def _raises_de(funcao):
    return [no for no in ast.walk(funcao) if _e_http404(no)]


def _guarda(no, pais):
    atual = pais.get(no)
    while atual is not None:
        if isinstance(atual, ast.If):
            return " ".join(_LINHAS[atual.test.lineno - 1 : atual.test.end_lineno])
        if isinstance(atual, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return ""
        atual = pais.get(atual)
    return ""


def test_nenhuma_porta_responde_inexistente_para_recusa_de_autorizacao():
    """`SC-165`: "não encontrado" fica com o que não existe e com a outra unidade.

    A varredura não lê status: lê **o que o `if` pergunta**. Um `raise Http404` guardado por uma
    condição que consulta base ou capacidade é recusa de autorização vestida de inexistência, e é
    a forma exata do defeito que esta feature corrigiu em quatro lugares.
    """
    pais = _pais()
    funcoes = _funcoes()
    vestidas = []
    for nome in PORTAS:
        for no in _raises_de(funcoes[nome]):
            guarda = _guarda(no, pais)
            if any(sinal in guarda for sinal in SINAIS_DE_AUTORIZACAO):
                vestidas.append(f"{nome}:{no.lineno} — if {guarda.strip()}")

    assert vestidas == [], (
        "porta responde 'não encontrado' a recusa de autorização:\n  " + "\n  ".join(vestidas)
    )


def test_toda_porta_decide_a_autorizacao_pelo_ponto_unico():
    """`SC-166` e `FR-481`: a recusa nomeia o que falta, e é um lugar só que sabe nomeá-lo.

    Uma porta que decida autorização por conta própria pode até responder 403 — e ainda assim
    devolver a frase muda que a `033` foi escrever. Foi a **ausência** de um ponto único que
    produziu quatro improvisos idênticos; criar o ponto e deixar uma porta fora reproduziria o
    problema com uma porta em vez de quatro.
    """
    funcoes = _funcoes()
    sem_ponto_unico = [
        nome
        for nome in PORTAS
        if not re.search(
            r"require_authorization_base|require_permission",
            "\n".join(_LINHAS[funcoes[nome].lineno - 1 : funcoes[nome].end_lineno]),
        )
    ]

    assert sem_ponto_unico == [], (
        f"portas que decidem autorização fora do ponto único: {sem_ponto_unico}"
    )


def test_toda_porta_filtra_o_escopo_na_propria_consulta():
    """`FR-487`: o que protege o escopo não é a ordem de avaliação — é o filtro.

    A porta da divulgação avalia capacidade **antes** do escopo e não vaza, porque quem não tem a
    capacidade recebe a mesma resposta para tudo. O que vazaria é buscar o objeto **sem** filtrar
    e decidir depois: aí objeto de outra unidade deixaria de ser indistinguível de inexistente.
    Nenhuma porta faz isso hoje, e é isso que esta asserção prende.
    """
    funcoes = _funcoes()
    sem_filtro = []
    for nome in PORTAS:
        corpo = "\n".join(_LINHAS[funcoes[nome].lineno - 1 : funcoes[nome].end_lineno])
        # `_processo_para_gerir` e `_peca_para_julgar` delegam a busca; o filtro mora no helper,
        # e por isso o nome dele também conta como evidência.
        if not re.search(r"institution_scope|_processo_do_ator|obter_edital", corpo):
            sem_filtro.append(nome)

    assert sem_filtro == [], (
        f"porta busca o objeto sem filtrar por escopo institucional: {sem_filtro} — é a única "
        "ordem que vaza a existência de Editais de outras unidades"
    )


# ---------------------------------------------------------------------------
# O detector de novidade — o que faz o critério valer amanhã, e não só no dia em que foi conferido.
# ---------------------------------------------------------------------------

_LINHA_DO_INVENTARIO = re.compile(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|")


def _funcoes_registradas():
    """As funções que o inventário de T003 classificou, lidas da tabela dele."""
    return {
        achado.group(1)
        for linha in INVENTARIO.read_text().splitlines()
        if (achado := _LINHA_DO_INVENTARIO.match(linha))
    }


def _funcoes_que_recusam():
    pais = _pais()
    encontradas = set()
    for no in ast.walk(_ARVORE):
        if not _e_http404(no):
            continue
        atual = pais.get(no)
        while atual is not None and not isinstance(atual, (ast.FunctionDef, ast.AsyncFunctionDef)):
            atual = pais.get(atual)
        encontradas.add(atual.name if atual is not None else "(módulo)")
    return encontradas


def test_o_inventario_cobre_toda_funcao_que_responde_inexistente():
    """Toda negativa nova tem de ser classificada por quem a escreveu.

    **É o que faltava para o critério sobreviver à próxima feature.** Sem isto, uma porta escrita
    depois nasce com a gramática antiga e nenhum teste reclama: os casos existentes falam das
    portas que já existiam, e a suíte fica verde sobre um defeito novo.

    A comparação é por **função**, e não por linha: linha muda a cada edição, e um detector que
    quebrasse a cada refatoração seria desligado na terceira vez. Um `raise Http404` a mais numa
    função já classificada não acorda ninguém; um numa função que o inventário não conhece
    reprova, e obriga quem o escreveu a dizer o que ele é.
    """
    novas = sorted(_funcoes_que_recusam() - _funcoes_registradas())

    assert novas == [], (
        "estas funções respondem 'não encontrado' e não estão no inventário das negativas:\n  "
        + "\n  ".join(novas)
        + "\n\nClassifique cada uma em "
        "`specs/033-navegacao-por-capacidade/inventario-das-negativas.md` como objeto "
        "inexistente, escopo institucional ou recusa de autorização. Se for a terceira, a "
        "gramática dela é a recusa explicada — e não o 404."
    )


def test_a_varredura_reconhece_uma_negativa_nao_registrada():
    """Quem verifica que o detector ainda enxerga.

    Sem este caso, um erro no `regex` do inventário faria `_funcoes_registradas` devolver o
    conjunto vazio ou o universo, e o detector acima passaria para sempre — em silêncio, que é a
    única maneira de uma varredura falhar.
    """
    registradas = _funcoes_registradas()

    assert len(registradas) > 30, (
        f"o inventário rendeu {len(registradas)} funções; a tabela dele não está sendo lida"
    )
    assert "_etapa_para_distribuir" in registradas
    assert "uma_porta_que_nao_existe" not in registradas


# ---------------------------------------------------------------------------
# A formulação — que é coisa diferente da taxonomia, e só ela fecha a `FR-486`.
# ---------------------------------------------------------------------------

TEMPLATES = RAIZ / "processo_seletivo/interface/templates/interface"

#: A formulação canônica, a que `detalhe.html` já praticava antes desta feature em *"Peça a alguém
#: com a permissão de publicar que conclua o ato"*.
#:
#: O que ela prende é **como o destinatário é nomeado**, e não a frase inteira: entre o verbo e o
#: destinatário cabe o objeto do pedido — *"Peça **acesso** a quem administra o sistema"* —, e
#: exigir a frase literal transformaria a `FR-486` numa proibição de dizer o que se pede.
CANONICA = re.compile(r"(a alguém com a permissão de|a quem|à |ao )")

#: As segundas redações para a mesma coisa. Cada uma é plausível e educada, e é justamente por
#: isso que elas entram sem que ninguém repare — e aí o produto passa a ter duas gramáticas para o
#: mesmo ato de pedir.
SEGUNDAS_REDACOES = ("Solicite ", "Entre em contato", "Contate ", "Procure o setor")


def _telas_que_instruem_a_pedir():
    return [
        caminho
        for caminho in sorted(TEMPLATES.glob("*.html"))
        if "Peça "
        in re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
            "",
            caminho.read_text(),
            flags=re.DOTALL,
        )
    ]


def test_toda_tela_que_manda_pedir_usa_a_formulacao_canonica():
    """`FR-486`: uma maneira de dizer isto, e não duas.

    **Verificar a taxonomia e verificar a formulação são coisas diferentes**, e as varreduras
    acima não cobrem esta: uma recusa pode responder o status certo, nomear a base certa e ainda
    assim inventar uma segunda redação — e aí o produto ganha duas gramáticas para o mesmo ato de
    pedir, que é o defeito que esta feature existe para não criar.

    Comentário não é afirmação, como nos irmãos desta pasta: a varredura lê o template sem
    `{% comment %}`. Sem isso, a prosa que **explica** a regra seria cobrada por ela.
    """
    telas = _telas_que_instruem_a_pedir()

    assert telas, "nenhuma tela instrui a pedir — a varredura deixou de enxergar"
    fora_do_padrao = []
    for caminho in telas:
        visivel = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
            "",
            caminho.read_text(),
            flags=re.DOTALL,
        )
        # O espaço é normalizado antes de casar: a frase canônica de `detalhe.html` ocupa duas
        # linhas do template, e uma varredura que lesse a quebra literal reprovaria justamente o
        # texto que serve de padrão para todas as outras.
        for trecho in re.findall(r"Peça [^.<]{0,80}", re.sub(r"\s+", " ", visivel)):
            if not CANONICA.search(trecho):
                fora_do_padrao.append(f"{caminho.name}: {trecho.strip()}")

    assert fora_do_padrao == [], "segunda formulação para 'a quem pedir':\n  " + "\n  ".join(
        fora_do_padrao
    )


def test_nenhuma_tela_inventa_uma_segunda_redacao():
    """O outro lado da `FR-486`: não basta que o que existe siga o padrão.

    A varredura acima só olha o que já começa com "Peça". Uma tela que dissesse "Solicite ao
    setor competente" passaria por ela intocada — a frase existe, resolve o mesmo problema, e
    nenhum caso a encontra.
    """
    encontradas = []
    for caminho in sorted(TEMPLATES.glob("*.html")):
        visivel = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
            "",
            caminho.read_text(),
            flags=re.DOTALL,
        )
        for expressao in SEGUNDAS_REDACOES:
            if expressao in visivel:
                encontradas.append(f"{caminho.name}: {expressao!r}")

    assert encontradas == [], "segunda gramática para o ato de pedir:\n  " + "\n  ".join(
        encontradas
    )


# ---------------------------------------------------------------------------
# 037 · as frases que **não** moram no template, e que a varredura acima não vê
# ---------------------------------------------------------------------------
#
# As duas varreduras acima leem o HTML. As conduções da `037` são produzidas em Python e chegam ao
# template como variável — de propósito, porque é isso que a `FR-543` significa: *usar o
# mecanismo*, e não *imitar o texto*. O efeito colateral é que elas passariam pelas duas sem serem
# olhadas, e a guarda ficaria com um buraco do tamanho da feature que ela acabou de admitir.


def _conducoes_produzidas():
    """As frases que as telas da `037` imprimem, pedidas a quem as produz.

    Importadas de `views`, e não recopiadas: uma cópia aqui seria a segunda redação que este
    arquivo inteiro existe para impedir, escrita dentro do guardião.
    """
    from processo_seletivo.interface.views import CONDUCAO_DA_COMPOSICAO, CONDUCAO_DA_RETIFICACAO

    return {
        "condução da Retificação": CONDUCAO_DA_RETIFICACAO,
        "condução da composição": CONDUCAO_DA_COMPOSICAO,
    }


def test_as_conducoes_produzidas_seguem_a_formulacao_canonica():
    """`FR-543` e `FR-543a`: a formulação continua única, e as frases novas passam por ela.

    O mesmo `CANONICA` que julga os templates, aplicado ao que o mecanismo devolve. E a forma é a
    **cheia**: entre o destinatário e o ponto final há a oração do ato, que é o que distingue
    *"peça a alguém com a permissão de X"* de *"peça a alguém com a permissão de X **que Y**"*.
    """
    for nome, frase in _conducoes_produzidas().items():
        trechos = re.findall(r"Peça [^.<]{0,80}", re.sub(r"\s+", " ", frase))

        assert trechos, f"{nome}: não instrui a pedir"
        for trecho in trechos:
            assert CANONICA.search(trecho), f"{nome}: segunda formulação — {trecho.strip()!r}"
            assert " que " in trecho, f"{nome}: sem a oração do ato (FR-543a) — {trecho.strip()!r}"


def test_nenhuma_conducao_produzida_inventa_uma_segunda_redacao():
    """O outro lado, aplicado ao que não está no template — irmão do caso acima."""
    for nome, frase in _conducoes_produzidas().items():
        for expressao in SEGUNDAS_REDACOES:
            assert expressao not in frase, f"{nome}: segunda gramática — {expressao!r}"


def test_nenhuma_conducao_produzida_nomeia_pessoa():
    """`FR-543b`: a permissão, e nunca alguém.

    Não há fila, designação nem nome próprio — é a disciplina que o produto já mantém, e que a
    `FR-485` registrou ao recusar mandar pedir "o papel de presidente", que não existe. O que se
    cobra aqui é a forma do destinatário: ele é sempre uma **capacidade** ou um **vínculo**, nunca
    um cargo nominal nem um setor.
    """
    for nome, frase in _conducoes_produzidas().items():
        assert re.search(r"Peça (a alguém com a permissão de|a quem|à |ao )", frase), (
            f"{nome}: o destinatário não é uma permissão nem um vínculo"
        )
