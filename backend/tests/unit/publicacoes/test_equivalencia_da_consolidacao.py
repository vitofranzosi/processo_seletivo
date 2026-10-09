"""068 — A prova de que nenhuma regra se perdeu: cada Perfil continua com toda a regra que tinha.

FR-1353 e SC-513. Para cada Perfil, as **unidades normativas** que o documento lhe aplica — cada
requisito, cada parágrafo de atribuições, o texto dos marcos, cada linha do quadro de vagas, cada
linha da tabela de modalidades, cada frase de reversão e de convocação, a descrição, os dados
exigidos, a remuneração — são comparadas como multiconjunto:

- **antes**: o bloco que o Perfil imprimia. Ele é composto pelo caminho do Edital de um Perfil só,
  que esta feature não toca (FR-1356, provado byte a byte pela fixture de contrato) e que usa as
  mesmas funções do bloco de antes; nos cenários da auditoria, o texto desse "antes" é conferido
  contra os PDFs que a `067` gravou (`specs/067-…/demonstracao/`), que são a `main` de antes;
- **depois**: o que se reconstrói **lendo só o documento consolidado** — o bloco do Perfil, a
  subseção a que ele remete (sem o título e sem a frase do FR-1347), a linha dele na tabela de
  vagas (cada célula volta a ser "Denominação (CÓDIGO): número", pela tabela de modalidades), a
  tabela de modalidades do grupo dele, as frases que o nomeiam ou valem para todos, e as linhas do
  método comum, seguindo a remissão.

O multiconjunto pega a frase perdida, a duplicada e a de outro Perfil. O que muda de propósito —
recuo, posição, número da tabela, a ordem das linhas de modalidades (ED-11) — não entra na unidade.
"""

import copy
import re
from collections import Counter

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes import test_consolidacao_por_perfil as cenarios
from tests.unit.publicacoes.cenarios_da_auditoria import congelado
from tests.unit.publicacoes.test_documento_da_auditoria_depois_da_067 import RODAPE
from tests.unit.publicacoes.test_pdf import texto_de

SECAO = 5
ROTULOS_DE_IDENTIFICACAO = ("Localidade:", "Vagas imediatas:", "Cadastro reserva:")

# ---------------------------------------------------------------------------
# Leitura estruturada da composição
# ---------------------------------------------------------------------------


def _normal(texto):
    return " ".join(str(texto).split())


def _tokens(itens):
    """Linhas e tabelas, na ordem: `("t", texto, fonte, recuo, antes)` e `("tab", legenda, linhas)`.

    A tabela é lida pela grade: cada célula vai à coluna cujas bordas contêm a posição dela, e as
    linhas que uma célula ocupa se juntam. A legenda são as linhas em negrito logo acima, a partir
    da que começa por "Tabela ".
    """
    tokens, indice = [], 0
    while indice < len(itens):
        item = itens[indice]
        if item[0] == "texto" and item[1]:
            _, texto, fonte, _tamanho, recuo, antes, *_ = item
            tokens.append(("t", texto, fonte, recuo, antes))
        elif item[0] == "abre_tabela":
            bordas = item[1]
            legenda = []
            while tokens and tokens[-1][0] == "t" and tokens[-1][2] == pdf.NEGRITO:
                legenda.insert(0, tokens.pop()[1])
                if legenda[0].startswith("Tabela "):
                    break
            linhas, atual, profundidade = [], None, 1
            indice += 1
            while profundidade:
                dentro = itens[indice]
                if dentro[0] in ("abre", "abre_tabela"):
                    profundidade += 1
                elif dentro[0] == "fecha":
                    profundidade -= 1
                elif dentro[0] == "abre_linha":
                    atual = [""] * (len(bordas) - 1)
                elif dentro[0] == "fecha_linha":
                    linhas.append([_normal(celula) for celula in atual])
                elif dentro[0] == "texto" and dentro[1]:
                    x = pdf.MARGEM + dentro[4]
                    coluna = max(c for c in range(len(bordas) - 1) if bordas[c] <= x + 0.01)
                    atual[coluna] = f"{atual[coluna]} {dentro[1]}"
                indice += 1
            tokens.append(("tab", _normal(" ".join(legenda)), linhas))
            continue
        indice += 1
    return tokens


def _composicao_da_secao(conteudo):
    composicao = pdf.Composicao()
    pdf._perfis(composicao, pdf._grafado(conteudo, previa=False), SECAO, pdf._Numerador())
    return _tokens(composicao.itens)


TITULO = re.compile(rf"^{SECAO}\.(\d+) ")


def _segmentos(tokens):
    """`(pré, [(título, corpo)])`: o que vem antes do primeiro N.k, e cada subseção N.k."""
    pre, segmentos = [], []
    for token in tokens:
        e_titulo = (
            token[0] == "t" and token[2] == pdf.NEGRITO and token[3] == 0 and TITULO.match(token[1])
        )
        continua_titulo = (
            token[0] == "t"
            and token[2] == pdf.NEGRITO
            and token[3] == 0
            and segmentos
            and not segmentos[-1][1]
        )
        if e_titulo:
            segmentos.append([token[1], []])
        elif continua_titulo:
            segmentos[-1][0] = f"{segmentos[-1][0]} {token[1]}"
        elif segmentos:
            segmentos[-1][1].append(token)
        else:
            pre.append(token)
    return pre, [(titulo, corpo) for titulo, corpo in segmentos]


def _paragrafos(linhas):
    """Linhas de texto em parágrafos: começa um novo a cada linha com espaço acima."""
    paragrafos = []
    for token in linhas:
        if not paragrafos or token[4] > 0:
            paragrafos.append(token[1])
        else:
            paragrafos[-1] = f"{paragrafos[-1]} {token[1]}"
    return [_normal(paragrafo) for paragrafo in paragrafos]


def _itens_com_marcador(linhas):
    itens = []
    for token in linhas:
        if token[1].startswith("• ") or not itens:
            itens.append(token[1])
        else:
            itens[-1] = f"{itens[-1]} {token[1]}"
    return [_normal(item) for item in itens]


def _partes(corpo):
    """O corpo de um Perfil por rótulo: `[(rótulo, valor do par ou None, tokens)]`.

    Rótulo é a linha em negrito com recuo 18; o par é o rótulo com dois-pontos seguido do valor na
    mesma linha. O que vem antes do primeiro rótulo é a descrição.
    """
    partes = [("descrição", None, [])]
    indice = 0
    while indice < len(corpo):
        token = corpo[indice]
        if token[0] == "t" and token[2] == pdf.NEGRITO and token[3] == 18:
            if token[1].endswith(":"):
                valor = corpo[indice + 1][1]
                partes.append((token[1][:-1], valor, []))
                indice += 2
                continue
            partes.append((token[1], None, []))
        else:
            partes[-1][2].append(token)
        indice += 1
    return partes


# ---------------------------------------------------------------------------
# As unidades normativas de um Perfil
# ---------------------------------------------------------------------------


def _unidades_do_bloco(corpo, subsecoes, metodo):
    unidades = []
    for rotulo, valor, tokens in _partes(corpo):
        # As linhas de recuo 0 são as frases do Perfil de antes, lidas com as tabelas dele.
        linhas = [token for token in tokens if token[0] == "t" and token[3] != 0]
        remuneracao = [t for t in linhas if t[1].startswith("Remuneração:")]
        unidades += [f"remuneração: {_normal(t[1])}" for t in remuneracao]
        linhas = [
            t for t in linhas if t not in remuneracao and not t[1].startswith("Carga horária:")
        ]
        if rotulo in ("Localidade", "Vagas imediatas", "Cadastro reserva"):
            continue
        if rotulo == "descrição":
            unidades += [f"descrição: {p}" for p in _paragrafos(linhas)]
        elif rotulo == "Atribuições":
            if valor:
                linhas = subsecoes[_item(valor)]
            unidades += [f"atribuição: {p}" for p in _paragrafos(linhas)]
        elif rotulo == "Requisitos":
            if valor:
                linhas = subsecoes[_item(valor)]
            unidades += [f"requisito: {item}" for item in _itens_com_marcador(linhas)]
        elif rotulo == "Dados exigidos na inscrição":
            unidades += [f"dado: {item}" for item in _itens_com_marcador(linhas)]
        elif rotulo.startswith("Marcos classificatórios"):
            if valor:
                texto = _normal(" ".join(t[1] for t in subsecoes[_item(valor)]))
                texto = texto.replace(_normal(pdf.MARCOS_SEPARADAMENTE), "", 1)
            else:
                texto = _normal(" ".join(t[1] for t in linhas))
            unidades.append(f"marcos: {_normal(_metodo_por_extenso(texto, metodo))}")
        else:
            raise AssertionError(f"rótulo inesperado no Perfil: {rotulo!r}")
        unidades += _unidades_das_tabelas(tokens)
    return unidades


def _item(valor):
    return re.search(r"item (\d+\.\d+)", valor)[1]


REMISSAO_DO_METODO = re.compile(r"Método: o comum a este Edital, descrito no item (\d+\.\d+)\.")


def _metodo_por_extenso(texto, metodo):
    """Troca a remissão do método comum pelas linhas que ela aponta (FR-1349)."""
    return REMISSAO_DO_METODO.sub(lambda casada: metodo[casada[1]], texto)


def _linhas_do_metodo(texto):
    inicio = texto.find("Método: comum a este Edital")
    if inicio < 0:
        return None
    fim = texto.find(" Habilitação:", inicio)
    return texto[inicio : fim if fim > 0 else len(texto)]


def _unidades_das_tabelas(tokens):
    """O quadro e a tabela de modalidades de dentro do bloco do Perfil — o "antes"."""
    unidades = []
    for token in tokens:
        if token[0] != "tab":
            continue
        _, legenda, linhas = token
        if "Quadro de vagas" in legenda:
            unidades += [f"vaga: {rotulo}: {numero}" for rotulo, numero in linhas[1:]]
        elif "Modalidades de concorrência" in legenda:
            unidades += [f"modalidade: {' | '.join(linha)}" for linha in linhas[1:]]
        else:
            raise AssertionError(f"tabela inesperada no Perfil: {legenda!r}")
    # As frases do Perfil — reversão e convocação — são as linhas de recuo 0 do bloco.
    frases = [token for token in tokens if token[0] == "t" and token[3] == 0]
    unidades += [f"frase: {p}" for p in _paragrafos(frases)]
    return unidades


def antes(conteudo, codigo):
    """O bloco que o Perfil imprimia, composto pelo caminho do Edital de um Perfil só."""
    sozinho = copy.deepcopy(conteudo)
    sozinho["profiles"] = [p for p in sozinho["profiles"] if p["code"] == codigo]
    _, segmentos = _segmentos(_composicao_da_secao(sozinho))
    ((titulo, corpo),) = segmentos
    return Counter([f"título: {titulo.split(' ', 1)[1]}", *_unidades_do_bloco(corpo, {}, {})])


def _codigos_da_enumeracao(texto, conhecidos):
    """Os códigos no começo de `texto` ("A, B e C, …" ou com aspas) e o que sobra depois."""
    codigos, resto = [], texto
    candidatos = sorted(conhecidos, key=len, reverse=True)
    while True:
        for codigo in candidatos:
            for grafia in (f"“{codigo}”", codigo):
                if resto.startswith(grafia):
                    codigos.append(codigo)
                    resto = resto[len(grafia) :]
                    break
            else:
                continue
            break
        else:
            raise AssertionError(f"enumeração ilegível: {texto!r}")
        if resto.startswith(" e "):
            resto = resto[3:]
            continue
        if resto.startswith(", ") and any(
            resto[2:].startswith(g) for c in candidatos for g in (f"“{c}”", c)
        ):
            resto = resto[2:]
            continue
        return codigos, resto


def depois(conteudo):
    """`{código: Counter}` — o que o documento consolidado aplica a cada Perfil."""
    pre, segmentos = _segmentos(_composicao_da_secao(conteudo))
    perfis = {}
    subsecoes = {}
    for titulo, corpo in segmentos:
        numero = TITULO.match(titulo)[0].strip()
        if " comuns aos Perfis " in titulo:
            subsecoes[numero] = [token for token in corpo if token[0] == "t"]
        else:
            perfis[titulo.split(" ", 1)[1].split(" — ", 1)[0]] = (titulo, corpo)
    conhecidos = list(perfis)
    metodo = {
        numero: linhas
        for numero, tokens in [
            *((n, t) for n, t in subsecoes.items()),
            *((TITULO.match(t)[0].strip(), c) for t, c in perfis.values()),
        ]
        if (linhas := _linhas_do_metodo(_normal(" ".join(x[1] for x in tokens if x[0] == "t"))))
    }

    unidades = {codigo: [] for codigo in conhecidos}
    for codigo, (titulo, corpo) in perfis.items():
        unidades[codigo].append(f"título: {titulo.split(' ', 1)[1]}")
        unidades[codigo] += _unidades_do_bloco(corpo, subsecoes, metodo)

    tabelas = [token for token in pre if token[0] == "tab"]
    modalidades = {}
    for _, legenda, linhas in tabelas:
        if "Modalidades de concorrência" not in legenda:
            continue
        if qualificada := re.search(r" — Perfi[ls] (.+)$", legenda):
            alcance, _ = _codigos_da_enumeracao(qualificada[1], conhecidos)
        else:
            alcance = conhecidos
        for codigo in alcance:
            assert codigo not in modalidades, f"{codigo} em duas tabelas de modalidades"
            modalidades[codigo] = linhas[1:]
            unidades[codigo] += [f"modalidade: {' | '.join(linha)}" for linha in linhas[1:]]

    for _, legenda, linhas in tabelas:
        if "Vagas por lista de concorrência" not in legenda:
            continue
        cabecalho, corpo = linhas[0], linhas[1:]
        if cabecalho[1] == "Lista de concorrência":
            atual = None
            for perfil_, rotulo, numero in corpo:
                atual = perfil_ or atual
                unidades[atual].append(f"vaga: {rotulo}: {numero}")
            continue
        for linha in corpo:
            codigo = linha[0]
            nomes = {
                celula.split(" — ", 1)[0]: celula.split(" — ", 1)[1]
                for celula, *_ in modalidades.get(codigo, [])
            }
            for coluna, numero in zip(cabecalho[1:], linha[1:], strict=True):
                if numero == "—":
                    continue
                rotulo = (
                    coluna
                    if coluna == pdf.AMPLA_CONCORRENCIA
                    else f"{nomes[coluna]} ({coluna})"
                    if coluna in nomes
                    else coluna
                )
                unidades[codigo].append(f"vaga: {rotulo}: {numero}")

    # As frases antes da primeira tabela de modalidades são as da reversão, e valem, sem prefixo,
    # para os Perfis da tabela de vagas (FR-1350); as de depois são as da convocação, e valem, sem
    # prefixo, para todos (FR-1351). O alcance é lido do documento, e não da regra que o compõe.
    com_linha = set()
    for _, legenda, linhas in tabelas:
        if "Vagas por lista de concorrência" in legenda:
            com_linha = {linha[0] for linha in linhas[1:] if linha[0]}
    primeira_de_modalidades = next(
        (i for i, token in enumerate(pre) if token[0] == "tab" and "Modalidades" in token[1]),
        len(pre),
    )
    for trecho, alcance in (
        (pre[:primeira_de_modalidades], [c for c in conhecidos if c in com_linha]),
        (pre[primeira_de_modalidades:], conhecidos),
    ):
        for frase in _paragrafos([token for token in trecho if token[0] == "t" and token[3] == 0]):
            prefixo = re.match(r"^(No Perfil|Nos Perfis) ", frase)
            if not prefixo:
                for codigo in alcance:
                    unidades[codigo].append(f"frase: {frase}")
                continue
            codigos, resto = _codigos_da_enumeracao(frase[prefixo.end() :], conhecidos)
            assert resto.startswith(", "), frase
            texto = f"{resto[2:3].upper()}{resto[3:]}"
            for codigo in codigos:
                unidades[codigo].append(f"frase: {texto}")
    return {codigo: Counter(lista) for codigo, lista in unidades.items()}


def _comparar(conteudo):
    reconstruido = depois(conteudo)
    for perfil in conteudo["profiles"]:
        codigo = perfil["code"]
        obtido, esperado = reconstruido[codigo], antes(conteudo, codigo)
        assert obtido == esperado, (
            codigo,
            "faltam",
            sorted((esperado - obtido).elements()),
            "sobram",
            sorted((obtido - esperado).elements()),
        )


# ---------------------------------------------------------------------------
# Os casos
# ---------------------------------------------------------------------------

P = cenarios.perfil
OUTRO_MARCO = {"marcos": [cenarios.marco("x", name="Sorteio público")]}

CASOS = {
    "todos iguais": lambda: cenarios.cenario_a(),
    "um marco diferente": lambda: cenarios.cenario_a(**{"INF-VAL": OUTRO_MARCO}),
    "dois grupos de marcos pelo método comum": lambda: cenarios.cenario_a(
        **{"INF-SMT": OUTRO_MARCO, "INF-VAL": OUTRO_MARCO}
    ),
    "primeiro Perfil com marco próprio": lambda: cenarios.cenario_a(**{"INF-BJN": OUTRO_MARCO}),
    "requisitos diferentes": lambda: cenarios.cenario_a(
        **{"INF-IUN": {"requisitos": (*cenarios.REQUISITOS, "Residir no polo")}}
    ),
    "reversões e convocações diferentes": lambda: cenarios.cenario_a(
        **{
            "INF-SMT": {"reversao": "ON_BALANCE", "convocacao": "INDIVIDUAL_MESSAGE"},
            "INF-VAL": {"reversao": None, "convocacao": None},
        }
    ),
    "modalidades diferentes": lambda: cenarios.cenario_a(
        **{"INF-VAL": {"percentuais": {"PPI": "30.0000"}}}
    ),
    "lista que só um declara": lambda: cenarios.cenario_a(
        **{
            "INF-IUN": {
                "vagas": (27, 10, 2, 1),
                "quadro": ("PPI", "PcD", "PTT"),
                "modalidades": ("PTT", "PcD", "PPI"),
            }
        }
    ),
    "sem vaga imediata e sem quadro": lambda: cenarios.cenario_a(
        **{"INF-IUN": {"vagas": (0, 0, 0)}, "INF-SMT": {"vagas": None, "reversao": None}}
    ),
    "atribuições comuns e próprias": lambda: cenarios.cenario_a(
        **{
            "INF-BJN": {"atribuicoes": "Mediar.\nAcompanhar."},
            "INF-IUN": {"atribuicoes": "Mediar.\nAcompanhar."},
            "INF-SMT": {"atribuicoes": "Corrigir."},
        }
    ),
    "método próprio idêntico": lambda: cenarios.cenario_a(
        **{
            c: {"marcos": [cenarios.marco(c, drawMethod={**cenarios.METODO, "occurrence": "X"})]}
            for c in cenarios.QUATRO
        }
    ),
    "cenário A da auditoria": lambda: congelado("A")["content"],
    "cenário B da auditoria": lambda: congelado("B")["content"],
}


@pytest.mark.parametrize("caso", sorted(CASOS))
def test_cada_perfil_tem_depois_exatamente_a_regra_que_tinha_antes(caso):
    _comparar(CASOS[caso]())


def test_a_leitura_pega_a_regra_que_se_perdesse(monkeypatch):
    """A prova reprova o defeito que ela existe para pegar: um requisito a menos na subseção."""
    original = pdf._requisitos_comuns

    def sem_o_ultimo(composicao, grupo, numero):
        truncado = [{**grupo[0], "requirements": grupo[0]["requirements"][:-1]}, *grupo[1:]]
        original(composicao, truncado, numero)

    monkeypatch.setattr(pdf, "_requisitos_comuns", sem_o_ultimo)
    with pytest.raises(AssertionError, match="faltam"):
        _comparar(cenarios.cenario_a())


def test_a_leitura_pega_a_frase_que_alcancasse_outro_perfil(monkeypatch):
    """E a frase sem prefixo que valesse para quem não a declarou."""
    monkeypatch.setattr(
        pdf,
        "_frases_da_convocacao",
        lambda perfis: (pdf.FraseConsolidada(cenarios.CONVOCACAO_PUBLICACAO),),
    )
    with pytest.raises(AssertionError, match="sobram"):
        _comparar(cenarios.cenario_a(**{"INF-VAL": {"convocacao": None}}))


# ---------------------------------------------------------------------------
# O "antes" dos cenários da auditoria é o dos PDFs da 067
# ---------------------------------------------------------------------------

DEMONSTRACAO_067 = (
    pdf.__file__.rsplit("/backend/", 1)[0] + "/specs/067-correcoes-de-norma-do-edital/demonstracao"
)


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_o_antes_reconstruido_e_o_que_o_pdf_da_067_imprimia(cenario):
    """Cada unidade de texto corrido do "antes" está, como texto, no PDF que a `067` gravou.

    As unidades de tabela ficam de fora: no texto do PDF, a célula que quebra em duas linhas se
    intercala com as vizinhas. As de tabela são provadas pelo número de linhas e pelo conteúdo
    das células, que não mudaram de função.
    """
    with open(f"{DEMONSTRACAO_067}/{cenario}-publicado-067.pdf", "rb") as arquivo:
        impresso = RODAPE.sub("", _normal(texto_de(arquivo.read())))
    conteudo = congelado(cenario)["content"]
    for perfil in conteudo["profiles"]:
        for unidade in antes(conteudo, perfil["code"]):
            tipo, texto = unidade.split(": ", 1)
            if tipo in ("vaga", "modalidade", "título"):
                continue
            assert texto in impresso, (perfil["code"], unidade)
