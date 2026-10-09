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

from django.utils import timezone

# Apelidado, e não importado como `marcos`: dentro de `_marcos` a variável local com esse nome é
# a lista de marcos do Perfil, e o módulo ficaria sombreado justamente na função que precisa dele.
from processo_seletivo.editais.domain import marcos as regras_do_marco
from processo_seletivo.editais.domain import quadro as quadro_do_perfil
from processo_seletivo.editais.domain.documentos import denominacao_do_codigo
from processo_seletivo.editais.domain.perfis import CAMPOS_DO_METODO
from processo_seletivo.editais.domain.secoes import GERADA
from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    ETAPA_NAO_IDENTIFICADA,
    criterio_com_a_ausencia,
    por_identificador,
)
from processo_seletivo.publicacoes.infrastructure import brasao, humano

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
    texto: str, tamanho: float, recuo: float, fonte: str = REGULAR, limite: float | None = None
) -> list[str]:
    """Reflui por largura real, e não por contagem de caracteres (FR-002, FR-032).

    `limite` é a largura da coluna, quando o texto é célula de tabela: sem ele o refluxo usaria a
    página inteira e a célula atravessaria as colunas vizinhas.
    """
    # A tolerância existe porque a largura de uma coluna é calculada a partir da largura do seu
    # próprio conteúdo: sem ela, a igualdade exata falha por arredondamento e a célula que definiu
    # a coluna é a primeira a quebrar dentro dela — foi assim que um `40` virou `4` e `0`.
    disponivel = (limite if limite is not None else LARGURA - 2 * MARGEM - recuo) + 0.01
    linhas, atual = [], ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if largura(candidato, tamanho, fonte) <= disponivel:
            atual = candidato
            continue
        if atual:
            linhas.append(atual)
        # Uma palavra sozinha mais larga que o espaço disponível não tem onde quebrar por espaço.
        # Parti-la é feio; deixá-la atravessar a margem é pior, e é o que acontecia.
        while largura(palavra, tamanho, fonte) > disponivel and len(palavra) > 1:
            corte = len(palavra)
            while corte > 1 and largura(palavra[:corte], tamanho, fonte) > disponivel:
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


def _moldura(topo, base):
    """O contorno de um bloco, da primeira à última linha que ele colocou na página."""
    return (
        "ret",
        MARGEM - 6,
        base - 4,
        LARGURA - 2 * MARGEM + 12,
        topo - base + FOLGA_DA_MOLDURA + 4,
    )


def _espacamento(texto, fonte, tamanho, recuo):
    """Quanto acrescentar a cada espaço para a linha alcançar a margem direita.

    É a justificação dos Editais de referência, e ela só é possível por causa de FR-002: sem
    largura real não há folga a distribuir. Linha de um espaço só, ou já cheia, não é esticada —
    espaço enorme entre duas palavras é pior que a margem irregular que ele tentaria corrigir.
    """
    espacos = str(texto).count(" ")
    if not espacos:
        return 0.0
    folga = (LARGURA - 2 * MARGEM - recuo) - largura(texto, tamanho, fonte)
    if folga <= 0:
        return 0.0
    por_espaco = folga / espacos
    return por_espaco if por_espaco <= tamanho * 0.35 else 0.0


def _x(texto, fonte, tamanho, recuo, alinhamento):
    """Onde a linha começa. Centralizar e alinhar à direita só é possível por causa de FR-002."""
    if alinhamento == ESQUERDA:
        return MARGEM + recuo
    util = LARGURA - 2 * MARGEM
    sobra = util - largura(texto, tamanho, fonte)
    return MARGEM + (sobra / 2 if alinhamento == CENTRO else sobra)


class Composicao:
    """Acumula itens com estilo, recuo e fronteira de bloco; a paginação acontece depois.

    O item deixou de ser sempre texto: `Traço` é a primitiva gráfica de FR-003, e o bloco é a
    fronteira que FR-004 pede. Nada disso é motor de layout — são três conceitos, e a decisão de
    quebra é uma cascata de cinco degraus que sempre termina em alternativa exequível.
    """

    ESPESSURA_DO_FIO = 0.6

    def __init__(self):
        self.itens: list = []

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
        partes = _quebrar(texto, tamanho, recuo, fonte)
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
                    tracos.append(_moldura(aberto["topo"], rastro[0][4] if rastro else y))
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
                    tracos.append(_moldura(aberto["topo"], y))
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
                x = _x(texto, fonte, tamanho, recuo, alinhamento)
                espaco = _espacamento(texto, fonte, tamanho, recuo) if justificar else 0.0
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
        anuncio_do_ato(snapshot).upper(),
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
    if snapshot.get("description"):
        composicao.escrever(snapshot["description"], tamanho=CORPO_TEXTO, antes=20, justificar=True)


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


def _x_na_celula(texto, fonte, tamanho, recuo, coluna, alinhamento):
    """Onde a célula começa dentro da sua coluna.

    Centralizar o cabeçalho é o que os Editais de referência fazem — e só é possível porque a
    largura da coluna e a do texto são ambas conhecidas (FR-002).
    """
    if alinhamento != CENTRO:
        return recuo
    return recuo + max((coluna - PADDING_DA_COLUNA - largura(texto, tamanho, fonte)) / 2, 0.0)


def _larguras_das_colunas(cabecalho, linhas, tamanho, disponivel):
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
            largura(cabecalho[c], tamanho, NEGRITO) if cabecalho else 0.0,
            *(largura(linha[c], tamanho, REGULAR) for linha in linhas),
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
    colunas = _larguras_das_colunas(
        cabecalho, linhas + ([rodape] if rodape else []), tamanho, disponivel
    )

    por_coluna = alinhamentos or [ESQUERDA] * len(linhas[0])

    def escrever_linha(celulas, fonte, repetir=False, alinhamento=None):
        refluidas = [
            # O teto do refluxo é a largura da coluna menos o mesmo padding com que ela foi
            # medida. Descontar mais do que se somou faria a célula que **definiu** a coluna
            # quebrar dentro dela — `Campus Serra` virava duas linhas.
            _quebrar(celula, tamanho, 0.0, fonte, limite=colunas[c] - PADDING_DA_COLUNA)
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
                        composicao.escrever(
                            f"{indice}º {criterio_com_a_ausencia(criterio, etapas, fatos)}",
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
    # A frase é a de `FRASE_DA_REVERSAO`, a mesma que a seção consolidada imprime (068): duas
    # grafias da mesma regra em dois lugares é como uma delas fica para trás.
    frase = FRASE_DA_REVERSAO.get(especie)
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
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
        FORMA_DE_CONVOCACAO_POR_EXTENSO,
    )

    frase = FORMA_DE_CONVOCACAO_POR_EXTENSO.get(perfil.get("callForm"))
    if not frase:
        return
    with composicao.bloco():
        composicao.escrever(
            f"A convocação dos classificados será feita {frase}.",
            antes=4.0,
            justificar=True,
        )


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
        reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
        if perfil.get("reserveLimit") is not None:
            reserva = f"{reserva} em {perfil['reserveLimit']}"
        linhas.append(
            [
                f"{perfil.get('code', '')} — {perfil.get('name', '')}",
                perfil.get("locality", "") or "—",
                str(perfil.get("immediateVacancies", 0)),
                reserva or "—",
                perfil.get("workload", "") or "—",
            ]
        )
    _tabela(
        composicao,
        ["Perfil", "Localidade", "Vagas", "Cadastro reserva", "Carga horária"],
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
    plano = plano_de_consolidacao(snapshot, secao)
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
                _remissao(composicao, "Marcos classificatórios", f"os descritos no item {numero}.")
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
                    ["Cadastro reserva", _reserva(perfil)],
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
            tamanho=CORPO_BLOCO,
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
            composicao.escrever(f"• {requisito}", tamanho=CORPO_TEXTO, recuo=32)


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


def _itens_do_bloco(funcao, *argumentos, **nomeados):
    """Os itens que `funcao` escreveria — a identidade de um bloco impresso (068, R-002, D-003).

    É a definição literal de "o documento os imprimiria iguais": texto, fonte, corpo, recuo,
    espaço, fronteiras de bloco, linha a linha. Uma chave por campos do snapshot teria de reproduzir
    cada regra do compositor — o método que governa, a habilitação, a ordem dos critérios, as
    omissões da `067` sob sorteio — e divergiria dele na primeira mudança.
    """
    rascunho = Composicao()
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


def plano_de_consolidacao(snapshot, secao=0):
    """O plano da seção de Perfis, ou `None` com um Perfil só (068, R-001, R-003)."""
    perfis = snapshot.get("profiles") or []
    if len(perfis) < 2:
        return None
    grupos = [
        (ATRIBUICOES, [tuple(grupo) for grupo in grupos_de_atribuicoes(perfis)]),
        (REQUISITOS, _agrupar(perfis, lambda perfil: _itens_do_bloco(_requisitos, perfil))),
        (
            MARCOS,
            _agrupar(perfis, lambda perfil: _itens_do_bloco(_marcos, snapshot, perfil, False)),
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
        vagas=_plano_da_tabela_de_vagas(perfis, listas),
        modalidades=_grupos_de_modalidades(perfis, listas),
        reversoes=_frases_da_reversao(perfis),
        convocacoes=_frases_da_convocacao(perfis),
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


def _plano_da_tabela_de_vagas(perfis, listas):
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
    if _cabe_lado_a_lado(cabecalho, matriz):
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


def _cabe_lado_a_lado(cabecalho, linhas, recuo=0.0):
    """As colunas cabem na página sem partir palavra? (068, R-004)

    A largura mínima de uma coluna é a da sua maior palavra, no cabeçalho ou numa célula, mais o
    padding. `_larguras_das_colunas` reparte o espaço entre as colunas longas, e uma palavra maior
    que a coluna seria partida ao meio por `_quebrar` — o código da lista ilegível no cabeçalho.
    """
    minimas = [
        max(
            max(
                largura(palavra, CORPO_TABELA, NEGRITO)
                for palavra in (cabecalho[c].split() or [""])
            ),
            *(
                largura(palavra, CORPO_TABELA, REGULAR)
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


def _frases_da_reversao(perfis):
    """A reversão é regra sobre as quantidades: só os Perfis da tabela de vagas (FR-1350)."""
    com_vaga = [perfil for perfil in perfis if _com_vaga_no_quadro(perfil)]
    pares = [
        (perfil, FRASE_DA_REVERSAO.get((perfil.get("vacancyReversion") or {}).get("kind")))
        for perfil in com_vaga
    ]
    return _frases_por_alcance(pares, com_vaga)


def _frases_da_convocacao(perfis):
    """A convocação é regra do Perfil inteiro, com quadro ou sem ele (FR-1351)."""
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
        FORMA_DE_CONVOCACAO_POR_EXTENSO,
    )

    pares = []
    for perfil in perfis:
        forma = FORMA_DE_CONVOCACAO_POR_EXTENSO.get(perfil.get("callForm"))
        pares.append(
            (perfil, f"A convocação dos classificados será feita {forma}." if forma else None)
        )
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


def _legenda_com_codigos(tabelas, titulo, perfis, recuo):
    """A legenda que nomeia Perfis, em linhas que nunca partem um código (068, R-008)."""
    rotulo = "Perfil" if len(perfis) == 1 else "Perfis"
    return _linhas_sem_partir(
        tabelas.legenda(f"{titulo} — {rotulo}"),
        _codigos_enumerados([perfil.get("code", "") for perfil in perfis]),
        CORPO_TEXTO,
        NEGRITO,
        recuo=recuo,
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
        legenda = _legenda_com_codigos(tabelas, titulo, grupo.perfis, recuo=0.0)
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
            linhas = _linhas_sem_partir(inicio, [*pedacos, *texto.split()], CORPO_TEXTO, REGULAR)
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
        f"{numero} {TITULO_DA_SUBSECAO[materia]}",
        _codigos_enumerados([perfil.get("code", "") for perfil in grupo]),
        CORPO_BLOCO,
        NEGRITO,
    )
    for indice, linha in enumerate(linhas):
        composicao.escrever(
            linha,
            tamanho=CORPO_BLOCO,
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
            MARCOS_SEPARADAMENTE,
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


def _linhas_sem_partir(inicio, pedacos, tamanho, fonte, recuo=0.0):
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
        if largura(candidato, tamanho, fonte) <= disponivel:
            atual = candidato
            continue
        linhas.append(atual)
        atual = pedaco
    linhas.append(atual)
    return linhas


def _reserva(perfil):
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
        largura_do_rotulo = largura(f"{rotulo}: ", CORPO_TEXTO, NEGRITO)
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
                tamanho=CORPO_BLOCO,
                fonte=NEGRITO,
                antes=ANTES_DE_BLOCO + 2,
                junto=True,
            )
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


def _titulo_do_grupo(perfil_id, modalidade_id, perfis, modalidades, codigo=None, snapshot=None):
    """O cabeçalho que diz **a quem** aquele bloco de documentos se dirige.

    A aplicabilidade é dado estruturado; aqui ela vira a frase que o candidato lê para saber se
    aquela alínea é com ele. Sem este cabeçalho, um laudo exigido só de uma modalidade pareceria
    exigido de todo mundo — que é exatamente o erro que a lista única de documentos produz nos
    Editais escritos à mão.
    """
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
                _titulo_do_grupo(perfil_id, modalidade_id, perfis, modalidades, codigo, snapshot),
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                antes=ANTES_DE_BLOCO,
                junto=True,
            )
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


def numeracao(snapshot):
    """O número que cada seção terá no documento: `{chave: número}` (054, FR-985).

    `None` para a seção que não sai; `0` para o preâmbulo, que sai sem número. **Uma regra só**, a
    que o compositor usa, lida também pela etapa Conteúdo e pela Revisão: eram três numerações — a
    ordem do catálogo na tela, a mesma ordem na Revisão, e a contagem do que sai no documento —, e
    com 22 seções e textuais vazias a tela diria "15" para a seção que o documento imprime como "9"
    (RC-26).
    """
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
                        f"{TITULO_DA_SUBSECAO[subsecao.materia]} {_enumerar(subsecao.codigos)}",
                    )
                )
        elif corpo is _etapas:
            for ordem, etapa in enumerate(snapshot.get("stages") or [], 1):
                itens.append(
                    ItemDoDocumento(f"{numero}.{ordem}", ITEM_ETAPA, etapa.get("name", ""))
                )
    return itens


def tabelas_do_documento(snapshot):
    """Quantas tabelas — "Tabela N" — o documento terá (065, D-004).

    A contagem acompanha `_Numerador` na composição. Com um Perfil, o quadro de vagas quando há
    linha e a de Modalidades quando há alguma; com dois ou mais (068), a de Perfis, a de vagas
    quando algum Perfil tem linha nela, e uma de Modalidades por grupo — as do plano que a
    composição lê. E o Cronograma. Só em seção que sai no documento.
    """
    snapshot = _grafado(snapshot, previa=False)
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


def _secoes(composicao, snapshot):
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
    for numero, (secao, corpo) in enumerate(numeraveis, 1):
        titulo = f"{numero}. {secao.get('title', '').upper()}"
        composicao.escrever(
            titulo, tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ANTES_DE_SECAO, junto=True
        )
        if corpo is not None:
            corpo(composicao, snapshot, numero, tabelas)
        else:
            paragrafos = [(texto, 0.0) for texto in _paragrafos(secao.get("content", ""))]
            paragrafos += _norma_da_secao(secao, snapshot)
            for indice, (paragrafo, recuo) in enumerate(paragrafos):
                composicao.escrever(
                    paragrafo,
                    tamanho=CORPO_TEXTO,
                    recuo=recuo,
                    antes=ANTES_DE_BLOCO if indice == 0 else ANTES_DE_PARAGRAFO,
                    justificar=True,
                )


# A seção textual onde a norma da inscrição que o sistema executa é publicada.
SECAO_DA_INSCRICAO = "inscricao"


def teto_de_inscricoes(snapshot):
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
    if teto == 1:
        return "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital."
    return f"Cada candidato poderá ter no máximo {teto} inscrições enviadas neste Edital."


# A seção textual onde a declaração do Requerimento de Matrícula é publicada (054, FR-996, D-006).
SECAO_DA_MATRICULA = "matricula"

MOMENTO_DO_REQUERIMENTO = {
    "AT_ENROLLMENT": "no ato da inscrição",
    "AT_CALL": "quando o candidato for convocado",
}

# O recuo da declaração transcrita: é texto que o candidato aceitará, e não redação do Edital, e o
# recuo é o que o separa das frases que o anunciam.
RECUO_DA_DECLARACAO = 18.0


def requerimento_de_matricula(snapshot):
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
    partes = [(f"O Requerimento de Matrícula será enviado {momento}.", 0.0)]
    declaracao = _paragrafos(requerimento.get("declarationText", ""))
    if declaracao:
        partes.append(("Ao enviá-lo, o candidato declarará:", 0.0))
        partes.extend((paragrafo, RECUO_DA_DECLARACAO) for paragrafo in declaracao)
    return partes


def _norma_da_secao(secao, snapshot):
    """Os parágrafos que o sistema acrescenta a uma seção textual, depois do texto de quem redigiu.

    **Na seção, e não num cabeçalho próprio.** O catálogo é fixo (006, FR-034), e uma seção nova só
    para uma frase mudaria a numeração de todo documento. A frase vem **depois** do texto, e nunca
    no lugar dele: o que o autor escreveu continua sendo o que abre a seção.

    Devolve pares `(texto, recuo)`. **Com norma, a seção sai mesmo sem texto do autor** (054,
    FR-984): a norma que o sistema executa não pode depender de alguém ter escrito na seção.
    """
    if secao.get("key") == SECAO_DA_INSCRICAO:
        frase = teto_de_inscricoes(snapshot)
        return [(frase, 0.0)] if frase else []
    if secao.get("key") == SECAO_DA_MATRICULA:
        return requerimento_de_matricula(snapshot)
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
        "identificada abaixo.",
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
    linhas, rodape, pagina, marca="", tracos=(), com_brasao=False, *, estrito=False
):
    partes = []
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
    for forma in tracos:
        if forma[0] == "fundo":
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
        (pagina, LARGURA - MARGEM - largura(pagina, CORPO_NOTA, REGULAR)),
    ):
        partes.append(
            b"BT /"
            + REGULAR.encode()
            + f" {CORPO_NOTA:.1f} Tf {x:.1f} {RODAPE - 16:.1f} Td (".encode()
            + _texto_pdf(texto, estrito=estrito)
            + b") Tj ET"
        )
    return b"\n".join(partes)


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
    composicao = Composicao()
    _cabecalho(composicao, snapshot, unidade, consolidacao)
    _secoes(composicao, snapshot)
    if not previa:
        # Autoridade e verificação são **um** bloco: quem assinou e a prova do que assinou não se
        # separam por acidente de paginação. Sem isso, um documento que termina perto do fim da
        # página deixa o SHA-256 sozinho na seguinte — que foi o que o primeiro exemplo com dois
        # Perfis mostrou, e que o cenário de referência escondia por caber.
        with composicao.bloco():
            _autoridade(composicao, autoridade, data_do_ato, unidade.local)
            _integridade(composicao, snapshot, content_hash)
    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = edital if previa else f"{edital} · Verificação {content_hash[:16]}…"
    return render_documento(
        composicao,
        identificacao=identificacao,
        marca=MARCA_DE_PREVIA if previa else "",
        estrito=True,
    )


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
