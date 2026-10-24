"""A diagramação do documento gerencial: blocos posicionados na página, sem dependência (100).

**Por que um compositor próprio.** O escritor do Edital (`publicacoes/infrastructure/pdf.py`) é um
paginador de texto corrido: empilha linhas, e só sabe desenhar as grades e as molduras que esse
fluxo pede, num tom de cinza. O relatório consolidado é outra peça — um painel executivo impresso,
com cartões de indicador, colunas lado a lado, barras e faixas de destaque —, e foi isso que se
perdeu quando ele foi composto como texto corrido (revisão visual de 24/10/2026). Acrescentar essas
primitivas ao escritor do Edital mudaria o documento oficial; aqui elas moram à parte.

**O que se reaproveita do escritor do Edital**, e por isso não há dependência nova: a fonte
embutida e a métrica dela, o texto em WinAnsi que recusa caractere sem grafia (`estrito`), o
refluxo por largura real, o brasão, e a montagem determinística do arquivo — sem data e sem
identificador, de modo que os mesmos blocos dão os mesmos bytes.

**O arquivo é marcado** (PDF estruturado): títulos, parágrafos, listas, tabelas e a figura das
barras — com texto alternativo — ficam na árvore de estrutura, e fio, fundo e a faixa de cada
página são artefatos. É o que o leitor de tela e a extração de texto precisam para ler na ordem.

**A paginação respeita os grupos.** Cartão, faixa de atenção, ficha e colunas não se partem;
título de seção não fica sozinho no pé da página; tabela longa continua na seguinte com o cabeçalho
repetido, e linha de tabela não se parte. O relatório do Edital (099), que passou a este compositor
depois, acrescentou o que o volume dele expôs: a nota fica com o bloco que explica, o título conta a
cadeia inteira até a tabela, e nenhuma parte de tabela fica com uma linha só.
"""

from dataclasses import dataclass, field

from processo_seletivo.publicacoes.infrastructure import brasao
from processo_seletivo.publicacoes.infrastructure import fonte as fonte_do_edital
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA,
    LARGURA,
    METRICA_DO_EDITAL,
    NEGRITO,
    NOME_DO_BRASAO,
    REGULAR,
    _cadeia_do_pdf,
    _montar_o_arquivo,
    _objeto_do_brasao,
    _quebrar,
    _texto_pdf,
    _uri,
)

METRICA = METRICA_DO_EDITAL

# --- A página -----------------------------------------------------------------------------------
# Margens da maquete aprovada: 16 mm nas laterais. A faixa de identificação ocupa o alto de toda
# página; o conteúdo começa abaixo dela e termina acima do pé.
MARGEM_X = 46.0
LARGURA_UTIL = LARGURA - 2 * MARGEM_X
Y_DA_FAIXA = ALTURA - 30.0
Y_DO_PE = 24.0
TOPO = ALTURA - 50.0
BASE = 42.0

# --- A paleta da maquete ------------------------------------------------------------------------
TINTA = (0.114, 0.114, 0.106)
TINTA_2 = (0.271, 0.271, 0.247)
TINTA_3 = (0.420, 0.420, 0.400)
FIO = (0.812, 0.812, 0.784)
FUNDO_SUAVE = (0.957, 0.957, 0.941)
DESTAQUE = (0.122, 0.306, 0.475)
ATENCAO = (0.541, 0.353, 0.000)
FUNDO_DE_ATENCAO = (0.984, 0.953, 0.886)
#: A barra do período anterior a um marco, na série diária: o destaque fica para o que veio depois.
BARRA = (0.435, 0.498, 0.561)

ESQUERDA, DIREITA = "esquerda", "direita"


def _cor(rgb, *, traco=False):
    return f"{rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} {'RG' if traco else 'rg'}"


def largura(texto, tamanho, fonte=REGULAR):
    return METRICA.largura(texto, tamanho, fonte)


def quebrar(texto, tamanho, limite, fonte=REGULAR):
    linhas = []
    for paragrafo in str(texto).split("\n"):
        linhas.extend(_quebrar(paragrafo, tamanho, 0.0, fonte, limite=limite, metrica=METRICA))
    return linhas


# --- A estrutura (PDF marcado) ------------------------------------------------------------------


class Elemento:
    """Um elemento da árvore de estrutura: o tipo, o pai, e o conteúdo marcado na ordem."""

    def __init__(self, tipo, pai=None, *, alt=None):
        self.tipo = tipo
        self.alt = alt
        self.pai = pai
        self.k = []
        if pai is not None:
            pai.k.append(("elemento", self))

    def filho(self, tipo, *, alt=None):
        return Elemento(tipo, self, alt=alt)


# --- A tela de uma página -----------------------------------------------------------------------


class Tela:
    """O que se desenha numa página: operadores, links e o conteúdo marcado."""

    def __init__(self, indice):
        self.indice = indice
        self.operadores = []
        self.links = []
        self.mcids = []  # o elemento de cada MCID, na ordem

    def _marcar(self, elemento, operadores):
        mcid = len(self.mcids)
        self.mcids.append(elemento)
        elemento.k.append(("conteudo", self.indice, mcid))
        self.operadores.append(f"/{elemento.tipo} <</MCID {mcid}>> BDC ".encode())
        self.operadores.extend(operadores)
        self.operadores.append(b" EMC")

    def _artefato(self, operadores):
        self.operadores.append(b"/Artifact BMC ")
        self.operadores.extend(operadores)
        self.operadores.append(b" EMC")

    def _conferir(self, x, y, medida):
        """Texto que passaria da margem, ou sairia do papel, é defeito de composição: recusa."""
        if x + medida > LARGURA - MARGEM_X + 0.5 or x < MARGEM_X - 0.5 or not 0 < y < ALTURA:
            raise ValueError(f"Texto fora da área útil da página: x={x:.1f}, y={y:.1f}.")

    def texto(self, x, y, texto, tamanho, *, fonte=REGULAR, cor=TINTA, elemento=None, uri=None):
        self._conferir(x, y, largura(texto, tamanho, fonte))
        operador = (
            f"BT {_cor(cor)} /{fonte} {tamanho:.2f} Tf {x:.2f} {y:.2f} Td (".encode()
            + _texto_pdf(texto, estrito=True)
            + b") Tj ET 0 g"
        )
        if elemento is None:
            self._artefato([operador])
        else:
            self._marcar(elemento, [operador])
        if uri:
            medida = largura(texto, tamanho, fonte)
            self.links.append(((x, y - tamanho * 0.25, x + medida, y + tamanho * 0.85), uri))

    def corrido(self, x, y, partes, tamanho, *, elemento):
        """Uma linha de trechos com fontes diferentes: `[(texto, fonte, cor)]`."""
        self._conferir(x, y, sum(largura(texto, tamanho, fonte) for texto, fonte, _ in partes))
        operadores = []
        cursor = x
        for texto, fonte, cor in partes:
            if not texto:
                continue
            operadores.append(
                f"BT {_cor(cor)} /{fonte} {tamanho:.2f} Tf {cursor:.2f} {y:.2f} Td (".encode()
                + _texto_pdf(texto, estrito=True)
                + b") Tj ET 0 g "
            )
            cursor += largura(texto, tamanho, fonte)
        self._marcar(elemento, operadores)

    def retangulo(self, x, y, w, h, *, fundo=None, borda=None, espessura=0.5):
        partes = []
        if fundo is not None:
            partes.append(f"{_cor(fundo)} {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f 0 g ".encode())
        if borda is not None:
            partes.append(
                f"{_cor(borda, traco=True)} {espessura:.2f} w "
                f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re S 0 G ".encode()
            )
        self._artefato(partes)

    def fio(self, x1, y1, x2, y2, *, cor=FIO, espessura=0.5, tracejado=False):
        traco, fim = ("[2 2] 0 d ", " [] 0 d") if tracejado else ("", "")
        self._artefato(
            [
                f"{_cor(cor, traco=True)} {espessura:.2f} w {traco}{x1:.2f} {y1:.2f} m "
                f"{x2:.2f} {y2:.2f} l S 0 G{fim}".encode()
            ]
        )

    def brasao(self, x, y, altura):
        largura_ = altura * brasao.LARGURA / brasao.ALTURA
        matriz = f"{largura_:.2f} 0 0 {altura:.2f} {x:.2f} {y:.2f}"
        self._artefato([f"q {matriz} cm /{NOME_DO_BRASAO} Do Q".encode()])
        return largura_

    def fluxo(self):
        return b"\n".join(self.operadores)


# --- Os blocos ----------------------------------------------------------------------------------


class Bloco:
    #: Espaço acima do bloco; some no alto da página.
    antes = 0.0
    #: O bloco não começa no pé da página sem o começo do bloco seguinte (títulos).
    junto_ao_seguinte = False
    #: O bloco não abre página sozinho: vai junto com o fim do anterior (notas de tabela).
    preso_ao_anterior = False
    #: O texto do marcador de navegação, quando o bloco abre uma seção.
    marcador = None
    nivel = 1

    def medir(self, w):
        raise NotImplementedError

    def minimo(self, w):
        """A menor altura com que o bloco pode começar numa página."""
        return self.medir(w)

    def partir(self, w, disponivel):
        """`(primeiro, resto)` que caiba em `disponivel`, ou `None` se o bloco não se parte."""
        return None

    def desenhar(self, tela, x, y, w, pai):
        raise NotImplementedError


@dataclass
class Espaco(Bloco):
    altura: float = 8.0

    def medir(self, w):
        return self.altura

    def desenhar(self, tela, x, y, w, pai):
        return None


class QuebraDePagina(Bloco):
    def medir(self, w):
        return 0.0

    def desenhar(self, tela, x, y, w, pai):
        return None


@dataclass
class Trecho:
    texto: str
    fonte: str = REGULAR
    cor: tuple = TINTA


def _quebrar_trechos(trechos, tamanho, limite):
    """Refluxo por palavra de uma linha de trechos com fontes diferentes."""
    palavras = []
    for trecho in trechos:
        for indice, palavra in enumerate(str(trecho.texto).split(" ")):
            if palavra == "":
                continue
            colada = indice == 0 and palavras and not str(trecho.texto).startswith(" ")
            palavras.append((palavra, trecho.fonte, trecho.cor, colada))
    linhas, atual, medida = [], [], 0.0
    for palavra, fonte, cor, colada in palavras:
        espaco = 0.0 if (not atual or colada) else largura(" ", tamanho, REGULAR)
        w = largura(palavra, tamanho, fonte)
        if atual and medida + espaco + w > limite + 0.01:
            linhas.append(atual)
            atual, medida, espaco = [], 0.0, 0.0
        if atual and espaco:
            # O espaço vai na fonte da palavra anterior, para que trechos iguais se juntem num
            # comando só — a extração de texto e o leitor de tela leem a frase, e não palavra a
            # palavra.
            anterior = atual[-1]
            atual[-1] = (anterior[0] + " ", anterior[1], anterior[2])
        if atual and atual[-1][1] == fonte and atual[-1][2] == cor:
            anterior = atual[-1]
            atual[-1] = (anterior[0] + palavra, fonte, cor)
        else:
            atual.append((palavra, fonte, cor))
        medida += espaco + w
    if atual:
        linhas.append(atual)
    return linhas or [[("", REGULAR, TINTA)]]


class Texto(Bloco):
    """Um parágrafo: texto simples ou trechos. Parte-se entre linhas, deixando duas de cada lado."""

    def __init__(
        self,
        texto,
        *,
        tamanho=9.5,
        fonte=REGULAR,
        cor=TINTA,
        entrelinha=1.42,
        antes=4.0,
        tipo="P",
        recuo=0.0,
        uri=None,
        marcador=None,
        nivel=1,
        junto=False,
        preso=False,
        alinhamento=ESQUERDA,
    ):
        self.trechos = (
            [Trecho(texto, fonte, cor)] if isinstance(texto, str) else [t for t in texto if t]
        )
        self.tamanho = tamanho
        self.entrelinha = entrelinha
        self.antes = antes
        self.tipo = tipo
        self.recuo = recuo
        self.uri = uri
        self.marcador = marcador
        self.nivel = nivel
        self.junto_ao_seguinte = junto
        self.preso_ao_anterior = preso
        self.alinhamento = alinhamento
        self._linhas = None
        #: As linhas já decididas, quando o parágrafo é a parte de um que se partiu.
        self._fixas = None

    def linhas(self, w):
        if self._fixas is not None:
            return self._fixas
        if self._linhas is None or self._linhas[0] != w:
            self._linhas = (w, _quebrar_trechos(self.trechos, self.tamanho, w - self.recuo))
        return self._linhas[1]

    @property
    def altura_da_linha(self):
        return self.tamanho * self.entrelinha

    def medir(self, w):
        return len(self.linhas(w)) * self.altura_da_linha

    def minimo(self, w):
        # O parágrafo de menos de quatro linhas não se parte: o mínimo dele é ele inteiro. Dizer
        # duas linhas deixava o título acima no pé da página, sem o parágrafo que ele abria (099).
        if len(self.linhas(w)) < 4:
            return self.medir(w)
        return 2 * self.altura_da_linha

    def partir(self, w, disponivel):
        linhas = self.linhas(w)
        cabem = int(disponivel // self.altura_da_linha)
        if len(linhas) < 4 or cabem < 2 or len(linhas) - cabem < 2:
            return None
        primeiro, resto = (
            _copia_de_texto(self, linhas[:cabem]),
            _copia_de_texto(self, linhas[cabem:]),
        )
        resto.antes = 0.0
        resto.marcador = None
        return primeiro, resto

    def desenhar(self, tela, x, y, w, pai):
        elemento = pai.filho(self.tipo)
        for indice, linha in enumerate(self.linhas(w)):
            base = y - self.tamanho * 0.92 - indice * self.altura_da_linha
            medida = sum(largura(t, self.tamanho, f) for t, f, _ in linha)
            inicio = x + self.recuo if self.alinhamento == ESQUERDA else x + w - medida
            if self.uri and len(linha) == 1:
                tela.texto(
                    inicio,
                    base,
                    linha[0][0],
                    self.tamanho,
                    fonte=linha[0][1],
                    cor=linha[0][2],
                    elemento=elemento,
                    uri=self.uri,
                )
            else:
                tela.corrido(inicio, base, linha, self.tamanho, elemento=elemento)


def _copia_de_texto(original, linhas):
    copia = Texto.__new__(Texto)
    copia.__dict__.update(original.__dict__)
    copia._fixas = linhas
    return copia


class TituloDeSecao(Texto):
    """O título de seção: corpo maior, negrito, fio escuro embaixo. Nunca sozinho no pé."""

    def __init__(self, texto, *, marcador=None, antes=16.0, tamanho=11.5, tipo="H2"):
        super().__init__(
            texto,
            tamanho=tamanho,
            fonte=NEGRITO,
            entrelinha=1.25,
            antes=antes,
            tipo=tipo,
            marcador=marcador or texto,
            junto=True,
        )

    def medir(self, w):
        return super().medir(w) + 6.0

    def minimo(self, w):
        return self.medir(w)

    def partir(self, w, disponivel):
        return None

    def desenhar(self, tela, x, y, w, pai):
        super().desenhar(tela, x, y, w, pai)
        base = y - self.medir(w) + 2.0
        tela.fio(x, base, x + w, base, cor=TINTA, espessura=0.8)


class Subtitulo(Texto):
    def __init__(self, texto, *, antes=10.0, marcador=None):
        super().__init__(
            texto,
            tamanho=9.8,
            fonte=NEGRITO,
            entrelinha=1.3,
            antes=antes,
            tipo="H3",
            marcador=marcador,
            nivel=2,
            junto=True,
        )

    def minimo(self, w):
        return self.medir(w)

    def partir(self, w, disponivel):
        return None


def Nota(texto, *, antes=3.0):  # noqa: N802 — um construtor de bloco, como os demais
    """A nota explica o bloco de cima, e por isso não abre página sozinha (099)."""
    return Texto(texto, tamanho=7.8, cor=TINTA_3, entrelinha=1.35, antes=antes, preso=True)


@dataclass
class Cabecalho(Bloco):
    """O alto da primeira página: brasão pequeno e as linhas do órgão, compactos."""

    linhas: tuple
    antes: float = 0.0
    ALTURA_DO_BRASAO = 30.0

    def medir(self, w):
        return max(self.ALTURA_DO_BRASAO, len(self.linhas) * 10.4) + 8.0

    def desenhar(self, tela, x, y, w, pai):
        largura_do_brasao = tela.brasao(x, y - self.ALTURA_DO_BRASAO, self.ALTURA_DO_BRASAO)
        elemento = pai.filho("P")
        topo_do_texto = y - (self.ALTURA_DO_BRASAO - len(self.linhas) * 10.4) / 2
        for indice, linha in enumerate(self.linhas):
            tela.texto(
                x + largura_do_brasao + 9,
                topo_do_texto - 8.2 - indice * 10.4,
                linha,
                8.5,
                fonte=NEGRITO if indice == 1 else REGULAR,
                cor=TINTA if indice == 1 else TINTA_2,
                elemento=elemento,
            )
        base = y - self.medir(w) + 2.0
        tela.fio(x, base, x + w, base)


@dataclass
class Ficha(Bloco):
    """Pares rótulo × valor em grade de duas colunas, com fio fino em cima de cada um."""

    pares: list  # (rótulo, valor, nota, destaque)
    colunas: int = 2
    antes: float = 10.0
    espaco: float = 18.0

    def _celulas(self, w):
        largura_ = (w - self.espaco * (self.colunas - 1)) / self.colunas
        celulas = []
        for _rotulo, valor, nota, _ in self.pares:
            linhas_do_valor = quebrar(valor, 9.0, largura_, NEGRITO)
            linhas_da_nota = quebrar(nota, 7.4, largura_) if nota else []
            altura = 4 + 9.6 + len(linhas_do_valor) * 11.6 + len(linhas_da_nota) * 9.6 + 4
            celulas.append((linhas_do_valor, linhas_da_nota, altura))
        return largura_, celulas

    def _alturas(self, w):
        _, celulas = self._celulas(w)
        return [
            max(c[2] for c in celulas[i : i + self.colunas])
            for i in range(0, len(celulas), self.colunas)
        ]

    def medir(self, w):
        return sum(self._alturas(w)) + 4 * (len(self._alturas(w)) - 1)

    def desenhar(self, tela, x, y, w, pai):
        largura_, celulas = self._celulas(w)
        alturas = self._alturas(w)
        lista = pai.filho("L")
        topo = y
        for indice, ((rotulo, _, _, destaque), (valor, nota, _)) in enumerate(
            zip(self.pares, celulas, strict=True)
        ):
            linha, coluna = divmod(indice, self.colunas)
            if coluna == 0 and linha:
                topo -= alturas[linha - 1] + 4
            cx = x + coluna * (largura_ + self.espaco)
            tela.fio(cx, topo, cx + largura_, topo)
            item = lista.filho("LI")
            tela.texto(cx, topo - 4 - 7.0, rotulo, 7.8, cor=TINTA_3, elemento=item.filho("Lbl"))
            corpo = item.filho("LBody")
            for i, parte in enumerate(valor):
                tela.texto(
                    cx,
                    topo - 4 - 9.6 - 8.6 - i * 11.6,
                    parte,
                    9.0,
                    fonte=NEGRITO,
                    cor=ATENCAO if destaque else TINTA,
                    elemento=corpo,
                )
            inicio_da_nota = topo - 4 - 9.6 - len(valor) * 11.6
            for i, parte in enumerate(nota):
                tela.texto(
                    cx, inicio_da_nota - 7.2 - i * 9.6, parte, 7.4, cor=TINTA_3, elemento=corpo
                )


@dataclass
class Cartao:
    valor: str
    rotulo: str
    base: str
    de: str = ""


@dataclass
class Cartoes(Bloco):
    """Os indicadores em cartões: o número grande, o rótulo, e a base que o explica embaixo."""

    cartoes: list
    colunas: int = 3
    antes: float = 8.0
    espaco: float = 8.0

    def _largura(self, w):
        return (w - self.espaco * (self.colunas - 1)) / self.colunas

    def _altura_do_cartao(self, cartao, w):
        interno = self._largura(w) - 18
        rotulo = quebrar(cartao.rotulo, 8.8, interno, NEGRITO)
        base = quebrar(cartao.base, 7.6, interno)
        return 3 + 7 + 21 + len(rotulo) * 11 + 2 + len(base) * 9.8 + 8, rotulo, base

    def _alturas(self, w):
        return [
            max(self._altura_do_cartao(c, w)[0] for c in self.cartoes[i : i + self.colunas])
            for i in range(0, len(self.cartoes), self.colunas)
        ]

    def medir(self, w):
        alturas = self._alturas(w)
        return sum(alturas) + self.espaco * (len(alturas) - 1)

    def desenhar(self, tela, x, y, w, pai):
        largura_ = self._largura(w)
        alturas = self._alturas(w)
        lista = pai.filho("L")
        topo = y
        for indice, cartao in enumerate(self.cartoes):
            linha, coluna = divmod(indice, self.colunas)
            if coluna == 0 and linha:
                topo -= alturas[linha - 1] + self.espaco
            altura = alturas[linha]
            cx = x + coluna * (largura_ + self.espaco)
            tela.retangulo(cx, topo - altura, largura_, altura, fundo=FUNDO_SUAVE)
            tela.retangulo(cx, topo - 3, largura_, 3, fundo=DESTAQUE)
            _, rotulo, base = self._altura_do_cartao(cartao, w)
            item = lista.filho("LI")
            corpo = item.filho("LBody")
            linha_do_valor = topo - 3 - 7 - 16
            tela.corrido(
                cx + 9,
                linha_do_valor,
                [(cartao.valor, NEGRITO, TINTA)],
                19,
                elemento=corpo,
            )
            if cartao.de:
                tela.texto(
                    cx + 9 + largura(cartao.valor, 19, NEGRITO) + 4,
                    linha_do_valor,
                    cartao.de,
                    9.0,
                    cor=TINTA_2,
                    elemento=corpo,
                )
            cursor = topo - 3 - 7 - 21
            for parte in rotulo:
                cursor -= 11
                tela.texto(cx + 9, cursor + 2.4, parte, 8.8, fonte=NEGRITO, elemento=corpo)
            cursor -= 2
            for parte in base:
                cursor -= 9.8
                tela.texto(cx + 9, cursor + 2.2, parte, 7.6, cor=TINTA_3, elemento=corpo)


@dataclass
class Atencao(Bloco):
    """A faixa de pontos de atenção: fundo âmbar claro, barra à esquerda, itens numerados.

    O número fica numa coluna própria, com o texto em recuo pendente: "1." colado ao começo da
    frase se lia "1.1 Edital".
    """

    titulo: str
    itens: list  # (título do item, texto)
    antes: float = 10.0
    TAMANHO = 8.8
    ENTRELINHA = 12.2

    def _recuo(self):
        return largura(f"{len(self.itens)}.", self.TAMANHO, NEGRITO) + 5

    def _linhas(self, w):
        interno = w - 14 - 12 - self._recuo()
        return [
            _quebrar_trechos([Trecho(titulo, NEGRITO), Trecho(" " + texto)], self.TAMANHO, interno)
            for titulo, texto in self.itens
        ]

    def medir(self, w):
        linhas = self._linhas(w)
        return 7 + 14 + sum(len(item) * self.ENTRELINHA + 3 for item in linhas) + 6

    def desenhar(self, tela, x, y, w, pai):
        altura = self.medir(w)
        tela.retangulo(x, y - altura, w, altura, fundo=FUNDO_DE_ATENCAO)
        tela.retangulo(x, y - altura, 3, altura, fundo=ATENCAO)
        secao = pai.filho("Sect")
        tela.texto(
            x + 14,
            y - 7 - 10,
            self.titulo,
            10.5,
            fonte=NEGRITO,
            cor=ATENCAO,
            elemento=secao.filho("H2"),
        )
        lista = secao.filho("L")
        recuo = self._recuo()
        cursor = y - 7 - 14
        for numero, item in enumerate(self._linhas(w), 1):
            elemento = lista.filho("LI")
            cursor -= 3
            for indice, linha in enumerate(item):
                cursor -= self.ENTRELINHA
                if indice == 0:
                    tela.texto(
                        x + 14,
                        cursor + 2.8,
                        f"{numero}.",
                        self.TAMANHO,
                        fonte=NEGRITO,
                        elemento=elemento.filho("Lbl"),
                    )
                tela.corrido(x + 14 + recuo, cursor + 2.8, linha, self.TAMANHO, elemento=elemento)


@dataclass
class Celula:
    """Uma célula com mais de um trecho em linhas: `[(texto, tamanho, fonte, cor, uri)]`."""

    partes: list


def _partes(celula, fonte_padrao):
    if isinstance(celula, Celula):
        return celula.partes
    return [(str(celula), None, fonte_padrao, TINTA, None)]


class Tabela(Bloco):
    """Tabela sem grade pesada: fio escuro sob o cabeçalho, fio claro entre linhas.

    Parte-se entre linhas, e cada parte repete o cabeçalho; uma linha nunca se parte. Nenhuma
    parte fica com uma linha só (099): a última linha sozinha no alto da página seguinte, ou a
    primeira sozinha no pé, deixava uma página quase vazia por causa de uma linha. Por isso a
    tabela de até três linhas não se parte, e a maior se parte deixando ao menos duas de cada lado.
    """

    #: Quantas linhas cada parte leva, no mínimo.
    MINIMO_POR_PARTE = 2

    def __init__(
        self,
        cabecalho,
        linhas,
        *,
        larguras,
        alinhamentos=None,
        tamanho=8.6,
        antes=4.0,
        rodape=None,
        resumo=None,
    ):
        self.cabecalho = cabecalho
        self.linhas = linhas
        self.larguras = larguras
        self.alinhamentos = alinhamentos or [ESQUERDA] * len(larguras)
        self.tamanho = tamanho
        self.antes = antes
        self.rodape = rodape
        self.resumo = resumo

    def _colunas(self, w):
        total = sum(self.larguras)
        return [w * f / total for f in self.larguras]

    def _linha(self, celulas, w, fonte):
        colunas = self._colunas(w)
        saida = []
        for coluna, celula in zip(colunas, celulas, strict=True):
            linhas_da_celula = []
            for texto, tamanho, fonte_da_parte, cor, uri in _partes(celula, fonte):
                tamanho = tamanho or self.tamanho
                for parte in quebrar(texto, tamanho, coluna - 8, fonte_da_parte):
                    linhas_da_celula.append((parte, tamanho, fonte_da_parte, cor, uri))
            saida.append(linhas_da_celula)
        altura = max(sum(t[1] * 1.3 for t in c) for c in saida) + 6
        return saida, altura

    def _altura_do_cabecalho(self, w):
        return self._linha(self.cabecalho, w, NEGRITO)[1] if self.cabecalho else 0.0

    def medir(self, w):
        alturas = [self._linha(linha, w, REGULAR)[1] for linha in self.linhas]
        if self.rodape:
            alturas.append(self._linha(self.rodape, w, NEGRITO)[1])
        return self._altura_do_cabecalho(w) + sum(alturas)

    def _parte_se(self):
        return len(self.linhas) >= 2 * self.MINIMO_POR_PARTE

    def minimo(self, w):
        if not self._parte_se():
            return self.medir(w)
        primeiras = self.linhas[: self.MINIMO_POR_PARTE]
        return self._altura_do_cabecalho(w) + sum(
            self._linha(linha, w, REGULAR)[1] for linha in primeiras
        )

    def partir(self, w, disponivel):
        if not self._parte_se():
            return None
        cabem, usado = 0, self._altura_do_cabecalho(w)
        for linha in self.linhas:
            altura = self._linha(linha, w, REGULAR)[1]
            if usado + altura > disponivel:
                break
            usado += altura
            cabem += 1
        cabem = min(cabem, len(self.linhas) - self.MINIMO_POR_PARTE)
        if cabem < self.MINIMO_POR_PARTE:
            return None
        primeiro = Tabela(
            self.cabecalho,
            self.linhas[:cabem],
            larguras=self.larguras,
            alinhamentos=self.alinhamentos,
            tamanho=self.tamanho,
            antes=self.antes,
            resumo=self.resumo,
        )
        resto = Tabela(
            self.cabecalho,
            self.linhas[cabem:],
            larguras=self.larguras,
            alinhamentos=self.alinhamentos,
            tamanho=self.tamanho,
            antes=0.0,
            rodape=self.rodape,
            resumo=self.resumo,
        )
        return primeiro, resto

    def desenhar(self, tela, x, y, w, pai):
        colunas = self._colunas(w)
        tabela = pai.filho("Table")
        cursor = y

        def escrever(celulas, fonte, tipo, fio_embaixo, espessura):
            nonlocal cursor
            conteudo, altura = self._linha(celulas, w, fonte)
            tr = tabela.filho("TR")
            cx = x
            for coluna, linhas_da_celula, alinhamento in zip(
                colunas, conteudo, self.alinhamentos, strict=True
            ):
                celula = tr.filho(tipo)
                deslocamento = 3 + 1
                for parte, tamanho, fonte_da_parte, cor, uri in linhas_da_celula:
                    deslocamento += tamanho * 1.3
                    medida = largura(parte, tamanho, fonte_da_parte)
                    px = cx + 4 if alinhamento == ESQUERDA else cx + coluna - 4 - medida
                    tela.texto(
                        px,
                        cursor - deslocamento + tamanho * 0.32,
                        parte,
                        tamanho,
                        fonte=fonte_da_parte,
                        cor=cor,
                        elemento=celula,
                        uri=uri,
                    )
                cx += coluna
            cursor -= altura
            tela.fio(x, cursor, x + w, cursor, cor=fio_embaixo, espessura=espessura)

        if self.cabecalho:
            escrever(self.cabecalho, NEGRITO, "TH", TINTA, 0.8)
        for linha in self.linhas:
            escrever(linha, REGULAR, "TD", FIO, 0.5)
        if self.rodape:
            escrever(self.rodape, NEGRITO, "TD", TINTA, 0.8)


@dataclass
class Barras(Bloco):
    """Barras horizontais com o valor escrito: rótulo, número e barra proporcional ao maior.

    É figura na estrutura, com o texto alternativo que lê os mesmos números — quem não vê a barra
    lê a série inteira.
    """

    itens: list  # (rótulo, valor)
    alt: str
    antes: float = 4.0
    ALTURA_DA_LINHA = 14.0

    def medir(self, w):
        return len(self.itens) * self.ALTURA_DA_LINHA + 4

    def desenhar(self, tela, x, y, w, pai):
        figura = pai.filho("Figure", alt=self.alt)
        maior = max((v for _, v in self.itens), default=0) or 1
        rotulo_w = max(largura(r, 8.4) for r, _ in self.itens) + 8
        valor_w = max(largura(str(v), 8.4, NEGRITO) for _, v in self.itens) + 8
        inicio = x + rotulo_w + valor_w
        disponivel = w - rotulo_w - valor_w - 4
        for indice, (rotulo, valor) in enumerate(self.itens):
            topo = y - indice * self.ALTURA_DA_LINHA
            base = topo - 10
            tela.texto(x, base, rotulo, 8.4, cor=TINTA_2, elemento=figura)
            tela.texto(
                x + rotulo_w + valor_w - 8 - largura(str(valor), 8.4, NEGRITO),
                base,
                str(valor),
                8.4,
                fonte=NEGRITO,
                elemento=figura,
            )
            comprimento = max(disponivel * valor / maior, 1.5 if valor else 0)
            if comprimento:
                tela.retangulo(inicio, base - 1, comprimento, 8.5, fundo=DESTAQUE)


@dataclass
class BarrasVerticais(Bloco):
    """A série longa: uma barra por período — dia ou semana —, da esquerda para a direita (099).

    `Barras` escreve o número ao lado de cada barra, e serve a meia dúzia de meses; sessenta dias
    não cabem assim. Aqui a barra se estreita com o número de períodos — o vão entre elas some
    quando ficaria mais largo que um quarto da barra —, o eixo nomeia no máximo `ROTULOS` períodos,
    sempre o primeiro e o último, e o número escrito é só o do pico. A série inteira vai no texto
    alternativo, que é o que o leitor de tela lê no lugar da figura.

    `marca` é `(índice, rótulo)`: a linha tracejada depois da barra `índice` — o término original
    de um prazo prorrogado —, com as barras de antes num tom e as de depois no destaque. `legenda`
    diz o que cada tom soma.
    """

    itens: list  # (rótulo no eixo, valor)
    alt: str
    marca: tuple | None = None
    legenda: list = field(default_factory=list)  # (texto, cor)
    antes: float = 4.0
    ALTURA = 62.0
    TOPO_LIVRE = 22.0
    EIXO = 12.0
    ROTULOS = 5

    def medir(self, w):
        return self.TOPO_LIVRE + self.ALTURA + self.EIXO + (13.0 if self.legenda else 0.0)

    def _rotulados(self):
        """Os índices que o eixo nomeia — a regra da série da Supervisão (`PulsoDoEdital.eixo`)."""
        total = len(self.itens)
        passo = max(1, -(-total // self.ROTULOS))
        return {
            indice
            for indice in range(total)
            if indice == total - 1 or (indice % passo == 0 and total - 1 - indice >= passo)
        }

    def _cor(self, indice):
        if self.marca is None:
            return DESTAQUE
        return BARRA if indice <= self.marca[0] else DESTAQUE

    def desenhar(self, tela, x, y, w, pai):
        figura = pai.filho("Figure", alt=self.alt)
        total = len(self.itens)
        if not total:
            return
        fatia = w / total
        vao = min(1.6, fatia * 0.25) if fatia >= 3 else 0.0
        maior = max(valor for _, valor in self.itens)
        base = y - self.TOPO_LIVRE - self.ALTURA

        def centrado(texto, tamanho, centro, fonte=REGULAR):
            medida = largura(texto, tamanho, fonte)
            return min(max(centro - medida / 2, x), x + w - medida)

        pico = None
        for indice, (_, valor) in enumerate(self.itens):
            if not valor:
                continue
            altura = max(self.ALTURA * valor / maior, 0.8)
            tela.retangulo(
                x + indice * fatia + vao / 2, base, fatia - vao, altura, fundo=self._cor(indice)
            )
            if valor == maior and pico is None:
                pico = indice
        tela.fio(x, base, x + w, base)
        if pico is not None:
            centro = x + (pico + 0.5) * fatia
            tela.texto(
                centrado(str(maior), 8.0, centro, NEGRITO),
                base + self.ALTURA + 3.0,
                str(maior),
                8.0,
                fonte=NEGRITO,
                elemento=figura,
            )
        for indice in sorted(self._rotulados()):
            rotulo = self.itens[indice][0]
            centro = x + (indice + 0.5) * fatia
            tela.texto(
                centrado(rotulo, 7.2, centro), base - 9.0, rotulo, 7.2, cor=TINTA_3, elemento=figura
            )
        if self.marca is not None:
            indice, rotulo = self.marca
            linha = x + (indice + 1) * fatia
            tela.fio(linha, base, linha, base + self.ALTURA + 8.0, cor=TINTA_2, tracejado=True)
            medida = largura(rotulo, 7.2)
            # O rótulo fica do lado da linha onde cabe: à esquerda, colado a ela, se houver espaço.
            inicio = linha - 3 - medida
            if inicio < x:
                inicio = min(linha + 3, x + w - medida)
            tela.texto(inicio, y - 7.0, rotulo, 7.2, cor=TINTA_2, elemento=figura)
        cursor = x
        for texto, cor in self.legenda:
            tela.retangulo(cursor, base - self.EIXO - 11.0, 6.0, 6.0, fundo=cor)
            tela.texto(
                cursor + 9.0, base - self.EIXO - 10.5, texto, 7.4, cor=TINTA_2, elemento=figura
            )
            cursor += 9.0 + largura(texto, 7.4) + 14.0


@dataclass
class Lista(Bloco):
    """Itens com marcador e recuo pendente. Parte-se entre itens."""

    itens: list
    marcador: str = "—"
    tamanho: float = 8.8
    antes: float = 3.0

    def _linhas(self, w):
        recuo = largura(self.marcador + " ", self.tamanho) + 2
        return recuo, [quebrar(item, self.tamanho, w - recuo) for item in self.itens]

    def medir(self, w):
        _, linhas = self._linhas(w)
        return sum(len(item) * self.tamanho * 1.38 + 2 for item in linhas)

    def minimo(self, w):
        _, linhas = self._linhas(w)
        return len(linhas[0]) * self.tamanho * 1.38 + 2 if linhas else 0

    def partir(self, w, disponivel):
        _, linhas = self._linhas(w)
        usado, cabem = 0.0, 0
        for item in linhas:
            altura = len(item) * self.tamanho * 1.38 + 2
            if usado + altura > disponivel:
                break
            usado += altura
            cabem += 1
        if cabem < 1 or cabem >= len(self.itens):
            return None
        return (
            Lista(self.itens[:cabem], self.marcador, self.tamanho, self.antes),
            Lista(self.itens[cabem:], self.marcador, self.tamanho, 0.0),
        )

    def desenhar(self, tela, x, y, w, pai):
        recuo, linhas = self._linhas(w)
        lista = pai.filho("L")
        cursor = y
        for item in linhas:
            elemento = lista.filho("LI")
            for indice, linha in enumerate(item):
                cursor -= self.tamanho * 1.38
                if indice == 0:
                    tela.texto(
                        x,
                        cursor + 2.6,
                        self.marcador,
                        self.tamanho,
                        cor=TINTA_3,
                        elemento=elemento.filho("Lbl"),
                    )
                tela.texto(x + recuo, cursor + 2.6, linha, self.tamanho, elemento=elemento)
            cursor -= 2


@dataclass
class Definicoes(Bloco):
    """Termo em negrito e definição embaixo. Parte-se entre pares; o par não se parte."""

    pares: list
    antes: float = 4.0

    def _altura(self, par, w):
        termo, definicao = par
        return (
            4 + len(quebrar(termo, 8.8, w, NEGRITO)) * 11.4 + len(quebrar(definicao, 8.4, w)) * 11.2
        )

    def medir(self, w):
        return sum(self._altura(p, w) for p in self.pares)

    def minimo(self, w):
        return self._altura(self.pares[0], w) if self.pares else 0

    def partir(self, w, disponivel):
        usado, cabem = 0.0, 0
        for par in self.pares:
            altura = self._altura(par, w)
            if usado + altura > disponivel:
                break
            usado += altura
            cabem += 1
        if cabem < 1 or cabem >= len(self.pares):
            return None
        return Definicoes(self.pares[:cabem], self.antes), Definicoes(self.pares[cabem:], 0.0)

    def desenhar(self, tela, x, y, w, pai):
        lista = pai.filho("L")
        cursor = y
        for termo, definicao in self.pares:
            item = lista.filho("LI")
            cursor -= 4
            for linha in quebrar(termo, 8.8, w, NEGRITO):
                cursor -= 11.4
                tela.texto(x, cursor + 2.6, linha, 8.8, fonte=NEGRITO, elemento=item.filho("Lbl"))
            corpo = item.filho("LBody")
            for linha in quebrar(definicao, 8.4, w):
                cursor -= 11.2
                tela.texto(x, cursor + 2.6, linha, 8.4, cor=TINTA_2, elemento=corpo)


@dataclass
class Colunas(Bloco):
    """Duas pilhas de blocos lado a lado. Não se parte: o par é um grupo."""

    esquerda: list
    direita: list
    antes: float = 4.0
    espaco: float = 16.0

    def _largura(self, w):
        return (w - self.espaco) / 2

    def _altura(self, pilha, w):
        total = 0.0
        for indice, bloco in enumerate(pilha):
            total += (bloco.antes if indice else 0.0) + bloco.medir(w)
        return total

    def medir(self, w):
        lw = self._largura(w)
        return max(self._altura(self.esquerda, lw), self._altura(self.direita, lw))

    def desenhar(self, tela, x, y, w, pai):
        lw = self._largura(w)
        for pilha, px in ((self.esquerda, x), (self.direita, x + lw + self.espaco)):
            secao = pai.filho("Div")
            cursor = y
            for indice, bloco in enumerate(pilha):
                cursor -= bloco.antes if indice else 0.0
                bloco.desenhar(tela, px, cursor, lw, secao)
                cursor -= bloco.medir(lw)


def abertura(*, orgao, titulo, subtitulo, natureza, pares, marcador):
    """O alto da primeira página dos documentos gerenciais — o mesmo no 099 e no 100.

    Brasão e órgão compactos, o título, a espécie ou o período no destaque, a natureza gerencial em
    corpo pequeno e a ficha de pares embaixo. Os dois relatórios abrem igual para que quem recebe
    os dois os reconheça como da mesma família.
    """
    return [
        Cabecalho(linhas=orgao),
        Texto(
            titulo,
            tamanho=16.5,
            fonte=NEGRITO,
            entrelinha=1.18,
            antes=12.0,
            tipo="H1",
            marcador=marcador,
        ),
        Texto(subtitulo, tamanho=10.0, fonte=NEGRITO, cor=DESTAQUE, antes=3.0),
        Texto(natureza, tamanho=8.2, cor=TINTA_3, antes=1.0),
        Ficha(pares),
    ]


# --- A paginação --------------------------------------------------------------------------------


@dataclass
class Colocacao:
    bloco: Bloco
    topo: float
    altura: float


def _minimo_da_cadeia(fila, w):
    """O menor começo de `fila[0]`, contando o que precisa ir junto com ele.

    Título, subtítulo e tabela formam uma cadeia: o título só pode ficar no pé se o subtítulo
    couber, e o subtítulo só se couber o começo da tabela. Olhar um bloco adiante deixava o título
    sozinho quando o subtítulo cabia e a tabela não (099). A nota presa entra na cadeia quando o
    bloco que ela explica não se parte — senão ela iria junto com a parte final dele.
    """
    bloco = fila[0]
    seguinte = fila[1] if len(fila) > 1 and not isinstance(fila[1], QuebraDePagina) else None
    if seguinte is not None and (
        bloco.junto_ao_seguinte
        or (seguinte.preso_ao_anterior and bloco.minimo(w) >= bloco.medir(w))
    ):
        return bloco.medir(w) + seguinte.antes + _minimo_da_cadeia(fila[1:], w)
    return bloco.minimo(w)


@dataclass
class Documento:
    """Os blocos, a faixa de cada página e a navegação; `paginar` decide onde cada um cai."""

    blocos: list
    faixa_esquerda: str
    faixa_direita: str
    pe: str
    titulo: str
    autor: str = ""
    paginas: list = field(default_factory=list)

    def paginar(self):
        w = LARGURA_UTIL
        paginas = [[]]
        cursor = TOPO
        fila = list(self.blocos)
        while fila:
            bloco = fila.pop(0)
            if isinstance(bloco, QuebraDePagina):
                if paginas[-1]:
                    paginas.append([])
                    cursor = TOPO
                continue
            vazia = not paginas[-1]
            antes = 0.0 if vazia else bloco.antes
            disponivel = cursor - BASE - antes
            altura = bloco.medir(w)
            necessario = altura
            seguinte = fila[0] if fila and not isinstance(fila[0], QuebraDePagina) else None
            if seguinte is not None and (bloco.junto_ao_seguinte or seguinte.preso_ao_anterior):
                necessario = altura + seguinte.antes + _minimo_da_cadeia(fila, w)
            if necessario <= disponivel:
                paginas[-1].append(Colocacao(bloco, cursor - antes, altura))
                cursor -= antes + altura
                continue
            partes = None if bloco.junto_ao_seguinte else bloco.partir(w, disponivel)
            if partes is not None:
                primeiro, resto = partes
                paginas[-1].append(Colocacao(primeiro, cursor - antes, primeiro.medir(w)))
                fila.insert(0, resto)
                paginas.append([])
                cursor = TOPO
                continue
            if vazia:
                # Nem a página inteira o comporta: parte-se no espaço que houver, ou cai assim.
                partes = bloco.partir(w, disponivel)
                if partes is not None:
                    primeiro, resto = partes
                    paginas[-1].append(Colocacao(primeiro, cursor, primeiro.medir(w)))
                    fila.insert(0, resto)
                else:
                    paginas[-1].append(Colocacao(bloco, cursor, altura))
                paginas.append([])
                cursor = TOPO
                continue
            fila.insert(0, bloco)
            paginas.append([])
            cursor = TOPO
        self.paginas = [p for p in paginas if p]
        return self.paginas

    def compor(self) -> bytes:
        paginas = self.paginar()
        raiz = Elemento("Document")
        telas = []
        marcadores = []
        for indice, colocacoes in enumerate(paginas):
            tela = Tela(indice)
            self._faixa(tela, indice, len(paginas))
            for colocacao in colocacoes:
                if colocacao.bloco.marcador:
                    marcadores.append(
                        (colocacao.bloco.nivel, colocacao.bloco.marcador, indice, colocacao.topo)
                    )
                colocacao.bloco.desenhar(tela, MARGEM_X, colocacao.topo, LARGURA_UTIL, raiz)
            telas.append(tela)
        return _arquivo(telas, raiz, marcadores, self.titulo, self.autor)

    def _faixa(self, tela, indice, total):
        """A identificação no alto e a natureza no pé, de toda página — artefatos da estrutura.

        Cada par tem de caber lado a lado: se não couber, é defeito de quem escreveu o texto, e a
        composição recusa em vez de sobrepor (revisão visual de 24/10/2026).
        """
        pagina = f"página {indice + 1} de {total}"
        for esquerda, direita, y in (
            (self.faixa_esquerda, self.faixa_direita, Y_DA_FAIXA),
            (self.pe, pagina, Y_DO_PE),
        ):
            if largura(esquerda, 7.4) + 12 + largura(direita, 7.4) > LARGURA_UTIL:
                raise ValueError(f"A faixa não cabe na página: {esquerda!r} e {direita!r}.")
            tela.texto(MARGEM_X, y, esquerda, 7.4, cor=TINTA_3)
            tela.texto(LARGURA - MARGEM_X - largura(direita, 7.4), y, direita, 7.4, cor=TINTA_3)
        tela.fio(MARGEM_X, Y_DA_FAIXA - 5, LARGURA - MARGEM_X, Y_DA_FAIXA - 5)
        tela.fio(MARGEM_X, Y_DO_PE + 9, LARGURA - MARGEM_X, Y_DO_PE + 9)


# --- O arquivo ----------------------------------------------------------------------------------


def _numero(valor):
    return f"{valor:.2f}"


def _arquivo(telas, raiz, marcadores, titulo, autor):
    """Os objetos do PDF marcado, numerados em ordem fixa: os mesmos blocos, os mesmos bytes."""
    objetos_das_fontes, ids_das_fontes = fonte_do_edital.objetos(4)
    primeira_pagina = 4 + len(objetos_das_fontes)
    ids_paginas = [primeira_pagina + 2 * i for i in range(len(telas))]
    proximo = primeira_pagina + 2 * len(telas)
    id_info = proximo
    id_outlines = proximo + 1
    ids_marcadores = [id_outlines + 1 + i for i in range(len(marcadores))]
    proximo = id_outlines + 1 + len(marcadores)
    ids_links = []
    for tela in telas:
        ids_links.append(list(range(proximo, proximo + len(tela.links))))
        proximo += len(tela.links)
    id_estrutura = proximo
    id_arvore_de_pais = proximo + 1
    elementos = []

    def percorrer(elemento):
        elementos.append(elemento)
        for especie, valor, *_ in elemento.k:
            if especie == "elemento":
                percorrer(valor)

    percorrer(raiz)
    ids_elementos = {id(e): id_arvore_de_pais + 1 + i for i, e in enumerate(elementos)}

    recursos = (
        f"/Resources << /Font << /F1 {ids_das_fontes[REGULAR]} 0 R "
        f"/F2 {ids_das_fontes[NEGRITO]} 0 R >> /XObject << /{NOME_DO_BRASAO} 3 0 R >> >> "
    )
    objetos = [
        (
            f"<< /Type /Catalog /Pages 2 0 R /Lang (pt-BR) /MarkInfo << /Marked true >> "
            f"/StructTreeRoot {id_estrutura} 0 R "
            f"/ViewerPreferences << /DisplayDocTitle true >> /PageMode /UseOutlines "
            f"/Outlines {id_outlines} 0 R >>"
        ).encode(),
        (
            "<< /Type /Pages /Kids ["
            + " ".join(f"{i} 0 R" for i in ids_paginas)
            + f"] /Count {len(telas)} >>"
        ).encode(),
        _objeto_do_brasao(),
        *objetos_das_fontes,
    ]
    for indice, tela in enumerate(telas):
        anotacoes = ""
        if ids_links[indice]:
            anotacoes = "/Annots [" + " ".join(f"{i} 0 R" for i in ids_links[indice]) + "] "
        objetos.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] {recursos}"
                f"{anotacoes}/StructParents {indice} /Tabs /S "
                f"/Contents {ids_paginas[indice] + 1} 0 R >>"
            ).encode()
        )
        fluxo = tela.fluxo()
        objetos.append(
            b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n" + fluxo + b"\nendstream"
        )
    objetos.append(
        f"<< /Title {_cadeia_do_pdf(titulo)} /Author {_cadeia_do_pdf(autor)} >>".encode()
    )
    # Marcadores num nível só, na ordem das seções: é o que o leitor de PDF mostra ao lado.
    if marcadores:
        objetos.append(
            f"<< /Type /Outlines /First {ids_marcadores[0]} 0 R /Last {ids_marcadores[-1]} 0 R "
            f"/Count {len(marcadores)} >>".encode()
        )
    else:
        objetos.append(b"<< /Type /Outlines /Count 0 >>")
    for indice, (_, texto, pagina, topo) in enumerate(marcadores):
        partes = [f"<< /Title {_cadeia_do_pdf(texto)} /Parent {id_outlines} 0 R"]
        if indice:
            partes.append(f"/Prev {ids_marcadores[indice - 1]} 0 R")
        if indice + 1 < len(marcadores):
            partes.append(f"/Next {ids_marcadores[indice + 1]} 0 R")
        partes.append(f"/Dest [{ids_paginas[pagina]} 0 R /XYZ null {_numero(topo + 4)} null] >>")
        objetos.append(" ".join(partes).encode())
    for tela in telas:
        for (x0, y0, x1, y1), uri in tela.links:
            retangulo = " ".join(_numero(v) for v in (x0, y0, x1, y1))
            objetos.append(
                f"<< /Type /Annot /Subtype /Link /Rect [{retangulo}] /Border [0 0 0] "
                f"/A << /S /URI /URI {_cadeia_do_pdf(_uri(uri))} >> >>".encode()
            )
    objetos.append(
        f"<< /Type /StructTreeRoot /K {ids_elementos[id(raiz)]} 0 R "
        f"/ParentTree {id_arvore_de_pais} 0 R >>".encode()
    )
    numeros = " ".join(
        f"{indice} [" + " ".join(f"{ids_elementos[id(e)]} 0 R" for e in tela.mcids) + "]"
        for indice, tela in enumerate(telas)
    )
    objetos.append(f"<< /Nums [{numeros}] >>".encode())
    for elemento in elementos:
        pai = ids_elementos[id(elemento.pai)] if elemento.pai else id_estrutura
        filhos = []
        for especie, valor, *resto in elemento.k:
            if especie == "elemento":
                filhos.append(f"{ids_elementos[id(valor)]} 0 R")
            else:
                pagina, mcid = valor, resto[0]
                filhos.append(f"<< /Type /MCR /Pg {ids_paginas[pagina]} 0 R /MCID {mcid} >>")
        alt = f" /Alt {_cadeia_do_pdf(elemento.alt)}" if elemento.alt else ""
        objetos.append(
            f"<< /Type /StructElem /S /{elemento.tipo} /P {pai} 0 R{alt} "
            f"/K [{' '.join(filhos)}] >>".encode()
        )
    return _montar_o_arquivo(objetos, informacao=id_info)
