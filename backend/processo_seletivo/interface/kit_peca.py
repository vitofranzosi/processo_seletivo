"""A peça do feed, 1080 × 1350: um template, composto da ficha e de mais nada (111, FR-3422).

**A composição é um modelo de caixas, e o SVG é a serialização dele** (`D-008`). O compositor produz
elementos posicionados — texto com o campo da ficha de onde veio, corpo, peso e caixa medida;
retângulos; linhas; a marca —, e só depois um serializador escreve o SVG. Na POC as conferências
sobre o SVG ficaram verdes com o endereço fora da margem e a quantidade dentro do rótulo; com as
caixas explícitas, área útil e colisão viram aritmética, e o teste geométrico é exato.

**Mede com a fonte e a regra do Edital, e desenha o que mediu** (`D-009`). A largura é a da
`MetricaEmbutida`, a quebra é a do compositor do ato, e o texto que entra no SVG já passou por
`grafia.normalizar` — a métrica mede o normalizado, e um rasterizador que recebesse o cru desenharia
outra largura. Quebra que parte palavra conta como "não cabe" (FR-3429): um endereço partido no
rodapé mudaria o destino.

**Recusa em vez de encolher sem fim, e nunca trunca** (FR-3426, FR-3429). O título desce de corpo
até o mínimo; se nenhum título oficial cabe, a tela oferece a manchete da lista fechada (FR-3427),
e sem ela a peça sai sem título e diz a omissão. O que sobra de um título cortado diria outra
coisa.

**A marca é a oficial** (FR-3432, `kit_ativos/ORIGEM.md`): a do Cefor, que tem a sua no pacote do
Ifes, e a do Ifes com a sigla escrita para as demais unidades. O template com ela ainda espera a
aprovação da comunicação (SC-1054), e por isso a chave `KIT_DE_DIVULGACAO_PECA` existe.
"""

import base64
import hashlib
import re
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from processo_seletivo.interface import kit_textos
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure import fonte
from processo_seletivo.publicacoes.infrastructure.fonte import METRICA, NEGRITO, REGULAR
from processo_seletivo.publicacoes.infrastructure.pdf import quebrar as quebra_do_edital

#: A versão do template, registrada em cada exportação (FR-3436). Mudar o desenho muda a versão, os
#: SVG de referência e pede nova revisão da comunicação (`D-010`, `D-016`).
TEMPLATE = "feed-1080x1350 · 1"

LARGURA, ALTURA = 1080, 1350
MARGEM = 80
UTIL = LARGURA - 2 * MARGEM
FAMILIA = "Edital Sans"
#: O mínimo legível a 1080 px de largura (FR-3428). Nenhum texto da peça fica abaixo dele.
CORPO_MINIMO = 24

# Os tokens do produto (`shared/static/shared/tokens.css`), e não uma paleta inventada para a peça.
# Todos passam AA sobre o fundo em que são desenhados, e o teste confere par a par.
VERDE_ESCURO = "#0b5a2a"
VERDE_TEXTO = "#146c37"
VERDE_CLARO = "#e7f5ec"
BRANCO = "#ffffff"
TEXTO = "#1c1c1c"
TEXTO_FRACO = "#555555"
BORDA = "#d4d4d4"
AMARELO = "#8a5300"
AMARELO_FUNDO = "#fdf5e5"

FAIXA = 210  # a faixa da marca, no topo
BLOCO_DO_PERIODO = 236
BLOCO_DO_NEUTRO = 200
RECUO_DO_BLOCO = 40
RODAPE = 1100  # a linha do rodapé; o selo termina antes da margem de baixo
FOLGA_DO_RODAPE = 30
#: A parte da folga que vai para cima do corpo (FR-3434): com duas opções, o vazio inteiro embaixo
#: fazia a peça parecer cortada. Só desloca — nada muda de tamanho nem de ordem.
PARTE_DA_FOLGA_EM_CIMA = 0.35

# O título, do maior ao menor corpo admitido, e o número de linhas em cada um.
CORPOS_DO_TITULO = ((52, 3), (46, 3), (40, 4), (36, 4))
CORPOS_DO_PERIODO = tuple(range(88, 55, -4))
CORPOS_DO_CAMINHO = tuple(range(34, CORPO_MINIMO - 1, -2))


@dataclass(frozen=True)
class Marca:
    arquivo: str
    sha256: str
    #: A parte do arquivo com tinta, em frações da largura e da altura: o PNG oficial traz a reserva
    #: de integridade como margem transparente, e é a parte visível que se alinha à margem da peça.
    visivel: tuple[float, float, float, float]
    descricao: str


MARCAS = {
    "Cefor": Marca(
        "cefor-horizontal-branco.png",
        "1f436a9e697431200cad18be19625d41d79b691132d8a912365794a177b14bb4",
        (0.0597, 0.2396, 0.9389, 0.7569),
        "Marca do Instituto Federal do Espírito Santo, Centro de Referência em Formação e em "
        "Educação a Distância",
    ),
    "Ifes": Marca(
        "ifes-horizontal-branco.png",
        "40dff3ef48f32793f4761e5ad6b25510bf8874a34e34c36c16735b1f34a8bfd5",
        (0.0597, 0.1944, 0.9389, 0.8021),
        "Marca do Instituto Federal do Espírito Santo",
    ),
}
PASTA_DAS_MARCAS = Path(__file__).resolve().parent / "kit_ativos"
LARGURA_DA_MARCA = 340
PROPORCAO_DA_MARCA = 720 / 288

# As frases fixas do template. A conferência aceita só estas, além dos valores da ficha e da
# manchete da lista fechada (FR-3423). Nomeadas, para a varredura de vocabulário as ler (T027).
FIXOS = {
    "chamada": "PROCESSO SELETIVO",
    "inscricoes": "INSCRIÇÕES",
    "prorrogado": "PRAZO PRORROGADO",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "oferta": "OFERTA",
    "todas": "Confira todas na página oficial",
    "rodape": "Condições, documentos e cronograma:",
}
HORARIO = "(horário de Brasília)"

HOST_LOCAL = (
    "A peça não é gerada neste acesso: o endereço público do sistema não é conhecido daqui, e a "
    "peça precisa dele no rodapé."
)
SEM_TITULO = "Nenhum título oficial cabe na peça, e ela sai sem título."
ESCOLHA_A_MANCHETE = (
    "Nenhum título oficial cabe na peça. Escolha uma manchete abaixo, ou a peça sai sem título."
)


class PecaRecusada(Exception):
    """A composição recusada, com o motivo dito para quem gera (FR-3429, FR-3430)."""

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


class MancheteInvalida(ValueError):
    """Índice de manchete fora da lista, ou manchete pedida quando um título oficial cabe."""


# ---- O modelo de caixas (D-008) ----------------------------------------------------------------


@dataclass(frozen=True)
class Texto:
    x: int
    y: int  # a linha de base
    conteudo: str  # já normalizado pela grafia: o que se mede é o que se desenha
    tamanho: int
    fonte: str
    campo: str
    cor: str
    fundo: str  # o fundo sobre o qual é desenhado, para o contraste
    ancora: str = "start"

    @property
    def largura(self):
        return METRICA.largura(self.conteudo, self.tamanho, self.fonte)

    @property
    def caixa(self):
        """`(esquerda, topo, direita, base)` em px, pela métrica tipográfica da fonte."""
        medidas = fonte.fontes()[self.fonte]
        esquerda = self.x - self.largura if self.ancora == "end" else self.x
        return (
            esquerda,
            self.y - medidas.ascendente * self.tamanho / 1000,
            esquerda + self.largura,
            self.y - medidas.descendente * self.tamanho / 1000,
        )


@dataclass(frozen=True)
class Retangulo:
    x: int
    y: int
    largura: int
    altura: int
    cor: str
    raio: int = 0

    @property
    def caixa(self):
        return (self.x, self.y, self.x + self.largura, self.y + self.altura)


@dataclass(frozen=True)
class Linha:
    x1: int
    x2: int
    y: int
    cor: str = BORDA


@dataclass(frozen=True)
class Imagem:
    x: int
    y: int
    largura: int
    altura: int
    marca: Marca
    campo: str = "marca"

    @property
    def caixa_visivel(self):
        esquerda, topo, direita, base = self.marca.visivel
        return (
            self.x + esquerda * self.largura,
            self.y + topo * self.altura,
            self.x + direita * self.largura,
            self.y + base * self.altura,
        )


def _deslocar(elemento, dy):
    return replace(elemento, y=elemento.y + dy)


@dataclass(frozen=True)
class Peca:
    elementos: tuple
    alternativo: str
    #: O campo do título desenhado — `titulo_sem_numero`, `titulo_do_processo`, `manchete` — ou
    #: vazio quando a peça saiu sem título.
    titulo: str
    manchete: str | None
    omissao: str
    #: Os elementos do corpo, entre o cabeçalho e o rodapé, e quanto desceram (FR-3434).
    corpo: tuple
    deslocamento: int

    @property
    def textos(self):
        return tuple(e for e in self.elementos if isinstance(e, Texto))


@dataclass
class _Composicao:
    elementos: list = field(default_factory=list)

    def texto(self, x, y, valor, *, tamanho, campo, cor, fundo, fonte=REGULAR, ancora="start"):
        conteudo = grafia.normalizar(str(valor))
        faltam = grafia.sem_grafia(conteudo)
        if faltam:
            nomes = ", ".join(grafia.descrever(c) for c in faltam)
            raise PecaRecusada(f"A peça não desenha o caractere {nomes}, em {_rotulo(campo)}.")
        elemento = Texto(round(x), round(y), conteudo, tamanho, fonte, campo, cor, fundo, ancora)
        self.elementos.append(elemento)
        return elemento

    def retangulo(self, x, y, largura, altura, *, cor, raio=0):
        caixa = (round(x), round(y), round(largura), round(altura))
        self.elementos.append(Retangulo(*caixa, cor, raio))

    def linha(self, y):
        self.elementos.append(Linha(MARGEM, LARGURA - MARGEM, round(y)))


_ROTULOS_DOS_CAMPOS = {
    "titulo_sem_numero": "o título do Edital",
    "titulo_do_processo": "o título do Processo",
    "manchete": "a manchete",
    "identificacao": "a identificação do Edital",
    "assinatura": "a assinatura",
    "caminho_curto": "o endereço do rodapé",
}


def _rotulo(campo):
    if campo.startswith("oferta"):
        return "o nome de uma opção de oferta"
    return _ROTULOS_DOS_CAMPOS.get(campo, campo.replace("_", " "))


# ---- Medida e quebra (D-009) ---------------------------------------------------------------------


def largura(texto, tamanho, peso=REGULAR):
    return METRICA.largura(texto, tamanho, peso)


def quebrar(texto, tamanho, peso=REGULAR, limite=UTIL):
    """As linhas, ou `None` se a quebra partiu palavra: isso conta como "não cabe" (FR-3429)."""
    texto = grafia.normalizar(str(texto))
    linhas = quebra_do_edital(texto, tamanho, 0, peso, limite=limite, metrica=METRICA)
    if " ".join(linhas).split() != texto.split():
        return None
    return linhas


def medidas_do_titulo(texto):
    """Os `(tamanho, linhas)` em que o título cabe, do maior corpo ao menor."""
    medidas = []
    for tamanho, maximo in CORPOS_DO_TITULO:
        linhas = quebrar(texto, tamanho, NEGRITO)
        if linhas is not None and len(linhas) <= maximo:
            medidas.append((tamanho, linhas))
    return medidas


def titulos_oficiais(ficha):
    """Os títulos oficiais, na ordem da FR-3426: o do Edital sem o número, e o do Processo."""
    candidatos = (
        ("titulo_sem_numero", ficha.titulo_sem_numero or ficha.titulo),
        ("titulo_do_processo", ficha.titulo_do_processo),
    )
    return [(campo, texto) for campo, texto in candidatos if texto]


def _opcoes_de_titulo(ficha, manchete):
    """`(campo, tamanho, linhas)` na ordem em que se tentam, até o corpo da peça caber.

    Primeiro o título do Edital em cada corpo, depois o do Processo, e a manchete só quando nenhum
    oficial cabe (FR-3426). O título desce de corpo antes de ceder a vez: com quatro polos e um
    título de três linhas, o corpo menor é o que deixa a oferta inteira.
    """
    opcoes = [
        (campo, tamanho, linhas)
        for campo, texto in titulos_oficiais(ficha)
        for tamanho, linhas in medidas_do_titulo(texto)
    ]
    if not opcoes and manchete is not None:
        opcoes = [("manchete", t, linhas) for t, linhas in medidas_do_titulo(manchete)]
    return opcoes


def _algum_oficial_cabe(ficha):
    return any(medidas_do_titulo(texto) for _, texto in titulos_oficiais(ficha))


def manchetes(ficha):
    """A lista fechada da FR-3427, só quando nenhum título oficial cabe (`D-013`).

    Derivada da ficha, e só dela: o nome comum, quando todas as opções têm o mesmo nome; o nome de
    cada opção, quando há até quatro; e "nome — localidade" da opção única. Fica só com as que cabem
    como título e passam a lista de vocabulário (FR-3414). Não há texto livre: a revisão mostrou que
    os filtros deixavam passar "Curso gratuito para todo o país".
    """
    if _algum_oficial_cabe(ficha) or not ficha.ofertas:
        return ()
    ofertas = ficha.ofertas
    nomes = [oferta.nome for oferta in ofertas if oferta.nome]
    candidatas = []
    if nomes and len(set(nomes)) == 1 and len(nomes) == len(ofertas):
        candidatas.append(nomes[0])
    if len(ofertas) <= kit_textos.TETO_DE_OPCOES:
        candidatas.extend(nomes)
    if len(ofertas) == 1 and ofertas[0].localidade:
        candidatas.append(" — ".join(filter(None, (ofertas[0].nome, ofertas[0].localidade))))
    vistas = []
    for candidata in candidatas:
        if candidata in vistas or fichas.termos_proibidos(candidata):
            continue
        if medidas_do_titulo(candidata):
            vistas.append(candidata)
    return tuple(vistas)


def escolher_manchete(ficha, indice):
    """O texto da manchete de índice `indice`, ou `MancheteInvalida` (contrato, 422)."""
    if indice is None:
        return None
    lista = manchetes(ficha)
    if not 0 <= indice < len(lista):
        raise MancheteInvalida("A manchete escolhida não está entre as oferecidas.")
    return lista[indice]


# ---- As partes ---------------------------------------------------------------------------------


def marca_da_unidade(ficha):
    """A marca da unidade, quando o pacote oficial tem a dela; senão a do Ifes, com a sigla."""
    if ficha.unidade_sigla in MARCAS:
        return MARCAS[ficha.unidade_sigla], False
    return MARCAS["Ifes"], True


def _cabecalho(c, ficha):
    c.retangulo(0, 0, LARGURA, FAIXA, cor=VERDE_ESCURO)
    marca, assinar = marca_da_unidade(ficha)
    altura = round(LARGURA_DA_MARCA / PROPORCAO_DA_MARCA)
    esquerda, topo, _, base = marca.visivel
    # A parte visível nas margens: a transparência em volta é a reserva de integridade do manual.
    x = MARGEM - round(esquerda * LARGURA_DA_MARCA)
    y = MARGEM - round(topo * altura)
    c.elementos.append(Imagem(x, y, LARGURA_DA_MARCA, altura, marca))
    if assinar:
        c.texto(
            LARGURA - MARGEM,
            FAIXA / 2 + 13,
            kit_textos.assinatura(ficha),
            tamanho=36,
            campo="assinatura",
            fonte=NEGRITO,
            cor=BRANCO,
            fundo=VERDE_ESCURO,
            ancora="end",
        )
    return marca


def _titulo(c, y, opcao):
    """O título escolhido, linha a linha. Nenhum título é truncado: ou cabe inteiro, ou não sai."""
    if opcao is None:
        return y
    campo, tamanho, linhas = opcao
    for linha in linhas:
        y += round(tamanho * 1.18)
        c.texto(
            MARGEM, y, linha, tamanho=tamanho, campo=campo, fonte=NEGRITO, cor=TEXTO, fundo=BRANCO
        )
    return y


def _hora_do_periodo(ficha):
    if ficha.inicio_data and ficha.fim_data:
        return f"até as {ficha.fim_hora} {HORARIO}"
    if ficha.inicio_data:
        return f"às {ficha.inicio_hora} {HORARIO}"
    return f"às {ficha.fim_hora} {HORARIO}"


def _periodo(c, ficha, y):
    """O destaque principal: o período em datas absolutas, e nenhuma palavra sobre o agora."""
    c.retangulo(MARGEM, y, UTIL, BLOCO_DO_PERIODO, cor=VERDE_ESCURO, raio=28)
    dentro = MARGEM + RECUO_DO_BLOCO
    disponivel = UTIL - 2 * RECUO_DO_BLOCO
    topo = y + 62
    c.texto(
        dentro,
        topo,
        FIXOS["inscricoes"],
        tamanho=30,
        campo="fixo",
        fonte=NEGRITO,
        cor=BRANCO,
        fundo=VERDE_ESCURO,
    )
    if ficha.prorrogado:
        # Na linha de "INSCRIÇÕES", à direita: o selo qualifica o período, e uma linha só para ele
        # empurrava a oferta para o rodapé num Edital de quatro polos.
        rotulo = FIXOS["prorrogado"]
        largura_do_selo = largura(rotulo, 24, NEGRITO) + 2 * 22
        direita = MARGEM + UTIL - RECUO_DO_BLOCO
        c.retangulo(
            direita - largura_do_selo, topo - 36, largura_do_selo, 48, cor=AMARELO_FUNDO, raio=24
        )
        c.texto(
            direita - 22,
            topo - 4,
            rotulo,
            tamanho=24,
            campo="fixo",
            fonte=NEGRITO,
            cor=AMARELO,
            fundo=AMARELO_FUNDO,
            ancora="end",
        )
    datas = ficha.periodo_curto
    tamanho = next((t for t in CORPOS_DO_PERIODO if largura(datas, t, NEGRITO) <= disponivel), None)
    if tamanho is None:
        raise PecaRecusada(f"O período não cabe no destaque da peça: {datas!r}.")
    c.texto(
        dentro,
        topo + 100,
        datas,
        tamanho=tamanho,
        campo="periodo_curto",
        fonte=NEGRITO,
        cor=BRANCO,
        fundo=VERDE_ESCURO,
    )
    c.texto(
        dentro,
        topo + 150,
        _hora_do_periodo(ficha),
        tamanho=30,
        campo="hora",
        cor=VERDE_CLARO,
        fundo=VERDE_ESCURO,
    )
    return y + BLOCO_DO_PERIODO


def _publicado(c, y):
    """O destaque do modo neutro: sem período designado, a peça não fala de inscrição (FR-3424)."""
    c.retangulo(MARGEM, y, UTIL, BLOCO_DO_NEUTRO, cor=VERDE_ESCURO, raio=28)
    dentro = MARGEM + RECUO_DO_BLOCO
    c.texto(
        dentro,
        y + 96,
        FIXOS["publicado"],
        tamanho=60,
        campo="fixo",
        fonte=NEGRITO,
        cor=BRANCO,
        fundo=VERDE_ESCURO,
    )
    c.texto(
        dentro,
        y + 150,
        FIXOS["consulte"],
        tamanho=30,
        campo="fixo",
        cor=VERDE_CLARO,
        fundo=VERDE_ESCURO,
    )
    return y + BLOCO_DO_NEUTRO


def _linhas_ou_recusa(texto, tamanho, peso, maximo, campo, limite=UTIL):
    linhas = quebrar(texto, tamanho, peso, limite=limite)
    if linhas is None or len(linhas) > maximo:
        raise PecaRecusada(f"{_rotulo(campo).capitalize()} não cabe na peça: {texto!r}.")
    return linhas


def _oferta(c, ficha, y):
    """A oferta pelo teto único de quatro opções (FR-3425)."""
    ofertas = ficha.ofertas
    if not ofertas:
        return y
    y += 64
    c.texto(
        MARGEM,
        y,
        FIXOS["oferta"],
        tamanho=26,
        campo="fixo",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        fundo=BRANCO,
    )
    # A soma, sempre com o número de opções que a repartem: "160 vagas" sozinho se lê como de
    # cada polo (a exceção declarada à FR-1607 da `072`).
    total = kit_textos.total_em_frase(ficha)
    if total:
        c.texto(
            LARGURA - MARGEM,
            y,
            total,
            tamanho=26,
            campo="total_de_vagas",
            fonte=NEGRITO,
            cor=VERDE_TEXTO,
            fundo=BRANCO,
            ancora="end",
        )
    if ficha.nomes_iguais:
        for linha in _linhas_ou_recusa(ofertas[0].nome, 32, NEGRITO, 2, "oferta_nome"):
            y += 44
            c.texto(
                MARGEM,
                y,
                linha,
                tamanho=32,
                campo="oferta_nome",
                fonte=NEGRITO,
                cor=TEXTO,
                fundo=BRANCO,
            )
    if not kit_textos.lista_as_opcoes(ficha):
        y += 58
        c.texto(
            MARGEM,
            y,
            f"{len(ofertas)} opções",
            tamanho=40,
            campo="contagem",
            fonte=NEGRITO,
            cor=TEXTO,
            fundo=BRANCO,
        )
        y += 46
        c.texto(
            MARGEM,
            y,
            FIXOS["todas"],
            tamanho=28,
            campo="fixo",
            cor=TEXTO_FRACO,
            fundo=BRANCO,
        )
        return y
    for oferta in ofertas:
        y = _linha_da_oferta(c, ficha, oferta, y)
    return y


def _linha_da_oferta(c, ficha, oferta, y):
    rotulo = kit_textos.rotulo_da_oferta(oferta, ficha)
    quantidade = oferta.quantidade
    campo = f"oferta_rotulo:{oferta.perfil_id}"
    # A coluna da quantidade é medida, e não reservada: "3 vagas e cadastro reserva" ocupa o dobro
    # de "40 vagas", e a largura fixa fazia um invadir o outro (POC).
    lado = UTIL - (largura(quantidade, 30, NEGRITO) + 32 if quantidade else 0)
    linhas = quebrar(rotulo, 30, REGULAR, limite=lado)
    empilhar = linhas is None or len(linhas) > 1
    if empilhar:
        linhas = _linhas_ou_recusa(rotulo, 30, REGULAR, 2, campo)
    y += 48
    topo = y
    for posicao, linha in enumerate(linhas):
        if posicao:
            y += 40
        c.texto(MARGEM, y, linha, tamanho=30, campo=campo, cor=TEXTO, fundo=BRANCO)
    if quantidade:
        if empilhar:
            y += 40
        c.texto(
            LARGURA - MARGEM,
            y if empilhar else topo,
            quantidade,
            tamanho=30,
            campo=f"oferta_quantidade:{oferta.perfil_id}",
            fonte=NEGRITO,
            cor=TEXTO,
            fundo=BRANCO,
            ancora="end",
        )
    c.linha(y + 20)
    return y + 8


def selo_da_versao(ficha):
    """A data da versão vigente e a referência curta da impressão (FR-3431)."""
    data = ficha.versao_desde_texto.split(",", 1)[0]
    return f"Versão vigente desde {data} · ref. {ficha.impressao[:8]}"


def busca_na_peca(ficha):
    sigla = f" – {ficha.unidade_sigla}" if ficha.unidade_sigla else ""
    return f"busque por {ficha.numero}/{ficha.ano}{sigla}"


def _rodape(c, ficha):
    """A chamada à página, o caminho curto, a busca e o selo da versão (FR-3431, EC-16)."""
    c.linha(RODAPE)
    c.texto(
        MARGEM,
        RODAPE + 42,
        FIXOS["rodape"],
        tamanho=26,
        campo="fixo",
        cor=TEXTO_FRACO,
        fundo=BRANCO,
    )
    # O endereço é da implantação, e o seu comprimento não se conhece de antemão: mede-se e desce de
    # corpo até o mínimo; se nem assim couber numa linha, a peça é recusada — partir o endereço
    # mudaria o destino.
    caminho = ficha.caminho_curto
    tamanho = next((t for t in CORPOS_DO_CAMINHO if largura(caminho, t, NEGRITO) <= UTIL), None)
    if tamanho is None:
        raise PecaRecusada(
            f"O endereço do sistema é longo demais para o rodapé da peça: {caminho!r}."
        )
    c.texto(
        MARGEM,
        RODAPE + 86,
        caminho,
        tamanho=tamanho,
        campo="caminho_curto",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        fundo=BRANCO,
    )
    c.texto(
        MARGEM,
        RODAPE + 124,
        busca_na_peca(ficha),
        tamanho=28,
        campo="busca",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        fundo=BRANCO,
    )
    c.texto(
        MARGEM,
        RODAPE + 162,
        selo_da_versao(ficha),
        tamanho=CORPO_MINIMO,
        campo="selo",
        cor=TEXTO_FRACO,
        fundo=BRANCO,
    )


# ---- O texto alternativo (FR-3433) -------------------------------------------------------------


def _alternativo(ficha, marca, corpo, rodape):
    """Em frases, com o que a peça **mostra**, na ordem em que mostra.

    Lê o que foi desenhado, e não a ficha: uma oferta que a peça resumiu em contagem não aparece por
    extenso aqui, porque quem ouve o texto alternativo precisa receber a mesma peça de quem a vê.
    """
    frases = [f"Peça de divulgação do {kit_textos.assinatura(ficha)}, com a {marca.descricao}."]
    por_campo = {}
    for elemento in corpo:
        if isinstance(elemento, Texto):
            por_campo.setdefault(elemento.campo, []).append(elemento.conteudo)

    def junto(campo):
        return " ".join(por_campo.get(campo, []))

    titulo = junto("titulo_sem_numero") or junto("titulo_do_processo") or junto("manchete")
    frases.append(
        f"Processo seletivo, {ficha.identificacao}: {titulo}."
        if titulo
        else f"Processo seletivo, {ficha.identificacao}."
    )
    if "periodo_curto" in por_campo:
        datas = junto("periodo_curto")
        prefixo = "Inscrições" if datas[:1].isalpha() else "Inscrições de"
        frases.append(f"{prefixo} {datas}, {junto('hora')}.")
        if ficha.prorrogado:
            frases.append("Prazo prorrogado.")
    elif FIXOS["publicado"] in por_campo.get("fixo", []):
        frases.append(f"Edital publicado. {FIXOS['consulte']}.")
    if FIXOS["oferta"] in por_campo.get("fixo", []):
        resumo = ", ".join(
            junto(campo) for campo in ("oferta_nome", "total_de_vagas") if campo in por_campo
        )
        itens = []
        if "contagem" in por_campo:
            itens.append(f"{junto('contagem')}; {FIXOS['todas'].lower()}")
        for oferta in ficha.ofertas:
            rotulo = junto(f"oferta_rotulo:{oferta.perfil_id}")
            if rotulo:
                quantidade = junto(f"oferta_quantidade:{oferta.perfil_id}")
                itens.append(f"{rotulo}: {quantidade}" if quantidade else rotulo)
        # "Oferta" abre a primeira frase que houver: sozinha, ela seria uma frase sem conteúdo.
        if resumo:
            frases.append(f"Oferta: {resumo}.")
            frases.extend(f"{item[:1].upper()}{item[1:]}." for item in itens)
        elif itens:
            frases.append(f"Oferta: {itens[0]}.")
            frases.extend(f"{item[:1].upper()}{item[1:]}." for item in itens[1:])
    por_campo = {e.campo: e.conteudo for e in rodape if isinstance(e, Texto)}
    frases.append(f"{FIXOS['rodape']} {por_campo['caminho_curto']}, {por_campo['busca']}.")
    frases.append(f"{por_campo['selo'].replace(' · ', ', ')}.")
    return " ".join(frases)


# ---- A composição ------------------------------------------------------------------------------


class _CorpoNaoCabe(PecaRecusada):
    """O corpo passou do rodapé: com outro título, ou outro corpo do mesmo, talvez caiba."""


def compor(ficha, *, manchete=None):
    """A `Peca`, ou `PecaRecusada` com o motivo. `manchete` é o índice na lista fechada."""
    if not ficha.tem_material:
        raise PecaRecusada(ficha.motivo)
    if not ficha.caminho_curto:
        raise PecaRecusada(HOST_LOCAL)
    escolhida = escolher_manchete(ficha, manchete)
    opcoes = _opcoes_de_titulo(ficha, escolhida)
    if opcoes:
        omissao = ""
    else:
        omissao = ESCOLHA_A_MANCHETE if manchetes(ficha) else SEM_TITULO
    recusa = None
    for opcao in opcoes or [None]:
        try:
            peca = _compor(ficha, opcao, omissao)
        except _CorpoNaoCabe as excecao:
            recusa = excecao
            continue
        ausentes = fora_dos_textos(peca, kit_textos.compor(ficha))
        if ausentes:
            # Defesa, e não caminho esperado: o teste de coerência prova que não acontece. Se
            # acontecer, a peça diria um número que o kit textual não diz, e não sai.
            raise PecaRecusada(f"A peça diria o que o kit textual não diz: {', '.join(ausentes)}.")
        return peca
    raise PecaRecusada(recusa.motivo)


def _compor(ficha, opcao, omissao):
    c = _Composicao()
    marca = _cabecalho(c, ficha)
    inicio_do_corpo = len(c.elementos)
    y = FAIXA + 66
    c.texto(
        MARGEM,
        y,
        FIXOS["chamada"],
        tamanho=28,
        campo="fixo",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        fundo=BRANCO,
    )
    y += 44
    c.texto(
        MARGEM,
        y,
        ficha.identificacao,
        tamanho=32,
        campo="identificacao",
        cor=TEXTO_FRACO,
        fundo=BRANCO,
    )
    y = _titulo(c, y + 4, opcao)
    y += 32
    y = _periodo(c, ficha, y) if ficha.modo == fichas.COM_PERIODO else _publicado(c, y)
    _oferta(c, ficha, y)

    corpo = c.elementos[inicio_do_corpo:]
    fundo_do_corpo = max(_base(elemento) for elemento in corpo)
    limite = RODAPE - FOLGA_DO_RODAPE
    if fundo_do_corpo > limite:
        raise _CorpoNaoCabe(
            "O conteúdo não cabe na peça sem descer abaixo do corpo mínimo: "
            f"o corpo termina em {round(fundo_do_corpo)} px, e o rodapé começa em {limite} px."
        )
    deslocamento = round((limite - fundo_do_corpo) * PARTE_DA_FOLGA_EM_CIMA)
    corpo = [_deslocar(elemento, deslocamento) for elemento in corpo]
    c.elementos[inicio_do_corpo:] = corpo

    inicio_do_rodape = len(c.elementos)
    _rodape(c, ficha)
    rodape = c.elementos[inicio_do_rodape:]
    campo_do_titulo = opcao[0] if opcao else ""
    return Peca(
        elementos=tuple(c.elementos),
        alternativo=_alternativo(ficha, marca, corpo, rodape),
        titulo=campo_do_titulo,
        manchete=(" ".join(opcao[2]) if campo_do_titulo == "manchete" else None),
        omissao=omissao,
        corpo=tuple(corpo),
        deslocamento=deslocamento,
    )


def _base(elemento):
    if isinstance(elemento, Texto):
        return elemento.caixa[3]
    if isinstance(elemento, Retangulo):
        return elemento.y + elemento.altura
    return elemento.y


# ---- A conferência de coerência (FR-3423) ------------------------------------------------------

_DATA = re.compile(r"\b\d{2}/\d{2}(?:/\d{4})?\b")
_HORA = re.compile(r"\b\d{2}h\d{2}\b")
_QUANTIDADE = re.compile(r"\b\d+ (?:vagas?|opções)\b")


def fora_dos_textos(peca, textos):
    """As datas, horas e quantidades da peça que o kit textual não traz. Vazio é coerente."""
    corpo_dos_textos = "\n".join(textos.values())
    ausentes = []
    for texto in peca.textos:
        if texto.campo == "selo":
            # A referência da impressão e a data da versão são do selo, e o kit textual diz a
            # versão na ressalva; o que se confere aqui é o que a peça afirma do Edital.
            continue
        for padrao in (_DATA, _HORA, _QUANTIDADE):
            for achado in padrao.findall(texto.conteudo):
                if achado not in corpo_dos_textos and achado not in ausentes:
                    ausentes.append(achado)
    return ausentes


# ---- A serialização (D-008, D-021) -------------------------------------------------------------


@cache
def _marca_em_base64(arquivo):
    return base64.b64encode((PASTA_DAS_MARCAS / arquivo).read_bytes()).decode("ascii")


@cache
def _fontes_embutidas():
    """O `@font-face` da Edital Sans em `data:`, regular e negrito (`D-021`).

    O SVG exportado é aberto fora do GPS — num navegador, no Inkscape, numa ferramenta de design —,
    e sem a fonte cada um desenharia com outra, e as caixas medidas extravasariam. A OFL permite
    embutir. O PNG não precisa: o rasterizador recebe as fontes por arquivo.
    """
    regras = []
    for recurso, peso in ((REGULAR, 400), (NEGRITO, 700)):
        dados = base64.b64encode(fonte.fontes()[recurso].dados).decode("ascii")
        regras.append(
            f'@font-face{{font-family:"{FAMILIA}";font-weight:{peso};'
            f'src:url(data:font/ttf;base64,{dados}) format("truetype")}}'
        )
    return "".join(regras)


def _elemento_em_svg(elemento):
    if isinstance(elemento, Texto):
        peso = "700" if elemento.fonte == NEGRITO else "400"
        ancora = ' text-anchor="end"' if elemento.ancora == "end" else ""
        return (
            f'<text x="{elemento.x}" y="{elemento.y}" font-family="{FAMILIA}" '
            f'font-size="{elemento.tamanho}" font-weight="{peso}" fill="{elemento.cor}"{ancora} '
            f"data-campo={quoteattr(elemento.campo)}>{escape(elemento.conteudo)}</text>"
        )
    if isinstance(elemento, Retangulo):
        raio = f' rx="{elemento.raio}"' if elemento.raio else ""
        return (
            f'<rect x="{elemento.x}" y="{elemento.y}" width="{elemento.largura}" '
            f'height="{elemento.altura}"{raio} fill="{elemento.cor}"/>'
        )
    if isinstance(elemento, Linha):
        return (
            f'<line x1="{elemento.x1}" y1="{elemento.y}" x2="{elemento.x2}" y2="{elemento.y}" '
            f'stroke="{elemento.cor}" stroke-width="2"/>'
        )
    # A marca entra em `data:`: o rasterizador não resolve nenhum recurso externo, e o arquivo
    # exportado é inteiro em si (D-007, item 4).
    return (
        f'<image x="{elemento.x}" y="{elemento.y}" width="{elemento.largura}" '
        f'height="{elemento.altura}" data-campo="marca" '
        f'href="data:image/png;base64,{_marca_em_base64(elemento.marca.arquivo)}"/>'
    )


def svg(peca, ficha, *, fonte_embutida=False):
    """O SVG da peça. `fonte_embutida` na exportação; o rasterizador recebe as fontes à parte."""
    estilo = f"<style>{_fontes_embutidas()}</style>" if fonte_embutida else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" '
        f'viewBox="0 0 {LARGURA} {ALTURA}" role="img" aria-labelledby="titulo descricao">'
        f'<title id="titulo">{escape(grafia.normalizar(ficha.identificacao))} — '
        "material de divulgação</title>"
        f'<desc id="descricao">{escape(grafia.normalizar(peca.alternativo))}</desc>'
        + estilo
        + "".join(_elemento_em_svg(elemento) for elemento in peca.elementos)
        + "</svg>"
    )


def conferir_marcas():
    """Os arquivos da marca são os que `ORIGEM.md` registra? `{arquivo: resumo}` dos que não são."""
    divergentes = {}
    for marca in MARCAS.values():
        resumo = hashlib.sha256((PASTA_DAS_MARCAS / marca.arquivo).read_bytes()).hexdigest()
        if resumo != marca.sha256:
            divergentes[marca.arquivo] = resumo
    return divergentes
