"""Renderizador do documento publicado (FR-023).

O PDF é derivado exclusivamente do snapshot homologado: Perfis, vagas, Cadastro Reserva,
modalidades, Regra Normativa e Cronograma são impressos como estão na versão, sem consultar
o banco. A cadeia "dados estruturados → versão homologada → PDF publicado" fica demonstrável
porque o mesmo snapshot sempre produz os mesmos bytes, e o hash do conteúdo aparece no
documento.

Sem dependência externa. O texto usa `WinAnsiEncoding`, que cobre o português — a versão
anterior codificava em ASCII e destruía todo acento de um documento oficial brasileiro.
"""

import re
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from django.utils import timezone

from processo_seletivo.editais.domain.secoes import GERADA
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
    for caractere in str(texto):
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


def _texto_pdf(valor: str) -> bytes:
    """WinAnsi cobre o português; o que não couber vira '?' em vez de quebrar o documento."""
    escapado = str(valor).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escapado.encode("cp1252", "replace")


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
                if quadro is not None and "inicio" in quadro:
                    quadro["linhas"].append((quadro["inicio"], y))
                    if len(quadro["linhas"]) == 1 and cabecalho_ativo:
                        quadro["cabecalho"] = (quadro["inicio"], y)
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

ORGAO = (
    "Ministério da Educação",
    "Instituto Federal do Espírito Santo",
    "Centro de Referência em Formação",
    "e em Educação a Distância",
)


def _cabecalho(composicao, snapshot):
    """A abertura de um ato administrativo (FR-005 a FR-007).

    Calibrado contra os Editais 62/2026 e 73/2026 do Cefor: a hierarquia vem de **peso, caixa alta
    e centralização**, não de corpo grande. Nos dois alvos o ato está em corpo próximo ao do texto,
    e destacar por tamanho produziria um título fora do padrão institucional.
    """
    # O brasão é desenhado fora do fluxo, em posição fixa na primeira página; aqui só se reserva
    # a altura dele, para que o órgão comece abaixo e não por baixo.
    composicao.espaco(ALTURA_DO_BRASAO + 6)
    for indice, linha in enumerate(ORGAO):
        composicao.escrever(
            linha,
            tamanho=CORPO_INSTITUCIONAL,
            alinhamento=CENTRO,
            antes=0.0 if indice else 4.0,
        )
    # Ato e objeto numa frase só, em negrito e caixa alta, como nos três Editais de referência.
    # Separá-los em linhas de corpos diferentes é o que fazia o documento parecer capa de
    # relatório: lá, o que identifica o ato é uma sentença, não um título.
    titulo = str(snapshot.get("title", "")).strip()
    ato = f"EDITAL Nº {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    # **Uma linha só.** Nos três Editais de referência o ato e o objeto são uma sentença. Quando o
    # título já abre por "Edital" — que é como se costuma escrevê-lo —, ele **é** essa sentença, e
    # imprimir os dois faria o documento anunciar o mesmo ato duas vezes.
    anuncio = (
        titulo if titulo.upper().startswith("EDITAL") else (f"{ato} — {titulo}" if titulo else ato)
    )
    composicao.escrever(
        anuncio.upper(), tamanho=CORPO_ATO, fonte=NEGRITO, antes=24, alinhamento=CENTRO
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

    O excesso é tirado sempre da coluna mais larga, e não distribuído: quem estoura a linha é a
    célula longa, e encolher a coluna do `Nº` para acomodá-la não ajudaria ninguém.
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
    piso = largura("MMMM", tamanho, REGULAR) + PADDING_DA_COLUNA
    while sum(naturais) > disponivel:
        maior = max(range(colunas), key=lambda c: naturais[c])
        sobra = disponivel - (sum(naturais) - naturais[maior])
        if sobra < piso:
            # Nem encolhendo a maior cabe: todas cedem na mesma proporção, e o refluxo por célula
            # cuida do resto. É o caso extremo, e sair da página não é alternativa.
            fator = disponivel / sum(naturais)
            return [n * fator for n in naturais]
        naturais[maior] = sobra
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
):
    """Uma tabela: colunas limitadas, células que refluem dentro da sua coluna.

    A altura de cada linha é a da célula mais alta — sem isso, uma célula de três linhas
    escreveria por cima da linha seguinte.
    """
    if not linhas:
        return
    disponivel = LARGURA - 2 * MARGEM - recuo
    colunas = _larguras_das_colunas(cabecalho, linhas, tamanho, disponivel)

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

    if legenda:
        composicao.escrever(
            legenda,
            tamanho=CORPO_TEXTO,
            fonte=NEGRITO,
            recuo=recuo,
            antes=ANTES_DE_BLOCO,
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


def _quadro_de_vagas(composicao, perfis, tabelas):
    """A visão global antes do detalhe — o `Quadro de vagas` dos Editais de referência.

    Um card por Perfil responde "como apresento esta entidade?". O Edital pergunta outra coisa:
    "qual a melhor composição para comunicar esta matéria?" — e a resposta, para dados comparáveis
    entre si, é uma tabela que os põe lado a lado. Com dez Perfis, dez fichas obrigam o leitor a
    percorrer o documento inteiro para saber quantas vagas existem.
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
        legenda=tabelas.legenda("Quadro de vagas"),
    )


def _perfis(composicao, snapshot, secao=0, tabelas=None):
    """O quadro de vagas, e depois cada Perfil como subseção.

    **Sem moldura externa.** O retângulo em volta de tudo produzia um cartão de interface
    impresso: tabela dentro de caixa dentro de caixa. Um Edital descreve a vaga em prosa e
    subtítulo numerado, e reserva a grade para o que é matriz.

    A subseção é numerada a partir da seção-mãe já resolvida, como as Etapas (FR-013).
    """
    perfis = snapshot.get("profiles") or []
    if len(perfis) > 1:
        _quadro_de_vagas(composicao, perfis, tabelas)

    for ordem, perfil in enumerate(perfis, 1):
        with composicao.bloco(coeso=False):
            with composicao.bloco():
                composicao.escrever(
                    f"{secao}.{ordem} {perfil.get('code', '')} — {perfil.get('name', '')}",
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
            if len(perfis) == 1:
                with composicao.bloco():
                    _pares(
                        composicao,
                        [
                            ["Localidade", perfil.get("locality", "") or "—"],
                            ["Vagas imediatas", str(perfil.get("immediateVacancies", 0))],
                            ["Cadastro reserva", _reserva(perfil)],
                        ],
                    )
            if perfil.get("duties"):
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
            for rotulo, chave in (("Carga horária", "workload"), ("Remuneração", "compensation")):
                if perfil.get(chave) and len(perfis) == 1:
                    composicao.escrever(
                        f"{rotulo}: {perfil[chave]}",
                        tamanho=CORPO_TEXTO,
                        recuo=18,
                        antes=ANTES_DE_LINHA,
                    )
            if perfil.get("compensation") and len(perfis) > 1:
                composicao.escrever(
                    f"Remuneração: {perfil['compensation']}",
                    tamanho=CORPO_TEXTO,
                    recuo=18,
                    antes=ANTES_DE_LINHA,
                )
            requisitos = perfil.get("requirements") or []
            if requisitos:
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
            _modalidades(composicao, perfil, tabelas, len(perfis) > 1)


def _reserva(perfil):
    reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
    if perfil.get("reserveLimit") is not None:
        reserva = f"{reserva} em {perfil['reserveLimit']}"
    return reserva or "—"


def _pares(composicao, pares, *, recuo=18.0):
    """Rótulo em negrito e valor na mesma linha — tipografia, não grade.

    Tabela é para comparar muitas linhas; poucos atributos de um único objeto se descrevem com
    peso tipográfico. Emoldurar quatro pares produz ficha administrativa, não Edital.
    """
    for rotulo, valor in pares:
        largura_do_rotulo = largura(f"{rotulo}: ", CORPO_TEXTO, NEGRITO)
        composicao.escrever(
            f"{rotulo}:", tamanho=CORPO_TEXTO, fonte=NEGRITO, recuo=recuo, antes=ANTES_DE_LINHA
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
    linhas = [
        [
            str(evento.get("order", "")),
            evento.get("description") or evento.get("type", ""),
            _instante(evento.get("startAt")),
            _instante(evento["endAt"]) if evento.get("endAt") else "—",
        ]
        for evento in eventos
    ]
    _tabela(
        composicao,
        ["Nº", "Evento", "Início", "Término"],
        linhas,
        recuo=0.0,
        alinhamentos=[CENTRO, ESQUERDA, CENTRO, CENTRO],
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


def _nomes_do_alcance(snapshot):
    perfis, modalidades = {}, {}
    for perfil in snapshot.get("profiles") or []:
        perfis[perfil.get("id")] = perfil.get("name") or perfil.get("code", "")
        for modalidade in perfil.get("competitionModalities") or []:
            modalidades[modalidade.get("id")] = modalidade.get("name") or modalidade.get("code", "")
    return perfis, modalidades


def _titulo_do_grupo(perfil_id, modalidade_id, perfis, modalidades):
    """O cabeçalho que diz **a quem** aquele bloco de documentos se dirige.

    A aplicabilidade é dado estruturado; aqui ela vira a frase que o candidato lê para saber se
    aquela alínea é com ele. Sem este cabeçalho, um laudo exigido só de uma modalidade pareceria
    exigido de todo mundo — que é exatamente o erro que a lista única de documentos produz nos
    Editais escritos à mão.
    """
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
        chave = (requisito.get("profileId"), requisito.get("modalityId"))
        grupos.setdefault(chave, []).append(requisito)
    for (perfil_id, modalidade_id), documentos in grupos.items():
        with composicao.bloco():
            composicao.escrever(
                _titulo_do_grupo(perfil_id, modalidade_id, perfis, modalidades),
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
}


def _materializaveis(snapshot):
    """As seções que **serão** compostas, na ordem do conteúdo publicado (FR-038).

    Uma seção gerada cuja fonte está vazia não é composta. Um título sobre nada não informa que não
    há nada — informa que alguém esqueceu de preencher, e num Edital sem Etapas de Avaliação isso
    seria falso: a coleção é opcional.
    """
    materializaveis = []
    for secao in sorted(snapshot.get("sections") or [], key=lambda item: item.get("order", 0)):
        if secao.get("type") == GERADA:
            corpo = _CORPO_GERADO.get(secao.get("source"))
            if corpo is None or not (snapshot.get(secao.get("source")) or []):
                continue
            materializaveis.append((secao, corpo))
        else:
            materializaveis.append((secao, None))
    return materializaveis


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
            for indice, paragrafo in enumerate(_paragrafos(secao.get("content", ""))):
                composicao.escrever(
                    paragrafo,
                    tamanho=CORPO_TEXTO,
                    antes=ANTES_DE_BLOCO if indice == 0 else ANTES_DE_PARAGRAFO,
                    justificar=True,
                )


def _autoridade(composicao, autoridade):
    """Quem praticou o ato — anunciado como registro, não como assinatura (FR-033).

    **A rubrica é deliberada.** Um nome centralizado sozinho ao pé de um Edital lê-se como
    assinatura, e este documento não tem assinatura: não há certificado, não há ICP, não há
    rubrica digitalizada (FR-036). O que ele tem é o registro imutável de quem praticou o ato, que
    a Publicação guardou. Anunciar isso — "Autoridade responsável pelo ato" — é a diferença entre
    informar e simular.

    O cargo só é composto quando diz algo além do nome. O catálogo de demonstração traz cargo no
    campo de nome, e repetir `Reitora do Ifes / Reitora` faria o documento parecer defeituoso onde
    ele apenas reflete o dado que existe.
    """
    composicao.escrever(
        "Autoridade responsável pelo ato",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_SECAO + 16,
        alinhamento=CENTRO,
        junto=True,
    )
    composicao.escrever(
        autoridade.nome,
        tamanho=CORPO_TEXTO,
        fonte=NEGRITO,
        antes=ANTES_DE_LINHA + 2,
        alinhamento=CENTRO,
    )
    cargo = str(autoridade.cargo or "").strip()
    if cargo and cargo.casefold() not in str(autoridade.nome or "").casefold():
        composicao.escrever(cargo, tamanho=CORPO_TEXTO, alinhamento=CENTRO)


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


def _fluxo_da_pagina(linhas, rodape, pagina, marca="", tracos=(), com_brasao=False):
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
            + _texto_pdf(texto)
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
            + _texto_pdf(texto)
            + b") Tj ET"
        )
    return b"\n".join(partes)


def render_edital_pdf(
    snapshot: dict,
    content_hash: str,
    modo: str = MODO_PUBLICADO,
    autoridade: AutoridadeSignataria | None = None,
) -> bytes:
    """O mesmo documento, em dois modos.

    Em `MODO_PUBLICADO` o resultado é o de sempre, byte a byte — uma fixture o guarda. Em
    `MODO_PREVIA` a seção de integridade não é composta e `content_hash` **não é lido em lugar
    nenhum**: um documento administrativo que parece publicado sem ter sido é risco normativo, e
    depender de o chamador passar vazio seria deixar a garantia com quem não a tem (FR-014).
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

    composicao = Composicao()
    _cabecalho(composicao, snapshot)
    _secoes(composicao, snapshot)
    if not previa:
        # Autoridade e verificação são **um** bloco: quem assinou e a prova do que assinou não se
        # separam por acidente de paginação. Sem isso, um documento que termina perto do fim da
        # página deixa o SHA-256 sozinho na seguinte — que foi o que o primeiro exemplo com dois
        # Perfis mostrou, e que o cenário de referência escondia por caber.
        with composicao.bloco():
            _autoridade(composicao, autoridade)
            _integridade(composicao, snapshot, content_hash)
    paginas = composicao.paginar()

    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = edital if previa else f"{edital} · Verificação {content_hash[:16]}…"
    fluxos = [
        _fluxo_da_pagina(
            linhas,
            identificacao,
            f"Página {numero} de {len(paginas)}",
            marca=MARCA_DE_PREVIA if previa else "",
            tracos=tracos,
            com_brasao=numero == 1,
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
