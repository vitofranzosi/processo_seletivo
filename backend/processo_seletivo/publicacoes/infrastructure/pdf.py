"""Renderizador do documento publicado (FR-023).

O PDF é derivado exclusivamente do snapshot homologado: Perfis, vagas, Cadastro Reserva,
modalidades, Regra Normativa e Cronograma são impressos como estão na versão, sem consultar
o banco. A cadeia "dados estruturados → versão homologada → PDF publicado" fica demonstrável
porque o mesmo snapshot sempre produz os mesmos bytes, e o hash do conteúdo aparece no
documento.

Sem dependência externa. O texto usa `WinAnsiEncoding`, que cobre o português — a versão
anterior codificava em ASCII e destruía todo acento de um documento oficial brasileiro. O que o
WinAnsi não cobre é normalizado ou recusado por `publicacoes.domain.grafia`, e nunca trocado por
`?` em silêncio no Edital (`doc/achado-documento-troca-caractere-por-interrogacao.md`).
"""

import re
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import quote

from django.utils import timezone

# Apelidado, e não importado como `marcos`: dentro de `_marcos` a variável local com esse nome é
# a lista de marcos do Perfil, e o módulo ficaria sombreado justamente na função que precisa dele.
from processo_seletivo.editais.domain import marcos as regras_do_marco
from processo_seletivo.editais.domain import quadro as quadro_do_perfil
from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.editais.domain.documentos import denominacao_do_codigo
from processo_seletivo.editais.domain.perfis import CAMPOS_DO_METODO
from processo_seletivo.editais.domain.secoes import GERADA
from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    ETAPA_NAO_IDENTIFICADA,
    REDACAO_1,
    REDACAO_2,
    REDACAO_VIGENTE,
    criterio_com_a_ausencia,
    frase_da_convocacao,
    inicial_minuscula,
    por_identificador,
)
from processo_seletivo.publicacoes.infrastructure import brasao, humano
from processo_seletivo.publicacoes.infrastructure import fonte as fonte_do_edital

LARGURA, ALTURA = 595, 842  # A4 em pontos
MARGEM = 56
TOPO = ALTURA - 64
RODAPE = 56

REGULAR, NEGRITO = "F1", "F2"
NOME_DO_BRASAO = "Im1"

# Larguras em milésimos de em, para ASCII 32 a 126, na ordem do código (`008`, D-001).
#
# São as métricas das fontes base-14, que são fixas e não dependem de instalação — a mesma razão
# pela qual o documento pode declarar Helvetica sem embutir arquivo de fonte. Antes desta feature a
# quebra contava **caracteres** e multiplicava por um fator médio de 0,52: conservador o bastante
# para refluir parágrafo, e inservível para centralizar um cabeçalho ou alinhar uma coluna.
_ASCII_REGULAR = (
    278,
    278,
    355,
    556,
    556,
    889,
    667,
    191,
    333,
    333,
    389,
    584,
    278,
    333,
    278,
    278,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    278,
    278,
    584,
    584,
    584,
    556,
    1015,
    667,
    667,
    722,
    722,
    667,
    611,
    778,
    722,
    278,
    500,
    667,
    556,
    833,
    722,
    778,
    667,
    778,
    722,
    667,
    611,
    722,
    667,
    944,
    667,
    667,
    611,
    278,
    278,
    278,
    469,
    556,
    333,
    556,
    556,
    500,
    556,
    556,
    278,
    556,
    556,
    222,
    222,
    500,
    222,
    833,
    556,
    556,
    556,
    556,
    333,
    500,
    278,
    556,
    500,
    722,
    500,
    500,
    500,
    334,
    260,
    334,
    584,
)
_ASCII_NEGRITO = (
    278,
    333,
    474,
    556,
    556,
    889,
    722,
    238,
    333,
    333,
    389,
    584,
    278,
    333,
    278,
    278,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    556,
    333,
    333,
    584,
    584,
    584,
    611,
    975,
    722,
    722,
    722,
    722,
    667,
    611,
    778,
    722,
    278,
    556,
    722,
    611,
    833,
    722,
    778,
    667,
    778,
    722,
    667,
    611,
    722,
    667,
    944,
    667,
    667,
    611,
    333,
    278,
    333,
    584,
    556,
    333,
    556,
    611,
    556,
    611,
    556,
    333,
    611,
    611,
    278,
    278,
    556,
    278,
    889,
    611,
    611,
    611,
    611,
    389,
    556,
    333,
    611,
    556,
    778,
    556,
    556,
    500,
    389,
    280,
    389,
    584,
)

# Em Helvetica o glifo acentuado é composto e **tem o avanço da letra-base**. Derivar daí, em vez
# de transcrever uma segunda tabela, elimina a classe inteira de erro de transcrição — e é o que
# permite medir português sem tabela paralela.
_BASE_ACENTUADA = str.maketrans(
    "ÀÁÂÃÄÅÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÝÑÇàáâãäåèéêëìíîïòóôõöùúûüýÿñç",
    "AAAAAAEEEEIIIIOOOOOUUUUYNCaaaaaaeeeeiiiiooooouuuuyync",
)

# O punhado de sinais que o documento usa e que não são letras nem ASCII.
_SINAIS = {
    "—": (1000, 1000),
    "–": (556, 556),
    "·": (278, 278),
    "•": (350, 350),
    "§": (556, 556),
    "°": (400, 400),
    "º": (365, 330),
    "ª": (370, 300),
    "“": (333, 500),
    "”": (333, 500),
    "‘": (222, 278),
    "’": (222, 278),
}

# Um caractere fora da tabela é medido como o glifo mais largo possível. É deliberadamente
# conservador: erra fazendo a linha quebrar cedo, nunca fazendo-a estourar a margem — que é o
# único dos dois erros que aparece no documento impresso.
_LARGURA_DESCONHECIDA = 1000


def largura(texto: str, tamanho: float, fonte: str = REGULAR) -> float:
    """A largura que `texto` ocupa, em pontos, quando desenhado naquele corpo (FR-002)."""
    tabela = _ASCII_NEGRITO if fonte == NEGRITO else _ASCII_REGULAR
    indice = 1 if fonte == NEGRITO else 0
    total = 0
    # Mede-se o que vai ser desenhado: sem normalizar, um espaço de largura zero colado do Word
    # contava como o glifo mais largo, e a linha quebrava cedo por causa de um caractere que some.
    for caractere in grafia.normalizar(texto):
        base = caractere.translate(_BASE_ACENTUADA)
        codigo = ord(base)
        if 32 <= codigo <= 126:
            total += tabela[codigo - 32]
        elif caractere in _SINAIS:
            total += _SINAIS[caractere][indice]
        else:
            total += _LARGURA_DESCONHECIDA
    return total * tamanho / 1000


class Metrica:
    """Como a composição mede o texto — a Helvetica de hoje, salvo quando outra é dada (069, R-005).

    **Da composição, e não do módulo.** O Edital passa a embutir a fonte e a medir pelas larguras
    dela, e o comprovante e a divulgação continuam com a Helvetica, byte a byte (FR-1383): as duas
    medidas só convivem se cada composição carregar a sua. Uma função global trocada pelo Edital
    mudaria, na mesma chamada, a quebra de linha de todo comprovante emitido depois.
    """

    def largura(self, texto: str, tamanho: float, fonte: str = REGULAR) -> float:
        return largura(texto, tamanho, fonte)


HELVETICA = Metrica()


# Os níveis tipográficos do documento, e apenas estes (FR-009). Nomeá-los é o que impede que a
# hierarquia volte a ser um punhado de números literais espalhados pela composição.
# Calibrados contra os Editais 62/2026, 73/2026 e 146/2025 do Cefor. A identificação do órgão é
# o **maior** texto da página — não o ato —, e os títulos de seção são negrito no mesmo corpo do
# texto, não corpo maior: num Edital a hierarquia vem do peso, e um título grande denuncia
# relatório. A primeira redação tinha isto exatamente ao contrário.
CORPO_INSTITUCIONAL = 13.0
CORPO_ATO = 12.0
CORPO_SECAO = 11.0
CORPO_BLOCO = 10.5
CORPO_TEXTO = 10.5
# A tabela usa corpo menor que o texto: ela é consulta, não leitura corrida, e um pouco menos de
# corpo é o que permite à coluna caber sem apertar a célula.
CORPO_TABELA = 9.5
CORPO_NOTA = 7.5
# **A hierarquia da `069`** (FR-1382): o título de seção ganha corpo e um fio abaixo, e a subseção
# um corpo próprio. A calibração da `008` — título no corpo do texto, a hierarquia pelo peso — dava
# título e parágrafo quase iguais num documento longo, e a auditoria de 08/10 o apontou (ED-16 e o
# teste heurístico). `CORPO_SECAO` continua o de antes: é o do comprovante e da divulgação, que não
# mudam (FR-1383).
CORPO_TITULO_DE_SECAO = 12.5
CORPO_SUBSECAO = 11.0
# O fundo do bloco destacado: o resumo, os dados do sorteio e a declaração (FR-1382). Mais claro que
# o cinza do cabeçalho de tabela, e só um tom — nenhuma informação depende de cor.
CINZA_DO_DESTAQUE = "0.95"
# Quanto o fio fica abaixo da linha de base do título de seção: o bastante para passar sob as
# descidas dele.
FIO_SOB_O_TITULO = 4.0

ESQUERDA, CENTRO, DIREITA = "esquerda", "centro", "direita"

# A escala de espaço vertical (FR-031). Nomeá-la é o que a torna uma decisão: com números
# literais espalhados pela composição, a distinção entre seção, bloco e parágrafo vira acidente.
# A ordem é o requisito — o leitor distingue os três níveis pelo ar que os separa.
ANTES_DE_SECAO = 20.0
ANTES_DE_BLOCO = 10.0
ANTES_DE_PARAGRAFO = 5.0
ANTES_DE_LINHA = 3.0

# Quanto o contorno de um bloco abre acima da primeira linha (FR-014).
FOLGA_DA_MOLDURA = 6.0
# E quanto ele desce quando um título veio junto na quebra: o fio precisa passar abaixo das
# descidas do título, não rente a elas.
FOLGA_APOS_TITULO = 16.0


# O modo do renderizador (FR-015). Um parâmetro, e não condicionais espalhadas pela composição:
# a diferença entre o que se revisa e o que se publica precisa ter **um** lugar onde está
# declarada, ou os dois documentos divergem sem que nada acuse.
@dataclass(frozen=True)
class AutoridadeSignataria:
    """Quem praticou o ato — nome e cargo, e nada além (FR-033, FR-034).

    **Não é assinatura**: esta feature não constrói certificado, imagem nem ICP (FR-037). É a
    representação documental da autoridade que a Publicação já registrou.

    Chega ao compositor como contexto do ato, separado do conteúdo publicado. Não entra no
    snapshot: o corpo normativo continua função pura do conteúdo homologado, e a autoridade é o
    único elemento derivado de metadado do ato. Nos dois fluxos de publicação o documento é
    composto **antes** de a `Publicacao` existir — não há o que consultar mesmo que se quisesse.
    """

    nome: str
    cargo: str
    # O ato de nomeação (054, FR-991), vazio quando a Publicação não o registrou.
    ato_de_nomeacao: str = ""


@dataclass(frozen=True)
class UnidadeDoAto:
    """A unidade que pratica o ato, como o documento a diz — o cabeçalho e o local (060, FR-1112).

    Contexto do ato, como a autoridade: não entra no snapshot, e o hash do conteúdo não muda por
    ela. Até a 060 eram as constantes `ORGAO` e `LOCAL`, e todo documento dizia o Cefor — inclusive
    o de um Edital de campus. **Obrigatória nos dois modos**, porque a prévia também imprime o
    cabeçalho, e **sem valor padrão**: um padrão seria o Cefor de novo, escondido num argumento.
    """

    # As linhas da unidade abaixo de `INSTITUICAO`, uma ou duas, na quebra em que foram registradas.
    cabecalho: tuple[str, ...]
    # O local do fecho — *"Vitória (ES)"*. Só o documento publicado o imprime.
    local: str
    # A sigla da unidade — "Cefor" —, que o anúncio em caixa alta preserva como foi registrada
    # (069, FR-1377) e o título do arquivo nomeia como autor (FR-1384). Vazia onde quem compõe não
    # a tem: o anúncio preserva então só a sigla da instituição e as palavras de caixa mista.
    sigla: str = ""


@dataclass(frozen=True)
class Consolidacao:
    """As datas que o documento de uma Retificação declara abaixo do anúncio (054, FR-995).

    Contexto do ato, como a autoridade e a data: não entra no snapshot, e o hash do conteúdo não
    muda por elas. `retificado_em` traz uma data por Retificação que o documento incorpora, esta
    inclusive, na ordem; `vigencia` só quando a desta começa em outro dia que o da publicação.
    """

    publicado_em: date
    retificado_em: tuple
    vigencia: date | None = None


MODO_PUBLICADO = "PUBLISHED"
MODO_PREVIA = "PREVIEW"
MODOS = (MODO_PUBLICADO, MODO_PREVIA)

MARCA_DE_PREVIA = "PRÉVIA — documento em elaboração, sem valor de publicação"
# A marca vive **fora** do fluxo normativo, numa faixa fixa acima da área útil (`008`, D-011).
# Escrita dentro do fluxo, ela empurrava todo o conteúdo e fazia a prévia quebrar em páginas
# diferentes daquelas em que o documento seria publicado — quem revisava a prévia revisava uma
# paginação que não era a que sai. Fora do fluxo, a igualdade das quebras é garantida por
# construção (FR-042), e a marca passa a aparecer em **todas** as páginas, e não só na primeira.
FAIXA_DE_PREVIA = ALTURA - 40
RESERVA = {
    "NONE": "não há",
    "LIMITED": "limitado",
    "UNLIMITED": "ilimitado",
}


class CaractereSemGrafia(ValueError):
    """Um texto do Edital chegou ao papel com caractere que o documento não imprime."""


def _texto_pdf(valor: str, *, estrito: bool = False) -> bytes:
    """O texto no repertório do WinAnsi, depois da normalização de `grafia`.

    **No Edital, o que sobra não pode virar `?`** (achado de 08/10). A validação recusa a publicação
    antes de o documento ser composto, e `estrito` é a segunda camada: se um campo impresso escapou
    dela, a publicação falha alto em vez de sair com a interrogação no ato oficial.

    Os outros documentos — comprovante, divulgação — continuam com o `?`. Neles o texto é nome de
    candidato, que nenhuma validação de publicação alcança; é registro à parte.
    """
    normalizado = grafia.normalizar(valor)
    if estrito and (faltantes := grafia.sem_grafia(normalizado)):
        raise CaractereSemGrafia(
            "O documento não imprime "
            + ", ".join(grafia.descrever(caractere) for caractere in faltantes)
            + f" em {normalizado!r}."
        )
    escapado = normalizado.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escapado.encode("cp1252", "replace")


def _grafado(valor, *, previa: bool):
    """O snapshot com todo texto normalizado — e, na prévia, com o que sobra à vista.

    Normalizar **antes** de compor, e não só ao escrever, é o que faz o separador de linha do Word
    separar parágrafo e o invisível não ocupar largura: a composição decide parágrafos e quebras
    lendo o texto, e precisa ler o que vai ser impresso.

    Na prévia, o caractere sem grafia sai como `[U+2265]`, e não como `?`: quem revisa vê o que
    precisa reescrever, e o código é o que se procura no mapa de caracteres. A paginação da prévia
    deixa de ser a da publicação nesse caso, e não importa — com ele, a publicação está recusada.
    """
    if isinstance(valor, str):
        texto = grafia.normalizar(valor)
        if previa:
            texto = "".join(
                caractere if grafia.representavel(caractere) else f"[{grafia.codigo(caractere)}]"
                for caractere in texto
            )
        return texto
    if isinstance(valor, dict):
        return {chave: _grafado(item, previa=previa) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [_grafado(item, previa=previa) for item in valor]
    return valor


def _quebrar(
    texto: str,
    tamanho: float,
    recuo: float,
    fonte: str = REGULAR,
    limite: float | None = None,
    metrica: Metrica = HELVETICA,
) -> list[str]:
    """Reflui por largura real, e não por contagem de caracteres (FR-002, FR-032).

    `limite` é a largura da coluna, quando o texto é célula de tabela: sem ele o refluxo usaria a
    página inteira e a célula atravessaria as colunas vizinhas. `metrica` é a da composição (069).
    """
    # A tolerância existe porque a largura de uma coluna é calculada a partir da largura do seu
    # próprio conteúdo: sem ela, a igualdade exata falha por arredondamento e a célula que definiu
    # a coluna é a primeira a quebrar dentro dela — foi assim que um `40` virou `4` e `0`.
    disponivel = (limite if limite is not None else LARGURA - 2 * MARGEM - recuo) + 0.01
    medir = metrica.largura
    linhas, atual = [], ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if medir(candidato, tamanho, fonte) <= disponivel:
            atual = candidato
            continue
        if atual:
            linhas.append(atual)
        # Uma palavra sozinha mais larga que o espaço disponível não tem onde quebrar por espaço.
        # Parti-la é feio; deixá-la atravessar a margem é pior, e é o que acontecia.
        while medir(palavra, tamanho, fonte) > disponivel and len(palavra) > 1:
            corte = len(palavra)
            while corte > 1 and medir(palavra[:corte], tamanho, fonte) > disponivel:
                corte -= 1
            linhas.append(palavra[:corte])
            palavra = palavra[corte:]
        atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


def _paragrafos(texto) -> list[str]:
    """Os parágrafos que a pessoa escreveu.

    `_quebrar` reflui o texto por palavra e descarta toda a estrutura de espaço em branco — o que
    fazia dois parágrafos digitados virarem um bloco corrido no documento, em silêncio, no único
    texto livre do produto. Aqui a quebra de linha é preservada como fronteira de parágrafo antes
    de o refluxo acontecer.

    Qualquer quebra separa; linhas em branco não criam parágrafo vazio. Um Edital escrito em
    linhas curtas — que é como se escreve norma — sai como linhas curtas, e não como um bloco.
    """
    return [
        bloco.strip() for bloco in re.split(r"[\r\n]+", str(texto or "").strip()) if bloco.strip()
    ]


def grupos_de_atribuicoes(perfis) -> list[list[dict]]:
    """Os Perfis que imprimem as mesmas atribuições, para que elas saiam uma vez só (064).

    Dez Perfis de Tutor, um por polo, com o mesmo texto de atribuições, repetiam esse texto dez
    vezes no documento. "Associar a outro Perfil" é, no sistema, duplicar ou colar: são cópias
    independentes, e nada as liga. Por isso a igualdade só pode ser a do texto (FR-1187).

    **A chave reusa `_paragrafos`, e não uma separação própria.** É ela que decide onde o documento
    quebra parágrafo, e `_quebrar` descarta o espaço entre palavras; a chave é feita das mesmas duas
    peças, e por isso nunca diz "igual" sobre dois textos que o documento imprime diferentes, nem
    "diferente" sobre dois que só diferem em espaço. A quebra de linha conta, porque é fronteira; o
    espaço e a quantidade de linhas em branco, não.

    **A comparação é sobre o texto normalizado por `grafia`, que é o que sai impresso.** A primeira
    versão comparava o texto cru, porque o documento trocava por "?" o que a fonte não representa, e
    o impresso juntaria `●` e `≥` por terem perdido o mesmo símbolo. Com a correção do "?", essa
    perda deixou de existir: o que `grafia` normaliza mantém o significado — `●` e `▪` são o
    marcador `•`, o espaço de largura zero some, `ç` decomposto é `ç` —, e o que ela não normaliza
    é recusado na publicação e aparece como `[U+2265]` na prévia, distinto de qualquer outro. Dois
    Perfis colados do Word em momentos diferentes, com um invisível de diferença, imprimem o mesmo
    texto e se juntam (decisão do responsável pelo produto, 08/10/2026). A chave normaliza ela
    mesma, e não confia em quem a chama: o documento já recebe o snapshot normalizado, mas a regra
    não pode depender do caminho.

    Nada além da identidade inteira agrupa (FR-1188): nem denominação, nem subconjunto, nem os
    mesmos parágrafos em outra ordem — o sistema não tem como saber que a ordem é indiferente. Texto
    vazio não forma grupo, e o Edital de um Perfil não tem grupo. Os grupos saem na ordem do
    primeiro Perfil de cada um, e os Perfis de cada grupo na ordem recebida — a do snapshot, por
    código.
    """
    if len(perfis) < 2:
        return []
    por_chave: dict[tuple[str, ...], list[dict]] = {}
    for perfil in perfis:
        texto = grafia.normalizar(perfil.get("duties") or "")
        chave = tuple(" ".join(paragrafo.split()) for paragrafo in _paragrafos(texto))
        if chave:
            por_chave.setdefault(chave, []).append(perfil)
    return [grupo for grupo in por_chave.values() if len(grupo) > 1]


def _instante(valor) -> str:
    """O instante em linguagem de Edital (`008`).

    `05/10/2026 14:00` é como um banco guarda; `05/10/2026, às 14h` é como um ato administrativo
    escreve. A conversão vive em `humano`, onde vive toda formatação humana.
    """
    if not valor:
        return "—"
    try:
        momento = datetime.fromisoformat(str(valor))
    except ValueError:
        return str(valor)
    if timezone.is_aware(momento):
        momento = timezone.localtime(momento)
    return humano.instante(momento)


FOLGA_DA_CELULA = 3.0
# O quadro abre logo abaixo da legenda que o anuncia: o bastante para o fio passar sob as descidas
# dela, e pouco o bastante para não invadir a primeira linha do próprio quadro.
FOLGA_ANTES_DO_QUADRO = 8.0
# O cinza da célula de cabeçalho. Os três Editais de referência o usam, e é o que separa a linha
# que **nomeia** as colunas das que trazem dado. Não é decoração nem paleta: é um tom, e é o único
# preenchimento do documento.
CINZA_DO_CABECALHO = "0.85"


def _grade(quadro, base):
    """Os fios de um quadro: contorno, divisão entre linhas e divisão entre colunas.

    Desenhada só depois de o texto estar colocado, pela mesma razão da moldura do Perfil (D-003):
    a altura de uma linha é a da sua célula mais alta, e medir antes seria medir duas vezes e
    aceitar que as duas medidas divirjam.
    """
    linhas = quadro["linhas"]
    if not linhas or quadro["topo"] is None:
        return []
    topo = quadro["topo"] + FOLGA_DA_CELULA
    fundo = min(base, linhas[-1][1]) - FOLGA_DA_CELULA - 3
    bordas = quadro["bordas"]
    formas = []
    # O sombreado vem primeiro: no PDF o que se emite depois cobre o que veio antes, e o fio da
    # grade precisa ficar por cima do cinza.
    if quadro.get("cabecalho"):
        _, fim = quadro["cabecalho"]
        base_do_cabecalho = fim - FOLGA_DA_CELULA - 3
        # O topo do sombreado é o **topo da grade**, não o início da linha: aquele é a linha de
        # base da legenda escrita acima, e o cinza subiria até encostar nela.
        formas.append(
            (
                "fundo",
                bordas[0],
                base_do_cabecalho,
                bordas[-1] - bordas[0],
                topo - base_do_cabecalho,
            )
        )
    formas.append(("ret", bordas[0], fundo, bordas[-1] - bordas[0], topo - fundo))
    # Um fio abaixo de cada linha, menos a última: aquela fecha no contorno.
    for _, fim in linhas[:-1]:
        altura = fim - FOLGA_DA_CELULA - 3
        formas.append(("seg", bordas[0], altura, bordas[-1], altura))
    for borda in bordas[1:-1]:
        formas.append(("seg", borda, fundo, borda, topo))
    return formas


# A moldura que pede fundo: o bloco destacado (069, FR-1382). Um valor de `moldura`, e não um campo
# novo do item `abre`, porque o item é tupla de três posições que a paginação e os testes desmontam.
DESTAQUE = "destaque"


def _moldura(topo, base, destaque=False):
    """O contorno de um bloco, da primeira à última linha que ele colocou na página.

    Com `destaque`, a forma é `caixa`: o mesmo retângulo, com fundo, que o escritor desenha antes
    de qualquer outro traço e de todo texto.
    """
    return (
        "caixa" if destaque else "ret",
        MARGEM - 6,
        base - 4,
        LARGURA - 2 * MARGEM + 12,
        topo - base + FOLGA_DA_MOLDURA + 4,
    )


def _espacamento(texto, fonte, tamanho, recuo, metrica=HELVETICA):
    """Quanto acrescentar a cada espaço para a linha alcançar a margem direita.

    É a justificação dos Editais de referência, e ela só é possível por causa de FR-002: sem
    largura real não há folga a distribuir. Linha de um espaço só, ou já cheia, não é esticada —
    espaço enorme entre duas palavras é pior que a margem irregular que ele tentaria corrigir.
    """
    espacos = str(texto).count(" ")
    if not espacos:
        return 0.0
    folga = (LARGURA - 2 * MARGEM - recuo) - metrica.largura(texto, tamanho, fonte)
    if folga <= 0:
        return 0.0
    por_espaco = folga / espacos
    return por_espaco if por_espaco <= tamanho * 0.35 else 0.0


def _x(texto, fonte, tamanho, recuo, alinhamento, metrica=HELVETICA):
    """Onde a linha começa. Centralizar e alinhar à direita só é possível por causa de FR-002."""
    if alinhamento == ESQUERDA:
        return MARGEM + recuo
    util = LARGURA - 2 * MARGEM
    sobra = util - metrica.largura(texto, tamanho, fonte)
    return MARGEM + (sobra / 2 if alinhamento == CENTRO else sobra)


# Acima desta fração da área útil em branco, um bloco divisível se divide em vez de saltar
# (069, R-011). Heurística calibrada nos cenários A e B, e não requisito: o requisito é o
# equilíbrio.
FRACAO_EM_BRANCO = 0.5
# Abaixo de tantas linhas, o bloco não se divide pelo equilíbrio: partir um bloco de três linhas
# deixa uma ou duas de cada lado, que é a viúva que a coesão existe para evitar.
LINHAS_PARA_DIVIDIR = 4


# O bloco coeso que nem o equilíbrio divide: o sumário (069). Verdadeiro como `coeso`, e por isso
# salta inteiro como qualquer coeso; só a divisão por equilíbrio o distingue.
INTEIRO = "inteiro"


def _divisivel(itens, inicio, fim):
    """O bloco tem o que dividir: linhas bastantes para que a divisão **possa** deixar duas de
    cada lado. Onde ela cai é o espaço que decide, e uma linha só no alto da página seguinte não
    está excluída — é a troca aceita contra a meia página em branco (FR-1392)."""
    linhas = sum(1 for item in itens[inicio : fim + 1] if item[0] == "texto" and item[1])
    return linhas >= LINHAS_PARA_DIVIDIR


class Composicao:
    """Acumula itens com estilo, recuo e fronteira de bloco; a paginação acontece depois.

    O item deixou de ser sempre texto: `Traço` é a primitiva gráfica de FR-003, e o bloco é a
    fronteira que FR-004 pede. Nada disso é motor de layout — são três conceitos, e a decisão de
    quebra é uma cascata de cinco degraus que sempre termina em alternativa exequível.
    """

    ESPESSURA_DO_FIO = 0.6

    def __init__(
        self, metrica: Metrica = HELVETICA, redacao: int = REDACAO_VIGENTE, equilibrio=False
    ):
        self.itens: list = []
        # A regra de equilíbrio da paginação do Edital (069, FR-1392, R-011). Desligada por padrão:
        # o comprovante e a divulgação paginam como sempre, byte a byte (FR-1383).
        self.equilibrio = equilibrio
        # A medida de toda quebra, posição e justificação desta composição (069, R-005).
        self.metrica = metrica
        # A redação das frases geradas (069, R-004). A vigente em todo documento composto agora; a
        # 1 só nas provas da história da `067` e da `068`, que compõem como se compunha.
        self.redacao = redacao
        # Os endereços escritos inteiros, antes do refluxo (069, R-012): uma palavra mais larga que
        # a coluna se parte, e o link do primeiro pedaço — "https://selecao.cefor.ifes.ed" — levaria
        # a outro lugar. Só vira link o que casar com um destes.
        self.enderecos: set = set()

    def escrever(
        self,
        texto,
        *,
        tamanho=CORPO_TEXTO,
        fonte=REGULAR,
        recuo=0.0,
        antes=0.0,
        alinhamento=ESQUERDA,
        junto=False,
        repetir=False,
        justificar=False,
    ):
        """`junto` é o "não me deixe sozinho no rodapé" de FR-022 e FR-030.

        Um título que fecha a página sem nada abaixo é o defeito que mais denuncia composição
        automática. A regra é local — a linha exige espaço para si **e** para a próxima —, e não
        um algoritmo de viúvas e órfãs.
        """
        # **Todas as partes herdam o `junto` pedido, e nenhuma o ganha sozinha.** A primeira
        # redação marcava toda parte intermediária de um refluxo como "não me separe da próxima",
        # para manter unidas as linhas de um parágrafo. Isso é cortesia, não requisito — e vira
        # laço quando o parágrafo é maior que a página: o paginador devolve a cadeia à página
        # nova, ela não cabe de novo, e o documento cresce em páginas vazias. Quebrar entre linhas
        # é o quinto degrau da cascata, e é o comportamento normal de um parágrafo longo.
        # A última linha de um parágrafo **não** se justifica: esticar os espaços de uma linha
        # curta produz o rio de branco que denuncia justificação feita sem cuidado. É a regra que
        # todo texto normativo segue, e é o que os Editais de referência fazem.
        _registrar_enderecos(self, texto)
        partes = _quebrar(texto, tamanho, recuo, fonte, metrica=self.metrica)
        for indice, parte in enumerate(partes):
            self.itens.append(
                (
                    "texto",
                    parte,
                    fonte,
                    tamanho,
                    recuo,
                    antes if indice == 0 else 0.0,
                    alinhamento,
                    junto,
                    repetir,
                    justificar and indice < len(partes) - 1,
                )
            )

    def regua(self):
        """Um fio de largura total, na posição corrente — o que separa o ato do seu metadado."""
        self.itens.append(("regua",))

    def espaco(self, altura=8.0):
        self.itens.append(("texto", "", REGULAR, 0.0, 0.0, altura, ESQUERDA, False, False, False))

    @contextmanager
    def bloco(self, *, moldura=False, coeso=True):
        """Uma fronteira que a paginação enxerga (FR-004).

        `coeso` diz que o bloco prefere não começar sem caber; `moldura` pede o contorno de FR-014.
        Blocos aninham — Perfil contém sub-blocos, sub-blocos contêm unidades —, e é o aninhamento
        que dá os degraus da cascata de FR-021.
        """
        self.itens.append(("abre", moldura, coeso))
        try:
            yield
        finally:
            self.itens.append(("fecha", moldura, coeso))

    @contextmanager
    def tabela(self, bordas=()):
        """Um quadro: cabeçalho que se repete e grade desenhada (FR-023, FR-026).

        `bordas` são as posições horizontais das divisões de coluna, da esquerda da tabela à
        direita. É o que falta a uma "tabela" que é só um alinhamento de texto — e é o que os
        Editais reais usam: fio em cada célula, não colunas soltas no branco.
        """
        self.itens.append(("abre_tabela", tuple(bordas)))
        try:
            yield
        finally:
            self.itens.append(("fecha", "tabela", False))

    @contextmanager
    def linha_de_tabela(self):
        """Uma linha do quadro — unidade da grade e **unidade segura de quebra** (FR-021).

        Coesa: uma célula que reflui em sete linhas não deixa a oitava sozinha na página seguinte.
        A cascata só quebra por dentro dela quando a própria linha for maior que uma página.
        """
        self.itens.append(("abre_linha",))
        self.itens.append(("abre", False, True))
        try:
            yield
        finally:
            self.itens.append(("fecha", False, True))
            self.itens.append(("fecha_linha",))

    # -- medição -------------------------------------------------------------

    @staticmethod
    def _altura(item):
        if item[0] != "texto":
            return 0.0
        _, texto, _, tamanho, _, antes, _, _, _, _ = item
        return antes + (tamanho * 1.45 if tamanho else 0.0)

    @classmethod
    def _extensao(cls, itens, inicio):
        """Onde termina o bloco aberto em `inicio`, e quanto ele mede."""
        profundidade, fim = 0, inicio
        for indice in range(inicio, len(itens)):
            # `abre_tabela` também abre — e fecha com o mesmo `fecha` dos demais. Não contá-lo
            # fazia a profundidade zerar cedo: a extensão do Perfil terminava no primeiro quadro
            # dele, a altura medida saía muito menor que a real, e o bloco era colocado numa
            # página onde não cabia. Era por isso que o Perfil aparecia partido.
            if itens[indice][0] in ("abre", "abre_tabela"):
                profundidade += 1
            elif itens[indice][0] == "fecha":
                profundidade -= 1
                if profundidade == 0:
                    fim = indice
                    break
        else:
            fim = len(itens) - 1
        return fim, sum(cls._altura(item) for item in itens[inicio : fim + 1])

    # -- paginação -----------------------------------------------------------

    def paginar(self):
        """Duas passadas: mede o bloco, decide se cabe, depois coloca (D-004).

        A cascata, na ordem, parando no primeiro degrau exequível: cabe no que resta → coloca;
        cabe numa página inteira → começa na próxima; não cabe numa página → abre o bloco e repete
        para cada sub-bloco; sub-bloco isolado não cabe → repete para suas unidades; unidade
        isolada não cabe → quebra entre linhas. **O último degrau é o que torna a regra sempre
        cumprível** — foi a ausência dele que tornou impossível a primeira redação da spec.
        """
        util = TOPO - (RODAPE + 24)
        paginas, atual, tracos, y = [], [], [], TOPO
        pilha = []
        indice = 0
        # O cabeçalho da tabela aberta agora. Guardá-lo é o que permite repeti-lo na continuação
        # (FR-026): sem isso, a página seguinte mostra números sem dizer de que são.
        cabecalho_ativo: list = []
        # A repetição é **pendente**, não imediata: emitido na quebra, o cabeçalho apareceria
        # sozinho numa página em que a tabela já terminou — o mesmo defeito do título órfão, uma
        # linha abaixo. Ele só se materializa quando há linha para encabeçar.
        cabecalho_pendente = False
        # A geometria do quadro só existe depois de o texto ser colocado: a altura de uma linha é
        # a da sua célula mais alta, e isso depende do refluxo. Por isso a grade é acumulada aqui
        # e emitida ao fechar a tabela — ou na quebra, para o trecho que ficou nesta página.
        quadro: dict | None = None

        def nova_pagina():
            """Fecha a página — **levando junto** o rastro de linhas que pediram companhia.

            Marcar a linha não basta: o título é colocado e só depois o bloco seguinte descobre que
            não cabe. Quem quebra a página é quem tem de devolver o título, senão ele fica para
            trás sozinho — que é o defeito de composição automática mais visível de todos.
            """
            nonlocal atual, tracos, y, cabecalho_pendente, quadro
            # O rastro é o que a quebra devolve à página nova. Ele tem de caber lá com folga
            # para o que vem em seguida: um título que arrastasse meia página deixaria de ser
            # cortesia e viraria a causa da quebra seguinte.
            rastro, altura_do_rastro = [], 0.0
            while atual and atual[-1][5]:
                candidato = atual[-1]
                altura_do_rastro += candidato[2] * 1.45
                if altura_do_rastro > util / 3:
                    break
                rastro.insert(0, atual.pop())
            for aberto in pilha:
                if aberto["moldura"] and aberto["topo"] is not None:
                    tracos.append(
                        _moldura(
                            aberto["topo"],
                            rastro[0][4] if rastro else y,
                            aberto["moldura"] == DESTAQUE,
                        )
                    )
            if quadro is not None:
                tracos.extend(_grade(quadro, rastro[0][4] if rastro else y))
            paginas.append((atual, tracos))
            atual, tracos, y = [], [], TOPO
            for texto, fonte, tamanho, x, _, junto, espaco in rastro:
                y -= tamanho * 1.45
                atual.append((texto, fonte, tamanho, x, y, junto, espaco))
            cabecalho_pendente = bool(cabecalho_ativo)
            if quadro is not None:
                quadro = {"bordas": quadro["bordas"], "topo": None, "linhas": []}
            # Um bloco que já estava aberto reabre a moldura abaixo do rastro, pela mesma razão.
            for aberto in pilha:
                if aberto["moldura"] and aberto["topo"] is not None:
                    aberto["topo"] = (y - FOLGA_APOS_TITULO) if rastro else y

        while indice < len(self.itens):
            item = self.itens[indice]

            if item[0] == "regua":
                tracos.append(("seg", MARGEM, y - 2, LARGURA - MARGEM, y - 2))
                indice += 1
                continue

            if item[0] == "abre_tabela":
                # O topo nasce **desconhecido**: fixá-lo aqui o poria na linha de base da legenda
                # escrita logo acima, e o fio cortaria o texto que apenas anuncia o quadro. Ele é
                # a posição em que a primeira linha do quadro começa, e não antes dela.
                quadro = {"bordas": item[1], "topo": None, "linhas": []}
                pilha.append({"moldura": False, "topo": None})
                indice += 1
                continue

            if item[0] == "abre_linha":
                if quadro is not None:
                    quadro["inicio"] = y
                    if quadro["topo"] is None:
                        # `y` aqui é a linha de base da legenda escrita logo acima, não um cursor
                        # livre: sem o desconto, o fio de topo sobe pela altura-x dela. É o mesmo
                        # ajuste que a moldura do Perfil precisou, pela mesma razão.
                        quadro["topo"] = y - (
                            FOLGA_ANTES_DO_QUADRO if atual and atual[-1][4] >= y else 0.0
                        )
                indice += 1
                continue

            if item[0] == "fecha_linha":
                if quadro is not None:
                    # **A linha que a quebra levou para a página seguinte começou na anterior**, e
                    # a quebra recomeça o quadro sem o início dela. Descartá-la aqui tirava da grade
                    # a primeira linha da página nova — e com ela o fio abaixo, que fundia duas
                    # linhas do Cronograma num bloco só (estudo de esforço, §12, item 14). Nesta
                    # página ela começa onde terminou a anterior, que é o cabeçalho repetido.
                    inicio = quadro.pop("inicio", None)
                    if inicio is None:
                        inicio = quadro["linhas"][-1][1] if quadro["linhas"] else y
                    quadro["linhas"].append((inicio, y))
                    if len(quadro["linhas"]) == 1 and cabecalho_ativo:
                        quadro["cabecalho"] = (inicio, y)
                indice += 1
                continue

            if item[0] == "abre":
                _, moldura, coeso = item
                fim, altura = self._extensao(self.itens, indice)
                cabe_aqui = y - altura >= RODAPE + 24
                if coeso and not cabe_aqui and altura <= util and atual:
                    # **Equilíbrio** (069, FR-1392): saltar o bloco inteiro deixaria mais da metade
                    # da área útil em branco, e ele pode se dividir — então divide-se, e a cascata
                    # desce para as unidades dele. Bloco destacado não se divide por isso: a
                    # moldura partida é pior que o branco.
                    em_branco = (y - (RODAPE + 24)) / util
                    if not (
                        self.equilibrio
                        and em_branco > FRACAO_EM_BRANCO
                        and not moldura
                        and coeso != INTEIRO
                        and _divisivel(self.itens, indice, fim)
                    ):
                        nova_pagina()
                # Não cabendo nem numa página inteira, o bloco é aberto e a mesma decisão desce
                # para os sub-blocos — que é o degrau seguinte da cascata, não um caso especial.
                # Se a última linha da página já ocupa este `y` — é o caso do título que veio
                # junto na quebra —, o contorno precisa começar **abaixo** dela: senão o fio sobe
                # pela altura-x do título que apenas anuncia o quadro.
                ocupado = bool(atual) and atual[-1][4] >= y
                topo = (y - FOLGA_APOS_TITULO) if ocupado else y
                pilha.append({"moldura": moldura, "topo": topo if moldura else None})
                indice += 1
                continue

            if item[0] == "fecha":
                if item[1] == "tabela":
                    cabecalho_ativo, cabecalho_pendente = [], False
                    if quadro is not None:
                        tracos.extend(_grade(quadro, y))
                        quadro = None
                aberto = pilha.pop()
                if aberto["moldura"] and aberto["topo"] is not None:
                    tracos.append(_moldura(aberto["topo"], y, aberto["moldura"] == DESTAQUE))
                indice += 1
                continue

            (_, texto, fonte, tamanho, recuo, antes, alinhamento, junto, repetir, justificar) = item
            altura = self._altura(item)
            # Uma linha "junto" precisa de espaço para si e para a seguinte: é o que impede o
            # título de fechar a página sozinho.
            necessario = altura
            if junto:
                proxima = next(
                    (
                        outro
                        for outro in self.itens[indice + 1 :]
                        if outro[0] == "texto" and outro[1]
                    ),
                    None,
                )
                if proxima is not None:
                    necessario += self._altura(proxima)
            if y - necessario < RODAPE + 24 and atual:
                nova_pagina()
                antes, altura = 0.0, altura - antes
            if texto and cabecalho_pendente:
                cabecalho_pendente = False
                antes_do_cabecalho = y
                y -= max(corpo for _, _, corpo, _ in cabecalho_ativo) * 1.45
                for repetido, sua_fonte, seu_corpo, seu_x in cabecalho_ativo:
                    atual.append((repetido, sua_fonte, seu_corpo, seu_x, y, False, 0.0))
                if quadro is not None:
                    # O cabeçalho repetido é a primeira linha do quadro nesta página: ele abre a
                    # grade, ganha o seu fio e o seu sombreado, como qualquer outra.
                    if quadro["topo"] is None:
                        quadro["topo"] = antes_do_cabecalho
                    quadro["linhas"].append((antes_do_cabecalho, y))
                    quadro["cabecalho"] = (antes_do_cabecalho, y)
            y -= altura
            if texto:
                x = _x(texto, fonte, tamanho, recuo, alinhamento, self.metrica)
                espaco = (
                    _espacamento(texto, fonte, tamanho, recuo, self.metrica) if justificar else 0.0
                )
                atual.append((texto, fonte, tamanho, x, y, junto, espaco))
                if repetir:
                    cabecalho_ativo.append((texto, fonte, tamanho, x))
            indice += 1

        paginas.append((atual, tracos))
        return [
            ([(*linha[:5], linha[6]) for linha in linhas], fios) for linhas, fios in paginas
        ] or [([], [])]


# A identificação do órgão é constante do documento, como já era — o que muda é a forma, não a
# origem (FR-005). O Processo e o objeto vêm do conteúdo publicado, que desde a `007` carrega o
# código e o título do Processo justamente para que o documento possa nomeá-lo.
# Quatro linhas, em caixa mista, como nos três Editais de referência — a unidade quebra em duas
# porque o nome é longo, e quebrá-la no lugar certo é decisão editorial, não refluxo.
# O brasão abre a primeira página, acima do órgão. Altura em pontos; a largura acompanha a
# proporção do arquivo, para que o símbolo nunca saia deformado.
ALTURA_DO_BRASAO = 42.0
LARGURA_DO_BRASAO = ALTURA_DO_BRASAO * brasao.LARGURA / brasao.ALTURA

# As linhas que todo documento do Ifes abre, qualquer que seja a unidade. As da unidade vêm depois,
# de `UnidadeDoAto` (060, FR-1112): até a 060, as quatro eram uma constante só, e as duas últimas
# diziam o Cefor em todo documento.
INSTITUICAO = (
    "Ministério da Educação",
    "Instituto Federal do Espírito Santo",
)


def linhas_do_orgao(unidade):
    """As linhas do órgão no cabeçalho: as da instituição e as da unidade, nesta ordem."""
    return (*INSTITUICAO, *unidade.cabecalho)


# "Edital", o número e o ano no começo do título, com ou sem o "Nº" e as grafias dele. O que vem
# depois é o objeto, separado por travessão, hífen, dois-pontos ou vírgula.
_ATO_NO_TITULO = re.compile(
    r"^\s*edital\s+(?:n\s*(?:º|°|o|\.º|\.°|\.)?\.?\s*)?(?P<numero>[^\s/]+)\s*/\s*(?P<ano>\d{4})"
    # O ano termina ali: "Edital 07/20261" não é o ato de 2026 seguido de "1".
    r"(?!\d)(?P<resto>.*)$",
    re.IGNORECASE | re.DOTALL,
)
_SEPARADOR_DO_OBJETO = " \t—–-:,."


def _mesmo_numero(escrito, declarado):
    """O número do título é o do ato, contado o zero à esquerda como grafia (revisão do PR 221).

    O número `7` e o título "Edital 07/2026" são o mesmo ato, e a comparação de texto os separava:
    o documento oficial abria com "EDITAL Nº 7/2026 — EDITAL 07/2026 — …". O não numérico — "07-A" —
    continua comparado como foi escrito, e "17" nunca passa por "7".
    """
    if escrito.isdigit() and declarado.isdigit():
        return int(escrito) == int(declarado)
    return escrito == declarado


def anuncio_do_ato(snapshot):
    """`EDITAL Nº <número>/<ano> — <título>`: o ato sai sempre de `number` e `year` (008, FR-006).

    **O RC-20 da auditoria de 26/09, corrigido pela DP-20.** A versão anterior imprimia o
    **título** no lugar do ato sempre que ele abria por "Edital", para o anúncio não repetir o ato.
    Mas o título é texto livre e se retifica, e `number`/`year` são a identidade do Edital
    (`uq_edital_scope_number_year`), a mesma que o rodapé e a verificação de integridade imprimem.
    No Edital 140/2025 do estudo de 21/09, a capa dizia um número e o rodapé outro; com o título
    *"Edital de seleção…"*, a capa não dizia número nenhum. Desde 28/09 o PDF é o documento oficial
    do piloto, e o ato que ele anuncia é o ato.

    **O título que repete exatamente o ato perde o prefixo**, para a abertura continuar uma sentença
    só, como nos Editais de referência. "Exatamente" é o mesmo número e o mesmo ano, em qualquer
    grafia do "Nº": um título que abre por outro número não é repetição, e sai inteiro depois do ato
    — é assim que a divergência fica à vista, em vez de escondida.
    """
    titulo = str(snapshot.get("title", "")).strip()
    numero = str(snapshot.get("number", "")).strip()
    ano = str(snapshot.get("year", "")).strip()
    ato = f"EDITAL Nº {numero}/{ano}"
    repeticao = _ATO_NO_TITULO.match(titulo)
    if repeticao and _mesmo_numero(repeticao["numero"], numero) and repeticao["ano"] == ano:
        titulo = repeticao["resto"].lstrip(_SEPARADOR_DO_OBJETO)
    return f"{ato} — {titulo}" if titulo else ato


# A sigla da instituição, que todo anúncio preserva como é escrita (069, FR-1377).
SIGLA_DA_INSTITUICAO = "Ifes"
_CAIXA_MISTA = re.compile(r"[a-zà-ÿ][A-ZÀ-Þ]")


def anuncio_em_caixa_alta(anuncio, sigla=""):
    """O anúncio em caixa alta, com as siglas como foram escritas (069, FR-1377, ED-24).

    `upper()` puro escrevia "EAD" e "CEFOR": a sigla da unidade e a da instituição saem como
    registradas, e a palavra de caixa mista ("EaD") também — a caixa dela é parte da grafia. O resto
    sobe, como nos Editais de referência.
    """
    preservadas = {palavra for palavra in (sigla, SIGLA_DA_INSTITUICAO) if palavra}

    def subir(palavra):
        nucleo = palavra.strip("()[],.;:“”\"'")
        if nucleo in preservadas or _CAIXA_MISTA.search(nucleo):
            return palavra
        return palavra.upper()

    # A barra e o hífen também separam: "Cefor/Ifes" e "Cefor-Ifes" guardam as duas siglas.
    return " ".join(
        "".join(subir(parte) for parte in re.split(r"([/\-–])", palavra))
        for palavra in anuncio.split(" ")
    )


def marca_de_consolidacao(consolidacao):
    """`Versão consolidada. Publicado em …; retificado em ….` (054, FR-995).

    **Os Editais da amostra marcam a retificação no próprio documento** — o "ANEXO I – CRONOGRAMA
    (RETIFICADO)" do 59/2026, os arquivos "retificado em 24.08.2026". O consolidado do sistema saía
    igual ao original, sem data nem marca, distinguível só pelo SHA-256 no pé: quem baixava o
    documento não sabia que versão tinha em mãos.
    """
    datas = [humano.data_por_extenso(data) for data in consolidacao.retificado_em]
    retificado = (
        ", em ".join(datas[:-1]) + " e em " + datas[-1] if len(datas) > 1 else "".join(datas)
    )
    frase = (
        f"Versão consolidada. Publicado em "
        f"{humano.data_por_extenso(consolidacao.publicado_em)}; retificado em {retificado}"
    )
    if consolidacao.vigencia is not None:
        frase += f", com vigência a partir de {humano.data_por_extenso(consolidacao.vigencia)}"
    return frase + "."


def _cabecalho(composicao, snapshot, unidade, consolidacao=None):
    """A abertura de um ato administrativo (FR-005 a FR-007).

    Calibrado contra os Editais 62/2026 e 73/2026 do Cefor: a hierarquia vem de **peso, caixa alta
    e centralização**, não de corpo grande. Nos dois alvos o ato está em corpo próximo ao do texto,
    e destacar por tamanho produziria um título fora do padrão institucional.
    """
    # O brasão é desenhado fora do fluxo, em posição fixa na primeira página; aqui só se reserva
    # a altura dele, para que o órgão comece abaixo e não por baixo.
    composicao.espaco(ALTURA_DO_BRASAO + 6)
    for indice, linha in enumerate(linhas_do_orgao(unidade)):
        composicao.escrever(
            linha,
            tamanho=CORPO_INSTITUCIONAL,
            alinhamento=CENTRO,
            antes=0.0 if indice else 4.0,
        )
    # Ato e objeto numa frase só, em negrito e caixa alta, como nos três Editais de referência.
    # Separá-los em linhas de corpos diferentes é o que fazia o documento parecer capa de
    # relatório: lá, o que identifica o ato é uma sentença, não um título.
    composicao.escrever(
        anuncio_em_caixa_alta(anuncio_do_ato(snapshot), unidade.sigla),
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=24,
        alinhamento=CENTRO,
    )
    if consolidacao is not None:
        composicao.escrever(
            marca_de_consolidacao(consolidacao),
            tamanho=CORPO_TEXTO,
            antes=ANTES_DE_BLOCO,
            alinhamento=CENTRO,
        )
    # **A descrição administrativa não é do ato** (069, FR-1378, ED-25): ela diz à equipe e ao
    # portal de que se trata o Edital, e no documento ela se lia como o primeiro parágrafo da norma.
    # Continua no conteúdo e no portal.


PADDING_DA_COLUNA = 12.0


class _Numerador:
    """As tabelas do documento, numeradas na ordem em que aparecem (`Tabela 1`, `Tabela 2`…).

    Os Editais de referência identificam cada quadro relevante, e é assim que o texto normativo
    consegue remetê-lo — "conforme a **TABELA 1**". Sem número, a remissão teria de descrever a
    tabela por extenso toda vez.
    """

    def __init__(self):
        self.contagem = 0

    def legenda(self, titulo):
        self.contagem += 1
        return f"Tabela {self.contagem} — {titulo}"


def _x_na_celula(texto, fonte, tamanho, recuo, coluna, alinhamento, metrica=HELVETICA):
    """Onde a célula começa dentro da sua coluna.

    Centralizar o cabeçalho é o que os Editais de referência fazem — e só é possível porque a
    largura da coluna e a do texto são ambas conhecidas (FR-002).
    """
    if alinhamento != CENTRO:
        return recuo
    return recuo + max(
        (coluna - PADDING_DA_COLUNA - metrica.largura(texto, tamanho, fonte)) / 2, 0.0
    )


def _larguras_das_colunas(cabecalho, linhas, tamanho, disponivel, metrica=HELVETICA):
    """A largura de cada coluna, medida pelo conteúdo **e limitada à área útil** (D-007).

    Medir pelo conteúdo é o que evita a proporção fixa que quebra no primeiro dado real. Mas
    medida sem teto, uma descrição longa soma além da página e empurra as colunas seguintes para
    fora do papel — o documento sai sem as datas, e nada acusa.

    O excesso é tirado só das colunas longas, e não distribuído: quem estoura a linha é a célula
    longa, e encolher a coluna do `Nº` para acomodá-la não ajudaria ninguém.

    **Longas no plural** (estudo de esforço, §12, item 7). A regra anterior tirava tudo da mais
    larga, e quando nem ela no piso bastava — Evento **e** Onde longos, no Cronograma do 78/2026 —
    todas encolhiam na mesma proporção: o `Nº` saía cortado pela borda e cada data ocupava três
    linhas. Agora cada coluna curta recebe o que pede, e as longas repartem em partes iguais o que
    sobrou; "curta" é a que cabe na parte igual de quem ainda não foi atendido.
    """
    colunas = len(linhas[0])
    naturais = [
        max(
            metrica.largura(cabecalho[c], tamanho, NEGRITO) if cabecalho else 0.0,
            *(metrica.largura(linha[c], tamanho, REGULAR) for linha in linhas),
        )
        + PADDING_DA_COLUNA
        for c in range(colunas)
    ]
    if sum(naturais) > disponivel:
        longas, restante = set(range(colunas)), disponivel
        while True:
            parte = restante / len(longas)
            curtas = [c for c in longas if naturais[c] <= parte]
            if not curtas:
                break
            for c in curtas:
                longas.remove(c)
                restante -= naturais[c]
        # Sem curta nenhuma, todas repartem por igual e o refluxo por célula cuida do resto: é o
        # caso extremo, e sair da página não é alternativa.
        return [restante / len(longas) if c in longas else naturais[c] for c in range(colunas)]
    sobra = disponivel - sum(naturais)
    if sobra > 0:
        # A folga é distribuída **em proporção**, e não entregue à coluna mais larga. Num quadro de
        # rótulo e valor, a coluna mais larga é a dos rótulos, e dar-lhe tudo empurra o valor para
        # a beira direita com um vão no meio — o quadro passa a parecer mal preenchido.
        total = sum(naturais)
        naturais = [n + sobra * n / total for n in naturais]
    return naturais


def _tabela(
    composicao,
    cabecalho,
    linhas,
    *,
    recuo=18.0,
    tamanho=CORPO_TABELA,
    alinhamentos=None,
    legenda=None,
    rodape=None,
):
    """Uma tabela: colunas limitadas, células que refluem dentro da sua coluna.

    A altura de cada linha é a da célula mais alta — sem isso, uma célula de três linhas
    escreveria por cima da linha seguinte.

    `rodape` é a última linha, em negrito — o total (054, FR-997). Entra na medida das colunas como
    as demais, para que o número do total caiba na coluna dele.
    """
    if not linhas:
        return
    disponivel = LARGURA - 2 * MARGEM - recuo
    metrica = composicao.metrica
    colunas = _larguras_das_colunas(
        cabecalho, linhas + ([rodape] if rodape else []), tamanho, disponivel, metrica
    )

    por_coluna = alinhamentos or [ESQUERDA] * len(linhas[0])

    def escrever_linha(celulas, fonte, repetir=False, alinhamento=None):
        for celula in celulas:
            _registrar_enderecos(composicao, celula)
        refluidas = [
            # O teto do refluxo é a largura da coluna menos o mesmo padding com que ela foi
            # medida. Descontar mais do que se somou faria a célula que **definiu** a coluna
            # quebrar dentro dela — `Campus Serra` virava duas linhas.
            _quebrar(
                celula,
                tamanho,
                0.0,
                fonte,
                limite=colunas[c] - PADDING_DA_COLUNA,
                metrica=metrica,
            )
            for c, celula in enumerate(celulas)
        ]
        with composicao.linha_de_tabela():
            for altura in range(max(len(parte) for parte in refluidas)):
                deslocamento, primeira_da_linha = recuo + FOLGA_DA_CELULA + 2, True
                for indice, partes in enumerate(refluidas):
                    texto = partes[altura] if altura < len(partes) else ""
                    if texto:
                        celula = _x_na_celula(
                            texto,
                            fonte,
                            tamanho,
                            deslocamento,
                            colunas[indice],
                            alinhamento or por_coluna[indice],
                            metrica,
                        )
                        composicao.escrever(
                            texto,
                            tamanho=tamanho,
                            fonte=fonte,
                            recuo=celula,
                            antes=(
                                (ANTES_DE_LINHA if altura == 0 else ANTES_DE_LINHA / 2)
                                if primeira_da_linha
                                else -(tamanho * 1.45)
                            ),
                            junto=repetir,
                            repetir=repetir,
                        )
                        primeira_da_linha = False
                    deslocamento += colunas[indice]

    # A legenda pode vir já em linhas: a que nomeia Perfis quebra entre os códigos, e nunca
    # dentro de um (068, R-008).
    for indice, linha in enumerate([legenda] if isinstance(legenda, str) else legenda or []):
        composicao.escrever(
            linha,
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            recuo=recuo,
            antes=ANTES_DE_BLOCO if indice == 0 else 0.0,
            junto=True,
        )

    # As divisões de coluna, em posição absoluta: é o que a grade precisa saber, e o que a
    # composição não teria como deduzir do texto já colocado.
    bordas, acumulado = [MARGEM + recuo], MARGEM + recuo
    for coluna in colunas:
        acumulado += coluna
        bordas.append(acumulado)

    with composicao.tabela(bordas=bordas):
        if cabecalho:
            escrever_linha(cabecalho, NEGRITO, repetir=True, alinhamento=CENTRO)
        for linha in linhas:
            escrever_linha(linha, REGULAR)
        if rodape:
            escrever_linha(rodape, NEGRITO)


# A grafia publicada vira frase. O documento não imprime `SOMA_PONDERADA` pelo mesmo motivo que
# não imprime UUID nem a forma canônica de quatro casas: o candidato lê a regra, não a grafia com
# que o sistema a guarda.
OPERACAO_DO_MARCO = {
    "SOMA_PONDERADA": "soma ponderada",
    "MEDIA_PONDERADA": "média ponderada",
}
NORMALIZACAO_DO_MARCO = {
    "NENHUMA": "nenhuma",
    "PELA_SOMA_DOS_PESOS": "pela soma dos pesos",
}
MODO_DE_ARREDONDAMENTO = {
    "MEIO_PARA_CIMA": "meio para cima",
    "MEIO_PARA_PAR": "meio para par",
    "TRUNCAR": "truncamento",
}
TIPO_DO_FATO = {"DATA": "data", "INTEIRO": "número inteiro"}

# A Etapa decisória enumerada por um marco é porta, e não parcela: ela não produz número e não
# entra na conta. `forma` é da `012`/`013`; aqui ela decide o que se escreve ao lado do nome.
DECISORIA = "DECISORIA"


def _enumerar(partes):
    """`a`, `a e b`, `a, b e c` — como um Edital enumera, e não como uma lista de código."""
    if len(partes) <= 1:
        return "".join(partes)
    return f"{', '.join(partes[:-1])} e {partes[-1]}"


def _etapa_com_o_peso(etapa):
    """O nome publicado da Etapa, e o peso com que ela entra na combinação (E2E15-008).

    **O peso existia no documento e estava no lugar errado.** Ele é publicado na seção da própria
    Etapa — que continua sendo a fonte autoritativa (FR-009) —, longe da regra que o consome. Quem
    lê "soma ponderada" precisa folhear até cada Etapa para reunir os fatores e refazer a conta;
    repeti-lo aqui não cria segunda fonte, porque é o mesmo `weight` que se lê.

    Porta não pondera: escrever "(peso …)" onde a Etapa não produz número afirmaria uma parcela
    que a combinação não tem. E Etapa pontuada sem peso não é impressa como "peso 1" — a
    publicação recusa esse marco (FR-067), e num rascunho em prévia inventar o número seria o
    documento completando a regra que o Edital não declarou.
    """
    nome = etapa.get("name") or ETAPA_NAO_IDENTIFICADA
    if etapa.get("forma") == DECISORIA:
        return f"{nome} (não pontua)"
    if etapa.get("weight") is not None:
        return f"{nome} (peso {humano.decimal(etapa['weight'])})"
    return nome


def _combinacao(marco, etapas):
    """A operação e as Etapas que ela combina, cada uma com o peso publicado.

    Sai como `soma ponderada das Etapas Prova didática (peso 2) e Análise de títulos (peso 1)`.
    """
    operacao = OPERACAO_DO_MARCO.get(marco.get("operation"), marco.get("operation", "") or "")
    enumeradas = [
        _etapa_com_o_peso(etapas.get(str(identificador)) or {})
        for identificador in marco.get("stages") or []
    ]
    if not enumeradas:
        return operacao
    artigo = "da Etapa" if len(enumeradas) == 1 else "das Etapas"
    return f"{operacao} {artigo} {_enumerar(enumeradas)}".strip()


def _arredondamento(marco):
    """A escala e o modo que fecham a conta: `2 casas decimais, meio para cima` (FR-068).

    Compõe o que estiver declarado e nada além: um rascunho em prévia sem `mode` imprime só a
    escala, em vez de o documento escolher um modo que a publicação ainda vai exigir.
    """
    arredondamento = marco.get("rounding") or {}
    escala, modo = arredondamento.get("scale"), arredondamento.get("mode")
    partes = []
    if isinstance(escala, int) and not isinstance(escala, bool):
        if escala == 0:
            partes.append("sem casas decimais")
        else:
            partes.append(f"{escala} casa decimal" if escala == 1 else f"{escala} casas decimais")
    if modo in MODO_DE_ARREDONDAMENTO:
        partes.append(MODO_DE_ARREDONDAMENTO[modo])
    return ", ".join(partes)


POR_EXTENSO = {
    1: "um",
    2: "dois",
    3: "três",
    4: "quatro",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
    10: "dez",
    15: "quinze",
    20: "vinte",
    30: "trinta",
}


def prazo_do_recurso(marco):
    """O prazo recursal do marco como o Edital o escreve — `2 (dois) dias corridos` —, ou `""`.

    **O número por extenso entre parênteses não é enfeite**: é como um ato administrativo escreve
    prazo, e é o que impede que um dígito trocado passe despercebido. Fora da tabela de números
    conhecidos, imprime-se só o algarismo — inventar a grafia de "cento e vinte e três" aqui seria
    mais chance de errar do que de acertar.

    **Função própria porque tem dois leitores** (067, D-005): a frase do marco, logo abaixo, e o
    aviso de conferência de recurso da validação, que põe o prazo dos marcos ao lado dos Eventos do
    Cronograma. Uma segunda redação do mesmo prazo seria a segunda fonte que o Princípio II proíbe.
    """
    janela = marco.get("appealWindow") if isinstance(marco, dict) else None
    if not isinstance(janela, dict) or not janela.get("admits"):
        return ""
    dias = janela.get("durationDays")
    if not isinstance(dias, int) or isinstance(dias, bool) or dias <= 0:
        return ""
    extenso = POR_EXTENSO.get(dias)
    quantos = f"{dias} ({extenso})" if extenso else str(dias)
    return f"{quantos} {'dias corridos' if dias != 1 else 'dia corrido'}"


def resultado_do_marco(marco):
    """Como o documento nomeia o resultado do marco: o nome entre aspas, ou o código, ou `""`.

    **Entre aspas, e não com artigo** (067, D-001). A auditoria sugeria "contra o resultado da
    Classificação por sorteio eletrônico", mas o nome do marco não tem gênero conhecido — "da Prova
    final", "do Sorteio público" —, e o documento não adivinha. As aspas dispensam o artigo para
    qualquer nome. O nome entra como foi escrito, aparado nas pontas; sem nome, o código — o que só
    uma prévia de rascunho pode ter, porque a gravação exige nome.
    """
    if not isinstance(marco, dict):
        return ""
    nome = str(marco.get("name") or "").strip() or str(marco.get("code") or "").strip()
    return f"“{nome}”" if nome else ""


def _janela_recursal(marco, *, objeto=None):
    """A frase normativa do recurso, que diz **de qual resultado** se recorre (FR-030; 067, ED-02).

    *"Caberá recurso contra o resultado de “Classificação final”, no prazo de 5 (cinco) dias
    corridos, contados da divulgação desse resultado."*

    **A frase não dizia o objeto, e o candidato não tinha como descobri-lo.** "Contados da
    divulgação do resultado" convivia, no mesmo documento, com o período de recurso do Cronograma e
    com o da seção textual — no cenário A da auditoria de 08/10/2026, um contra o sorteio, outro
    contra a análise documental —, e nada dizia qual era qual. O recurso que o sistema processa é
    contra a publicação do resultado **deste marco** (`doc/decisao-018-escopo-institucional-do-
    recurso.md`, §1), e é ele que a frase passa a nomear (`resultado_do_marco`). Sem nome e sem
    código — só numa prévia de rascunho —, sai a frase de antes: o documento não inventa nome.

    **`objeto` é só da Revisão** (067, D-012). Ela agrupa marcos de Perfis diferentes que declaram a
    mesma regra, com a denominação de cada grupo na linha de cima; com o nome dentro da frase, cada
    Perfil viraria um grupo. Ela passa `"deste marco"`, e a frase é a mesma, com o nome dito pela
    linha da denominação. O documento compõe um marco por vez, e nunca passa `objeto`.

    **O silêncio não imprime nada, e a negativa imprime** (FR-028, FR-113). São coisas diferentes:
    marco que nada declara conserva as vias que a lei dá fora deste sistema, e escrever "não cabe
    recurso" ali afirmaria norma que o Edital não publicou. Já `admits` falso **é** norma — a
    recusa de interpor a cita, e o candidato tem direito de conferi-la no documento; calá-la aqui
    deixaria a recusa citando o que não está escrito em lugar nenhum.
    """
    janela = marco.get("appealWindow")
    if not isinstance(janela, dict):
        return ""
    if objeto is None:
        resultado = resultado_do_marco(marco)
        objeto = f"de {resultado}" if resultado else ""
    if janela.get("admits") is False:
        return f"Não caberá recurso contra o resultado {objeto or 'deste marco'}."
    prazo = prazo_do_recurso(marco)
    if not prazo:
        return ""
    if objeto:
        return (
            f"Caberá recurso contra o resultado {objeto}, no prazo de {prazo}, contados da "
            "divulgação desse resultado."
        )
    return f"Caberá recurso no prazo de {prazo}, contados da divulgação do resultado."


def _regra_de_corte(marco, etapas):
    """A frase normativa do corte, como um Edital a escreve (014, FR-185).

    *"Progridem para a Entrevista os 10 (dez) primeiros desta ordem, mais 20 suplentes."*

    O número por extenso entre parênteses segue a regra da janela recursal, e pelo mesmo motivo: é
    como um ato administrativo escreve quantidade, e é o que impede que um dígito trocado passe
    despercebido.

    **O alvo derivado não imprime número**, e a razão é que ele não tem um: a quantidade é a do
    quadro de vagas do recorte, que já está publicado alguns parágrafos acima, e copiá-la aqui
    criaria uma segunda resposta para a mesma pergunta — que é exatamente o que o Princípio II
    proíbe. O documento diz de onde ela vem.

    **O marco terminal não imprime nada sobre Etapa**: ele corta para a análise e para a chamada, e
    escrever "não alimenta Etapa alguma" no Edital afirmaria ao candidato uma tecnicalidade do
    sistema, e não uma norma do certame.

    O empate e a continuação, que completam a regra, têm frase própria logo abaixo
    (`_empate_no_corte`, `_continuacao_do_corte`).
    """
    regra = marco.get("cutRule")
    if not isinstance(regra, dict):
        return ""
    um_so = False
    if regra.get("targetKind") == "FROM_VACANCY_TABLE":
        quantos = "os primeiros desta ordem, até o número de vagas ofertadas no recorte"
    else:
        alvo = regra.get("targetCount")
        if not isinstance(alvo, int) or isinstance(alvo, bool) or alvo < 0:
            return ""
        extenso = POR_EXTENSO.get(alvo)
        numero = f"{alvo} ({extenso})" if extenso else str(alvo)
        # "Progridem os 1 (um) primeiros" saía do alvo fixo de um, e a Revisão repetia a frase.
        um_so = alvo == 1
        quantos = f"o {numero} primeiro" if um_so else f"os {numero} primeiros"
        quantos = f"{quantos} desta ordem"
    # A guarda da ausência é explícita, e não um `or ""` depois do `str()`: `str(None)` é a string
    # `"None"`, que é verdadeira — o `or` nunca dispararia, e bastaria existir uma Etapa de `id`
    # igual a `"None"` para o documento nomear a Etapa errada.
    governada = regra.get("governedStage")
    destino = etapas.get(str(governada)) if governada else None
    nome = destino.get("name") if isinstance(destino, dict) else ""
    para = f" para {nome}" if nome else ""
    excedente = regra.get("surplusCount")
    com_suplentes = isinstance(excedente, int) and not isinstance(excedente, bool) and excedente > 0
    verbo = "Progride" if um_so and not com_suplentes else "Progridem"
    frase = f"{verbo}{para} {quantos}"
    if com_suplentes:
        extenso = POR_EXTENSO.get(excedente)
        numero = f"{excedente} ({extenso})" if extenso else str(excedente)
        plural = "suplentes" if excedente != 1 else "suplente"
        frase = f"{frase}, mais {numero} {plural}"
    return f"{frase}."


# **O empate e a continuação são a outra metade da Regra de Corte** (014, FR-185), e o documento
# imprimia só a primeira: dos seis campos de `faixa.CAMPOS_DA_REGRA`, quatro. Os dois que faltavam
# mudam quem continua no certame — com alvo de 10 e três empatados na 10ª posição, um Edital leva
# doze e o outro não emite o corte —, e quem lesse só o documento não reconstituía a regra que o
# sistema aplica. A Revisão lê as mesmas frases daqui: duas redações da mesma regra seriam duas
# normas, e a conferência diria uma coisa enquanto o Edital publica outra.
#
# **A frase segue a do corte, e a pressupõe**: "essa quantidade" é a que o par `Corte` acabou de
# dizer. Alvo mais suplentes, e não só o alvo — é a última posição da faixa emitida que o empate
# atravessa (FR-195, FR-196).
EMPATE_NO_CORTE = {
    "ADMITS_SURPLUS": (
        "Havendo empate na última posição, progridem todos os empatados, ainda que excedam essa "
        "quantidade."
    ),
    "STRICT": "Havendo empate na última posição, essa quantidade não é excedida.",
}
CONTINUACAO_DO_CORTE = {
    "ALLOWED": "Poderá haver chamada, nesta ordem, além dos que este corte publicar.",
    "NONE": "Não haverá chamada além dos que este corte publicar.",
}


def _empate_no_corte(marco):
    """A frase do desfecho do empate que atravessa a faixa, ou `""` (014, FR-181, FR-185).

    Valor fora do vocabulário não é impresso: a publicação o recusa (FR-182), e numa prévia de
    rascunho escrever a chave crua poria no papel um identificador de máquina.
    """
    regra = marco.get("cutRule")
    return EMPATE_NO_CORTE.get(regra.get("tieOutcome"), "") if isinstance(regra, dict) else ""


def _continuacao_do_corte(marco):
    """A frase da continuação além da faixa publicada, ou `""` (014, FR-226, FR-185)."""
    regra = marco.get("cutRule")
    return (
        CONTINUACAO_DO_CORTE.get(regra.get("continuation"), "") if isinstance(regra, dict) else ""
    )


def _habilitacao_ao_sorteio(snapshot, perfil, marco, etapas):
    """Quem participa do sorteio deste marco, na frase do Edital (021, R-012).

    **Lida do método que governa**, e não da chave do marco: é o que a publicação da relação lê
    (`sorteios/application/relacao.py`), e o documento não pode descrever um universo e a relação
    projetar outro. Só o método próprio a carrega — o comum não tem como saber quais Etapas cada
    marco enumera —, e o marco que referencia o comum sorteia todas as inscrições submetidas.

    **A ausência é impressa, e não calada**, ao contrário do método incompleto em prévia: sem Etapa
    de habilitação, entram todas as submetidas — é norma, e é a que decide quem é sorteado. O
    Princípio VI pede o PDF correspondendo à versão homologada, e a `FR-465` o método que governa;
    nenhuma das duas se cumpre com o documento calando o universo do sorteio.

    Etapa declarada que não resolve não é impressa como "todas": afirmaria um universo maior do que
    o declarado. A publicação recusa essa referência (`_validar_etapa_de_habilitacao`), e a prévia
    de um rascunho assim sai sem a linha.
    """
    identidade = marco.get("id")
    metodo = (
        regras_do_marco.metodo_que_governa(
            snapshot, perfil_id=perfil.get("id"), marco_id=identidade
        )
        if identidade
        else None
    ) or marco.get("drawMethod")
    declarada = (metodo or {}).get("qualifyingStageId")
    if not declarada:
        return "participam todas as inscrições submetidas"
    etapa = etapas.get(str(declarada))
    if not isinstance(etapa, dict) or not etapa.get("name"):
        return ""
    return f"participam apenas as inscrições habilitadas na Etapa {etapa['name']}"


#: Como a ordem do marco nasce, em português (032, FR-464). A ausência não entra: marco do acervo
#: que não declara a forma não ganha o par, e sai do documento exatamente como sempre saiu.
FORMA_DA_ORDEM = {
    "POR_PONTUACAO": "pela pontuação combinada das Etapas",
    "POR_SORTEIO": "por sorteio",
}


# ---------------------------------------------------------------------------
# 069 — A redação 2 das frases geradas
# ---------------------------------------------------------------------------
#
# **Cada frase daqui diz o mesmo que a da redação 1, na voz do candidato** (FR-1360, FR-1361). As
# variantes, a frase de antes e a nota de equivalência de cada uma estão em
# `specs/069-edital-linguagem-simples/contracts/redacao.md`, e um teste prende cada uma
# (`tests/unit/publicacoes/test_redacao_das_frases.py`). As funções da redação 1 continuam acima,
# intactas: os atos publicados antes da `069` as dizem, e as provas da história da `067` e da `068`
# as leem (R-004).
#
# **Os nomes declarados vão entre aspas, sem artigo** — a Etapa, o marco, a fonte e a ocorrência do
# sorteio —, pela regra da decisão 001 da `067`: o nome não tem gênero conhecido, e o documento não
# adivinha.

CLASSIFICACAO_SEPARADA = (
    "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria "
    "classificação e o seu próprio resultado."
)
CABECALHO_DO_DESEMPATE = "Critérios de desempate, nesta ordem:"
FRASE_DE_AUTENTICIDADE = (
    "Autenticidade — este documento corresponde integralmente à versão homologada do Edital "
    "identificada abaixo."
)
ANUNCIO_DOS_DADOS_DECLARADOS = "Na inscrição, informe também:"
# O rótulo que a `068` gerava com o termo do sistema (FR-1366, D-007). Só o rótulo muda: o número e
# o destino da remissão são os mesmos (FR-1399).
ROTULO_DAS_REGRAS = {REDACAO_1: "Marcos classificatórios", REDACAO_2: "Regras de classificação"}
# "Inscrições" é feminino: "1 (uma)", "2 (duas)". O resto da tabela não tem gênero.
_POR_EXTENSO_FEMININO = {1: "uma", 2: "duas"}


def _aspas(nome):
    return f"“{nome}”"


def _numero_por_extenso(numero, *, feminino=False):
    """`15 (quinze)`, ou só o algarismo fora da tabela — a regra de `prazo_do_recurso`."""
    extenso = (_POR_EXTENSO_FEMININO if feminino else {}).get(numero) or POR_EXTENSO.get(numero)
    return f"{numero} ({extenso})" if extenso else str(numero)


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def frase_da_forma_da_ordem(marco):
    """C3 — "A ordem de classificação segue a nota final.", ou `""`.

    Sob sorteio, a forma é dita pelo título da subseção e pela habilitação (C2, C4). Marco do acervo
    que não declara a forma não ganha a frase, como não ganhava o par `Ordem` (032, FR-464).
    """
    if marco.get("orderProduction") == "POR_PONTUACAO":
        return "A ordem de classificação segue a nota final."
    return ""


def frase_da_habilitacao(snapshot, perfil, marco, etapas):
    """C4 e C5 — quem participa do sorteio, pela mesma leitura de `_habilitacao_ao_sorteio`."""
    lida = _habilitacao_ao_sorteio(snapshot, perfil, marco, etapas)
    if not lida:
        return ""
    if lida == "participam todas as inscrições submetidas":
        return "Participam do sorteio todas as inscrições enviadas."
    identidade = marco.get("id")
    metodo = (
        regras_do_marco.metodo_que_governa(
            snapshot, perfil_id=perfil.get("id"), marco_id=identidade
        )
        if identidade
        else None
    ) or marco.get("drawMethod")
    etapa = etapas.get(str((metodo or {}).get("qualifyingStageId"))) or {}
    return f"Participam do sorteio só as inscrições habilitadas na Etapa {_aspas(etapa['name'])}."


def _peso_um(etapa):
    return etapa.get("weight") is not None and humano.decimal(etapa["weight"]) == "1"


def frases_da_combinacao(marco, etapas):
    """C6 a C10 — a conta da nota final, dita como conta.

    **A Etapa decisória sai da conta e é dita à parte** (C10): na redação 1 ela aparecia na lista da
    soma com "(não pontua)", que dizia a mesma coisa num lugar onde parecia parcela. A média
    ponderada de uma Etapa só é a pontuação dela, e sai como a C6.
    """
    operacao = marco.get("operation")
    resolvidas = [
        etapas.get(str(identificador)) or {} for identificador in marco.get("stages") or []
    ]
    pontuadas = [etapa for etapa in resolvidas if etapa.get("forma") != DECISORIA]
    decisorias = [etapa for etapa in resolvidas if etapa.get("forma") == DECISORIA]
    normaliza = marco.get("normalization") == "PELA_SOMA_DOS_PESOS"

    def nome(etapa):
        # A Etapa que o conteúdo não resolve é dita como ausente, e sem aspas: entre aspas, a
        # ausência se leria como o nome de uma Etapa.
        return _aspas(etapa["name"]) if etapa.get("name") else ETAPA_NAO_IDENTIFICADA

    def com_peso(etapa):
        if etapa.get("weight") is None:
            return nome(etapa)
        return f"{nome(etapa)} (peso {humano.decimal(etapa['weight'])})"

    frases = []
    if pontuadas and operacao in OPERACAO_DO_MARCO:
        if len(pontuadas) == 1:
            etapa = pontuadas[0]
            simples = (
                operacao == "MEDIA_PONDERADA" or _peso_um(etapa) or etapa.get("weight") is None
            )
            if simples and not normaliza:
                frases.append(f"A nota final é a pontuação obtida na Etapa {nome(etapa)}.")
            else:
                frases.append(
                    f"A nota final é a pontuação obtida na Etapa {com_peso(etapa)}, multiplicada "
                    "pelo seu peso."
                )
        elif operacao == "SOMA_PONDERADA":
            frases.append(
                "A nota final é a soma das pontuações nas Etapas "
                f"{_enumerar([com_peso(etapa) for etapa in pontuadas])}, cada uma multiplicada "
                "pelo seu peso."
            )
        else:
            frases.append(
                "A nota final é a média ponderada das pontuações nas Etapas "
                f"{_enumerar([com_peso(etapa) for etapa in pontuadas])}."
            )
        if normaliza:
            frases.append("Depois, o resultado é dividido pela soma dos pesos.")
    if len(decisorias) == 1:
        frases.append(f"A Etapa {nome(decisorias[0])} não entra na conta: ela não dá pontos.")
    elif decisorias:
        frases.append(
            f"As Etapas {_enumerar([nome(etapa) for etapa in decisorias])} não entram na conta: "
            "elas não dão pontos."
        )
    return frases


_MODO_DO_ARREDONDAMENTO_2 = {
    "MEIO_PARA_CIMA": "; a partir da metade, arredonda-se para cima",
    "MEIO_PARA_PAR": "; na metade exata, arredonda-se para o algarismo par mais próximo",
    "TRUNCAR": ", desprezando-se as demais",
}


def frase_do_arredondamento(marco):
    """C11 a C14 — a escala e o modo, dito pelo que acontece na metade (L7). `""` sem escala."""
    arredondamento = marco.get("rounding") or {}
    escala, modo = arredondamento.get("scale"), arredondamento.get("mode")
    if not _inteiro(escala):
        return ""
    if escala == 0:
        para = "um número inteiro"
    else:
        para = "1 casa decimal" if escala == 1 else f"{escala} casas decimais"
    regra = _MODO_DO_ARREDONDAMENTO_2.get(modo, "")
    if modo == "TRUNCAR" and escala == 0:
        regra = ", desprezando-se as casas decimais"
    return f"A nota final é arredondada para {para}{regra}."


def frases_da_ordem(snapshot, perfil, marco):
    """Como a ordem do marco nasce, em frases: C3 a C14, e C4 ou C5 sob sorteio.

    **A mesma decisão da redação 1, pela forma declarada** (032, FR-468; 067, ED-03): sob sorteio
    não há conta nem arredondamento, e a habilitação só sai com o método que a governa.
    """
    etapas = por_identificador(snapshot.get("stages"))
    if regras_do_marco.declara_sorteio(marco):
        if not _metodo_do_marco(snapshot, perfil, marco):
            return []
        habilitacao = frase_da_habilitacao(snapshot, perfil, marco, etapas)
        return [habilitacao] if habilitacao else []
    frases = []
    if forma := frase_da_forma_da_ordem(marco):
        frases.append(forma)
    frases.extend(frases_da_combinacao(marco, etapas))
    if arredondamento := frase_do_arredondamento(marco):
        frases.append(arredondamento)
    return frases


EMPATE_NO_CORTE_2 = {
    "ADMITS_SURPLUS": (
        "Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem "
        "esse número."
    ),
    "STRICT": "Se houver empate na última posição, esse número não é ultrapassado.",
}
CONTINUACAO_DO_CORTE_2 = {
    # **Sem condição** (K9): "se ainda sobrarem vagas" era a condição que a primeira redação da
    # amostra acrescentava, e que a norma declarada não tem (achado 1 da conferência por enunciado).
    "ALLOWED": (
        "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem."
    ),
    "NONE": "Não serão chamados candidatos além desses.",
}
SUPLENTES_SEM_CADASTRO = (
    "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas "
    "pelos primeiros classificados."
)


def frase_da_continuacao(marco):
    """K9 e K10 — a continuação além dos que o corte publica, ou `""`."""
    regra = marco.get("cutRule")
    return (
        CONTINUACAO_DO_CORTE_2.get(regra.get("continuation"), "") if isinstance(regra, dict) else ""
    )


def frases_do_corte(marco, etapas, *, sem_cadastro):
    """K1 a K10 — **a unidade indivisível** (FR-1375, R-009): corte, empate, suplentes, continuação.

    O empate fala de "esse número", e a continuação de "além desses": separadas na partilha parcial
    entre o comum e o de um grupo, as frases perderiam o referente — foi o terceiro erro da amostra.
    Por isso saem sempre juntas, e quem agrupa compara a unidade inteira.

    **A explicação dos suplentes só sai sem cadastro de reserva em Perfil nenhum** (K7, FR-1362):
    com cadastro, como os suplentes e o cadastro se relacionam é a pendência DP-05, e o documento
    não a explica. `sem_cadastro` é do Edital, e não do Perfil: a frase diz "as vagas deste
    Edital".
    """
    regra = marco.get("cutRule")
    if not isinstance(regra, dict):
        return []
    um_so = False
    if regra.get("targetKind") == "FROM_VACANCY_TABLE":
        quantos = (
            "os primeiros classificados de cada lista de concorrência, em número igual ao das "
            "vagas dessa lista"
        )
    else:
        alvo = regra.get("targetCount")
        if not _inteiro(alvo) or alvo < 0:
            return []
        um_so = alvo == 1
        quantos = (
            "o 1 (um) primeiro classificado"
            if um_so
            else f"os {_numero_por_extenso(alvo)} primeiros classificados"
        )
    excedente = regra.get("surplusCount")
    com_suplentes = _inteiro(excedente) and excedente > 0
    plural = not (um_so and not com_suplentes)
    governada = regra.get("governedStage")
    destino = etapas.get(str(governada)) if governada else None
    nome = destino.get("name") if isinstance(destino, dict) else ""
    if nome:
        inicio = f"{'Passam' if plural else 'Passa'} para a Etapa {_aspas(nome)}"
    else:
        inicio = "Seguem no processo" if plural else "Segue no processo"
    frase = f"{inicio} {quantos}"
    if com_suplentes:
        suplentes = "suplentes" if excedente != 1 else "suplente"
        frase += f", mais {_numero_por_extenso(excedente)} {suplentes}"
    unidade = [f"{frase}."]
    if not regras_do_marco.declara_sorteio(marco):
        if empate := EMPATE_NO_CORTE_2.get(regra.get("tieOutcome"), ""):
            unidade.append(empate)
    if com_suplentes and sem_cadastro:
        unidade.append(SUPLENTES_SEM_CADASTRO)
    if continuacao := frase_da_continuacao(marco):
        unidade.append(continuacao)
    return unidade


def frases_do_desempate(marco, etapas, fatos):
    """T8 — os critérios na ordem declarada, cada um com o efeito da ausência ("1º …")."""
    criterios = sorted(marco.get("tiebreakers") or [], key=lambda item: item.get("order") or 0)
    return [
        f"{indice}º {criterio_com_a_ausencia(criterio, etapas, fatos, redacao=REDACAO_2)}"
        for indice, criterio in enumerate(criterios, start=1)
    ]


def frase_do_recurso(marco, *, objeto=None):
    """R1 a R5 — de que resultado se recorre, e em que prazo; nunca o canal (FR-1363).

    O objeto e o silêncio seguem `_janela_recursal`: sem declaração, nada; a negativa é norma, e
    sai.
    `objeto` é só da Revisão, que agrupa marcos de nomes diferentes ("deste marco", 067, D-012).
    """
    janela = marco.get("appealWindow")
    if not isinstance(janela, dict):
        return ""
    if objeto is None:
        resultado = resultado_do_marco(marco)
        objeto = f"de {resultado}" if resultado else ""
    if janela.get("admits") is False:
        return f"Não caberá recurso contra o resultado {objeto or 'deste marco'}."
    prazo = prazo_do_recurso(marco)
    if not prazo:
        return ""
    if objeto:
        return (
            f"Contra o resultado {objeto}: no prazo de {prazo}, contados da divulgação desse "
            "resultado."
        )
    return f"Cabe recurso no prazo de {prazo}, contados da divulgação do resultado."


def _origem_do_metodo_2(snapshot, marco):
    """S2 a S4 — a origem do método na palavra do candidato: "deste sorteio", não "deste marco"."""
    origem = _origem_do_metodo(snapshot, marco)
    if origem == "comum a este Edital":
        return origem
    if origem.endswith("diverge do comum deste Edital"):
        return "próprio deste sorteio, diferente do comum deste Edital"
    return "próprio deste sorteio"


def dados_do_sorteio(snapshot, perfil, marco):
    """S1 a S7 — os dados que permitem a qualquer pessoa refazer o sorteio (FR-1376, FR-465).

    `(abertura, pares)`, ou `None` sem método. A abertura diz a fonte, a ocorrência e o instante;
    os pares, o método com o algoritmo, como o concurso é escolhido, a semente e a substituição —
    os sete campos, e só os declarados, como a redação 1 (`_metodo_do_marco`).
    """
    identidade = marco.get("id")
    metodo = (
        regras_do_marco.metodo_que_governa(
            snapshot, perfil_id=perfil.get("id"), marco_id=identidade
        )
        if identidade
        else None
    ) or marco.get("drawMethod")
    if not isinstance(metodo, dict) or not metodo:
        return None
    partes = []
    if ocorrencia := _valor_do_campo_do_metodo("occurrence", metodo):
        partes.append(f"de {_aspas(ocorrencia)}")
    if fonte := _valor_do_campo_do_metodo("source", metodo):
        partes.append(f"da fonte {_aspas(fonte)}")
    if metodo.get("occurrenceAt"):
        partes.append(f"de {_valor_do_campo_do_metodo('occurrenceAt', metodo)}")
    conferir = "Com os dados abaixo, qualquer pessoa pode refazer o sorteio e conferir o resultado."
    abertura = (
        f"A ordem será definida a partir do resultado {', '.join(partes)}. {conferir}"
        if partes
        else conferir
    )
    algoritmo = _valor_do_campo_do_metodo("algorithm", metodo)
    metodo_ = _origem_do_metodo_2(snapshot, marco) + (
        f"; algoritmo {algoritmo}." if algoritmo else "."
    )
    pares = [["Método", metodo_]]
    if derivacao := _valor_do_campo_do_metodo("derivation", metodo):
        pares.append(["Qual concurso", derivacao])
    if semente := _valor_do_campo_do_metodo("normalization", metodo):
        pares.append(["Semente", f"o número usado no sorteio: {inicial_minuscula(semente)}"])
    if substituicao := _valor_do_campo_do_metodo("substitutionRule", metodo):
        pares.append(["Se faltar", substituicao])
    return abertura, pares


FRASE_DA_REVERSAO_2 = {
    "ON_EXHAUSTION": (
        "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas "
        "passam para a ampla concorrência do mesmo código."
    ),
    "ON_BALANCE": (
        "As vagas reservadas de um código que não forem preenchidas passam para a ampla "
        "concorrência do mesmo código."
    ),
}


def frase_da_reversao(especie, *, redacao=REDACAO_VIGENTE):
    """V1 e V2 — o gatilho e o destino; "a respectiva" ampla concorrência é a do mesmo código."""
    tabela = FRASE_DA_REVERSAO if redacao == REDACAO_1 else FRASE_DA_REVERSAO_2
    return tabela.get(especie, "")


def frase_do_periodo_de_inscricoes(evento):
    """V9 — **frase nova, gerada** do Evento marcado como período de inscrições (FR-1369)."""
    inicio, fim = evento.get("startAt"), evento.get("endAt")
    periodo = f"de {_instante(inicio)}, a {_instante(fim)}" if fim else f"em {_instante(inicio)}"
    return f"Período de inscrições: {periodo} (Cronograma, nº {evento.get('order', '')})."


def itens_dos_dados_declarados(fatos):
    """V10 — "a data de nascimento;", "o número de meses de experiência." — sem o tipo (FR-1366)."""
    itens = []
    for fato in fatos:
        rotulo = inicial_minuscula(fato.get("label") or fato.get("code") or "")
        if fato.get("type") == "DATA":
            itens.append(f"a {rotulo}")
        elif fato.get("type") == "INTEIRO":
            itens.append(f"o número de {rotulo}")
        else:
            itens.append(rotulo)
    return [
        f"{item}{'.' if indice == len(itens) - 1 else ';'}" for indice, item in enumerate(itens)
    ]


def frase_do_uso_no_desempate(numero):
    """V10 — onde os dados declarados são usados, quando algum critério os usa."""
    return f"Esses dados são usados no desempate (item {numero})."


def lembrete_do_requerimento(numero, *, na_inscricao=False):
    """V13 — **frase nova** (ED-18): o Requerimento enviado na inscrição, lembrado onde se busca."""
    if na_inscricao:
        return f"A inscrição inclui o Requerimento de Matrícula (item {numero})."
    return (
        f"Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item {numero})."
    )


def frase_da_etapa(etapa, eventos):
    """E1 a E3 — o caráter, a forma de concluir, a pontuação e o período, em frases.

    Só o que está declarado, pela régua de `_etapas` (FR-009, FR-066): imprimir "peso 1" onde o
    Edital nada disse seria o documento afirmando regra que a Publicação não contém. E tudo o que
    está declarado: os pares da redação 1 saíam para qualquer forma de Etapa, e as frases também.
    """
    caracteres = _enumerar([rotulo for chave, rotulo in CARATER_DA_ETAPA if etapa.get(chave)])
    partes = []
    if etapa.get("maximumScore") is not None:
        partes.append(f"pontuação máxima de {humano.decimal(etapa['maximumScore'])}")
    if etapa.get("minimumScore") is not None:
        partes.append(f"nota mínima de {humano.decimal(etapa['minimumScore'])}")
    if etapa.get("weight") is not None:
        partes.append(f"peso {humano.decimal(etapa['weight'])}")
    frases = []
    if etapa.get("forma") == DECISORIA:
        favoravel = etapa.get("rotuloFavoravel") or "favorável"
        desfavoravel = etapa.get("rotuloDesfavoravel") or "desfavorável"
        resultado = f"o resultado é {_aspas(favoravel)} ou {_aspas(desfavoravel)}."
        frases.append(f"Etapa {caracteres}: {resultado}" if caracteres else f"O{resultado[1:]}")
        if partes:
            frases.append(f"A Etapa tem {_enumerar(partes)}.")
    elif caracteres or partes:
        frase = f"Etapa {caracteres}" if caracteres else "Etapa"
        if partes:
            frase += f", com {_enumerar(partes)}" if caracteres else f" com {_enumerar(partes)}"
        frases.append(f"{frase}.")
    previstas = etapa.get("evaluationsPerRegistration")
    if _inteiro(previstas):
        quantas = _numero_por_extenso(previstas, feminino=True)
        avaliacoes = "avaliação" if previstas == 1 else "avaliações"
        frases.append(f"Cada inscrição recebe {quantas} {avaliacoes}.")
    evento = eventos.get(etapa.get("scheduleEventId")) if etapa.get("scheduleEventId") else None
    if evento and evento.get("startAt"):
        if evento.get("endAt"):
            frases.append(
                f"Será feita de {_instante(evento['startAt'])}, a {_instante(evento['endAt'])}."
            )
        else:
            frases.append(f"Será feita em {_instante(evento['startAt'])}.")
    return " ".join(frases)


def texto_do_documento(documento):
    """D5 — o nome, "(facultativo)" quando é, e a instrução depois do travessão, em minúscula."""
    texto = documento.get("name", "") or ""
    if not documento.get("required", True):
        texto += " (facultativo)"
    if documento.get("instructions"):
        texto += f" — {inicial_minuscula(documento['instructions'])}"
    return texto


def frase_do_cadastro(perfil):
    """P2 — o cadastro de reserva por extenso (FR-1371), com o limite como é."""
    tipo, limite = perfil.get("reserveType"), perfil.get("reserveLimit")
    if tipo == "LIMITED" and _inteiro(limite):
        return f"cadastro de reserva de até {_numero_por_extenso(limite)} classificados por Perfil"
    if tipo == "UNLIMITED":
        return "cadastro de reserva sem limite de classificados"
    if tipo == "NONE":
        return "não há cadastro de reserva"
    return ""


def _igual_em_todos(perfis, chave):
    valores = {repr(perfil.get(chave)) for perfil in perfis}
    return len(valores) == 1 and bool(perfis[0].get(chave))


def frase_dos_atributos_comuns(perfis):
    """P1 — o que é **igual em todos os Perfis**, uma vez (FR-1374), ou `""`.

    Só o que é igual em todos, por identidade do valor: nome, descrição, carga horária,
    remuneração e cadastro de reserva. A descrição só entra junto do nome comum — sem ele, "Em
    todos os Perfis: atua no polo…" não diria de quem; a tabela de características a leva.

    **O Edital de um Perfil não tem "todos os Perfis"**, e a frase sai como "Perfil P1: …": a
    matriz de vagas não traz nome e a tabela de características só existe com dois Perfis, e sem
    esta frase o corpo calava o nome, a descrição, a carga horária, a remuneração e o cadastro do
    único Perfil — que a apresentação plana imprime.
    """
    if not perfis:
        return ""
    partes = []
    if _igual_em_todos(perfis, "name"):
        nome = perfis[0]["name"]
        if _igual_em_todos(perfis, "description"):
            descricao = inicial_minuscula(perfis[0]["description"]).rstrip(". ")
            nome = f"{nome} — {descricao}"
        partes.append(nome)
    if _igual_em_todos(perfis, "workload"):
        partes.append(f"carga horária de {perfis[0]['workload']}")
    if _igual_em_todos(perfis, "compensation"):
        partes.append(f"remuneração: {inicial_minuscula(perfis[0]['compensation'])}")
    cadastros = {frase_do_cadastro(perfil) for perfil in perfis}
    if len(cadastros) == 1 and (cadastro := cadastros.pop()):
        partes.append(cadastro)
    if not partes:
        return ""
    if len(perfis) == 1:
        return f"Perfil {perfis[0].get('code', '')}: {'; '.join(partes)}."
    return f"Em todos os Perfis: {'; '.join(partes)}."


def remissao_as_regras(numero, *, redacao=REDACAO_VIGENTE):
    """G2 — o rótulo e a remissão às regras comuns: o mesmo número e o mesmo destino (FR-1399)."""
    if redacao == REDACAO_1:
        return ROTULO_DAS_REGRAS[REDACAO_1], f"os descritos no item {numero}."
    return ROTULO_DAS_REGRAS[REDACAO_2], f"as descritas no item {numero}."


def titulo_da_subsecao_comum(materia, *, redacao=REDACAO_VIGENTE):
    """G3 — o título da subseção comum da `068`; só o de marcos muda na redação 2."""
    if materia == MARCOS and redacao != REDACAO_1:
        return f"{ROTULO_DAS_REGRAS[REDACAO_2]} comuns aos Perfis"
    return TITULO_DA_SUBSECAO[materia]


def sem_cadastro_de_reserva(snapshot):
    """Nenhum Perfil do Edital tem cadastro de reserva? — a condição da K7 (FR-1362)."""
    perfis = snapshot.get("profiles") or []
    return bool(perfis) and all(perfil.get("reserveType") == "NONE" for perfil in perfis)


def _publica_a_mesma_norma(proprio, comum):
    """Os dois métodos publicam a mesma norma? (032, FR-466)

    **A comparação é sobre os sete campos que o documento imprime, e não sobre o dicionário
    inteiro** — e a distinção custou um defeito. O método do **marco** carrega um décimo campo que
    o método **comum** nunca tem: `qualifyingStageId`, a Etapa que habilita a participar do
    sorteio, que é do marco porque depende de quais Etapas aquele marco enumera
    (`metodo_comum_do_formulario` a remove de propósito). O formulário a grava como `None` quando
    ninguém a declara — e a igualdade bruta então achava diferença entre dois métodos idênticos:
    o documento anunciava *"diverge do comum deste Edital"* sobre um marco que publica, campo a
    campo, exatamente o método comum.

    **E o critério é o que o leitor vê.** O documento imprime os sete; anunciar uma divergência que
    ele não mostra manda quem lê procurar no papel uma diferença que não está lá — num documento
    normativo e imutável, que é onde o erro não tem conserto. A Etapa de habilitação também sai no
    papel (`_habilitacao_ao_sorteio`), e continua fora da comparação: ela **especifica** o que o
    comum não tem como dizer, e não o contraria. Comparar pelo **valor impresso**, e
    não pela chave crua, é o que amarra a afirmação ao artefato: o documento não diz que diverge
    aquilo que ele mesmo mostra igual.
    """
    return all(
        _valor_do_campo_do_metodo(campo, proprio or {})
        == _valor_do_campo_do_metodo(campo, comum or {})
        for campo, _, _ in CAMPOS_DO_METODO
    )


def _origem_do_metodo(snapshot, marco):
    """Qual das três grafias de `Método:` vale para este marco (032, FR-466).

    **Três, e só três** — a quarta, nem próprio nem comum, não chega ao documento: `FR-467` a
    recusa na publicação.

    **A divergência é nomeada quando existe**, e não sempre que há os dois. Um marco que declara o
    próprio idêntico ao comum não diverge de nada, e escrever que diverge seria o documento
    afirmando uma diferença que ninguém publicou — que é o oposto do que a `FR-466` pede. O que
    conta como "idêntico" está em `_publica_a_mesma_norma`, e não é a igualdade bruta.
    """
    proprio = marco.get("drawMethod") or None
    comum = (snapshot or {}).get("drawMethod") or None
    if proprio is None:
        return "comum a este Edital"
    if comum is not None and not _publica_a_mesma_norma(proprio, comum):
        return "próprio deste marco — diverge do comum deste Edital"
    return "próprio deste marco"


def _valor_do_campo_do_metodo(campo, metodo):
    """O valor publicável de um dos sete campos, na grafia que o documento imprime.

    Duas conversões, e as duas existem porque o campo não é texto simples: o instante da ocorrência
    é escrito como um Edital escreve data e hora, e a normalização e a substituição são pares
    `rule`/`text` — imprime-se o `text`, que é a frase publicada que a pessoa lê. O identificador
    fica de fora do papel: ele é o que a máquina aplica, e o terceiro que reimplementa o encontra
    no manifesto do sorteio, não no Edital.
    """
    valor = metodo.get(campo)
    if campo == "occurrenceAt":
        return _instante(valor)
    if isinstance(valor, dict):
        return valor.get("text") or ""
    return str(valor) if valor else ""


def _metodo_do_marco(snapshot, perfil, marco):
    """Os pares do método que governa este marco, na ordem e com os rótulos de `CAMPOS_DO_METODO`.

    **A resolução é a de `marcos.metodo_que_governa`** (032, FR-465), que é o ponto único desde a
    `030`: o marco que não declara método próprio referencia o comum do Edital. Reimplementá-la
    aqui criaria a segunda leitura que a `030` existe para não ter — e a divergência entre as duas
    apareceria como documento publicado dizendo uma coisa e sorteio fazendo outra.

    **O `snapshot` inteiro já chegava a `_marcos`**, e é por isso que o método comum está ao
    alcance sem mudar assinatura nenhuma: ele mora na raiz do mesmo conteúdo.

    **O documento publica a norma, e não o resultado.** Ele imprime a ocorrência que **fixará** a
    semente, e nunca a semente: no dia da publicação ela ainda não existe. Quem publica a semente é
    o documento do resultado do sorteio, que já o faz — e a verificação pública compara os dois.

    Campo vazio não é impresso: numa prévia de rascunho o método pode estar pela metade, e inventar
    o que falta seria o documento completando a regra que o Edital não declarou. No conteúdo
    publicado isso não acontece, porque `FR-467` e `draw_method_invalid` o recusam antes.
    """
    identidade = marco.get("id")
    metodo = (
        regras_do_marco.metodo_que_governa(
            snapshot, perfil_id=perfil.get("id"), marco_id=identidade
        )
        if identidade
        else None
    ) or marco.get("drawMethod")
    if not isinstance(metodo, dict) or not metodo:
        return []
    pares = [["Método", _origem_do_metodo(snapshot, marco)]]
    pares.extend(
        [rotulo, valor]
        for campo, _, rotulo in CAMPOS_DO_METODO
        if (valor := _valor_do_campo_do_metodo(campo, metodo))
    )
    return pares


def _marcos(
    composicao, snapshot, perfil, nomear_perfil=False, *, comum=False, metodo_remetido=None
):
    """As regras de classificação do Perfil, na redação da composição (069, R-004).

    A redação 2 diz a mesma regra em frases e itens, sem os rótulos "Ordem:", "Corte:",
    "Continuação:" (FR-1366); a 1 é a de antes, intacta, para as provas da história.
    """
    if composicao.redacao == REDACAO_1:
        _marcos_na_redacao_1(
            composicao,
            snapshot,
            perfil,
            nomear_perfil,
            comum=comum,
            metodo_remetido=metodo_remetido,
        )
        return
    _marcos_na_redacao_2(
        composicao, snapshot, perfil, nomear_perfil, comum=comum, metodo_remetido=metodo_remetido
    )


def _marcos_na_redacao_2(
    composicao, snapshot, perfil, nomear_perfil=False, *, comum=False, metodo_remetido=None
):
    """As regras de classificação de cada marco, na ordem do contrato da `068` (069, FR-1360).

    A ordem é a de antes: como a ordem nasce, o sorteio, o recurso, a unidade do corte e o
    desempate. O que muda é a forma: os pares viram frases, e as frases da mesma regra viram itens
    de lista, com o recuo pendente que o ED-16 pedia. A coesão e a quebra por partes na subseção
    comum são as da `068`.
    """
    marcos = perfil.get("classificationMilestones") or []
    if not marcos:
        return
    etapas = por_identificador(snapshot.get("stages"))
    fatos = por_identificador(perfil.get("declaredFacts"))
    metodo_remetido = metodo_remetido or {}
    sem_cadastro = sem_cadastro_de_reserva(snapshot)
    degrau = 18.0 if comum else 32.0

    def parte():
        return composicao.bloco() if comum else nullcontext()

    titulo = ROTULO_DAS_REGRAS[REDACAO_2]
    if nomear_perfil:
        titulo = f"{titulo} — {perfil.get('code', '')}"
    with composicao.bloco(coeso=False):
        if not comum:
            composicao.escrever(
                titulo,
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                recuo=18,
                antes=ANTES_DE_BLOCO,
                junto=True,
            )
        for marco in marcos:
            with composicao.bloco(coeso=not comum):
                with parte():
                    composicao.escrever(
                        f"{marco.get('code', '')} — {marco.get('name', '')}",
                        tamanho=CORPO_TEXTO,
                        fonte=NEGRITO,
                        recuo=degrau,
                        antes=ANTES_DE_BLOCO,
                        junto=True,
                    )
                    for frase in frases_da_ordem(snapshot, perfil, marco):
                        _item(composicao, "•", frase, recuo=degrau)
                sorteia = regras_do_marco.declara_sorteio(marco)
                if sorteia and (dados := dados_do_sorteio(snapshot, perfil, marco)):
                    with parte():
                        abertura, pares = dados
                        # As linhas do método comum saem uma vez no documento (068, FR-1349):
                        # aqui, se já saíram noutro item, fica a remissão.
                        if (remetido := metodo_remetido.get(id(marco))) is not None:
                            abertura = ""
                            pares = [
                                ["Método", f"o comum a este Edital, descrito no item {remetido}."]
                            ]
                        # Os dados para conferir o sorteio, em bloco destacado (FR-1376, FR-1382).
                        with composicao.bloco(moldura=DESTAQUE):
                            composicao.escrever(
                                "Sorteio",
                                tamanho=CORPO_TEXTO,
                                fonte=NEGRITO,
                                recuo=degrau,
                                antes=ANTES_DE_BLOCO,
                                junto=True,
                            )
                            if abertura:
                                composicao.escrever(
                                    abertura,
                                    recuo=degrau + 14,
                                    antes=ANTES_DE_LINHA,
                                    justificar=True,
                                )
                            _pares(composicao, pares, recuo=degrau + 14)
                            composicao.espaco(4.0)
                if recurso := frase_do_recurso(marco):
                    with parte():
                        composicao.escrever(
                            "Recurso",
                            tamanho=CORPO_TEXTO,
                            fonte=NEGRITO,
                            recuo=degrau,
                            antes=ANTES_DE_LINHA,
                            junto=True,
                        )
                        composicao.escrever(
                            recurso, recuo=degrau + 14, antes=ANTES_DE_LINHA, justificar=True
                        )
                if corte := frases_do_corte(marco, etapas, sem_cadastro=sem_cadastro):
                    with parte():
                        for indice, frase in enumerate(corte):
                            _item(
                                composicao,
                                "•",
                                frase,
                                recuo=degrau,
                                antes=ANTES_DE_BLOCO if indice == 0 else ANTES_DE_LINHA,
                            )
                if desempate := frases_do_desempate(marco, etapas, fatos):
                    with parte():
                        composicao.escrever(
                            CABECALHO_DO_DESEMPATE,
                            tamanho=CORPO_TEXTO,
                            fonte=NEGRITO,
                            recuo=degrau,
                            antes=ANTES_DE_LINHA,
                            junto=True,
                        )
                        for frase in desempate:
                            ordinal, texto = frase.split(" ", 1)
                            _item(composicao, ordinal, texto, recuo=degrau + 14)


def _item(composicao, marcador, texto, *, recuo, antes=ANTES_DE_LINHA, fonte=REGULAR):
    """Um item de lista: o marcador na margem e o texto alinhado depois dele (069, ED-16, FR-1382).

    **O recuo pendente é a largura do marcador e do espaço**, medida pela métrica da composição: a
    segunda linha começa exatamente sob a primeira palavra do item, e não sob o marcador — era o
    ED-16 da auditoria. O marcador e a primeira linha são um texto só, e por isso o item se lê como
    antes ("• requisito") em qualquer extração.

    **O item não se parte entre páginas** (FR-1391): a continuação de um critério sozinha no topo da
    página seguinte perde o marcador que diz de que item ela é. O que for maior que a página cai no
    último degrau da cascata, e se parte entre linhas — a única exceção que a FR-1391 admite.
    """
    prefixo = f"{marcador} "
    pendente = composicao.metrica.largura(prefixo, CORPO_TEXTO, fonte)
    _registrar_enderecos(composicao, texto)
    linhas = _quebrar(texto, CORPO_TEXTO, recuo + pendente, fonte, metrica=composicao.metrica)
    with composicao.bloco():
        for indice, linha in enumerate(linhas):
            composicao.itens.append(
                (
                    "texto",
                    f"{prefixo}{linha}" if indice == 0 else linha,
                    fonte,
                    CORPO_TEXTO,
                    recuo if indice == 0 else recuo + pendente,
                    antes if indice == 0 else 0.0,
                    ESQUERDA,
                    False,
                    False,
                    False,
                )
            )


def _marcos_na_redacao_1(
    composicao, snapshot, perfil, nomear_perfil=False, *, comum=False, metodo_remetido=None
):
    """Os marcos classificatórios por extenso, com o que basta para refazer a ordem publicada.

    **Deixou de ser tabela, e a troca é a resposta ao que faltava.** Três colunas cabiam enquanto o
    marco dizia só "soma ponderada" e "maior valor declarado"; com o alvo de cada critério, o que
    fazer na ausência do valor, os pesos das Etapas enumeradas, a normalização e o arredondamento,
    a mesma grade viraria um parágrafo espremido em célula. Grade é para comparar linhas entre si —
    e marcos não se comparam: cada um é uma regra que se lê inteira (E2E15-004/005/008).

    **A ordem impressa é a `order` de cada critério**, e não a posição em que ele aparece no
    conteúdo: é ela que a norma declara, e imprimir a posição faria o documento dizer uma coisa e
    o cálculo fazer outra depois de uma Retificação que reordenasse.

    O `snapshot` inteiro chega aqui porque as Etapas são do Edital, não do Perfil: sem elas não há
    como resolver `stageId` para nome nem ler o peso publicado. Os fatos, ao contrário, são do
    Perfil que os declara.

    **Na subseção comum (068), `comum`**: sem o rótulo "Marcos classificatórios" — o título da
    subseção o diz — e um degrau à esquerda, como a `064` fez com as atribuições. O texto é o mesmo,
    linha a linha (FR-1348); muda só o recuo, que é hierarquia, e não regra. `metodo_remetido` diz,
    por marco, o item em que as linhas do método comum já saíram (FR-1349).
    """
    marcos = perfil.get("classificationMilestones") or []
    if not marcos:
        return
    etapas = por_identificador(snapshot.get("stages"))
    fatos = por_identificador(perfil.get("declaredFacts"))
    metodo_remetido = metodo_remetido or {}
    # O degrau do marco: 32 no Perfil, sob o rótulo; 18 na subseção comum, sob o título dela.
    degrau = 18.0 if comum else 32.0

    # **Na subseção comum, o marco quebra entre as suas partes** — cabeçalho e pares, sorteio,
    # recurso e corte, desempate —, e não salta inteiro. Um marco de 25 linhas coeso deixava um
    # terço da página em branco antes da subseção (cenário B da auditoria, p. 9): o branco que a
    # `064` registrou e esta feature existe para não repetir. As partes são fronteiras semânticas,
    # como as do Perfil (FR-021 da `008`). No Perfil, o marco continua coeso como sempre foi: o
    # Edital de um Perfil sai com os mesmos bytes (FR-1356).
    def parte():
        return composicao.bloco() if comum else nullcontext()

    titulo = "Marcos classificatórios"
    if nomear_perfil:
        titulo = f"{titulo} — {perfil.get('code', '')}"
    with composicao.bloco(coeso=False):
        if not comum:
            composicao.escrever(
                titulo,
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                recuo=18,
                antes=ANTES_DE_BLOCO,
                junto=True,
            )
        for marco in marcos:
            with composicao.bloco(coeso=not comum):
                with parte():
                    composicao.escrever(
                        f"{marco.get('code', '')} — {marco.get('name', '')}",
                        tamanho=CORPO_TEXTO,
                        fonte=NEGRITO,
                        recuo=degrau,
                        antes=ANTES_DE_BLOCO,
                        junto=True,
                    )
                    # **Tudo abaixo é decidido pela forma que o marco declara**, e não pela inferida
                    # (032, FR-464). A distinção protege o acervo: marco composto antes da `030` não
                    # declara `orderProduction`, e a ausência **é** a afirmação — ele não ganha o
                    # par `Ordem` e sai do documento exatamente como sempre saiu, com a combinação
                    # que sempre imprimiu. Ler a forma por inferência aqui mudaria a saída de um
                    # marco antigo que carrega método, e documento publicado não muda de conteúdo.
                    forma = marco.get("orderProduction") or ""
                    sorteia = regras_do_marco.declara_sorteio(marco)
                    pares = []
                    ordem = FORMA_DA_ORDEM.get(forma)
                    if ordem:
                        pares.append(["Ordem", ordem])
                    # **Aquela ordem não vem de nota** (032, FR-468). Imprimir "soma ponderada da
                    # Etapa…" sob um marco de sorteio era o documento afirmando um método falso — o
                    # `ACH-50` da auditoria de 16/09/2026, lido no papel que a candidata recebe.
                    if not sorteia:
                        combinacao = _combinacao(marco, etapas)
                        if combinacao:
                            pares.append(["Combinação", combinacao])
                        normalizacao = NORMALIZACAO_DO_MARCO.get(marco.get("normalization"))
                        if normalizacao:
                            pares.append(["Normalização", normalizacao])
                    # **E também não há o que arredondar** (067, ED-03, FR-1313). O sorteio tem a
                    # mesma razão da combinação, e o arredondamento ficou para trás: a validação o
                    # exigia de todo marco, a tela o preenchia, e o documento imprimia "2 casas
                    # decimais, meio para cima" sob uma ordem sorteada. A forma aqui é a declarada,
                    # pela função que a validação e a Revisão também leem (D-004).
                    arredondamento = "" if sorteia else _arredondamento(marco)
                    if arredondamento:
                        pares.append(["Arredondamento", arredondamento])
                    _pares(composicao, pares, recuo=degrau)
                # O bloco do método, entre o arredondamento e o recurso — a ordem é a que
                # `contracts/marco-no-documento.md` fixa, e ela faz parte do contrato.
                if sorteia and (metodo := _metodo_do_marco(snapshot, perfil, marco)):
                    with parte():
                        # Depois dos sete, e fora deles: não é campo do método comum, e por isso não
                        # entra na comparação que nomeia a divergência (`_publica_a_mesma_norma`).
                        # As linhas do método comum saem uma vez no documento (068, FR-1349): aqui,
                        # se já saíram noutro item, fica a remissão — e a habilitação, que é do
                        # marco.
                        if (remetido := metodo_remetido.get(id(marco))) is not None:
                            metodo = [
                                ["Método", f"o comum a este Edital, descrito no item {remetido}."]
                            ]
                        if habilitacao := _habilitacao_ao_sorteio(snapshot, perfil, marco, etapas):
                            metodo = [*metodo, ["Habilitação", habilitacao]]
                        composicao.escrever(
                            "Sorteio",
                            tamanho=CORPO_TEXTO,
                            fonte=NEGRITO,
                            recuo=degrau,
                            antes=ANTES_DE_LINHA,
                            junto=True,
                        )
                        _pares(composicao, metodo, recuo=degrau + 14)
                with parte():
                    posteriores = []
                    janela = _janela_recursal(marco)
                    if janela:
                        posteriores.append(["Recurso", janela])
                    corte = _regra_de_corte(marco, etapas)
                    if corte:
                        posteriores.append(["Corte", corte])
                        # A ordem sorteada é total — cada posição é única —, e o empate na última
                        # posição não acontece (067, FR-1314). A validação já não exige o desfecho
                        # sob sorteio (`FR-928`); o documento ainda o imprimia quando gravado.
                        if not sorteia and (empate := _empate_no_corte(marco)):
                            posteriores.append(["Empate no corte", empate])
                        if continuacao := _continuacao_do_corte(marco):
                            posteriores.append(["Continuação", continuacao])
                    _pares(composicao, posteriores, recuo=degrau)
                criterios = sorted(
                    marco.get("tiebreakers") or [], key=lambda item: item.get("order") or 0
                )
                if not criterios:
                    continue
                with parte():
                    composicao.escrever(
                        "Critérios de desempate:",
                        tamanho=CORPO_TEXTO,
                        fonte=NEGRITO,
                        recuo=degrau,
                        antes=ANTES_DE_LINHA,
                        junto=True,
                    )
                    for indice, criterio in enumerate(criterios, start=1):
                        frase = criterio_com_a_ausencia(criterio, etapas, fatos, redacao=REDACAO_1)
                        composicao.escrever(
                            f"{indice}º {frase}",
                            tamanho=CORPO_TEXTO,
                            recuo=degrau + 14,
                            antes=ANTES_DE_LINHA,
                        )


def _fatos_declarados(composicao, perfil):
    """Os dados que a inscrição vai exigir, anunciados antes de ela começar (E2E15-005).

    O Edital declara `declaredFacts`, a inscrição os exige e os **congela na submissão**, e o
    desempate os consome — mas o documento normativo nunca os lia. O candidato descobria quais
    dados seriam coletados na tela de revisão, no instante do envio: um dado irreversível exigido
    sem aviso prévio no único texto que o obriga.

    **Aqui, e não numa seção institucional.** "CRITÉRIOS DE CLASSIFICAÇÃO" é texto padrão vindo de
    `sections`, e dado derivado não se enxerta em texto de catálogo. O lugar é o Perfil que os
    declara, ao lado dos Requisitos — onde quem está decidindo se concorre àquela vaga já está
    lendo o que ela exige, e antes das Modalidades e dos marcos que os consomem.

    **O documento anuncia o que será exigido; não afirma o que o sistema faz com o valor.** O
    congelamento na submissão é comportamento da inscrição e não viaja no conteúdo publicado —
    escrevê-lo aqui seria o Edital afirmando regra que a Publicação não contém.
    """
    fatos = perfil.get("declaredFacts") or []
    if not fatos:
        return
    if composicao.redacao != REDACAO_1:
        # V10: os mesmos dados, sem o tipo entre parênteses (FR-1366), em itens de lista.
        with composicao.bloco():
            composicao.escrever(
                ANUNCIO_DOS_DADOS_DECLARADOS,
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                recuo=18,
                antes=ANTES_DE_BLOCO,
                junto=True,
            )
            for item in itens_dos_dados_declarados(fatos):
                _item(composicao, "•", item, recuo=32)
        return
    with composicao.bloco():
        composicao.escrever(
            "Dados exigidos na inscrição",
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            recuo=18,
            antes=ANTES_DE_BLOCO,
            junto=True,
        )
        for fato in fatos:
            rotulo = fato.get("label") or fato.get("code", "")
            tipo = TIPO_DO_FATO.get(fato.get("type"))
            composicao.escrever(
                f"• {rotulo} ({tipo})" if tipo else f"• {rotulo}",
                tamanho=CORPO_TEXTO,
                recuo=32,
            )


def _quadro_de_vagas_do_perfil(composicao, perfil, tabelas, nomear_perfil=False):
    """O quadro de vagas: quantas vagas cabem em cada lista de concorrência (025, FR-169).

    **Bloco próprio, e não coluna nova na tabela de Modalidades.** Aquela tabela já omite coluna sem
    valor, e acrescentar "Vagas" ali seria tentador e barato. Mas ela é tabela de **Modalidades**, e
    a linha geral não é Modalidade nenhuma: o `AC 56` não teria onde morar, que é precisamente o
    defeito que a D-002 recusou no modelo de dados. Repeti-lo na apresentação publicaria um quadro
    que não fecha.

    **A linha geral vem primeiro**, rotulada "Ampla concorrência", independentemente da posição
    dela no array — é apresentação, e é o que a D-009 autoriza. As reservadas saem na ordem
    declarada, que não é recalculada nem alfabetizada.

    **Sem quadro, o bloco não sai — e nenhuma frase o substitui.** Um "quadro não declarado"
    impresso seria uma afirmação nova sobre um Edital que não a fez, e é o que a SC-050 cobra:
    nenhum Edital publicado antes desta feature passa a afirmar zero vaga em lugar nenhum.

    **Sem vaga imediata, nem quadro nem reversão** (067, ED-12, D-003). O Perfil só de cadastro de
    reserva imprimia um quadro inteiro de zeros e a frase sobre "vagas reservadas" que não existem
    — reserva de vaga onde não há vaga (16 Perfis no cenário B da auditoria de 08/10/2026). O que
    é verdade continua: a linha do Perfil, com 0 vaga e o cadastro, e a tabela de Modalidades, com
    percentual e fundamento. **E nenhuma frase o substitui**: como a reserva se aplica ao cadastro
    (RC-58) não é regra que o sistema declare — a convocação desses Perfis é feita fora dele.
    """
    linhas_do_quadro = perfil.get("vacancyTable") or []
    if not linhas_do_quadro or quadro_do_perfil.sem_vaga_imediata(perfil):
        return
    denominacoes = {
        str(modalidade.get("id")): (
            f"{modalidade.get('name', '')} ({modalidade.get('code', '')})"
            if modalidade.get("code")
            else modalidade.get("name", "")
        )
        for modalidade in perfil.get("competitionModalities") or []
        if modalidade.get("id")
    }
    gerais = [linha for linha in linhas_do_quadro if not linha.get("modalityId")]
    reservadas = [linha for linha in linhas_do_quadro if linha.get("modalityId")]
    linhas = [
        [
            "Ampla concorrência"
            if not linha.get("modalityId")
            else denominacoes.get(str(linha["modalityId"]), ""),
            str(linha.get("immediateVacancies", 0)),
        ]
        for linha in gerais + reservadas
    ]
    titulo = "Quadro de vagas"
    if nomear_perfil:
        titulo = f"{titulo} — {perfil.get('code', '')}"
    with composicao.bloco():
        _tabela(
            composicao,
            ["Lista de concorrência", "Vagas imediatas"],
            linhas,
            alinhamentos=[ESQUERDA, CENTRO],
            legenda=tabelas.legenda(titulo),
        )
    _reversao_declarada(composicao, perfil)


def _reversao_declarada(composicao, perfil):
    """A frase da reversão, abaixo do quadro que ela governa (016, D-007).

    **Sai junto do quadro, e não em bloco próprio**, porque é uma regra sobre aquelas quantidades:
    lida longe delas, o candidato teria de procurar a qual Perfil ela se aplica.

    **Sem declaração, nenhuma frase sai** — nem "não há reversão". É a mesma disciplina que a `025`
    aplicou ao quadro ausente: um Edital que não declarou reversão não passa a afirmar coisa alguma
    sobre ela, e imprimir a negação seria afirmação nova sobre ato já publicado.
    """
    especie = (perfil.get("vacancyReversion") or {}).get("kind")
    if not especie:
        return
    # A frase é a de `frase_da_reversao`, a mesma que a seção consolidada imprime (068): duas
    # grafias da mesma regra em dois lugares é como uma delas fica para trás.
    frase = frase_da_reversao(especie, redacao=composicao.redacao)
    if not frase:
        return
    with composicao.bloco():
        # `escrever`, e não `paragrafo`: a `Composicao` não tem esse método, e eu o inventei por
        # analogia. O teste da reversão pegou — a publicação inteira devolvia 500.
        composicao.escrever(frase, antes=4.0, justificar=True)


def _forma_de_convocacao_declarada(composicao, perfil):
    """Como este Perfil comunica a convocação (019, D-009, R-007).

    **Fora de `_quadro_de_vagas_do_perfil`, e não dentro dele.** A reversão mora lá porque é regra
    sobre aquelas quantidades; esta é regra sobre como a pessoa é alcançada, e existe mesmo em
    Perfil sem quadro publicado. Pô-la lá a faria desaparecer exatamente nos Editais anteriores ao
    degrau 12 — que são os que mais precisam dela impressa.

    **Sem declaração, nenhuma frase sai — nem "não declarou".** É a disciplina que a `025` aplicou
    ao quadro ausente e que a `016` repetiu na reversão: um Edital que não declarou forma não passa
    a afirmar coisa alguma sobre ela, e imprimir a negação seria afirmação nova sobre ato já
    publicado. Quem convoca é que encontra a recusa, na tela, e não o leitor do documento.

    **A frase vem do vocabulário do publicado**, e não é escrita aqui: duas grafias da mesma forma
    em módulos diferentes é como uma delas fica para trás — e aqui a renomeação seria uma
    Retificação, que o outro lado nem veria.
    """
    frase = frase_da_convocacao(perfil.get("callForm"), redacao=composicao.redacao)
    if not frase:
        return
    with composicao.bloco():
        composicao.escrever(frase, antes=4.0, justificar=True)


def _modalidades(composicao, perfil, tabelas, nomear_perfil=False):
    """As modalidades em tabela — sem perder o que a frase corrida dizia (FR-018, FR-019).

    O documento anterior imprimia `Regra Normativa — fundamento: …; versão: …; percentual: …`.
    A frase sai; versão e vigência **permanecem**, porque tabular não pode virar perder. E
    modalidade sem percentual não ganha célula construída para preencher a coluna: a ausência é
    materializada como ausência.
    """
    modalidades = perfil.get("competitionModalities") or []
    if not modalidades:
        return
    linhas = []
    for modalidade in modalidades:
        regra = modalidade.get("normativeRule") or {}
        percentual = regra.get("percentage")
        linhas.append(
            [
                f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
                f"{humano.decimal(percentual)}%" if percentual else "",
                regra.get("foundation", "") or "",
            ]
        )
    # Coluna em que **nenhuma** modalidade tem valor não é impressa. Um Edital só de ampla
    # concorrência não deve exibir uma coluna de percentual inteira vazia: seria informação
    # inexistente ocupando espaço para preencher a tabela (FR-019).
    # **A versão da Regra Normativa não é matéria de Edital.** Ela é proveniência, e sai pela mesma
    # razão que `schemaVersion` e os UUIDs saíram: o candidato lê o fundamento — a lei que reserva
    # a vaga —, não a data em que a regra foi cadastrada. Continua no conteúdo publicado.
    cabecalho = ["Modalidade", "Percentual", "Fundamento normativo"]
    presentes = [c for c in range(len(cabecalho)) if any(linha[c] for linha in linhas)]
    titulo = "Modalidades de concorrência"
    if nomear_perfil:
        titulo = f"{titulo} — {perfil.get('code', '')}"
    with composicao.bloco():
        _tabela(
            composicao,
            [cabecalho[c] for c in presentes],
            [[linha[c] or "—" for c in presentes] for linha in linhas],
            alinhamentos=[ESQUERDA if c == 0 else CENTRO for c in presentes],
            legenda=tabelas.legenda(titulo),
        )


def _quadro_de_perfis(composicao, perfis, tabelas):
    """A visão global antes do detalhe: os Perfis lado a lado.

    Um card por Perfil responde "como apresento esta entidade?". O Edital pergunta outra coisa:
    "qual a melhor composição para comunicar esta matéria?" — e a resposta, para dados comparáveis
    entre si, é uma tabela que os põe lado a lado. Com dez Perfis, dez fichas obrigam o leitor a
    percorrer o documento inteiro para saber quantas vagas existem.

    **Esta função chamava-se `_quadro_de_vagas`, e o nome estava errado.** Ela tabula *Perfis* —
    `Perfil`, `Localidade`, `Vagas`, `Cadastro reserva`, `Carga horária` —, e não a repartição das
    vagas por lista de concorrência, que é o que o domínio chama de quadro de vagas e que a `025`
    passou a publicar em `_quadro_de_vagas_do_perfil`. O Princípio I proíbe o mesmo termo nomear
    dois conceitos.

    **A renomeação da função não mudou o documento; a da legenda mudou, de propósito.** Trocar o
    nome de uma função privada não altera byte nenhum do que se publica — mas quem lê o Edital lê a
    legenda, e ela continuava dizendo "Quadro de vagas" algumas linhas acima da tabela que agora
    tem esse nome. Ela passou a dizer "Perfis de vaga", e o documento mudou aí.

    **A fixture de bytes não pega essa mudança**, e é bom saber por quê antes de confiar nela: ela
    tem um Perfil só, e esta tabela só é composta com mais de um. Quem mexer aqui confere o
    resultado por `test_as_duas_tabelas_de_vagas_nao_se_chamam_a_mesma_coisa`, que compõe dois.
    """
    linhas = []
    for perfil in perfis:
        linhas.append(
            [
                f"{perfil.get('code', '')} — {perfil.get('name', '')}",
                perfil.get("locality", "") or "—",
                str(perfil.get("immediateVacancies", 0)),
                _reserva(perfil, redacao=composicao.redacao),
                perfil.get("workload", "") or "—",
            ]
        )
    cadastro = "Cadastro reserva" if composicao.redacao == REDACAO_1 else "Cadastro de reserva"
    _tabela(
        composicao,
        ["Perfil", "Localidade", "Vagas", cadastro, "Carga horária"],
        linhas,
        recuo=0.0,
        alinhamentos=[ESQUERDA, ESQUERDA, CENTRO, ESQUERDA, CENTRO],
        # **A legenda mudou com a `025`, e não é ajuste de gosto** (E2E25-005). Ela dizia "Quadro
        # de vagas", e o documento passou a publicar, algumas linhas abaixo, uma tabela com esse
        # nome que é outra coisa: a repartição das vagas de **um** Perfil por lista de
        # concorrência. Duas tabelas homônimas no mesmo documento, dizendo coisas diferentes, é
        # exatamente a ambiguidade que o Princípio I existe para não ter — e a renomeação da
        # função privada, sozinha, não a alcançava, porque quem lê o Edital lê a legenda.
        legenda=tabelas.legenda("Perfis de vaga"),
        # **O total de vagas** (054, FR-997). Nenhum lugar do documento somava as vagas, e o leitor
        # de um Edital com sete polos fazia a conta; o 28/2026 fecha o quadro com "Total de vagas
        # 280". Só as imediatas: o cadastro reserva não é vaga, e somá-lo diria que há mais vagas
        # do que o Edital oferece.
        #
        # **Sem vaga imediata, não há linha de total.** No Edital só de cadastro de reserva — o
        # 89/2026, de Mediadores UAB, cadastrado em 30/09 — a linha dizia "Total 0", e o leitor
        # entendia que o Edital não oferece nada, quando oferece o cadastro. A coluna "Cadastro
        # reserva" da mesma tabela já diz o que há.
        rodape=["Total", "", str(total), "", ""] if (total := _total_de_vagas(perfis)) else None,
    )


def _total_de_vagas(perfis):
    total = 0
    for perfil in perfis:
        try:
            total += int(perfil.get("immediateVacancies") or 0)
        except (TypeError, ValueError):
            continue
    return total


def _perfis(composicao, snapshot, secao=0, tabelas=None):
    """A tabela comparativa de Perfis, e depois cada Perfil como subseção.

    **Sem moldura externa.** O retângulo em volta de tudo produzia um cartão de interface
    impresso: tabela dentro de caixa dentro de caixa. Um Edital descreve a vaga em prosa e
    subtítulo numerado, e reserva a grade para o que é matriz.

    A subseção é numerada a partir da seção-mãe já resolvida, como as Etapas (FR-013).

    **Com dois ou mais Perfis, o que se repete sai uma vez** (064 e 068). As atribuições (064), os
    requisitos e os marcos idênticos vão a subseções comuns **depois do último Perfil**, e cada
    Perfil do grupo remete a elas; as vagas saem numa tabela Perfil × lista e as modalidades em
    tabelas agrupadas, logo depois da tabela de Perfis; as frases de reversão e de convocação, uma
    vez, abaixo delas. Pôr as subseções no fim, e não antes dos Perfis, é o que deixa intactos os
    números dos Perfis — que o texto livre do Edital cita ("conforme o item 5.2") e que uma
    inserção no meio deslocaria em silêncio a cada Retificação que desfizesse um grupo (068, D-001).

    O Edital de um Perfil não passa por nada disso: sai como saía, byte a byte (068, FR-1356).
    """
    perfis = snapshot.get("profiles") or []
    if len(perfis) == 1:
        _perfil_unico(composicao, snapshot, perfis[0], secao, tabelas)
        return
    if not perfis:
        return
    plano = plano_de_consolidacao(
        snapshot, secao, metrica=composicao.metrica, redacao=composicao.redacao
    )
    _quadro_de_perfis(composicao, perfis, tabelas)
    _tabela_de_vagas(composicao, plano, tabelas)
    _frases_consolidadas(composicao, plano.reversoes)
    for grupo in plano.modalidades:
        _tabela_de_modalidades(composicao, grupo, len(perfis), tabelas)
    _frases_consolidadas(composicao, plano.convocacoes)

    for ordem, perfil in enumerate(perfis, 1):
        with composicao.bloco(coeso=False):
            _identificacao_do_perfil(composicao, perfil, f"{secao}.{ordem}")
            if numero := plano.remissao(perfil, ATRIBUICOES):
                _remissao(composicao, "Atribuições", f"as descritas no item {numero}.")
            else:
                _atribuicoes(composicao, perfil)
            if perfil.get("compensation"):
                composicao.escrever(
                    f"Remuneração: {perfil['compensation']}",
                    tamanho=CORPO_TEXTO,
                    recuo=18,
                    antes=ANTES_DE_LINHA,
                )
            if numero := plano.remissao(perfil, REQUISITOS):
                _remissao(composicao, "Requisitos", f"os descritos no item {numero}.")
            else:
                _requisitos(composicao, perfil)
            _fatos_declarados(composicao, perfil)
            if numero := plano.remissao(perfil, MARCOS):
                _remissao(composicao, *remissao_as_regras(numero, redacao=composicao.redacao))
            else:
                _marcos(composicao, snapshot, perfil, True, metodo_remetido=plano.metodo_remetido)

    for subsecao in plano.subsecoes:
        if subsecao.materia == ATRIBUICOES:
            _atribuicoes_comuns(composicao, subsecao.perfis, subsecao.numero)
        elif subsecao.materia == REQUISITOS:
            _requisitos_comuns(composicao, subsecao.perfis, subsecao.numero)
        else:
            _marcos_comuns(composicao, snapshot, subsecao, plano.metodo_remetido)


def _perfil_unico(composicao, snapshot, perfil, secao, tabelas):
    """O Perfil do Edital de um Perfil só — a composição de antes da `064`, sem mudar um item.

    Os pares de identificação, a carga horária e o quadro e as modalidades dentro do Perfil: sem
    tabela de Perfis acima, este é o único lugar onde eles saem.
    """
    with composicao.bloco(coeso=False):
        _identificacao_do_perfil(composicao, perfil, f"{secao}.1")
        with composicao.bloco():
            _pares(
                composicao,
                [
                    ["Localidade", perfil.get("locality", "") or "—"],
                    ["Vagas imediatas", str(perfil.get("immediateVacancies", 0))],
                    [
                        "Cadastro reserva"
                        if composicao.redacao == REDACAO_1
                        else "Cadastro de reserva",
                        _reserva(perfil, redacao=composicao.redacao),
                    ],
                ],
            )
        _atribuicoes(composicao, perfil)
        for rotulo, chave in (("Carga horária", "workload"), ("Remuneração", "compensation")):
            if perfil.get(chave):
                composicao.escrever(
                    f"{rotulo}: {perfil[chave]}",
                    tamanho=CORPO_TEXTO,
                    recuo=18,
                    antes=ANTES_DE_LINHA,
                )
        _requisitos(composicao, perfil)
        _fatos_declarados(composicao, perfil)
        _quadro_de_vagas_do_perfil(composicao, perfil, tabelas, False)
        _forma_de_convocacao_declarada(composicao, perfil)
        _modalidades(composicao, perfil, tabelas, False)
        _marcos(composicao, snapshot, perfil, False)


def _identificacao_do_perfil(composicao, perfil, numero):
    with composicao.bloco():
        composicao.escrever(
            f"{numero} {perfil.get('code', '')} — {perfil.get('name', '')}",
            tamanho=CORPO_SUBSECAO,
            fonte=NEGRITO,
            antes=ANTES_DE_BLOCO + 4,
            junto=True,
        )
        if perfil.get("description"):
            composicao.escrever(
                perfil["description"],
                tamanho=CORPO_TEXTO,
                recuo=18,
                antes=ANTES_DE_PARAGRAFO,
                justificar=True,
            )


def _atribuicoes(composicao, perfil):
    """O bloco próprio de atribuições do Perfil — o que a `064` não juntou."""
    if not perfil.get("duties"):
        return
    with composicao.bloco():
        composicao.escrever(
            "Atribuições",
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            recuo=18,
            antes=ANTES_DE_BLOCO,
            junto=True,
        )
        for paragrafo in _paragrafos(perfil["duties"]):
            composicao.escrever(
                paragrafo,
                tamanho=CORPO_TEXTO,
                recuo=32,
                antes=ANTES_DE_LINHA,
                justificar=True,
            )


def _requisitos(composicao, perfil):
    """O bloco próprio de requisitos — e a chave da identidade deles (068, R-002)."""
    requisitos = perfil.get("requirements") or []
    if not requisitos:
        return
    with composicao.bloco():
        composicao.escrever(
            "Requisitos",
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            recuo=18,
            antes=ANTES_DE_BLOCO,
            junto=True,
        )
        for requisito in requisitos:
            if composicao.redacao == REDACAO_1:
                composicao.escrever(f"• {requisito}", tamanho=CORPO_TEXTO, recuo=32)
            else:
                _item(composicao, "•", requisito, recuo=32, antes=0.0)


def _remissao(composicao, rotulo, valor):
    """Rótulo e valor na mesma linha, no lugar do bloco que o Perfil não imprime (064, 068).

    Como "Localidade:" no Edital de um Perfil: a remissão é um valor curto, e o rótulo continua onde
    o candidato o procura. Com o espaço de sub-bloco, e não o de linha: é o mesmo degrau do
    cabeçalho do bloco no Perfil vizinho, e os dois não podem parecer níveis diferentes.
    """
    with composicao.bloco():
        _pares(composicao, [[rotulo, valor]], antes=ANTES_DE_BLOCO)


# ---------------------------------------------------------------------------
# 068 — O plano de consolidação
# ---------------------------------------------------------------------------

ATRIBUICOES, REQUISITOS, MARCOS = "atribuicoes", "requisitos", "marcos"
AMPLA_CONCORRENCIA = "Ampla concorrência"
MATRIZ, FORMA_LONGA = "matriz", "longa"
TITULO_DA_SUBSECAO = {
    ATRIBUICOES: "Atribuições comuns aos Perfis",
    REQUISITOS: "Requisitos comuns aos Perfis",
    MARCOS: "Marcos classificatórios comuns aos Perfis",
}
# A frase que a subseção comum de marcos diz antes deles (068, FR-1347). O marco é **de cada
# Perfil** — cada um tem a sua ordem e o seu resultado, e recorre-se contra o resultado de cada um.
# Impresso uma vez sob "comuns aos Perfis …", sem ela, ele se leria como uma classificação conjunta:
# no cenário B da auditoria, "os 10 primeiros" passaria a valer para os 18 Perfis somados. Ela não
# fala em corte, porque nem todo marco tem corte, e afirmaria regra que o marco não declara.
MARCOS_SEPARADAMENTE = (
    "Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as inscrições do "
    "próprio Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado."
)
FRASE_DA_REVERSAO = {
    "ON_EXHAUSTION": (
        "Havendo ausência de candidatos aprovados na reserva de vagas, o quantitativo será "
        "destinado à respectiva ampla concorrência."
    ),
    "ON_BALANCE": (
        "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não "
        "preenchido será destinado à respectiva ampla concorrência."
    ),
}


@dataclass(frozen=True)
class SubsecaoComum:
    """Uma subseção que imprime uma vez o bloco de um grupo de Perfis."""

    numero: str
    materia: str
    perfis: tuple

    @property
    def codigos(self):
        return tuple(perfil.get("code", "") for perfil in self.perfis)


@dataclass(frozen=True)
class TabelaDeVagas:
    forma: str
    cabecalho: tuple
    linhas: tuple


@dataclass(frozen=True)
class GrupoDeModalidades:
    perfis: tuple
    cabecalho: tuple
    linhas: tuple


@dataclass(frozen=True)
class FraseConsolidada:
    """Uma frase do Perfil dita uma vez; `codigos` vazio quando ela vale para todos."""

    texto: str
    codigos: tuple = ()


@dataclass(frozen=True)
class PlanoDeConsolidacao:
    """Tudo o que a composição decide antes de escrever a seção de Perfis (068, R-001).

    **Antes, e não durante**: a remissão sai antes do item a que remete, e o método comum pode ser
    impresso num Perfil e remetido de uma subseção posterior. O número tem de existir antes de a
    primeira linha ser escrita, e tem de vir da mesma lista que numera as subseções — duas
    contagens poderiam divergir e publicar uma remissão para o item errado. E as funções que dizem
    o que o documento numera (`itens_do_documento`, `tabelas_do_documento`) leem este mesmo plano,
    para que a conferência de remissões da `065` veja o que a composição escreve (D-004 dela).

    As chaves de `remissoes` e de `metodo_remetido` são a identidade do objeto, e não o `id` do
    Perfil ou do marco, que nada obriga a ser único no snapshot que chega aqui — é a escolha da
    `064`. Por isso o plano vale para o snapshot de que foi calculado, e para nenhum outro.
    """

    subsecoes: tuple
    remissoes: dict
    listas: tuple
    vagas: TabelaDeVagas | None
    modalidades: tuple
    reversoes: tuple
    convocacoes: tuple
    metodo_remetido: dict

    def remissao(self, perfil, materia):
        return self.remissoes.get((id(perfil), materia))


def _itens_do_bloco(funcao, *argumentos, redacao=REDACAO_VIGENTE, **nomeados):
    """Os itens que `funcao` escreveria — a identidade de um bloco impresso (068, R-002, D-003).

    É a definição literal de "o documento os imprimiria iguais": texto, fonte, corpo, recuo,
    espaço, fronteiras de bloco, linha a linha. Uma chave por campos do snapshot teria de reproduzir
    cada regra do compositor — o método que governa, a habilitação, a ordem dos critérios, as
    omissões da `067` sob sorteio — e divergiria dele na primeira mudança.
    """
    rascunho = Composicao(redacao=redacao)
    funcao(rascunho, *argumentos, **nomeados)
    return tuple(rascunho.itens)


def _agrupar(perfis, chave):
    """Os grupos de dois ou mais Perfis de mesma chave, na ordem do primeiro de cada um.

    Chave vazia — bloco que não sai — não agrupa, como na `064` (FR-1188).
    """
    por_chave = {}
    for perfil in perfis:
        if valor := chave(perfil):
            por_chave.setdefault(valor, []).append(perfil)
    return [tuple(grupo) for grupo in por_chave.values() if len(grupo) > 1]


def plano_de_consolidacao(snapshot, secao=0, *, metrica=HELVETICA, redacao=REDACAO_VIGENTE):
    """O plano da seção de Perfis, ou `None` com um Perfil só (068, R-001, R-003).

    `metrica` é a da composição que vai escrever a seção (069): ela decide se a tabela de vagas
    cabe lado a lado. Quem só conta itens e tabelas não depende dela — a forma da tabela muda, a
    quantidade não.
    """
    perfis = snapshot.get("profiles") or []
    if len(perfis) < 2:
        return None
    grupos = [
        (ATRIBUICOES, [tuple(grupo) for grupo in grupos_de_atribuicoes(perfis)]),
        (
            REQUISITOS,
            _agrupar(perfis, lambda perfil: _itens_do_bloco(_requisitos, perfil, redacao=redacao)),
        ),
        (
            MARCOS,
            _agrupar(
                perfis,
                lambda perfil: _itens_do_bloco(_marcos, snapshot, perfil, False, redacao=redacao),
            ),
        ),
    ]
    subsecoes, remissoes = [], {}
    proximo = len(perfis) + 1
    for materia, da_materia in grupos:
        for grupo in da_materia:
            numero = f"{secao}.{proximo}"
            proximo += 1
            subsecoes.append(SubsecaoComum(numero, materia, grupo))
            for perfil in grupo:
                remissoes[(id(perfil), materia)] = numero
    listas = _ordem_das_listas(perfis)
    return PlanoDeConsolidacao(
        subsecoes=tuple(subsecoes),
        remissoes=remissoes,
        listas=listas,
        vagas=_plano_da_tabela_de_vagas(perfis, listas, metrica),
        modalidades=_grupos_de_modalidades(perfis, listas),
        reversoes=_frases_da_reversao(perfis, redacao),
        convocacoes=_frases_da_convocacao(perfis, redacao),
        metodo_remetido=_metodo_remetido(snapshot, perfis, secao, subsecoes, remissoes),
    )


def _rotulo_da_lista(modalidade):
    """Como a lista aparece no cabeçalho da tabela de vagas: o código, ou o nome sem código."""
    return modalidade.get("code") or modalidade.get("name", "")


def _reservadas_no_quadro(perfil):
    """`[(rótulo, modalidade, linha)]` das listas reservadas do quadro, na ordem declarada."""
    modalidades = {
        str(modalidade.get("id")): modalidade
        for modalidade in perfil.get("competitionModalities") or []
        if modalidade.get("id")
    }
    reservadas = []
    for linha in perfil.get("vacancyTable") or []:
        if not linha.get("modalityId"):
            continue
        modalidade = modalidades.get(str(linha["modalityId"]), {})
        reservadas.append((_rotulo_da_lista(modalidade), modalidade, linha))
    return reservadas


def _ordem_das_listas(perfis):
    """Uma ordem de listas para o documento inteiro (068, R-005, ED-11).

    A linha geral primeiro; as reservadas na ordem em que os quadros as declaram, Perfil a Perfil —
    a primeira ocorrência decide —; as modalidades que nenhum quadro declara, na ordem do snapshot.
    O quadro é a única ordem que alguém escolheu: a do snapshot é a do código, pela collation do
    banco, e era por isso que o mesmo Perfil imprimia PPI, PcD no quadro e PcD, PPI na tabela de
    modalidades.

    A modalidade de ampla concorrência declarada não é lista: é a "grafia armadilha" da linha
    geral, e fica de fora.
    """
    listas = [AMPLA_CONCORRENCIA]
    for perfil in perfis:
        for rotulo, _, _ in _reservadas_no_quadro(perfil):
            if rotulo not in listas:
                listas.append(rotulo)
    for perfil in perfis:
        geral = perfil.get("generalCompetitionModalityId")
        for modalidade in perfil.get("competitionModalities") or []:
            rotulo = _rotulo_da_lista(modalidade)
            if modalidade.get("id") != geral and rotulo not in listas:
                listas.append(rotulo)
    return tuple(listas)


def _com_vaga_no_quadro(perfil):
    """O Perfil tem linha na tabela de vagas? Quadro declarado e vaga imediata (067, D-003)."""
    return bool(perfil.get("vacancyTable")) and not quadro_do_perfil.sem_vaga_imediata(perfil)


def _plano_da_tabela_de_vagas(perfis, listas, metrica=HELVETICA):
    """A tabela de vagas: matriz quando cabe, forma longa quando não (068, R-004, FR-1342)."""
    com_vaga = [perfil for perfil in perfis if _com_vaga_no_quadro(perfil)]
    if not com_vaga:
        return None
    por_perfil = []
    for perfil in com_vaga:
        celulas = {}
        for linha in perfil.get("vacancyTable") or []:
            if not linha.get("modalityId"):
                celulas[AMPLA_CONCORRENCIA] = (AMPLA_CONCORRENCIA, linha)
        for rotulo, modalidade, linha in _reservadas_no_quadro(perfil):
            nome = modalidade.get("name", "")
            completo = f"{nome} ({modalidade['code']})" if modalidade.get("code") else nome
            celulas[rotulo] = (completo, linha)
        por_perfil.append((perfil, celulas))
    colunas = [rotulo for rotulo in listas if any(rotulo in celulas for _, celulas in por_perfil)]
    matriz = tuple(
        (
            perfil.get("code", ""),
            *(
                str(celulas[rotulo][1].get("immediateVacancies", 0)) if rotulo in celulas else "—"
                for rotulo in colunas
            ),
        )
        for perfil, celulas in por_perfil
    )
    cabecalho = ("Perfil", *colunas)
    if _cabe_lado_a_lado(cabecalho, matriz, metrica=metrica):
        return TabelaDeVagas(MATRIZ, cabecalho, matriz)
    longa = tuple(
        (
            perfil.get("code", "") if indice == 0 else "",
            celulas[rotulo][0],
            str(celulas[rotulo][1].get("immediateVacancies", 0)),
        )
        for perfil, celulas in por_perfil
        for indice, rotulo in enumerate(rotulo for rotulo in colunas if rotulo in celulas)
    )
    return TabelaDeVagas(FORMA_LONGA, ("Perfil", "Lista de concorrência", "Vagas imediatas"), longa)


def _cabe_lado_a_lado(cabecalho, linhas, recuo=0.0, metrica=HELVETICA):
    """As colunas cabem na página sem partir palavra? (068, R-004)

    A largura mínima de uma coluna é a da sua maior palavra, no cabeçalho ou numa célula, mais o
    padding. `_larguras_das_colunas` reparte o espaço entre as colunas longas, e uma palavra maior
    que a coluna seria partida ao meio por `_quebrar` — o código da lista ilegível no cabeçalho.
    """
    minimas = [
        max(
            max(
                metrica.largura(palavra, CORPO_TABELA, NEGRITO)
                for palavra in (cabecalho[c].split() or [""])
            ),
            *(
                metrica.largura(palavra, CORPO_TABELA, REGULAR)
                for linha in linhas
                for palavra in (str(linha[c]).split() or [""])
            ),
        )
        + PADDING_DA_COLUNA
        for c in range(len(cabecalho))
    ]
    return sum(minimas) <= LARGURA - 2 * MARGEM - recuo


def _linhas_de_modalidades(perfil, listas):
    """O cabeçalho e as linhas da tabela de modalidades do Perfil, na ordem das listas (068, R-005).

    As células são as de `_modalidades`; muda só a ordem das linhas: a modalidade de ampla
    concorrência declarada à frente, depois a ordem do documento, e o que ela não tem, como veio.
    """
    modalidades = perfil.get("competitionModalities") or []
    if not modalidades:
        return None
    geral = perfil.get("generalCompetitionModalityId")

    def posicao(par):
        indice, modalidade = par
        rotulo = _rotulo_da_lista(modalidade)
        return (
            0 if geral and modalidade.get("id") == geral else 1,
            listas.index(rotulo) if rotulo in listas else len(listas),
            indice,
        )

    linhas = []
    for _, modalidade in sorted(enumerate(modalidades), key=posicao):
        regra = modalidade.get("normativeRule") or {}
        percentual = regra.get("percentage")
        linhas.append(
            [
                f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
                f"{humano.decimal(percentual)}%" if percentual else "",
                regra.get("foundation", "") or "",
            ]
        )
    cabecalho = ["Modalidade", "Percentual", "Fundamento normativo"]
    presentes = [c for c in range(len(cabecalho)) if any(linha[c] for linha in linhas)]
    return (
        tuple(cabecalho[c] for c in presentes),
        tuple(tuple(linha[c] or "—" for c in presentes) for linha in linhas),
    )


def _grupos_de_modalidades(perfis, listas):
    """Uma tabela por grupo de Perfis de tabela idêntica — inclusive o grupo de um (068, R-006)."""
    por_chave = {}
    for perfil in perfis:
        if tabela := _linhas_de_modalidades(perfil, listas):
            por_chave.setdefault(tabela, []).append(perfil)
    return tuple(
        GrupoDeModalidades(tuple(grupo), cabecalho, linhas)
        for (cabecalho, linhas), grupo in por_chave.items()
    )


def _frases_por_alcance(pares, alcance):
    """Uma frase por texto, com os códigos — ou sem eles quando ela vale para todo o alcance."""
    por_texto = {}
    for perfil, texto in pares:
        if texto:
            por_texto.setdefault(texto, []).append(perfil)
    if len(por_texto) == 1:
        texto, grupo = next(iter(por_texto.items()))
        if len(grupo) == len(alcance):
            return (FraseConsolidada(texto),)
    return tuple(
        FraseConsolidada(texto, tuple(perfil.get("code", "") for perfil in grupo))
        for texto, grupo in por_texto.items()
    )


def _frases_da_reversao(perfis, redacao=REDACAO_VIGENTE):
    """A reversão é regra sobre as quantidades: só os Perfis da tabela de vagas (FR-1350)."""
    com_vaga = [perfil for perfil in perfis if _com_vaga_no_quadro(perfil)]
    pares = [
        (
            perfil,
            frase_da_reversao((perfil.get("vacancyReversion") or {}).get("kind"), redacao=redacao),
        )
        for perfil in com_vaga
    ]
    return _frases_por_alcance(pares, com_vaga)


def _frases_da_convocacao(perfis, redacao=REDACAO_VIGENTE):
    """A convocação é regra do Perfil inteiro, com quadro ou sem ele (FR-1351)."""
    pares = [
        (perfil, frase_da_convocacao(perfil.get("callForm"), redacao=redacao) or None)
        for perfil in perfis
    ]
    return _frases_por_alcance(pares, perfis)


def _governado_pelo_metodo_comum(snapshot, perfil, marco):
    return (
        regras_do_marco.declara_sorteio(marco)
        and _origem_do_metodo(snapshot, marco) == "comum a este Edital"
        and bool(_metodo_do_marco(snapshot, perfil, marco))
    )


def _metodo_remetido(snapshot, perfis, secao, subsecoes, remissoes):
    """O item em que as linhas do método comum saem, para cada marco que só remete a ele (FR-1349).

    Os lugares em que marcos são impressos, na ordem do documento: os Perfis que imprimem os
    próprios, depois as subseções comuns. O primeiro marco governado pelo método comum imprime as
    sete linhas; os seguintes, a remissão. No caso comum — todos os marcos iguais — há um lugar só,
    e nenhuma remissão.
    """
    lugares = [
        (f"{secao}.{ordem}", perfil)
        for ordem, perfil in enumerate(perfis, 1)
        if (id(perfil), MARCOS) not in remissoes
    ] + [(item.numero, item.perfis[0]) for item in subsecoes if item.materia == MARCOS]
    primeiro, remetido = None, {}
    for numero, perfil in lugares:
        for marco in perfil.get("classificationMilestones") or []:
            if not _governado_pelo_metodo_comum(snapshot, perfil, marco):
                continue
            if primeiro is None:
                primeiro = numero
            else:
                remetido[id(marco)] = primeiro
    return remetido


# ---------------------------------------------------------------------------
# 068 — A composição consolidada
# ---------------------------------------------------------------------------


def _legenda_com_codigos(tabelas, titulo, perfis, recuo, metrica=HELVETICA):
    """A legenda que nomeia Perfis, em linhas que nunca partem um código (068, R-008)."""
    rotulo = "Perfil" if len(perfis) == 1 else "Perfis"
    return _linhas_sem_partir(
        tabelas.legenda(f"{titulo} — {rotulo}"),
        _codigos_enumerados([perfil.get("code", "") for perfil in perfis]),
        CORPO_TEXTO,
        NEGRITO,
        recuo=recuo,
        metrica=metrica,
    )


def _tabela_de_vagas(composicao, plano, tabelas):
    """As vagas de todos os Perfis numa tabela: a resposta a "quantas vagas PPI no polo X" (D-002).

    Substitui o quadro de vagas de cada Perfil. O cabeçalho traz o código da lista, para que dez
    listas caibam numa página; o nome está na tabela de modalidades, logo abaixo, na mesma ordem.
    Lista que o Perfil não declara sai "—", e não "0": zero seria afirmar uma lista que ele não tem.
    """
    vagas = plano.vagas
    if vagas is None:
        return
    with composicao.bloco():
        _tabela(
            composicao,
            list(vagas.cabecalho),
            [list(linha) for linha in vagas.linhas],
            recuo=0.0,
            alinhamentos=[ESQUERDA]
            + (
                [CENTRO] * (len(vagas.cabecalho) - 1)
                if vagas.forma == MATRIZ
                else [ESQUERDA, CENTRO]
            ),
            legenda=tabelas.legenda("Vagas por lista de concorrência"),
        )


def _tabela_de_modalidades(composicao, grupo, total_de_perfis, tabelas):
    """Uma tabela de modalidades por grupo; sem qualificador quando o grupo é o Edital (R-006)."""
    titulo = "Modalidades de concorrência"
    if len(grupo.perfis) == total_de_perfis:
        legenda = tabelas.legenda(titulo)
    else:
        legenda = _legenda_com_codigos(
            tabelas, titulo, grupo.perfis, recuo=0.0, metrica=composicao.metrica
        )
    with composicao.bloco():
        _tabela(
            composicao,
            list(grupo.cabecalho),
            [list(linha) for linha in grupo.linhas],
            recuo=0.0,
            alinhamentos=[ESQUERDA if c == 0 else CENTRO for c in range(len(grupo.cabecalho))],
            legenda=legenda,
        )


def _frases_consolidadas(composicao, frases):
    """As frases que os Perfis repetiam, uma vez, logo abaixo das tabelas que elas governam.

    O texto é o de sempre. Quando a frase não vale para todo o alcance, ela começa pelos códigos
    dos Perfis a que vale — "Nos Perfis A e B, na hipótese …" —, numa frase quebrada por pedaços,
    para que nenhum código se parta entre duas linhas (R-007, R-008).
    """
    for indice, frase in enumerate(frases):
        antes = ANTES_DE_BLOCO if indice == 0 else ANTES_DE_PARAGRAFO
        with composicao.bloco():
            if not frase.codigos:
                composicao.escrever(frase.texto, antes=antes, justificar=True)
                continue
            inicio = "No Perfil" if len(frase.codigos) == 1 else "Nos Perfis"
            pedacos = _codigos_enumerados(list(frase.codigos))
            pedacos[-1] = f"{pedacos[-1]},"
            texto = f"{frase.texto[:1].lower()}{frase.texto[1:]}"
            linhas = _linhas_sem_partir(
                inicio,
                [*pedacos, *texto.split()],
                CORPO_TEXTO,
                REGULAR,
                metrica=composicao.metrica,
            )
            _escrever_linhas(composicao, linhas, antes=antes)


def _escrever_linhas(composicao, linhas, *, antes, recuo=0.0):
    """Um parágrafo já quebrado em linhas, justificado como `escrever` justifica.

    `escrever` reflui por palavra; aqui a quebra já foi decidida por pedaços, e reescrever cada
    linha por `escrever` perderia a justificação — ele só justifica as linhas que ele mesmo quebra.
    """
    for indice, linha in enumerate(linhas):
        composicao.itens.append(
            (
                "texto",
                linha,
                REGULAR,
                CORPO_TEXTO,
                recuo,
                antes if indice == 0 else 0.0,
                ESQUERDA,
                False,
                False,
                indice < len(linhas) - 1,
            )
        )


def _titulo_da_subsecao_comum(composicao, numero, materia, grupo):
    """O título que nomeia os códigos, e nunca a denominação (064, FR-1189 dela)."""
    linhas = _linhas_sem_partir(
        f"{numero} {titulo_da_subsecao_comum(materia, redacao=composicao.redacao)}",
        _codigos_enumerados([perfil.get("code", "") for perfil in grupo]),
        CORPO_SUBSECAO,
        NEGRITO,
        metrica=composicao.metrica,
    )
    for indice, linha in enumerate(linhas):
        composicao.escrever(
            linha,
            tamanho=CORPO_SUBSECAO,
            fonte=NEGRITO,
            antes=ANTES_DE_BLOCO + 4 if indice == 0 else 0.0,
            junto=True,
        )


def _requisitos_comuns(composicao, grupo, numero):
    """A subseção que imprime uma vez os requisitos de um grupo de Perfis (068, FR-1352, D-003).

    O molde da subseção de atribuições da `064`: um bloco coeso, os itens um degrau à esquerda —
    o título da subseção é o rótulo deles —, com o marcador de sempre.
    """
    with composicao.bloco():
        _titulo_da_subsecao_comum(composicao, numero, REQUISITOS, grupo)
        for requisito in grupo[0].get("requirements") or []:
            if composicao.redacao != REDACAO_1:
                _item(composicao, "•", requisito, recuo=18, antes=0.0)
                continue
            with composicao.bloco():
                composicao.escrever(f"• {requisito}", tamanho=CORPO_TEXTO, recuo=18)


def _marcos_comuns(composicao, snapshot, subsecao, metodo_remetido):
    """A subseção que imprime uma vez os marcos de um grupo de Perfis (068, FR-1346 a FR-1348).

    **Aberta, e não coesa como a das atribuições**: a coesão fica em cada marco, como no Perfil. O
    título e a frase do FR-1347 vão `junto`, e a quebra de página os leva com o marco que salta.

    Os marcos são compostos a partir do primeiro Perfil do grupo — pela regra que formou o grupo,
    os de todos imprimem o mesmo texto.
    """
    with composicao.bloco(coeso=False):
        _titulo_da_subsecao_comum(composicao, subsecao.numero, MARCOS, subsecao.perfis)
        composicao.escrever(
            MARCOS_SEPARADAMENTE if composicao.redacao == REDACAO_1 else CLASSIFICACAO_SEPARADA,
            tamanho=CORPO_TEXTO,
            recuo=18,
            antes=ANTES_DE_PARAGRAFO,
            junto=True,
            justificar=True,
        )
        _marcos(
            composicao,
            snapshot,
            subsecao.perfis[0],
            comum=True,
            metodo_remetido=metodo_remetido,
        )


def _atribuicoes_comuns(composicao, grupo, numero):
    """A subseção que imprime uma vez as atribuições de um grupo de Perfis (064).

    **O título nomeia os códigos, e nunca a denominação.** Dois "Tutor presencial" de textos
    diferentes não se juntam, e dois Perfis de denominações diferentes e mesmo texto se juntam: o
    que diz a quem o texto vale é o código, que é único no Edital.

    **Um bloco coeso, ao contrário do Perfil.** A paginação só faz saltar inteiro o bloco coeso: o
    que não cabe no resto da página mas cabe numa página inteira começa na seguinte, e o que não
    cabe nem nela desce aos parágrafos, cada um num bloco próprio — a cascata do FR-021 da `008`,
    que a subseção comum obedece como um Perfil. Aberto como o Perfil se abre, ele começaria no
    rodapé mesmo cabendo inteiro na página seguinte.

    Os parágrafos são os do primeiro Perfil do grupo, que são, pela regra que formou o grupo, os de
    todos; recuo 18 porque o título da subseção é o rótulo deles.
    """
    with composicao.bloco():
        _titulo_da_subsecao_comum(composicao, numero, ATRIBUICOES, grupo)
        for paragrafo in _paragrafos(grupo[0].get("duties")):
            with composicao.bloco():
                composicao.escrever(
                    paragrafo,
                    tamanho=CORPO_TEXTO,
                    recuo=18,
                    antes=ANTES_DE_LINHA,
                    justificar=True,
                )


def _codigos_enumerados(codigos):
    """Os códigos como o título os enumera — "A, B e C" —, em pedaços que não se partem.

    **O código é texto livre**, e nada impede que ele contenha a vírgula ou o " e " da própria
    enumeração: "Tutor e Mediador" e "TEC" sairiam "Tutor e Mediador e TEC", que se lê como três
    Perfis. Quando algum código do grupo tem um desses separadores, **todos** vão entre aspas — no
    grupo inteiro, e não só no ambíguo, para que a regra de leitura seja uma só dentro do título.

    Cada pedaço é um código com o separador que o segue, e o " e " anda junto do último: é o que
    `_linhas_sem_partir` recebe para não quebrar a linha dentro de um código.
    """
    if any(", " in codigo or " e " in codigo for codigo in codigos):
        codigos = [f"“{codigo}”" for codigo in codigos]
    if len(codigos) <= 1:
        return list(codigos)
    return [f"{codigo}," for codigo in codigos[:-2]] + [codigos[-2], f"e {codigos[-1]}"]


def _linhas_sem_partir(inicio, pedacos, tamanho, fonte, recuo=0.0, metrica=HELVETICA):
    """O texto em linhas que quebram **entre** os pedaços, nunca dentro de um.

    `_quebrar` reflui por palavra, e um código com espaço — "ADS - P06", que é como os polos do
    Edital 90/2026 se chamam — saía partido: "ADS" no fim de uma linha e "- P06" no começo da
    outra, e o candidato não acha o próprio código. O espaço inseparável não resolve, porque
    `_quebrar` divide em todo espaço que `str.split` reconhece, e ele está entre eles.

    Serve aos títulos das subseções comuns (064), às legendas e às frases que enumeram códigos
    (068); `recuo` estreita a linha para o texto que não começa na margem.

    O pedaço maior que a linha inteira sai sozinho, e é `escrever` que o parte — o último degrau de
    sempre, para que a composição conclua.
    """
    disponivel = LARGURA - 2 * MARGEM - recuo
    linhas, atual = [], inicio
    for pedaco in pedacos:
        candidato = f"{atual} {pedaco}"
        if metrica.largura(candidato, tamanho, fonte) <= disponivel:
            atual = candidato
            continue
        linhas.append(atual)
        atual = pedaco
    linhas.append(atual)
    return linhas


def _reserva(perfil, *, redacao=REDACAO_VIGENTE):
    """O cadastro de reserva do Perfil, como valor de célula ou de par.

    Na redação 2, pelo efeito (P2): "até 15 (quinze) classificados", e não "limitado em 15".
    """
    if redacao != REDACAO_1:
        tipo, limite = perfil.get("reserveType"), perfil.get("reserveLimit")
        if tipo == "LIMITED" and _inteiro(limite):
            return f"até {_numero_por_extenso(limite)} classificados"
        if tipo == "UNLIMITED":
            return "sem limite de classificados"
        if tipo == "NONE":
            return "não há"
    reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
    if perfil.get("reserveLimit") is not None:
        reserva = f"{reserva} em {perfil['reserveLimit']}"
    return reserva or "—"


def _pares(composicao, pares, *, recuo=18.0, antes=ANTES_DE_LINHA):
    """Rótulo em negrito e valor na mesma linha — tipografia, não grade.

    Tabela é para comparar muitas linhas; poucos atributos de um único objeto se descrevem com
    peso tipográfico. Emoldurar quatro pares produz ficha administrativa, não Edital.

    `antes` é o espaço acima de cada par: o de linha, quando os pares se seguem; o de sub-bloco,
    quando o par ocupa o lugar de um sub-bloco, como a remissão às atribuições comuns (064).
    """
    for rotulo, valor in pares:
        largura_do_rotulo = composicao.metrica.largura(f"{rotulo}: ", CORPO_TEXTO, NEGRITO)
        composicao.escrever(
            f"{rotulo}:", tamanho=CORPO_TEXTO, fonte=NEGRITO, recuo=recuo, antes=antes
        )
        composicao.escrever(
            valor,
            tamanho=CORPO_TEXTO,
            recuo=recuo + largura_do_rotulo,
            antes=-(CORPO_TEXTO * 1.45),
        )


def _cronograma(composicao, snapshot, secao=0, tabelas=None):
    """O Cronograma em tabela, com **rótulo humano**, não com o código do tipo.

    `INSCRICAO — Período de inscrições` denuncia o sistema por trás do documento: `INSCRICAO` é
    chave de enumeração, e num Edital publicado ela não significa nada a mais do que a descrição
    que a acompanha. O código continua no conteúdo publicado; o que muda é o que se imprime — a
    mesma decisão que tirou `PLANEJADO` do documento na `007`.
    """
    eventos = snapshot.get("schedule") or []
    if not eventos:
        return
    # **A coluna do local só aparece quando algum Evento declara um** (021, FR-057). Uma coluna de
    # travessões em todo Edital anterior ao degrau 11 ocuparia largura para afirmar nada — e a
    # ausência já significa "não declarado", que é diferente de "acontece em lugar nenhum".
    algum_local = any((evento.get("location") or "").strip() for evento in eventos)
    if composicao.redacao != REDACAO_1:
        # O período numa coluna, como se lê: "de … a …" (texto alvo da spec). Início e término
        # em duas colunas obrigavam a juntar de cabeça as duas metades de cada linha.
        _tabela(
            composicao,
            ["Nº", "Evento", "Quando", *(["Onde"] if algum_local else [])],
            [
                [
                    str(evento.get("order", "")),
                    evento.get("description") or evento.get("type", ""),
                    _periodo_do_evento(evento),
                    *([evento.get("location") or "—"] if algum_local else []),
                ]
                for evento in eventos
            ],
            recuo=0.0,
            alinhamentos=[CENTRO, ESQUERDA, ESQUERDA, *([ESQUERDA] if algum_local else [])],
            legenda=tabelas.legenda("Cronograma"),
        )
        return
    linhas = [
        [
            str(evento.get("order", "")),
            evento.get("description") or evento.get("type", ""),
            _instante(evento.get("startAt")),
            _instante(evento["endAt"]) if evento.get("endAt") else "—",
            *([evento.get("location") or "—"] if algum_local else []),
        ]
        for evento in eventos
    ]
    _tabela(
        composicao,
        ["Nº", "Evento", "Início", "Término", *(["Onde"] if algum_local else [])],
        linhas,
        recuo=0.0,
        alinhamentos=[CENTRO, ESQUERDA, CENTRO, CENTRO, *([ESQUERDA] if algum_local else [])],
        legenda=tabelas.legenda("Cronograma"),
    )


CARATER_DA_ETAPA = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _periodo_do_evento(evento):
    """`de 03/11/2026, às 08h, a 10/11/2026, às 23h59`, ou o instante único."""
    if evento.get("endAt"):
        return f"de {_instante(evento.get('startAt'))}, a {_instante(evento['endAt'])}"
    return _instante(evento.get("startAt"))


def _etapas(composicao, snapshot, secao=0, tabelas=None):
    """As Etapas na ordem definida, com o que estiver informado.

    Peso, nota mínima e caráter só aparecem quando existem: imprimir "peso: —" afirmaria uma
    ponderação vazia onde a ausência quer dizer que a Etapa não pondera.

    A subseção é numerada a partir do número da seção-mãe **já resolvido** (FR-013). Fixar `6.`
    repetiria, uma camada abaixo, o defeito que a numeração em dois passos corrige.
    """
    eventos = {
        evento.get("id"): evento
        for evento in (snapshot.get("schedule") or [])
        if isinstance(evento, dict)
    }
    for ordem, etapa in enumerate(snapshot.get("stages") or [], 1):
        with composicao.bloco():
            composicao.escrever(
                f"{secao}.{ordem} {etapa.get('name', '')}",
                tamanho=CORPO_SUBSECAO,
                fonte=NEGRITO,
                antes=ANTES_DE_BLOCO + 2,
                junto=True,
            )
            if composicao.redacao != REDACAO_1:
                # E1 a E3: os pares viram uma frase, com o mesmo que estava declarado.
                if frase := frase_da_etapa(etapa, eventos):
                    composicao.escrever(frase, antes=ANTES_DE_PARAGRAFO, justificar=True)
                continue
            caracteres = [rotulo for chave, rotulo in CARATER_DA_ETAPA if etapa.get(chave)]
            pares = []
            if caracteres:
                pares.append(["Caráter", " e ".join(caracteres)])
            if etapa.get("weight") is not None:
                pares.append(["Peso", humano.decimal(etapa["weight"])])
            if etapa.get("minimumScore") is not None:
                pares.append(["Nota mínima", humano.decimal(etapa["minimumScore"])])
            # O incremento da `012`. Impressos só quando declarados: Edital publicado antes dele
            # não os carrega, e imprimir "1 avaliação" onde o Edital nada disse seria o documento
            # afirmando regra que a Publicação não contém (FR-009, FR-066).
            if etapa.get("maximumScore") is not None:
                pares.append(["Pontuação máxima", humano.decimal(etapa["maximumScore"])])
            previstas = etapa.get("evaluationsPerRegistration")
            if previstas is not None:
                quantas = "1 avaliação" if previstas == 1 else f"{previstas} avaliações"
                pares.append(["Avaliações por inscrição", quantas])
            # A forma da conclusão, pela mesma régua: impressa só quando declarada, e com os
            # rótulos **deste** Edital. Sem isto, a fonte estruturada e o documento divergem, e o
            # candidato lê um Edital que não diz como sua Etapa é concluída — P-007 valendo só na
            # metade que ninguém vê (D-008, FR-119).
            if etapa.get("forma") == DECISORIA:
                favoravel = etapa.get("rotuloFavoravel") or "favorável"
                desfavoravel = etapa.get("rotuloDesfavoravel") or "desfavorável"
                pares.append(["Resultado", f"{favoravel} ou {desfavoravel}"])
            # As datas são do Evento e não são copiadas: o documento as lê de lá, como o domínio.
            # E o rótulo humano é que vai para o papel, não a chave do tipo.
            evento = eventos.get(etapa.get("scheduleEventId"))
            if evento:
                periodo = _instante(evento.get("startAt"))
                if evento.get("endAt"):
                    periodo += f" a {_instante(evento['endAt'])}"
                pares.append(["Realização", periodo])
            # Poucos atributos de um único objeto se descrevem com peso tipográfico, não com
            # grade: emoldurá-los produzia ficha administrativa, não Edital.
            _pares(composicao, pares)


def _alinea(indice):
    """`a)`, `b)`, … e depois `aa)`, como um ato normativo enumera alíneas."""
    letras = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(ord("a") + resto) + letras
    return f"{letras})"


def _rotulo_do_perfil(perfil):
    """`LP01 — Tutor Presencial`: a grafia que a tabela de Perfis e o título da seção dele já usam.

    **O código entra porque o nome não distingue.** Um Edital de tutoria abre um código de inscrição
    por polo para a mesma função: os dezesseis Perfis do 140/2025 se chamam todos "Tutor
    Presencial", e o cabeçalho composto só com `name` imprimia dezesseis vezes "Dos candidatos ao
    perfil Tutor Presencial:", indistinguíveis. Quem se inscreveu em Aracruz não tinha como saber
    qual bloco era o dele — que é exatamente o erro que este cabeçalho existe para não cometer.

    **A grafia não é escolhida aqui.** É a que o leitor já viu na tabela de Perfis e no título da
    seção daquele Perfil, e por isso é a que ele procura. Duas grafias para o mesmo objeto no mesmo
    documento obrigariam a casá-las de cabeça.

    O nome sozinho continua valendo quando não há código, e vice-versa: a validação de publicação
    exige os dois, e compor `" — "` sobre um campo vazio produziria um travessão órfão em conteúdo
    que nenhum teste de publicação alcança.
    """
    code = (perfil.get("code") or "").strip()
    name = (perfil.get("name") or "").strip()
    if code and name:
        return f"{code} — {name}"
    return name or code


def _nomes_do_alcance(snapshot):
    perfis, modalidades = {}, {}
    for perfil in snapshot.get("profiles") or []:
        perfis[perfil.get("id")] = _rotulo_do_perfil(perfil)
        for modalidade in perfil.get("competitionModalities") or []:
            modalidades[modalidade.get("id")] = modalidade.get("name") or modalidade.get("code", "")
    return perfis, modalidades


def _titulo_do_grupo(
    perfil_id,
    modalidade_id,
    perfis,
    modalidades,
    codigo=None,
    snapshot=None,
    *,
    redacao=REDACAO_VIGENTE,
):
    """O cabeçalho que diz **a quem** aquele bloco de documentos se dirige.

    A aplicabilidade é dado estruturado; aqui ela vira a frase que o candidato lê para saber se
    aquela alínea é com ele. Sem este cabeçalho, um laudo exigido só de uma modalidade pareceria
    exigido de todo mundo — que é exatamente o erro que a lista única de documentos produz nos
    Editais escritos à mão.
    """
    if redacao != REDACAO_1:
        return _titulo_do_grupo_2(perfil_id, modalidade_id, perfis, codigo, snapshot)
    if codigo:
        # O recorte transversal (044, FR-712): um grupo por código, sem Perfil. O título é o que o
        # PDF já imprimia para "Todos os Perfis + Modalidade" — a diferença é que agora ele é
        # verdadeiro, porque o portal aplica pelo mesmo critério. A denominação é a de qualquer
        # Perfil que tem o código: a publicação impede que sejam duas.
        return (
            "Dos candidatos concorrentes na modalidade "
            f"{denominacao_do_codigo(snapshot or {}, codigo)}:"
        )
    if perfil_id is None and modalidade_id is None:
        return "De todos os candidatos:"
    if modalidade_id is None:
        return f"Dos candidatos ao perfil {perfis.get(perfil_id, '')}:"
    if perfil_id is None:
        return f"Dos candidatos concorrentes na modalidade {modalidades.get(modalidade_id, '')}:"
    return (
        f"Dos candidatos ao perfil {perfis.get(perfil_id, '')} concorrentes na modalidade "
        f"{modalidades.get(modalidade_id, '')}:"
    )


def _lista_por_extenso(modalidade):
    """`pessoas pretas, pardas e indígenas (PPI)` — o nome em minúscula, e o código."""
    nome = inicial_minuscula(modalidade.get("name") or "")
    codigo = modalidade.get("code") or ""
    if nome and codigo:
        return f"{nome} ({codigo})"
    return nome or codigo


def _titulo_do_grupo_2(perfil_id, modalidade_id, perfis, codigo, snapshot):
    """D1 a D4 — a quem o grupo de documentos se dirige, e que é **além** dos de todos.

    "Também" diz o que a redação 1 deixava implícito: os documentos do grupo se somam aos que todos
    apresentam. O alcance é o mesmo — todos, o Perfil, a lista, o Perfil e a lista.
    """
    modalidades = {}
    for perfil in (snapshot or {}).get("profiles") or []:
        for modalidade in perfil.get("competitionModalities") or []:
            modalidades.setdefault(modalidade.get("id"), modalidade)
            modalidades.setdefault(("codigo", modalidade.get("code")), modalidade)
    if codigo:
        lista = modalidades.get(("codigo", codigo)) or {"code": codigo}
        return f"Também, de quem concorre às vagas para {_lista_por_extenso(lista)}:"
    if perfil_id is None and modalidade_id is None:
        return "De todos os candidatos:"
    lista = _lista_por_extenso(modalidades.get(modalidade_id) or {})
    if modalidade_id is None:
        return f"Também, de quem concorre ao Perfil {perfis.get(perfil_id, '')}:"
    if perfil_id is None:
        return f"Também, de quem concorre às vagas para {lista}:"
    return f"Também, de quem concorre ao Perfil {perfis.get(perfil_id, '')} nas vagas para {lista}:"


def _anexos(composicao, snapshot, secao=0, tabelas=None):
    """A relação dos Anexos que acompanham este Edital (020, FR-027).

    **Lista, e não conteúdo.** O documento principal cita os anexos e não carrega os bytes deles: a
    prática observada retifica um anexo sozinho, e incorporar faria a correção de um formulário
    reescrever o documento normativo inteiro (D-002).

    **E não imprime endereço** (FR-027a). O endereço vive no canal — a página pública da seleção e a
    consulta da publicação —, para que os bytes imutáveis não fiquem presos a um domínio que um dia
    muda, e para que a identidade da publicação não precise existir antes de o documento ser
    composto.

    O rótulo é reproduzido como o autor o escreveu, inteiro. Nada aqui numera nem renumera: a ordem
    é a do conteúdo publicado, e o número, se houver, está dentro do rótulo.
    """
    anexos = snapshot.get("attachments") or []
    if not anexos:
        return
    with composicao.bloco():
        for anexo in sorted(anexos, key=lambda item: item.get("order", 0)):
            composicao.escrever(
                anexo.get("label", ""),
                tamanho=CORPO_TEXTO,
                recuo=18.0,
                antes=ANTES_DE_LINHA,
            )


def _documentos_exigidos(composicao, snapshot, secao=0, tabelas=None):
    """Os documentos que o candidato precisa apresentar, agrupados por a quem se aplicam.

    Alíneas, e não tabela: é lista normativa curta, do tipo que um Edital escreve em prosa
    enumerada. A numeração recomeça em cada grupo porque cada grupo é a lista de uma pessoa — quem
    concorre na ampla concorrência não precisa saber que a alínea `d)` existe para outra.

    A ordem dos grupos é a do conteúdo publicado, e dentro de cada um, a ordem declarada. Nada é
    reordenado aqui: a ordem é decisão de quem elaborou, e o documento a reproduz.
    """
    requisitos = snapshot.get("documentRequirements") or []
    if not requisitos:
        return
    perfis, modalidades = _nomes_do_alcance(snapshot)
    grupos = {}
    for requisito in sorted(requisitos, key=lambda item: item.get("order", 0)):
        chave = (
            requisito.get("profileId"),
            requisito.get("modalityId"),
            requisito.get("modalityCode") or None,
        )
        grupos.setdefault(chave, []).append(requisito)
    for (perfil_id, modalidade_id, codigo), documentos in grupos.items():
        with composicao.bloco():
            composicao.escrever(
                _titulo_do_grupo(
                    perfil_id,
                    modalidade_id,
                    perfis,
                    modalidades,
                    codigo,
                    snapshot,
                    redacao=composicao.redacao,
                ),
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                antes=ANTES_DE_BLOCO,
                junto=True,
            )
            if composicao.redacao != REDACAO_1:
                # D5, em alíneas com o recuo pendente (ED-16).
                for indice, documento in enumerate(documentos):
                    _item(composicao, _alinea(indice), texto_do_documento(documento), recuo=18.0)
                continue
            for indice, documento in enumerate(documentos):
                texto = f"{_alinea(indice)} {documento.get('name', '')}"
                if documento.get("instructions"):
                    texto += f" — {documento['instructions']}"
                if not documento.get("required", True):
                    texto += " (facultativo)"
                composicao.escrever(texto, tamanho=CORPO_TEXTO, recuo=18.0, antes=ANTES_DE_LINHA)


# Cada seção gerada nomeia a coleção que a origina; aqui está o que fazer com cada uma. Uma origem
# que não estiver neste mapa não é composta — e a validação de publicação já recusa origem que
# divirja do catálogo, então isso não é silêncio: é a consequência de uma recusa que veio antes.
_CORPO_GERADO = {
    "profiles": _perfis,
    "schedule": _cronograma,
    "stages": _etapas,
    "documentRequirements": _documentos_exigidos,
    "attachments": _anexos,
}


def _materializaveis(snapshot):
    """As seções que **serão** compostas, na ordem do conteúdo publicado (FR-038).

    Uma seção gerada cuja fonte está vazia não é composta. Um título sobre nada não informa que não
    há nada — informa que alguém esqueceu de preencher, e num Edital sem Etapas de Avaliação isso
    seria falso: a coleção é opcional.

    **A textual vazia também não** (054, FR-982). O catálogo passou a ter as seções das quatro
    famílias da amostra, e cada Edital usa as suas: a que ninguém escreveu não é seção deste Edital.
    A exceção é a que carrega norma que o sistema executa (FR-984) — o teto na Inscrição, o
    Requerimento na Matrícula —, que sai ainda que quem elabora não tenha escrito nada nela.
    """
    materializaveis = []
    for secao in sorted(snapshot.get("sections") or [], key=lambda item: item.get("order", 0)):
        if secao.get("type") == GERADA:
            corpo = _CORPO_GERADO.get(secao.get("source"))
            if corpo is None or not (snapshot.get(secao.get("source")) or []):
                continue
            materializaveis.append((secao, corpo))
        elif _paragrafos(secao.get("content", "")) or _norma_da_secao(secao, snapshot):
            materializaveis.append((secao, None))
    return materializaveis


def _apresentacao():
    from processo_seletivo.publicacoes.infrastructure import apresentacao

    return apresentacao


def por_perguntas(snapshot):
    """O documento deste snapshot sai na apresentação por perguntas? (069, R-001)"""
    return catalogo.apresentacao_de(snapshot) == catalogo.POR_PERGUNTAS


def numeracao(snapshot):
    """O número que cada seção terá no documento: `{chave: número}` (054, FR-985).

    **Pela apresentação do snapshot** (069, R-003): na por perguntas, o número é o apresentado —
    "N" para a seção, "N.k" para a chave que sai como subseção. Na plana, o de sempre.

    `None` para a seção que não sai; `0` para o preâmbulo, que sai sem número. **Uma regra só**, a
    que o compositor usa, lida também pela etapa Conteúdo e pela Revisão: eram três numerações — a
    ordem do catálogo na tela, a mesma ordem na Revisão, e a contagem do que sai no documento —, e
    com 22 seções e textuais vazias a tela diria "15" para a seção que o documento imprime como "9"
    (RC-26).
    """
    if por_perguntas(snapshot):
        return _apresentacao().numeracao(snapshot)
    numeros = {secao.get("key"): None for secao in snapshot.get("sections") or []}
    proximo = 1
    for secao, _ in _materializaveis(snapshot):
        if secao.get("key") == SECAO_DE_PREAMBULO:
            numeros[secao.get("key")] = 0
            continue
        numeros[secao.get("key")] = proximo
        proximo += 1
    return numeros


def numeracao_impressa(snapshot):
    """`numeracao` sobre o texto como o documento o imprime, já normalizado (065, FR-1202).

    O compositor normaliza o snapshot antes de compor (`_grafado`), e é sobre o normalizado que ele
    decide se uma seção textual tem parágrafo. Uma seção que só tivesse caractere invisível sairia
    vazia — e sem número — no documento, e com número numa leitura do texto cru. A conferência da
    numeração digitada compara com o que sai impresso, e por isso lê daqui.
    """
    return numeracao(_grafado(snapshot, previa=False))


# As naturezas dos itens que o documento imprime com número (065, D-004; 068).
ITEM_SECAO, ITEM_PERFIL, ITEM_ATRIBUICOES_COMUNS, ITEM_ETAPA = (
    "secao",
    "perfil",
    "atribuicoes_comuns",
    "etapa",
)
ITEM_REQUISITOS_COMUNS, ITEM_MARCOS_COMUNS = "requisitos_comuns", "marcos_comuns"
NATUREZA_DA_SUBSECAO = {
    ATRIBUICOES: ITEM_ATRIBUICOES_COMUNS,
    REQUISITOS: ITEM_REQUISITOS_COMUNS,
    MARCOS: ITEM_MARCOS_COMUNS,
}


@dataclass(frozen=True)
class ItemDoDocumento:
    """Um número que o documento imprime como identificação, e o que ele identifica (065)."""

    numero: str
    natureza: str
    descricao: str


def itens_do_documento(snapshot):
    """As seções e subseções que o documento imprime com número, pela regra que as compõe (065).

    **Mora aqui, e não na validação**, porque é a mesma regra da composição (D-004): as seções são
    as de `numeracao`; as subseções de Perfis são as de `_perfis`, com as comuns da `064` depois do
    último Perfil; as de Etapas, as de `_etapas`. Reescrevê-la noutro módulo seria a segunda regra
    de numeração que a `054` (FR-985) existe para não ter. O guardião
    (`tests/unit/publicacoes/test_itens_do_documento.py`) compõe o documento de verdade e compara.

    **Não compõe e não muda nada**: nenhuma linha da composição depende desta função, e o documento
    sai com os mesmos bytes (FR-1219). O preâmbulo não tem número, e não é item.
    """
    snapshot = _grafado(snapshot, previa=False)
    if por_perguntas(snapshot):
        return _apresentacao().itens(snapshot)
    numeros = numeracao(snapshot)
    itens = []
    for secao, corpo in _materializaveis(snapshot):
        numero = numeros.get(secao.get("key"))
        if not numero:
            continue
        itens.append(ItemDoDocumento(str(numero), ITEM_SECAO, secao.get("title", "")))
        if corpo is _perfis:
            perfis = snapshot.get("profiles") or []
            for ordem, perfil in enumerate(perfis, 1):
                itens.append(
                    ItemDoDocumento(
                        f"{numero}.{ordem}",
                        ITEM_PERFIL,
                        f"{perfil.get('code', '')} — {perfil.get('name', '')}",
                    )
                )
            # As subseções comuns são as do plano que a composição lê (068, R-009).
            plano = plano_de_consolidacao(snapshot, numero)
            for subsecao in plano.subsecoes if plano else ():
                itens.append(
                    ItemDoDocumento(
                        subsecao.numero,
                        NATUREZA_DA_SUBSECAO[subsecao.materia],
                        f"{titulo_da_subsecao_comum(subsecao.materia)} "
                        f"{_enumerar(subsecao.codigos)}",
                    )
                )
        elif corpo is _etapas:
            for ordem, etapa in enumerate(snapshot.get("stages") or [], 1):
                itens.append(
                    ItemDoDocumento(f"{numero}.{ordem}", ITEM_ETAPA, etapa.get("name", ""))
                )
    return itens


LEGENDA_DE_TABELA = re.compile(r"^Tabela \d+ — ")


def tabelas_do_documento(snapshot):
    """Quantas tabelas — "Tabela N" — o documento terá (065, D-004).

    A contagem acompanha `_Numerador` na composição. Com um Perfil, o quadro de vagas quando há
    linha e a de Modalidades quando há alguma; com dois ou mais (068), a de Perfis, a de vagas
    quando algum Perfil tem linha nela, e uma de Modalidades por grupo — as do plano que a
    composição lê. E o Cronograma. Só em seção que sai no documento.
    """
    snapshot = _grafado(snapshot, previa=False)
    if por_perguntas(snapshot):
        # A contagem é a da composição, e não uma segunda regra: compõe-se o corpo e contam-se as
        # legendas que ele escreveu.
        rascunho = Composicao()
        _apresentacao().compor(rascunho, snapshot)
        return sum(
            1
            for item in rascunho.itens
            if item[0] == "texto" and item[2] == NEGRITO and LEGENDA_DE_TABELA.match(item[1])
        )
    total = 0
    for _, corpo in _materializaveis(snapshot):
        if corpo is _perfis:
            perfis = snapshot.get("profiles") or []
            if plano := plano_de_consolidacao(snapshot):
                total += 1 + (1 if plano.vagas else 0) + len(plano.modalidades)
                continue
            for perfil in perfis:
                # O quadro sai pela mesma regra de `_quadro_de_vagas_do_perfil` (067, D-007).
                sai = perfil.get("vacancyTable") and not quadro_do_perfil.sem_vaga_imediata(perfil)
                total += 1 if sai else 0
                total += 1 if perfil.get("competitionModalities") else 0
        elif corpo is _cronograma:
            total += 1
    return total


# A seção que abre o Edital não é seção: é preâmbulo (FR-010). Nos Editais de referência o ato
# enunciativo da autoridade — "A Diretora [...] faz saber [...]" — vem logo abaixo do título, sem
# número e sem cabeçalho, e a numeração começa nas disposições preliminares. Numerá-lo como "1."
# faria o documento anunciar uma seção onde há uma abertura.
SECAO_DE_PREAMBULO = "apresentacao"


def _secoes(composicao, snapshot, *, paginas=None, com_sumario=False, fecho=None):
    """Preâmbulo, e depois as seções numeradas em dois passos (FR-010 a FR-012).

    **A ordem dos dois passos é o requisito.** Numerar durante a iteração produziria `5.`, `7.`,
    `8.` no primeiro Edital sem Etapas de Avaliação — um defeito que o cenário de demonstração não
    revela, porque nele está tudo preenchido. O número é da materialização: ele não existe no
    conteúdo homologado e não sobrevive a uma mudança de ordem (FR-012).
    """
    tabelas = _Numerador()
    materializaveis = _materializaveis(snapshot)

    preambulo = [secao for secao, _ in materializaveis if secao.get("key") == SECAO_DE_PREAMBULO]
    for secao in preambulo:
        for indice, paragrafo in enumerate(_paragrafos(secao.get("content", ""))):
            composicao.escrever(
                paragrafo,
                tamanho=CORPO_TEXTO,
                antes=ANTES_DE_SECAO if indice == 0 else ANTES_DE_PARAGRAFO,
                justificar=True,
            )

    numeraveis = [
        (secao, corpo) for secao, corpo in materializaveis if secao.get("key") != SECAO_DE_PREAMBULO
    ]
    rotulos = [
        f"{numero}. {secao.get('title', '').upper()}"
        for numero, (secao, _) in enumerate(numeraveis, 1)
    ]
    # O sumário também na apresentação plana (R-016): é navegação, e não move número nem remissão.
    if com_sumario:
        sumario(composicao, rotulos, paginas or {})
    for numero, (secao, corpo) in enumerate(numeraveis, 1):
        titulo = rotulos[numero - 1]
        with com_o_fecho(composicao, fecho if numero == len(numeraveis) else None):
            composicao.escrever(
                titulo,
                tamanho=CORPO_TITULO_DE_SECAO,
                fonte=NEGRITO,
                antes=ANTES_DE_SECAO,
                junto=True,
            )
            if corpo is not None:
                corpo(composicao, snapshot, numero, tabelas)
            else:
                _texto_da_secao(composicao, secao, snapshot)
    if not numeraveis and fecho is not None:
        fecho()
    return rotulos


@contextmanager
def com_o_fecho(composicao, fecho):
    """A última seção e o fecho num bloco só (069, FR-1391, contrato do documento §7).

    A página só com a data, a autoridade e a autenticidade era o defeito da auditoria: o fecho é
    coeso, e quando não cabia saltava sozinho. Agora ele vai com a última seção sempre que as duas
    cabem numa página; e quando não cabem, a última linha da seção pede companhia (`junto`), e a
    quebra a leva junto com o fecho — o ato nunca começa uma página pela própria data.
    """
    if fecho is None:
        yield
        return
    with composicao.bloco():
        yield
        prender_a_ultima_linha(composicao)
        fecho()


def prender_a_ultima_linha(composicao):
    """Marca a última linha escrita como `junto`: a quebra que vier logo depois a leva.

    **Não a linha de dentro de um quadro ou de uma moldura.** A quebra leva a linha e não a grade
    nem o contorno: a última célula da tabela saía sozinha no alto da página do fecho, fora do
    quadro, e a última linha do destaque, fora da moldura, deixando a faixa vazia na página de
    antes. Terminando a seção num deles, o fecho volta a poder começar a página — o defeito antigo,
    e menor que uma célula sem a tabela dela.
    """
    for indice in range(len(composicao.itens) - 1, -1, -1):
        item = composicao.itens[indice]
        if item[0] == "fecha_linha" or (item[0] == "fecha" and item[1]):
            return
        if item[0] == "texto" and item[1]:
            composicao.itens[indice] = (*item[:7], True, *item[8:])
            return


def sumario(composicao, rotulos, paginas):
    """O sumário das seções numeradas, com a página em que cada uma começa (069, FR-1372).

    Composto em passadas (R-012): a primeira descobre as páginas, a seguinte as imprime, e uma
    terceira converge se o sumário tiver mudado a paginação. **Inteiro**: salta para a página
    seguinte quando não cabe, e o equilíbrio não o divide — partido, ele seria pior para quem o usa
    que o branco que deixa (verificação, achado 5).
    """
    if not rotulos:
        return
    medida = composicao.metrica.largura
    util = LARGURA - 2 * MARGEM
    ponto = medida(" .", CORPO_TEXTO)
    with composicao.bloco(coeso=INTEIRO):
        composicao.escrever(
            "Sumário",
            tamanho=CORPO_SUBSECAO,
            fonte=NEGRITO,
            antes=ANTES_DE_SECAO,
            junto=True,
        )
        for indice, rotulo in enumerate(rotulos):
            pagina = str(paginas.get(rotulo, 0))
            livre = util - medida(pagina, CORPO_TEXTO) - medida(rotulo, CORPO_TEXTO) - 8.0
            pontos = " ." * max(int(livre / ponto), 0)
            composicao.escrever(
                f"{rotulo}{pontos}",
                antes=ANTES_DE_LINHA if indice else ANTES_DE_PARAGRAFO,
            )
            composicao.escrever(pagina, alinhamento=DIREITA, antes=-(CORPO_TEXTO * 1.45))


def _paginas_das_secoes(paginas, rotulos):
    """Em que página começa cada seção: a do título dela, desenhado no corpo do título de seção."""
    achadas = {}
    for numero, (linhas, _) in enumerate(paginas, 1):
        for texto, fonte, tamanho, *_ in linhas:
            if fonte != NEGRITO or tamanho != CORPO_TITULO_DE_SECAO:
                continue
            for rotulo in rotulos:
                if rotulo not in achadas and (texto == rotulo or rotulo.startswith(f"{texto} ")):
                    achadas[rotulo] = numero
                    break
    return achadas


def _texto_da_secao(composicao, secao, snapshot, *, antes=ANTES_DE_BLOCO):
    """O texto de quem redigiu, e depois a norma que o sistema acrescenta (054, FR-984).

    **A declaração do Requerimento sai em bloco destacado** (069, FR-1382), e a frase que a anuncia
    vai com ela: as duas são uma regra, e a paginação não as separa quando cabem numa página
    (FR-1391).
    """
    paragrafos = [(texto, 0.0) for texto in _paragrafos(secao.get("content", ""))]
    paragrafos += _norma_da_secao(secao, snapshot, composicao.redacao)
    declaracao = [texto for texto, recuo in paragrafos if recuo == RECUO_DA_DECLARACAO]
    corrido = [(texto, recuo) for texto, recuo in paragrafos if recuo != RECUO_DA_DECLARACAO]
    anuncio = corrido.pop() if declaracao and corrido else None
    for indice, (paragrafo, recuo) in enumerate(corrido):
        composicao.escrever(
            paragrafo,
            tamanho=CORPO_TEXTO,
            recuo=recuo,
            antes=antes if indice == 0 else ANTES_DE_PARAGRAFO,
            justificar=True,
        )
    if not declaracao:
        return
    with composicao.bloco():
        if anuncio is not None:
            composicao.escrever(
                anuncio[0],
                tamanho=CORPO_TEXTO,
                antes=antes if not corrido else ANTES_DE_PARAGRAFO,
                justificar=True,
                junto=True,
            )
        with composicao.bloco(moldura=DESTAQUE):
            for indice, paragrafo in enumerate(declaracao):
                composicao.escrever(
                    paragrafo,
                    tamanho=CORPO_TEXTO,
                    recuo=RECUO_NO_DESTAQUE,
                    antes=ANTES_DE_BLOCO + 2 if indice == 0 else ANTES_DE_PARAGRAFO,
                    justificar=True,
                )
            composicao.espaco(4.0)


# A seção textual onde a norma da inscrição que o sistema executa é publicada.
SECAO_DA_INSCRICAO = "inscricao"


def teto_de_inscricoes(snapshot, *, redacao=REDACAO_VIGENTE):
    """A frase do teto de inscrições por candidato, ou `None` sem teto (015, FR-063).

    **O RC-12 da auditoria de 26/09, corrigido pela DP-20.** O teto era executado na submissão
    (`inscricoes/application/submissao.py`, `_conferir_o_teto`), estava no conteúdo publicado e não
    saía no documento: a norma que recusa a segunda inscrição de alguém não era lida por ninguém
    antes da recusa. Desde 28/09 o PDF é o documento oficial do piloto, e norma executada sem
    publicação é norma que o candidato não teve como conhecer.

    A ausência significa *sem limite* (FR-063), e sem limite não há o que dizer: o documento não
    inventa uma frase para o que o Edital não declarou. Conta só a inscrição enviada (FR-064), e a
    frase diz isso, porque o rascunho abandonado não consome o direito.
    """
    teto = snapshot.get("maxInscricoesPorCandidato")
    if not isinstance(teto, int) or isinstance(teto, bool):
        return None
    if redacao == REDACAO_1:
        if teto == 1:
            return "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital."
        return f"Cada candidato poderá ter no máximo {teto} inscrições enviadas neste Edital."
    # V7, V8: "enviar" diz o mesmo que "ter enviada" — o rascunho não conta (FR-064) —, e o número
    # ganha o extenso, como todo número de regra do documento.
    if teto == 1:
        return "Cada candidato pode enviar apenas 1 (uma) inscrição neste Edital."
    return (
        f"Cada candidato pode enviar no máximo {_numero_por_extenso(teto, feminino=True)} "
        "inscrições neste Edital."
    )


# A seção textual onde a declaração do Requerimento de Matrícula é publicada (054, FR-996, D-006).
SECAO_DA_MATRICULA = "matricula"

MOMENTO_DO_REQUERIMENTO = {
    "AT_ENROLLMENT": "no ato da inscrição",
    "AT_CALL": "quando o candidato for convocado",
}

# O recuo da declaração transcrita: é texto que o candidato aceitará, e não redação do Edital, e o
# recuo é o que o separa das frases que o anunciam. Desde a `069` ela sai em bloco destacado, e o
# recuo marca qual parágrafo vai para dentro dele; dentro, o texto fica a `RECUO_NO_DESTAQUE` da
# margem, que é o que o contorno deixa livre.
RECUO_DA_DECLARACAO = 18.0
RECUO_NO_DESTAQUE = 8.0


def requerimento_de_matricula(snapshot, *, redacao=REDACAO_VIGENTE):
    """As frases do Requerimento de Matrícula e a declaração, ou `[]` sem Requerimento (FR-996).

    **A Q-10 da `029`, fechada pela `054`.** O candidato aceita a declaração no portal, e o Edital
    não a publicava: quem lia o ato oficial não via o que teria de declarar. Desde 28/09 o PDF é o
    documento oficial do piloto, e a declaração é norma do certame.

    **O texto é o do conteúdo publicado, o mesmo campo que o portal exibe para aceite**
    (`requerimentos/application/preencher.py`, `declaracao_publicada`) — uma fonte só, e por isso a
    declaração publicada e a aceita não divergem. Só as quebras de linha viram parágrafos.

    Devolve pares `(texto, recuo)`: as frases que anunciam, sem recuo, e a declaração, com ele.
    """
    requerimento = snapshot.get("matriculationRequest")
    if not isinstance(requerimento, dict) or not requerimento.get("moment"):
        return []
    momento = MOMENTO_DO_REQUERIMENTO.get(requerimento["moment"], str(requerimento["moment"]))
    declaracao = _paragrafos(requerimento.get("declarationText", ""))
    if redacao == REDACAO_1:
        partes = [(f"O Requerimento de Matrícula será enviado {momento}.", 0.0)]
        if declaracao:
            partes.append(("Ao enviá-lo, o candidato declarará:", 0.0))
    else:
        # V11, V12: no presente, e a frase que anuncia a declaração junto da que diz o momento — as
        # duas são uma regra só, e a paginação não as separa da declaração (FR-1391).
        anuncio = f"O Requerimento de Matrícula é enviado {momento}."
        if declaracao:
            anuncio += " Ao enviá-lo, o candidato declara:"
        partes = [(anuncio, 0.0)]
    partes.extend((paragrafo, RECUO_DA_DECLARACAO) for paragrafo in declaracao)
    return partes


def _norma_da_secao(secao, snapshot, redacao=REDACAO_VIGENTE):
    """Os parágrafos que o sistema acrescenta a uma seção textual, depois do texto de quem redigiu.

    **Na seção, e não num cabeçalho próprio.** O catálogo é fixo (006, FR-034), e uma seção nova só
    para uma frase mudaria a numeração de todo documento. A frase vem **depois** do texto, e nunca
    no lugar dele: o que o autor escreveu continua sendo o que abre a seção.

    Devolve pares `(texto, recuo)`. **Com norma, a seção sai mesmo sem texto do autor** (054,
    FR-984): a norma que o sistema executa não pode depender de alguém ter escrito na seção.
    """
    if secao.get("key") == SECAO_DA_INSCRICAO:
        frase = teto_de_inscricoes(snapshot, redacao=redacao)
        return [(frase, 0.0)] if frase else []
    if secao.get("key") == SECAO_DA_MATRICULA:
        return requerimento_de_matricula(snapshot, redacao=redacao)
    return []


def norma_acrescentada(key, snapshot):
    """O texto que o documento acrescentará à seção `key`, para a tela o mostrar (054, UX-132)."""
    return [texto for texto, _ in _norma_da_secao({"key": key}, snapshot)]


def fecho(local, data_do_ato):
    """`Vitória (ES), 29 de setembro de 2026.` — o local e a data do ato (054, FR-989).

    O local é o da unidade do Edital (060, FR-1113). A 054 o fixou como constante porque o Cefor
    publica de Vitória; um Edital do Campus Serra não é praticado lá.
    """
    return f"{local}, {humano.data_por_extenso(data_do_ato)}."


def _autoridade(composicao, autoridade, data_do_ato, local):
    """O fecho do ato: local e data, e quem o praticou — como registro, não como assinatura.

    **Local e data** (054, FR-989, emenda à FR-036 da 008). A `008` os proibia — *"a data do ato não
    é conteúdo normativo"* —, e os quinze Editais da amostra os têm. Desde 28/09 o PDF é o ato
    oficial do piloto, e um ato sem data é o defeito mais visível dele. A data não é conteúdo
    normativo, e continua não sendo: chega como contexto do ato, como a autoridade, e o hash do
    conteúdo não muda por ela. Alinhada à direita, como nos quinze.

    **A rubrica é deliberada.** Um nome centralizado sozinho ao pé de um Edital lê-se como
    assinatura, e este documento não tem assinatura: não há certificado, não há ICP, não há
    rubrica digitalizada (FR-037 da 008). Como o ato é assinado é pergunta aberta com o Cefor, e
    "Autoridade responsável pelo ato" é verdade em qualquer resposta.

    **O nome, quando houver; o cargo; o ato de nomeação, quando houver** (054, FR-993). O catálogo
    trazia a designação do cargo no campo de nome — "Diretora do Cefor" —, e o documento a
    imprimia onde o leitor espera um nome. Sem nome registrado, o cargo sai sozinho, em negrito, na
    linha do nome; com nome, o cargo vem abaixo, e o ato de nomeação por último.
    """
    composicao.escrever(
        fecho(local, data_do_ato),
        tamanho=CORPO_TEXTO,
        antes=ANTES_DE_SECAO + 8,
        alinhamento=DIREITA,
        junto=True,
    )
    composicao.escrever(
        "Autoridade responsável pelo ato",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_SECAO + 8,
        alinhamento=CENTRO,
        junto=True,
    )
    nome = str(autoridade.nome or "").strip()
    cargo = str(autoridade.cargo or "").strip()
    # O cargo contido no nome não se repete: pela API, quem publica declara nome e cargo, e
    # `Reitora do Ifes / Reitora` faria o documento parecer defeituoso onde só reflete o dado.
    linhas = [nome] if nome and cargo.casefold() in nome.casefold() else [nome, cargo]
    for indice, linha in enumerate(linha for linha in linhas if linha):
        composicao.escrever(
            linha,
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO if indice == 0 else REGULAR,
            antes=ANTES_DE_LINHA + 2 if indice == 0 else 0.0,
            alinhamento=CENTRO,
        )
    ato = str(autoridade.ato_de_nomeacao or "").strip()
    if ato:
        composicao.escrever(ato, tamanho=CORPO_TEXTO, alinhamento=CENTRO)


def _integridade(composicao, snapshot, content_hash):
    """A verificação, subordinada ao ato (FR-037 a FR-039).

    Ela precisa estar presente e precisa estar **abaixo** — em corpo de nota, separada por um fio
    fino, compacta. Um bloco de quatro linhas em corpo de texto depois da assinatura lê-se como a
    décima primeira seção do Edital; o que ele é, na verdade, é metadado de autenticidade.
    """
    composicao.espaco(ANTES_DE_SECAO)
    composicao.regua()
    composicao.escrever(
        "Verificação de integridade — este documento deriva integralmente da versão homologada "
        "identificada abaixo."
        if composicao.redacao == REDACAO_1
        else FRASE_DE_AUTENTICIDADE,
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA + 3,
    )
    processo = " — ".join(
        parte
        for parte in (snapshot.get("processoCode", ""), snapshot.get("processoTitle", ""))
        if parte
    )
    composicao.escrever(
        f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')} · "
        f"Processo Seletivo {processo}",
        tamanho=CORPO_NOTA,
    )
    composicao.escrever(f"SHA-256 do conteúdo: {content_hash}", tamanho=CORPO_NOTA)


def _fluxo_da_pagina(
    linhas,
    rodape,
    pagina,
    marca="",
    tracos=(),
    com_brasao=False,
    *,
    estrito=False,
    metrica=HELVETICA,
    fio_sob_o_titulo=False,
):
    partes = []
    if fio_sob_o_titulo:
        tracos = [*tracos, *_fios_sob_os_titulos(linhas)]
    if com_brasao:
        # `cm` põe a matriz de escala e a posição; `Do` desenha o XObject. `q`/`Q` isolam a
        # transformação para que nada depois dela herde a escala da imagem.
        x = (LARGURA - LARGURA_DO_BRASAO) / 2
        y = TOPO - ALTURA_DO_BRASAO + 4
        partes.append(
            f"q {LARGURA_DO_BRASAO:.2f} 0 0 {ALTURA_DO_BRASAO:.2f} {x:.2f} {y:.2f} cm "
            f"/{NOME_DO_BRASAO} Do Q".encode()
        )
    # Os fios primeiro: no PDF, o que é emitido depois cobre o que veio antes. Emitir contorno
    # antes de letra garante que nenhum fio passe por cima de um glifo — sem precisar de camada,
    # z-index ou qualquer conceito de composição gráfica (D-002).
    # A caixa do bloco destacado vem antes de todo outro traço: o fundo dela cobriria o que viesse
    # antes. A ordenação é estável, e sem caixa a ordem dos traços é a de sempre — o comprovante e a
    # divulgação saem com os mesmos bytes.
    for forma in sorted(tracos, key=lambda traco: traco[0] != "caixa"):
        if forma[0] == "caixa":
            _, x, y, largura_do_traco, altura = forma
            partes.append(
                f"{CINZA_DO_DESTAQUE} g "
                f"{x:.1f} {y:.1f} {largura_do_traco:.1f} {altura:.1f} re f 0 g "
                f"{Composicao.ESPESSURA_DO_FIO} w "
                f"{x:.1f} {y:.1f} {largura_do_traco:.1f} {altura:.1f} re S".encode()
            )
        elif forma[0] == "fundo":
            _, x, y, largura_do_traco, altura = forma
            partes.append(
                f"{CINZA_DO_CABECALHO} g "
                f"{x:.1f} {y:.1f} {largura_do_traco:.1f} {altura:.1f} re f 0 g".encode()
            )
        elif forma[0] == "ret":
            _, x, y, largura_do_traco, altura = forma
            partes.append(
                f"{Composicao.ESPESSURA_DO_FIO} w "
                f"{x:.1f} {y:.1f} {largura_do_traco:.1f} {altura:.1f} re S".encode()
            )
        else:
            _, x1, y1, x2, y2 = forma
            partes.append(
                f"{Composicao.ESPESSURA_DO_FIO} w "
                f"{x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S".encode()
            )
    if marca:
        partes.append(
            b"BT /"
            + NEGRITO.encode()
            + f" 9.0 Tf {MARGEM:.1f} {FAIXA_DE_PREVIA:.1f} Td (".encode()
            + _texto_pdf(marca)
            + b") Tj ET"
        )
    for texto, fonte, tamanho, x, y, espaco in linhas:
        # `Tw` acrescenta largura a cada espaço da linha: é como o PDF justifica, sem que o
        # compositor precise posicionar palavra por palavra. Fora do bloco de texto ele volta a
        # zero, para não vazar para a linha seguinte.
        partes.append(
            b"BT "
            + (f"{espaco:.3f} Tw ".encode() if espaco else b"")
            + b"/"
            + fonte.encode()
            + f" {tamanho:.1f} Tf {x:.1f} {y:.1f} Td (".encode()
            + _texto_pdf(texto, estrito=estrito)
            + b") Tj"
            + (b" 0 Tw" if espaco else b"")
            + b" ET"
        )
    # Identificação à esquerda, página à direita: o rodapé usa a largura em vez de empilhar tudo
    # num canto, e fica em corpo de nota para não competir com o conteúdo.
    for texto, x in (
        (rodape, MARGEM),
        (pagina, LARGURA - MARGEM - metrica.largura(pagina, CORPO_NOTA, REGULAR)),
    ):
        partes.append(
            b"BT /"
            + REGULAR.encode()
            + f" {CORPO_NOTA:.1f} Tf {x:.1f} {RODAPE - 16:.1f} Td (".encode()
            + _texto_pdf(texto, estrito=estrito)
            + b") Tj ET"
        )
    return b"\n".join(partes)


def _fios_sob_os_titulos(linhas):
    """O fio fino sob cada título de seção do Edital (069, FR-1382).

    **Derivado da linha desenhada**, e não um traço da composição: o título que a quebra de página
    leva para a página seguinte leva o fio junto, sem que a paginação precise saber dele. Título que
    quebra em duas linhas ganha o fio só abaixo da última.
    """
    fios = []
    for indice, (_, fonte, tamanho, _, y, _) in enumerate(linhas):
        if fonte != NEGRITO or tamanho != CORPO_TITULO_DE_SECAO:
            continue
        seguinte = linhas[indice + 1] if indice + 1 < len(linhas) else None
        if seguinte and seguinte[1] == NEGRITO and seguinte[2] == CORPO_TITULO_DE_SECAO:
            continue
        altura = y - FIO_SOB_O_TITULO
        fios.append(("seg", MARGEM, altura, LARGURA - MARGEM, altura))
    return fios


def render_edital_pdf(
    snapshot: dict,
    content_hash: str,
    modo: str = MODO_PUBLICADO,
    *,
    unidade: UnidadeDoAto,
    autoridade: AutoridadeSignataria | None = None,
    data_do_ato: date | None = None,
    consolidacao: Consolidacao | None = None,
) -> bytes:
    """O mesmo documento, em dois modos.

    Em `MODO_PUBLICADO` o resultado é o de sempre, byte a byte — uma fixture o guarda. Em
    `MODO_PREVIA` a seção de integridade não é composta e `content_hash` **não é lido em lugar
    nenhum**: um documento administrativo que parece publicado sem ter sido é risco normativo, e
    depender de o chamador passar vazio seria deixar a garantia com quem não a tem (FR-014).

    `data_do_ato` e `consolidacao` são contexto do ato, como a autoridade (054, FR-990, FR-995), e
    seguem a mesma regra de presença: a data é obrigatória no publicado e recusada na prévia; a
    consolidação só existe no documento de uma Retificação, que é sempre publicado.

    `unidade` é obrigatória nos dois modos (060, FR-1112): a prévia também abre com o cabeçalho, e
    só o publicado fecha com o local.
    """
    if modo not in MODOS:
        raise ValueError(f"Modo de renderização desconhecido: {modo!r}.")
    previa = modo == MODO_PREVIA
    # A presença da autoridade é determinada pelo **modo**, não pelo chamador (FR-035). Recusar
    # nos dois sentidos é o que impede os dois erros: um ato publicado sem quem o praticou, e uma
    # prévia que parece publicada.
    if previa and autoridade is not None:
        raise ValueError("A prévia não decorre de Publicação e não tem autoridade signatária.")
    if not previa and autoridade is None:
        raise ValueError("O documento publicado exige a autoridade signatária do ato.")
    if previa and (data_do_ato is not None or consolidacao is not None):
        raise ValueError("A prévia não decorre de Publicação e não tem data nem consolidação.")
    if not previa and data_do_ato is None:
        raise ValueError("O documento publicado exige a data do ato.")

    snapshot = _grafado(snapshot, previa=previa)
    perguntas = por_perguntas(snapshot)

    def compor(paginas):
        # A fonte embutida mede o texto do Edital (069, FR-1381): a quebra, a justificação e a
        # posição são as do glifo que o arquivo carrega, em qualquer leitor.
        composicao = Composicao(metrica=METRICA_DO_EDITAL, equilibrio=True)
        _cabecalho(composicao, snapshot, unidade, consolidacao)

        def fecho():
            # Autoridade e verificação são **um** bloco: quem assinou e a prova do que assinou não
            # se separam por acidente de paginação. Sem isso, um documento que termina perto do fim
            # da página deixa o SHA-256 sozinho na seguinte — que foi o que o primeiro exemplo com
            # dois Perfis mostrou, e que o cenário de referência escondia por caber.
            with composicao.bloco():
                _autoridade(composicao, autoridade, data_do_ato, unidade.local)
                _integridade(composicao, snapshot, content_hash)

        # O fecho entra **dentro** do bloco da última seção (069): ver `com_o_fecho`.
        fecho_do_ato = None if previa else fecho
        if perguntas:
            plano = _apresentacao().compor(
                composicao, snapshot, paginas=paginas, fecho=fecho_do_ato
            )
            rotulos = [secao.rotulo for secao in plano.secoes]
        else:
            rotulos = _secoes(
                composicao, snapshot, paginas=paginas, com_sumario=True, fecho=fecho_do_ato
            )
        return composicao, rotulos

    # O sumário diz a página de cada seção, e a página depende do sumário: compõe-se até as páginas
    # que ele imprime serem as em que as seções caem (R-012). Converge na segunda ou na terceira.
    paginas = {}
    for _ in range(4):
        composicao, rotulos = compor(paginas)
        paginado = composicao.paginar()
        achadas = _paginas_das_secoes(paginado, rotulos)
        if achadas == paginas:
            break
        paginas = achadas
    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = edital if previa else f"{edital} · Verificação {content_hash[:16]}…"
    return _arquivo_do_edital(
        composicao,
        identificacao=identificacao,
        marca=MARCA_DE_PREVIA if previa else "",
        paginas=paginado,
        navegacao=navegacao_do_edital(snapshot, unidade, rotulos),
    )


METRICA_DO_EDITAL = fonte_do_edital.METRICA


@dataclass(frozen=True)
class Navegacao:
    """O que o arquivo do Edital oferece para navegar (069, FR-1384 a FR-1388, R-012).

    `marcadores` são `(nível, texto, prefixo)`: o texto do marcador e o começo da linha em negrito
    que o documento imprime para a seção ("5. ") ou a subseção ("5.1 "). `sumario` são os rótulos
    das seções como o sumário os imprime, na ordem.
    """

    titulo: str
    autor: str
    marcadores: tuple = ()
    sumario: tuple = ()


def navegacao_do_edital(snapshot, unidade, rotulos):
    """Título, autor e marcadores do Edital, pela lista de itens que numera o documento (R-003)."""
    marcadores = []
    for item in itens_do_documento(snapshot):
        if item.natureza == ITEM_SECAO:
            marcadores.append((1, f"{item.numero}. {item.descricao}", f"{item.numero}. "))
        else:
            marcadores.append((2, f"{item.numero} {item.descricao}", f"{item.numero} "))
    sigla = getattr(unidade, "sigla", "") or ""
    # O anúncio em caixa mista: "Edital nº 91/2026 — …", que é o que o leitor mostra na janela.
    titulo = re.sub(r"^EDITAL N[ºO°]", "Edital nº", anuncio_do_ato(snapshot))
    return Navegacao(
        titulo=titulo,
        autor=f"Ifes — {sigla}" if sigla else "Ifes",
        marcadores=tuple(marcadores),
        sumario=tuple(rotulos),
    )


def _cadeia_do_pdf(valor):
    """Uma cadeia de texto do PDF: literal quando ASCII; `<FEFF…>` em UTF-16BE, quando não."""
    valor = str(valor)
    try:
        valor.encode("ascii")
    except UnicodeEncodeError:
        return "<FEFF" + valor.encode("utf-16-be").hex().upper() + ">"
    return "(" + valor.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ")"


# Os endereços que o texto impresso escreve e que viram link (R-012). Nenhum é acrescentado: o link
# cobre o que está desenhado, e só isso.
ENDERECO_DE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
ENDERECO_DA_WEB = re.compile(r"https?://[^\s»”\"<>]+[^\s»”\"<>.,;:)]")


def _registrar_enderecos(composicao, texto):
    """Guarda, na composição, os endereços do texto inteiro — antes de o refluxo os partir."""
    enderecos = getattr(composicao, "enderecos", None)
    if enderecos is None:
        return
    for padrao in (ENDERECO_DE_EMAIL, ENDERECO_DA_WEB):
        enderecos.update(casado.group(0) for casado in padrao.finditer(str(texto)))


def _uri(endereco):
    """O alvo do link em ASCII, como a `/URI` exige: o acento vai em `%XX`, do UTF-8."""
    return quote(endereco, safe=":/?#[]@!$&'()*+,;=%~-._")


def _posicoes_dos_titulos(paginas, marcadores):
    """`[(página, y)]` de cada marcador: a linha em negrito que começa pelo prefixo dele.

    Procura em ordem, a partir do anterior, porque o mesmo prefixo pode reaparecer adiante — e o
    sumário, que repete os títulos, não é negrito, e por isso não é confundido com eles.
    """
    posicoes, pagina, linha = [], 0, 0
    for _, _, prefixo in marcadores:
        achado = None
        for numero in range(pagina, len(paginas)):
            linhas = paginas[numero][0]
            for indice in range(linha if numero == pagina else 0, len(linhas)):
                texto, fonte, tamanho, _, y, _ = linhas[indice]
                if fonte == NEGRITO and texto.startswith(prefixo):
                    achado = (numero, indice, y + tamanho)
                    break
            if achado:
                break
        if achado is None:
            posicoes.append(None)
            continue
        pagina, linha = achado[0], achado[1] + 1
        posicoes.append((achado[0], achado[2]))
    return posicoes


def _anotacoes(paginas, navegacao, metrica, posicoes, enderecos=None):
    """Por página, os links: do sumário para a seção, e dos endereços escritos no texto.

    `enderecos`, os escritos inteiros: o pedaço de um endereço partido pelo refluxo não vira link.
    """
    por_numero = {}
    for (nivel, _, prefixo), posicao in zip(navegacao.marcadores, posicoes, strict=True):
        if nivel == 1 and posicao is not None:
            por_numero[prefixo] = posicao
    anotacoes = [[] for _ in paginas]
    for numero, (linhas, _) in enumerate(paginas):
        for texto, fonte, tamanho, x, y, espaco in linhas:
            retangulo_da_linha = (MARGEM, y - 3, LARGURA - MARGEM, y + tamanho)
            if fonte == REGULAR and " ." in texto:
                for rotulo in navegacao.sumario:
                    prefixo = rotulo.split(" ", 1)[0] + " "
                    if texto.startswith(rotulo) and prefixo in por_numero:
                        anotacoes[numero].append(
                            ("destino", retangulo_da_linha, por_numero[prefixo])
                        )
                        break
            for padrao, esquema in ((ENDERECO_DE_EMAIL, "mailto:"), (ENDERECO_DA_WEB, "")):
                for casado in padrao.finditer(texto):
                    if esquema and texto[: casado.start()].endswith(("/", ":")):
                        continue
                    if enderecos is not None and casado.group(0) not in enderecos:
                        continue
                    antes = texto[: casado.start()]
                    inicio = x + metrica.largura(antes, tamanho, fonte) + espaco * antes.count(" ")
                    fim = inicio + metrica.largura(casado.group(0), tamanho, fonte)
                    fim += espaco * casado.group(0).count(" ")
                    anotacoes[numero].append(
                        ("endereco", (inicio, y - 3, fim, y + tamanho), esquema + casado.group(0))
                    )
    return anotacoes


def _numero(valor):
    return f"{valor:.2f}".rstrip("0").rstrip(".")


def _arquivo_do_edital(composicao, *, identificacao, marca="", paginas=None, navegacao=None):
    """O arquivo do Edital: o de `render_documento`, com a fonte embutida (069, R-005).

    **Escritor próprio, e não um parâmetro do compartilhado.** O comprovante se regenera a cada
    download e promete ao candidato o SHA-256 do arquivo; o escritor dele não pode mudar um byte
    (FR-1383). O do Edital muda só no que é do Edital: as fontes `/TrueType` embutidas nos mesmos
    recursos `F1` e `F2`, a medida da página pela fonte embutida e o fio sob os títulos de seção.

    Objetos: 1 catálogo, 2 páginas, 3 brasão, depois as seis das fontes e os pares página/conteúdo
    — numeração fixa, para que o mesmo snapshot dê os mesmos bytes. Com `navegacao` (069, R-012),
    depois deles: o `/Info`, a raiz e os itens dos marcadores, e as anotações de link. Sem data e
    sem `/ID`, e sem `/StructTreeRoot` — o arquivo continua sem marcação (FR-1388).
    """
    paginas = paginas if paginas is not None else composicao.paginar()
    fluxos = [
        _fluxo_da_pagina(
            linhas,
            identificacao,
            f"Página {numero} de {len(paginas)}",
            marca=marca,
            tracos=tracos,
            com_brasao=numero == 1,
            estrito=True,
            metrica=composicao.metrica,
            fio_sob_o_titulo=True,
        )
        for numero, (linhas, tracos) in enumerate(paginas, 1)
    ]
    objetos_das_fontes, ids_das_fontes = fonte_do_edital.objetos(4)
    primeira_pagina = 4 + len(objetos_das_fontes)
    ids_paginas = [primeira_pagina + indice * 2 for indice in range(len(fluxos))]
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            b"<< /Type /Pages /Kids ["
            + b" ".join(f"{identificador} 0 R".encode() for identificador in ids_paginas)
            + f"] /Count {len(fluxos)} >>".encode()
        ),
        _objeto_do_brasao(),
        *objetos_das_fontes,
    ]
    recursos = (
        f"/Resources << /Font << /F1 {ids_das_fontes[REGULAR]} 0 R "
        f"/F2 {ids_das_fontes[NEGRITO]} 0 R >> "
        f"/XObject << /{NOME_DO_BRASAO} 3 0 R >> >> "
    ).encode()
    if navegacao is None:
        for indice, fluxo in enumerate(fluxos):
            objetos.append(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] ".encode()
                + recursos
                + f"/Contents {ids_paginas[indice] + 1} 0 R >>".encode()
            )
            objetos.append(
                b"<< /Length "
                + str(len(fluxo)).encode()
                + b" >>\nstream\n"
                + fluxo
                + b"\nendstream"
            )
        return _montar_o_arquivo(objetos)

    posicoes = _posicoes_dos_titulos(paginas, navegacao.marcadores)
    anotacoes = _anotacoes(
        paginas, navegacao, composicao.metrica, posicoes, getattr(composicao, "enderecos", None)
    )
    marcadores = [
        (nivel, texto, posicao)
        for (nivel, texto, _), posicao in zip(navegacao.marcadores, posicoes, strict=True)
        if posicao is not None
    ]
    id_da_informacao = primeira_pagina + 2 * len(fluxos)
    id_dos_marcadores = id_da_informacao + 1
    ids_dos_itens = [id_dos_marcadores + 1 + indice for indice in range(len(marcadores))]
    proxima = id_dos_marcadores + 1 + len(marcadores)
    ids_das_anotacoes = []
    for da_pagina in anotacoes:
        ids_das_anotacoes.append(list(range(proxima, proxima + len(da_pagina))))
        proxima += len(da_pagina)

    objetos[0] = (
        b"<< /Type /Catalog /Pages 2 0 R /Lang (pt-BR) "
        b"/ViewerPreferences << /DisplayDocTitle true >> /PageMode /UseOutlines "
        + f"/Outlines {id_dos_marcadores} 0 R >>".encode()
    )
    for indice, fluxo in enumerate(fluxos):
        anotadas = ""
        if ids_das_anotacoes[indice]:
            anotadas = "/Annots [" + " ".join(f"{i} 0 R" for i in ids_das_anotacoes[indice]) + "] "
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] ".encode()
            + recursos
            + f"{anotadas}/Contents {ids_paginas[indice] + 1} 0 R >>".encode()
        )
        objetos.append(
            b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n" + fluxo + b"\nendstream"
        )
    objetos.append(
        f"<< /Title {_cadeia_do_pdf(navegacao.titulo)} "
        f"/Author {_cadeia_do_pdf(navegacao.autor)} >>".encode()
    )

    def destino(posicao):
        pagina, topo = posicao
        return f"/Dest [{ids_paginas[pagina]} 0 R /XYZ null {_numero(topo + 4)} null]"

    # Os dois níveis: cada seção, e as subseções dela logo abaixo, fechadas (`/Count` negativo).
    pais = [indice for indice, (nivel, _, _) in enumerate(marcadores) if nivel == 1]
    filhos = {pai: [] for pai in pais}
    pai_atual = None
    for indice, (nivel, _, _) in enumerate(marcadores):
        if nivel == 1:
            pai_atual = indice
        elif pai_atual is not None:
            filhos[pai_atual].append(indice)
    soltos = [
        i
        for i, (nivel, _, _) in enumerate(marcadores)
        if nivel != 1 and not any(i in lista for lista in filhos.values())
    ]
    topo_da_arvore = sorted(pais + soltos)
    objetos.append(
        (
            f"<< /Type /Outlines /First {ids_dos_itens[topo_da_arvore[0]]} 0 R "
            f"/Last {ids_dos_itens[topo_da_arvore[-1]]} 0 R /Count {len(topo_da_arvore)} >>"
            if topo_da_arvore
            else "<< /Type /Outlines /Count 0 >>"
        ).encode()
    )
    irmaos = {}
    for grupo in (topo_da_arvore, *filhos.values()):
        for posicao, indice in enumerate(grupo):
            irmaos[indice] = (
                grupo[posicao - 1] if posicao else None,
                grupo[posicao + 1] if posicao + 1 < len(grupo) else None,
            )
    pai_de = {filho: pai for pai, lista in filhos.items() for filho in lista}
    for indice, (_, texto, posicao) in enumerate(marcadores):
        anterior, seguinte = irmaos[indice]
        pai = ids_dos_itens[pai_de[indice]] if indice in pai_de else id_dos_marcadores
        partes = [f"<< /Title {_cadeia_do_pdf(texto)} /Parent {pai} 0 R"]
        if anterior is not None:
            partes.append(f"/Prev {ids_dos_itens[anterior]} 0 R")
        if seguinte is not None:
            partes.append(f"/Next {ids_dos_itens[seguinte]} 0 R")
        if filhos.get(indice):
            partes.append(
                f"/First {ids_dos_itens[filhos[indice][0]]} 0 R "
                f"/Last {ids_dos_itens[filhos[indice][-1]]} 0 R /Count -{len(filhos[indice])}"
            )
        partes.append(f"{destino(posicao)} >>")
        objetos.append(" ".join(partes).encode())
    for da_pagina in anotacoes:
        for especie, (x0, y0, x1, y1), alvo in da_pagina:
            retangulo = " ".join(_numero(valor) for valor in (x0, y0, x1, y1))
            acao = (
                destino(alvo)
                if especie == "destino"
                else (f"/A << /S /URI /URI {_cadeia_do_pdf(_uri(alvo))} >>")
            )
            objetos.append(
                f"<< /Type /Annot /Subtype /Link /Rect [{retangulo}] /Border [0 0 0] "
                f"{acao} >>".encode()
            )
    return _montar_o_arquivo(objetos, informacao=id_da_informacao)


def _objeto_do_brasao():
    return (
        f"<< /Type /XObject /Subtype /Image /Width {brasao.LARGURA} "
        f"/Height {brasao.ALTURA} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
        f"/Filter /FlateDecode /Length {len(brasao.FLUXO)} >>\nstream\n".encode()
        + brasao.FLUXO
        + b"\nendstream"
    )


def _montar_o_arquivo(objetos, *, raiz=1, informacao=None):
    """Os objetos numerados, a tabela de referências e o trailer — sem `/ID` e sem data."""
    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    deslocamentos = []
    for indice, objeto in enumerate(objetos, 1):
        deslocamentos.append(len(saida))
        saida.extend(f"{indice} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(saida)
    saida.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode())
    for deslocamento in deslocamentos:
        saida.extend(f"{deslocamento:010d} 00000 n \n".encode())
    info = f" /Info {informacao} 0 R" if informacao else ""
    saida.extend(
        f"trailer << /Size {len(objetos) + 1} /Root {raiz} 0 R{info} >>\nstartxref\n{xref}\n"
        "%%EOF\n".encode()
    )
    return bytes(saida)


def render_documento(
    composicao, *, identificacao, marca="", com_brasao=True, estrito=False
) -> bytes:
    """Pagina uma composição e monta o arquivo PDF.

    Extraída de `render_edital_pdf` quando o comprovante de inscrição passou a ser gerado no
    servidor: os dois documentos são diferentes em tudo o que dizem e idênticos em como viram
    arquivo. O que estava embutido num deles era, na verdade, a infraestrutura dos dois.

    O resultado é determinístico — não há data de criação embutida, nem identificador aleatório —,
    e é isso que permite publicar o resumo de um documento gerado e esperar que ele confira.

    `estrito` recusa caractere sem grafia em vez de trocá-lo por `?` (achado de 08/10), e só o
    Edital o liga: é o único documento cujo texto passa por validação antes de ser composto.
    """
    paginas = composicao.paginar()
    fluxos = [
        _fluxo_da_pagina(
            linhas,
            identificacao,
            f"Página {numero} de {len(paginas)}",
            marca=marca,
            tracos=tracos,
            com_brasao=com_brasao and numero == 1,
            estrito=estrito,
        )
        for numero, (linhas, tracos) in enumerate(paginas, 1)
    ]

    # Objetos: 1 catálogo, 2 páginas, 3 e 4 fontes, 5 brasão, depois pares página/conteúdo.
    primeiro_pagina = 6
    ids_paginas = [primeiro_pagina + indice * 2 for indice in range(len(fluxos))]
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            b"<< /Type /Pages /Kids ["
            + b" ".join(f"{identificador} 0 R".encode() for identificador in ids_paginas)
            + f"] /Count {len(fluxos)} >>".encode()
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        (
            f"<< /Type /XObject /Subtype /Image /Width {brasao.LARGURA} "
            f"/Height {brasao.ALTURA} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
            f"/Filter /FlateDecode /Length {len(brasao.FLUXO)} >>\nstream\n".encode()
            + brasao.FLUXO
            + b"\nendstream"
        ),
    ]
    for indice, fluxo in enumerate(fluxos):
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] ".encode()
            + b"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> "
            + f"/XObject << /{NOME_DO_BRASAO} 5 0 R >> >> ".encode()
            + f"/Contents {ids_paginas[indice] + 1} 0 R >>".encode()
        )
        objetos.append(
            b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n" + fluxo + b"\nendstream"
        )

    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    deslocamentos = []
    for indice, objeto in enumerate(objetos, 1):
        deslocamentos.append(len(saida))
        saida.extend(f"{indice} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(saida)
    saida.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode())
    for deslocamento in deslocamentos:
        saida.extend(f"{deslocamento:010d} 00000 n \n".encode())
    saida.extend(
        f"trailer << /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(saida)
