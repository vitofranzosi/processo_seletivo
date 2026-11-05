"""A peça do kit de divulgação, composta da ficha e de um template declarado (111, 119).

**A composição é um modelo de caixas, e o SVG é a serialização dele** (`D-008` da `111`). O
compositor produz elementos posicionados — texto com o campo da ficha de onde veio, corpo, fonte e
caixa medida; retângulos; linhas; a marca —, e só depois um serializador escreve o SVG. Na POC as
conferências sobre o SVG ficaram verdes com o endereço fora da margem e a quantidade dentro do
rótulo; com as caixas explícitas, área útil e colisão viram aritmética, e o teste geométrico é
exato.

**O desenho vem da declaração do template** (119, `D-003`, `D-004`): tamanho do formato, paleta,
fontes por papel, frases, corpos e recaídas são dados de `kit_familias/`, e este módulo os lê. A
peça da `111` é a família Institucional (`D-002`), desenhada pelo compositor de fluxo, e os SVG de
referência dela não mudaram um byte com a generalização (SC-1133). `compor(ficha, manchete=...)`
continua sendo a peça Institucional; `compor_template(ficha, template, escolha)` é a entrada geral.

**Mede com a fonte que desenha, e desenha o que mediu** (`D-009` da `111`, `D-005`). A largura é a
de `kit_fontes`, a quebra é a do compositor do ato, e o texto que entra no SVG já passou por
`grafia.normalizar` — a métrica mede o normalizado, e um rasterizador que recebesse o cru desenharia
outra largura. Quebra que parte palavra conta como "não cabe" (FR-3429): um endereço partido no
rodapé mudaria o destino.

**Recusa em vez de encolher sem fim, e nunca trunca** (FR-3426, FR-3429). O título desce de corpo
até o mínimo; se nenhum título oficial cabe, a tela oferece a manchete da lista fechada (FR-3427),
e sem ela a peça sai sem título e diz a omissão. O que sobra de um título cortado diria outra
coisa.
"""

import base64
import hashlib
import re
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from processo_seletivo.interface import kit_familias, kit_fontes, kit_textos
from processo_seletivo.interface.kit_familias import institucional
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure.pdf import quebrar as quebra_do_edital

#: O template da peça de produção da `111`, que `compor(ficha, manchete=...)` desenha.
INSTITUCIONAL = institucional.POST
#: O identificador dele, registrado em cada exportação (FR-3436). Mudar o desenho muda a versão, os
#: SVG de referência e pede nova revisão da comunicação (`D-010`, `D-016` da `111`).
TEMPLATE = INSTITUCIONAL.identificador

# Os nomes que a `111` exportava, agora lidos da declaração da Institucional. Ficam como apelidos:
# a tela, o pacote, a galeria e o teste geométrico os leem, e a peça de produção é esta.
LARGURA, ALTURA = INSTITUCIONAL.formato.largura, INSTITUCIONAL.formato.altura
MARGEM = INSTITUCIONAL.formato.margem
UTIL = INSTITUCIONAL.formato.util
CORPO_MINIMO = INSTITUCIONAL.formato.corpo_minimo
BRANCO = institucional.PALETA["branco"]
BORDA = institucional.PALETA["borda"]
RODAPE = INSTITUCIONAL.dimensoes["rodape"]
FOLGA_DO_RODAPE = INSTITUCIONAL.dimensoes["folga_do_rodape"]
REGULAR = institucional.FONTES["corpo"]
NEGRITO = institucional.FONTES["titulo"]
FIXOS = institucional.FRASES
HORARIO = institucional.HORARIO
Marca = kit_familias.Ativo
MARCAS = {
    "Cefor": institucional.ATIVOS["marca-cefor"],
    "Ifes": institucional.ATIVOS["marca-ifes"],
}
PASTA_DAS_MARCAS = institucional.FAMILIA.pasta_dos_ativos

HOST_LOCAL = (
    "A peça não é gerada neste acesso: o endereço público do sistema não é conhecido daqui, e a "
    "peça precisa dele no rodapé."
)
SEM_TITULO = "Nenhum título oficial cabe na peça, e ela sai sem título."
ESCOLHA_A_MANCHETE = (
    "Nenhum título oficial cabe na peça. Escolha uma manchete abaixo, ou a peça sai sem título."
)


@dataclass(frozen=True)
class Escolha:
    """O que quem gera escolheu, além do template (FR-3806, `D-008`). Não é guardada."""

    #: O índice na lista fechada de manchetes (FR-3427 da `111`).
    manchete: int | None = None
    variante: str | None = None
    imagem: str | None = None
    #: O texto da manchete, resolvido pela tela contra a lista da família (FR-3818): vale só nos
    #: formatos em que nenhum título oficial cabe.
    manchete_texto: str | None = None


class PecaRecusada(Exception):
    """A composição recusada, com o motivo dito para quem gera (FR-3429, FR-3430)."""

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


ESCOLHA_INDISPONIVEL = "A escolha não está disponível; abra o kit de novo."


class EscolhaInvalida(PecaRecusada):
    """Família, variante, imagem, formato ou manchete fora das listas fechadas (EC-9).

    Uma classe só, e filha de `PecaRecusada`: a prévia, que só sabe responder "não encontrado",
    trata a escolha forjada como a peça que não existe neste acesso, e quem chamar `compor_template`
    com imagem fora do banco recebe a recusa, e não um 500.
    """

    def __init__(self, motivo=ESCOLHA_INDISPONIVEL):
        super().__init__(motivo)


class MancheteInvalida(ValueError):
    """Índice de manchete fora da lista, ou manchete pedida quando um título oficial cabe."""


# ---- O modelo de caixas (D-008) ----------------------------------------------------------------


@dataclass(frozen=True)
class Texto:
    x: int
    y: int  # a linha de base
    conteudo: str  # já normalizado pela grafia: o que se mede é o que se desenha
    tamanho: int
    fonte: str  # a chave em `kit_fontes.FONTES`
    campo: str
    cor: str
    fundo: str  # o fundo sobre o qual é desenhado, para o contraste
    ancora: str = "start"

    @property
    def largura(self):
        return kit_fontes.METRICA.largura(self.conteudo, self.tamanho, self.fonte)

    @property
    def caixa(self):
        """`(esquerda, topo, direita, base)` em px, pela métrica tipográfica da fonte."""
        medidas = kit_fontes.medidas(self.fonte)
        if self.ancora == "end":
            esquerda = self.x - self.largura
        elif self.ancora == "middle":
            esquerda = self.x - self.largura / 2
        else:
            esquerda = self.x
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
    marca: kit_familias.Ativo
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


@dataclass(frozen=True)
class Figura:
    """Um arquivo da família desenhado na peça: a imagem do banco, um ativo fixo (D-004)."""

    x: int
    y: int
    largura: int
    altura: int
    arquivo: str
    tipo: str  # "image/jpeg" ou "image/png"
    campo: str
    #: Pinta por inteiro o retângulo que ocupa (o balão é branco por dentro): texto declarado sobre
    #: ele tem esse fundo, e não o da imagem embaixo.
    opaca: bool = False
    #: A cor de dentro da figura opaca, quando não é o branco (o balão roxo da FIC). Não vai ao SVG:
    #: é o que o teste geométrico confere contra o fundo declarado do texto.
    cor: str = ""

    @property
    def caixa(self):
        return (self.x, self.y, self.x + self.largura, self.y + self.altura)


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
    template: kit_familias.Template = INSTITUCIONAL
    #: O que saiu da peça sem a recusar, para a tela dizer (FR-3818, FR-3820).
    avisos: tuple = ()
    #: A imagem do banco escolhida, quando a família tem banco.
    imagem: kit_familias.Imagem | None = None

    @property
    def textos(self):
        return tuple(e for e in self.elementos if isinstance(e, Texto))


@dataclass
class _Composicao:
    template: kit_familias.Template
    elementos: list = field(default_factory=list)

    @property
    def familia(self):
        return kit_familias.familia(self.template.familia)

    @property
    def formato(self):
        return self.template.formato

    def cor(self, nome):
        return self.familia.cor(nome)

    def fonte(self, caixa):
        """A chave da fonte da caixa, pelo papel que ela declara."""
        return self.familia.fonte(self.template.caixa(caixa).fonte)

    def escrever(self, caixa, x, y, valor, *, campo, tamanho=None, ancora=None):
        """O texto na fonte, na cor e no fundo da caixa; o corpo é o primeiro dela, se não dito."""
        declarada = self.template.caixa(caixa)
        return self._texto(
            x,
            y,
            valor,
            tamanho=declarada.corpos[0] if tamanho is None else tamanho,
            campo=campo,
            cor=self.cor(declarada.cor),
            fundo=self.cor(declarada.fundo),
            fonte=self.fonte(caixa),
            ancora=declarada.alinhamento if ancora is None else ancora,
        )

    def _texto(self, x, y, valor, *, tamanho, campo, cor, fundo, fonte, ancora):
        conteudo = grafia.normalizar(str(valor))
        faltam = grafia.sem_grafia(conteudo)
        if faltam:
            nomes = ", ".join(grafia.descrever(c) for c in faltam)
            raise PecaRecusada(f"A peça não desenha o caractere {nomes}, em {_rotulo(campo)}.")
        faltam = kit_fontes.sem_glifo(conteudo, fonte)
        if faltam:
            # A grafia admite, e a fonte da família não desenha (FR-3823, EC-13): o rasterizador
            # completaria com outra fonte, e a peça mediria uma largura e desenharia outra.
            nomes = ", ".join(grafia.descrever(c) for c in faltam)
            raise PecaRecusada(
                f"A fonte {kit_fontes.FONTES[fonte].familia} não desenha o caractere {nomes}, "
                f"em {_rotulo(campo)}."
            )
        elemento = Texto(round(x), round(y), conteudo, tamanho, fonte, campo, cor, fundo, ancora)
        self.elementos.append(elemento)
        return elemento

    def retangulo(self, x, y, largura, altura, *, cor, raio=0):
        caixa = (round(x), round(y), round(largura), round(altura))
        self.elementos.append(Retangulo(*caixa, self.cor(cor), raio))

    def linha(self, y):
        margem = self.formato.margem
        cor = self.cor("borda")
        self.elementos.append(Linha(margem, self.formato.largura - margem, round(y), cor))


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


def largura(texto, tamanho, fonte=REGULAR):
    """A largura em px, na fonte do kit de chave `fonte`."""
    return kit_fontes.METRICA.largura(texto, tamanho, fonte)


def quebrar(texto, tamanho, fonte=REGULAR, limite=UTIL):
    """As linhas, ou `None` se a quebra partiu palavra: isso conta como "não cabe" (FR-3429)."""
    texto = grafia.normalizar(str(texto))
    linhas = quebra_do_edital(texto, tamanho, 0, fonte, limite=limite, metrica=kit_fontes.METRICA)
    if " ".join(linhas).split() != texto.split():
        return None
    return linhas


def medidas_do_titulo(texto, template=INSTITUCIONAL):
    """Os `(tamanho, linhas)` em que o título cabe no template, do maior corpo ao menor."""
    caixa = template.caixa("titulo")
    fonte = kit_familias.familia(template.familia).fonte(caixa.fonte)
    medidas = []
    for tamanho, maximo in caixa.medidas():
        linhas = quebrar(texto, tamanho, fonte, limite=template.formato.util)
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


def _opcoes_de_titulo(ficha, manchete, template):
    """`(campo, tamanho, linhas)` na ordem em que se tentam, até o corpo da peça caber.

    Primeiro o título do Edital em cada corpo, depois o do Processo, e a manchete só quando nenhum
    oficial cabe (FR-3426). O título desce de corpo antes de ceder a vez: com quatro polos e um
    título de três linhas, o corpo menor é o que deixa a oferta inteira.
    """
    opcoes = [
        (campo, tamanho, linhas)
        for campo, texto in titulos_oficiais(ficha)
        for tamanho, linhas in medidas_do_titulo(texto, template)
    ]
    if not opcoes and manchete is not None:
        opcoes = [("manchete", t, linhas) for t, linhas in medidas_do_titulo(manchete, template)]
    return opcoes


def _algum_oficial_cabe(ficha, template):
    return any(medidas_do_titulo(texto, template) for _, texto in titulos_oficiais(ficha))


def manchetes(ficha, template=INSTITUCIONAL):
    """A lista fechada da FR-3427, só quando nenhum título oficial cabe (`D-013`).

    Derivada da ficha, e só dela: o nome comum, quando todas as opções têm o mesmo nome; o nome de
    cada opção, quando há até quatro; e "nome — localidade" da opção única. Fica só com as que cabem
    como título e passam a lista de vocabulário (FR-3414). Não há texto livre: a revisão mostrou que
    os filtros deixavam passar "Curso gratuito para todo o país".
    """
    if _algum_oficial_cabe(ficha, template) or not ficha.ofertas:
        return ()
    return tuple(c for c in _candidatas(ficha) if medidas_do_titulo(c, template))


def _candidatas(ficha):
    """As manchetes que a ficha dá, sem repetir e sem termo da FR-3414, antes de medir."""
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
        vistas.append(candidata)
    return vistas


def escolher_manchete(ficha, indice, template=INSTITUCIONAL):
    """O texto da manchete de índice `indice`, ou `MancheteInvalida` (contrato, 422)."""
    if indice is None:
        return None
    lista = manchetes(ficha, template)
    if not 0 <= indice < len(lista):
        raise MancheteInvalida("A manchete escolhida não está entre as oferecidas.")
    return lista[indice]


# ---- As partes do compositor de fluxo (a Institucional) ----------------------------------------


def marca_da_unidade(ficha):
    """A marca da unidade, quando o pacote oficial tem a dela; senão a do Ifes, com a sigla."""
    nome = institucional.MARCA_DA_UNIDADE.get(ficha.unidade_sigla)
    if nome:
        return institucional.ATIVOS[nome], False
    return institucional.ATIVOS[institucional.MARCA_PADRAO], True


def _cabecalho(c, ficha):
    dimensoes = c.template.dimensoes
    faixa = dimensoes["faixa"]
    c.retangulo(0, 0, c.formato.largura, faixa, cor="verde_escuro")
    marca, assinar = marca_da_unidade(ficha)
    largura_da_marca = dimensoes["largura_da_marca"]
    altura = round(largura_da_marca / dimensoes["proporcao_da_marca"])
    esquerda, topo, _, base = marca.visivel
    # A parte visível nas margens: a transparência em volta é a reserva de integridade do manual.
    x = c.formato.margem - round(esquerda * largura_da_marca)
    y = c.formato.margem_vertical - round(topo * altura)
    c.elementos.append(Imagem(x, y, largura_da_marca, altura, marca))
    if assinar:
        c.escrever(
            "assinatura",
            c.formato.largura - c.formato.margem,
            faixa / 2 + 13,
            kit_textos.assinatura(ficha),
            campo="assinatura",
        )
    return marca


def _titulo(c, y, opcao):
    """O título escolhido, linha a linha. Nenhum título é truncado: ou cabe inteiro, ou não sai."""
    if opcao is None:
        return y
    campo, tamanho, linhas = opcao
    for linha in linhas:
        y += round(tamanho * 1.18)
        c.escrever("titulo", c.formato.margem, y, linha, campo=campo, tamanho=tamanho)
    return y


def _hora_do_periodo(ficha):
    if ficha.inicio_data and ficha.fim_data:
        return f"até as {ficha.fim_hora} {HORARIO}"
    if ficha.inicio_data:
        return f"às {ficha.inicio_hora} {HORARIO}"
    return f"às {ficha.fim_hora} {HORARIO}"


def _periodo(c, ficha, y):
    """O destaque principal: o período em datas absolutas, e nenhuma palavra sobre o agora."""
    dimensoes, frases = c.template.dimensoes, c.familia.frases
    margem, util = c.formato.margem, c.formato.util
    recuo = dimensoes["recuo_do_bloco"]
    bloco = dimensoes["bloco_do_periodo"]
    c.retangulo(margem, y, util, bloco, cor="verde_escuro", raio=dimensoes["raio_do_bloco"])
    dentro = margem + recuo
    disponivel = util - 2 * recuo
    topo = y + 62
    c.escrever("inscricoes", dentro, topo, frases["inscricoes"], campo="fixo")
    if ficha.prorrogado:
        # Na linha de "INSCRIÇÕES", à direita: o selo qualifica o período, e uma linha só para ele
        # empurrava a oferta para o rodapé num Edital de quatro polos.
        rotulo = frases["prorrogado"]
        selo = c.template.caixa("selo_prorrogado")
        largura_do_selo = largura(rotulo, selo.corpos[0], c.fonte("selo_prorrogado")) + 2 * 22
        direita = margem + util - recuo
        c.retangulo(
            direita - largura_do_selo, topo - 36, largura_do_selo, 48, cor=selo.fundo, raio=24
        )
        c.escrever("selo_prorrogado", direita - 22, topo - 4, rotulo, campo="fixo")
    datas = ficha.periodo_curto
    fonte = c.fonte("periodo")
    corpos = c.template.caixa("periodo").corpos
    tamanho = next((t for t in corpos if largura(datas, t, fonte) <= disponivel), None)
    if tamanho is None:
        raise PecaRecusada(f"O período não cabe no destaque da peça: {datas!r}.")
    c.escrever("periodo", dentro, topo + 100, datas, campo="periodo_curto", tamanho=tamanho)
    c.escrever("hora", dentro, topo + 150, _hora_do_periodo(ficha), campo="hora")
    return y + bloco


def _publicado(c, y):
    """O destaque do modo neutro: sem período designado, a peça não fala de inscrição (FR-3424)."""
    dimensoes, frases = c.template.dimensoes, c.familia.frases
    margem = c.formato.margem
    bloco = dimensoes["bloco_do_neutro"]
    c.retangulo(
        margem, y, c.formato.util, bloco, cor="verde_escuro", raio=dimensoes["raio_do_bloco"]
    )
    dentro = margem + dimensoes["recuo_do_bloco"]
    c.escrever("publicado", dentro, y + 96, frases["publicado"], campo="fixo")
    c.escrever("consulte", dentro, y + 150, frases["consulte"], campo="fixo")
    return y + bloco


def _linhas_ou_recusa(texto, tamanho, fonte, maximo, campo, limite=UTIL):
    linhas = quebrar(texto, tamanho, fonte, limite=limite)
    if linhas is None or len(linhas) > maximo:
        raise PecaRecusada(f"{_rotulo(campo).capitalize()} não cabe na peça: {texto!r}.")
    return linhas


def _oferta(c, ficha, y):
    """A oferta pelo teto único de quatro opções (FR-3425)."""
    ofertas = ficha.ofertas
    if not ofertas:
        return y
    margem, frases = c.formato.margem, c.familia.frases
    y += 64
    c.escrever("rotulo_da_oferta", margem, y, frases["oferta"], campo="fixo")
    # A soma, sempre com o número de opções que a repartem: "160 vagas" sozinho se lê como de
    # cada polo (a exceção declarada à FR-1607 da `072`).
    total = kit_textos.total_em_frase(ficha)
    if total:
        direita = c.formato.largura - margem
        c.escrever("total_de_vagas", direita, y, total, campo="total_de_vagas")
    if ficha.nomes_iguais:
        nome = c.template.caixa("oferta_nome")
        (tamanho, maximo), *_ = nome.medidas()
        linhas = _linhas_ou_recusa(
            ofertas[0].nome,
            tamanho,
            c.fonte("oferta_nome"),
            maximo,
            "oferta_nome",
            limite=c.formato.util,
        )
        for linha in linhas:
            y += 44
            c.escrever("oferta_nome", margem, y, linha, campo="oferta_nome")
    if not kit_textos.lista_as_opcoes(ficha):
        y += 58
        c.escrever("contagem", margem, y, f"{len(ofertas)} opções", campo="contagem")
        y += 46
        c.escrever("todas", margem, y, frases["todas"], campo="fixo")
        return y
    for oferta in ofertas:
        y = _linha_da_oferta(c, ficha, oferta, y)
    return y


def _linha_da_oferta(c, ficha, oferta, y):
    rotulo = kit_textos.rotulo_da_oferta(oferta, ficha)
    quantidade = oferta.quantidade
    campo = f"oferta_rotulo:{oferta.perfil_id}"
    margem, util = c.formato.margem, c.formato.util
    (tamanho, maximo), *_ = c.template.caixa("oferta_rotulo").medidas()
    fonte_do_rotulo = c.fonte("oferta_rotulo")
    tamanho_da_quantidade = c.template.caixa("oferta_quantidade").corpos[0]
    # A coluna da quantidade é medida, e não reservada: "3 vagas e cadastro reserva" ocupa o dobro
    # de "40 vagas", e a largura fixa fazia um invadir o outro (POC).
    if quantidade:
        medida = largura(quantidade, tamanho_da_quantidade, c.fonte("oferta_quantidade"))
        lado = util - (medida + 32)
    else:
        lado = util
    linhas = quebrar(rotulo, tamanho, fonte_do_rotulo, limite=lado)
    empilhar = linhas is None or len(linhas) > 1
    if empilhar:
        linhas = _linhas_ou_recusa(rotulo, tamanho, fonte_do_rotulo, maximo, campo, limite=util)
    y += 48
    topo = y
    for posicao, linha in enumerate(linhas):
        if posicao:
            y += 40
        c.escrever("oferta_rotulo", margem, y, linha, campo=campo)
    if quantidade:
        if empilhar:
            y += 40
        c.escrever(
            "oferta_quantidade",
            c.formato.largura - margem,
            y if empilhar else topo,
            quantidade,
            campo=f"oferta_quantidade:{oferta.perfil_id}",
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
    margem, util = c.formato.margem, c.formato.util
    rodape = c.template.dimensoes["rodape"]
    c.linha(rodape)
    c.escrever("rodape", margem, rodape + 42, c.familia.frases["rodape"], campo="fixo")
    # O endereço é da implantação, e o seu comprimento não se conhece de antemão: mede-se e desce de
    # corpo até o mínimo; se nem assim couber numa linha, a peça é recusada — partir o endereço
    # mudaria o destino.
    caminho = ficha.caminho_curto
    fonte = c.fonte("caminho_curto")
    corpos = c.template.caixa("caminho_curto").corpos
    tamanho = next((t for t in corpos if largura(caminho, t, fonte) <= util), None)
    if tamanho is None:
        raise PecaRecusada(
            f"O endereço do sistema é longo demais para o rodapé da peça: {caminho!r}."
        )
    c.escrever(
        "caminho_curto", margem, rodape + 86, caminho, campo="caminho_curto", tamanho=tamanho
    )
    c.escrever("busca", margem, rodape + 124, busca_na_peca(ficha), campo="busca")
    c.escrever("selo_da_versao", margem, rodape + 162, selo_da_versao(ficha), campo="selo")


# ---- O texto alternativo (FR-3433) -------------------------------------------------------------


def _alternativo(ficha, marca, corpo, rodape, fixos):
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
    elif fixos["publicado"] in por_campo.get("fixo", []):
        frases.append(f"Edital publicado. {fixos['consulte']}.")
    if fixos["oferta"] in por_campo.get("fixo", []):
        resumo = ", ".join(
            junto(campo) for campo in ("oferta_nome", "total_de_vagas") if campo in por_campo
        )
        itens = []
        if "contagem" in por_campo:
            itens.append(f"{junto('contagem')}; {fixos['todas'].lower()}")
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
    frases.append(f"{fixos['rodape']} {por_campo['caminho_curto']}, {por_campo['busca']}.")
    frases.append(f"{por_campo['selo'].replace(' · ', ', ')}.")
    return " ".join(frases)


# ---- A composição ------------------------------------------------------------------------------


class _CorpoNaoCabe(PecaRecusada):
    """O corpo passou do rodapé: com outro título, ou outro corpo do mesmo, talvez caiba."""


def compor(ficha, *, manchete=None):
    """A peça Institucional, ou `PecaRecusada` com o motivo. `manchete` é o índice na lista."""
    return compor_template(ficha, INSTITUCIONAL, Escolha(manchete=manchete))


def compor_template(ficha, template, escolha=None):
    """A `Peca` do template para a ficha e a escolha, ou `PecaRecusada` com o motivo (FR-3803)."""
    if not ficha.tem_material:
        raise PecaRecusada(ficha.motivo)
    if not ficha.caminho_curto:
        raise PecaRecusada(HOST_LOCAL)
    return COMPOSITORES[template.composicao](ficha, template, escolha or Escolha())


def _compor_em_fluxo(ficha, template, escolha):
    """O compositor da Institucional: as caixas empilhadas na ordem do conteúdo."""
    escolhida = escolher_manchete(ficha, escolha.manchete, template)
    opcoes = _opcoes_de_titulo(ficha, escolhida, template)
    if opcoes:
        omissao = ""
    else:
        omissao = ESCOLHA_A_MANCHETE if manchetes(ficha, template) else SEM_TITULO
    recusa = None
    for opcao in opcoes or [None]:
        try:
            peca = _compor(ficha, template, opcao, omissao)
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


def _compor(ficha, template, opcao, omissao):
    c = _Composicao(template)
    dimensoes, margem = template.dimensoes, template.formato.margem
    marca = _cabecalho(c, ficha)
    inicio_do_corpo = len(c.elementos)
    y = dimensoes["faixa"] + 66
    c.escrever("chamada", margem, y, c.familia.frases["chamada"], campo="fixo")
    y += 44
    c.escrever("identificacao", margem, y, ficha.identificacao, campo="identificacao")
    y = _titulo(c, y + 4, opcao)
    y += 32
    y = _periodo(c, ficha, y) if ficha.modo == fichas.COM_PERIODO else _publicado(c, y)
    _oferta(c, ficha, y)

    corpo = c.elementos[inicio_do_corpo:]
    fundo_do_corpo = max(_base(elemento) for elemento in corpo)
    limite = dimensoes["rodape"] - dimensoes["folga_do_rodape"]
    if fundo_do_corpo > limite:
        raise _CorpoNaoCabe(
            "O conteúdo não cabe na peça sem descer abaixo do corpo mínimo: "
            f"o corpo termina em {round(fundo_do_corpo)} px, e o rodapé começa em {limite} px."
        )
    deslocamento = round((limite - fundo_do_corpo) * dimensoes["parte_da_folga_em_cima"])
    corpo = [_deslocar(elemento, deslocamento) for elemento in corpo]
    c.elementos[inicio_do_corpo:] = corpo

    inicio_do_rodape = len(c.elementos)
    _rodape(c, ficha)
    rodape = c.elementos[inicio_do_rodape:]
    campo_do_titulo = opcao[0] if opcao else ""
    return Peca(
        elementos=tuple(c.elementos),
        alternativo=_alternativo(ficha, marca, corpo, rodape, c.familia.frases),
        titulo=campo_do_titulo,
        manchete=(" ".join(opcao[2]) if campo_do_titulo == "manchete" else None),
        omissao=omissao,
        corpo=tuple(corpo),
        deslocamento=deslocamento,
        template=template,
    )


#: O compositor de cada template, pelo nome que ele declara em `composicao`.
COMPOSITORES = {"fluxo-institucional": _compor_em_fluxo}


def _base(elemento):
    if isinstance(elemento, Texto):
        return elemento.caixa[3]
    if isinstance(elemento, Retangulo):
        return elemento.y + elemento.altura
    return elemento.y


# ---- O compositor de caixas posicionadas (119, D-004, FR-3815–FR-3825) -------------------------
#
# As famílias da comunicação: cada caixa tem o seu retângulo, e as que não têm entram, empilhadas,
# no painel — o retângulo de cor lisa de altura variável dos templates ("o retângulo amarelo pode
# aumentar ou diminuir a altura"), preso pela base. O fundo é a imagem do banco, inteira; as partes
# dela que não podem receber texto (foto, padrões, rodapé) estão em `dimensoes["obstaculos"]`, e o
# teste geométrico as confere.

#: A altura de uma linha, em corpos: a caixa tipográfica da Poppins mede 1,4 corpo (1050 + 350
#: milésimos), e linhas mais juntas que isso teriam caixas que se cruzam.
ENTRELINHA = 1.42


def entrelinha(fonte):
    """A altura de uma linha, em corpos, na fonte de chave dada.

    A `ENTRELINHA`, ou a caixa tipográfica da fonte quando ela é maior: a Space Mono da FIC mede
    1,48 corpo (1120 + 361 milésimos), e duas linhas dela a 1,42 teriam caixas que se cruzam. A
    Poppins mede 1,40, e a peça da Pós Lato Sensu não muda.
    """
    medidas = kit_fontes.medidas(fonte)
    return max(ENTRELINHA, (medidas.ascendente - medidas.descendente) / 1000)


SEM_TITULO_EM = "O título oficial não coube em: {formatos}."
SEM_CONTATO_EM = "O contato não coube em: {formatos}."
#: FR-3836: o formato que passou ao resumo diz na tela; as ofertas completas seguem nos textos.
RESUMO_EM = (
    "As opções não couberam listadas em: {formatos}. Esses formatos trazem o total e o convite à "
    "página; as opções completas estão nos textos."
)


class _NaoCabe(PecaRecusada):
    """Uma caixa obrigatória não coube em nenhum corpo: o template é recusado (FR-3824)."""


def _linhas_na_caixa(texto, caixa, fonte, largura_util, altura=None):
    """`(corpo, linhas)` no maior corpo em que o texto cabe na caixa, ou `None`."""
    for corpo, maximo in caixa.medidas():
        linhas = quebrar(texto, corpo, fonte, limite=largura_util)
        if linhas is None or len(linhas) > maximo:
            continue
        if altura is not None and len(linhas) * corpo * entrelinha(fonte) > altura + 0.5:
            continue
        return corpo, linhas
    return None


def _x_da_ancora(retangulo, alinhamento):
    x, _, largura, _ = retangulo
    return {"start": x, "middle": x + largura / 2, "end": x + largura}[alinhamento]


def _escrever_em(c, nome, retangulo, linhas, corpo, campo):
    """As linhas na caixa de retângulo dado, do topo, pela linha de base da fonte."""
    caixa = c.template.caixa(nome)
    ascendente = kit_fontes.medidas(c.fonte(nome)).ascendente / 1000
    x = _x_da_ancora(retangulo, caixa.alinhamento)
    y = retangulo[1]
    for linha in linhas:
        c.escrever(nome, x, y + ascendente * corpo, linha, campo=campo, tamanho=corpo)
        y += corpo * entrelinha(c.fonte(nome))
    return y


def _caixa_unica(c, nome, texto, campo, *, recusa):
    """Uma caixa posicionada de uma linha só, ou a recusa com o motivo (FR-3824)."""
    caixa = c.template.caixa(nome)
    x, y, largura_, altura = caixa.retangulo
    medida = _linhas_na_caixa(texto, caixa, c.fonte(nome), largura_, altura)
    if medida is None:
        raise _NaoCabe(recusa.format(texto=texto, formato=c.formato.chave))
    corpo, linhas = medida
    _escrever_em(c, nome, caixa.retangulo, linhas, corpo, campo)


def _resolver_titulo(ficha, template, escolha):
    """`(campo, corpo, linhas)` do título, pela ordem da FR-3426 da `111`, ou `None` (FR-3818)."""
    caixa = template.caixa("titulo")
    fonte = kit_familias.familia(template.familia).fonte(caixa.fonte)
    _, _, largura_, altura = caixa.retangulo
    for campo, texto in titulos_oficiais(ficha):
        medida = _linhas_na_caixa(texto, caixa, fonte, largura_, altura)
        if medida:
            return (campo, *medida)
    if escolha.manchete_texto:
        medida = _linhas_na_caixa(escolha.manchete_texto, caixa, fonte, largura_, altura)
        if medida:
            return ("manchete", *medida)
    return None


def titulo_oficial_cabe(ficha, template):
    """Algum título oficial cabe na caixa de título do template? (FR-3818)."""
    if template.composicao != "caixas":
        return _algum_oficial_cabe(ficha, template)
    return _resolver_titulo(ficha, template, Escolha()) is not None


def _itens_do_painel(c, ficha, frases, resumir=False):
    """`[(caixa, texto, campo)]` do painel, na ordem em que a peça os mostra."""
    itens = []
    nomes = c.template.dimensoes["painel"]["itens"]
    for nome in nomes:
        if nome == "periodo":
            if ficha.modo == fichas.COM_PERIODO:
                if ficha.prorrogado and "faixa" not in c.template.dimensoes:
                    itens.append(("selo_prorrogado", frases["prorrogado"], "fixo"))
                if ficha.fim_data:
                    itens.append(("periodo", f"{frases['ate']} {ficha.fim_data}", "periodo_curto"))
                    itens.append(("hora", f"às {ficha.fim_hora} {frases['horario']}", "hora"))
                    if ficha.inicio_data:
                        itens.append(
                            ("inicio", f"{frases['inicio']} {ficha.inicio_data}", "inicio")
                        )
                else:
                    texto = f"{frases['a_partir']} {ficha.inicio_data}"
                    itens.append(("periodo", texto, "periodo_curto"))
                    itens.append(("hora", f"às {ficha.inicio_hora} {frases['horario']}", "hora"))
            else:
                itens.append(("publicado", frases["publicado"], "fixo"))
                itens.append(("consulte", frases["consulte"], "fixo"))
        elif nome == "ofertas" and c.template.tem_ofertas and ficha.ofertas:
            total = kit_textos.total_em_frase(ficha)
            if total:
                itens.append(("total", total, "total_de_vagas"))
            if kit_textos.lista_as_opcoes(ficha) and not resumir:
                for oferta, linha in zip(
                    ficha.ofertas, kit_textos.linhas_da_oferta(ficha), strict=True
                ):
                    itens.append(("oferta", linha, f"oferta:{oferta.perfil_id}"))
            else:
                # O total já diz o número de opções ("160 vagas em 4 opções"); a contagem só sai
                # sozinha quando não há total (FR-3425 da `111`).
                if not total:
                    itens.append(("contagem", f"{len(ficha.ofertas)} opções", "contagem"))
                itens.append(("todas", frases["todas"], "fixo"))
        elif nome == "busca":
            itens.append(("busca", busca_na_peca(ficha), "busca"))
        elif nome == "selo_da_versao":
            itens.append(("selo_da_versao", selo_da_versao(ficha), "selo"))
    return itens


#: As famílias em que a FR-3836 admite o resumo por falta de espaço. Fica no motor, e não na
#: declaração do template, para que a lista não mude o resumo dos templates já aprovados; outra
#: família só entra por emenda da FR-3836, e então aqui.
RESUMO_POR_ESPACO = frozenset({"pos-lato-sensu"})
CARGA_NAO_CABE = "A carga horária não cabe no {formato} no corpo mínimo: {cargas}."


def _carga_que_nao_cabe(c, ficha):
    """As cargas horárias cuja linha não cabe na caixa da oferta, e que sem elas caberia (EC-3)."""
    caixa = c.template.caixa("oferta")
    util = c.template.dimensoes["painel"]["largura"] - 2 * c.template.dimensoes["painel"]["recuo"]
    sem = replace(ficha, ofertas=tuple(replace(o, carga_horaria="") for o in ficha.ofertas))
    culpadas = []
    for oferta, com_carga, sem_carga in zip(
        ficha.ofertas,
        kit_textos.linhas_da_oferta(ficha),
        kit_textos.linhas_da_oferta(sem),
        strict=True,
    ):
        if not oferta.carga_horaria or oferta.carga_horaria in culpadas:
            continue
        fonte = c.fonte("oferta")
        if _linhas_na_caixa(com_carga, caixa, fonte, util) is None and (
            _linhas_na_caixa(sem_carga, caixa, fonte, util) is not None
        ):
            culpadas.append(oferta.carga_horaria)
    return culpadas


def _painel(c, ficha, frases):
    """O painel com as opções listadas, ou o resumo; `True` quando resumiu (FR-3836).

    Pela ordem da FR-3836, que formaliza a exceção à FR-3425 da `111` para os templates de caixas:

    1. as opções listadas, cada caixa no maior corpo que a deixa caber;
    2. as opções listadas no **corpo mínimo** da caixa de oferta — a lista legível vem antes do
       resumo;
    3. se a carga horária é o que não cabe na linha, a recusa nomeando-a (EC-3): o resumo a
       apagaria da peça sem dizer;
    4. o resumo — o total, ou a contagem, e o convite à página —, nunca para uma opção só, que
       viraria "1 opções".
    """
    try:
        _painel_com(c, ficha, frases, resumir=False)
        return False
    except _NaoCabe:
        if not (c.template.tem_ofertas and kit_textos.lista_as_opcoes(ficha)):
            raise
    try:
        _painel_com(c, ficha, frases, resumir=False, oferta_no_minimo=True)
        return False
    except _NaoCabe:
        culpadas = _carga_que_nao_cabe(c, ficha)
        if culpadas:
            texto = "; ".join(f"«{carga}»" for carga in culpadas)
            raise _NaoCabe(CARGA_NAO_CABE.format(formato=c.formato.chave, cargas=texto)) from None
        if len(ficha.ofertas) < 2 or c.template.familia not in RESUMO_POR_ESPACO:
            raise
    _painel_com(c, ficha, frases, resumir=True)
    return True


def _painel_com(c, ficha, frases, *, resumir, oferta_no_minimo=False):
    """O retângulo de cor lisa preso pela base, com os itens empilhados de cima (D-004)."""
    painel = c.template.dimensoes["painel"]
    x, largura_ = painel["x"], painel["largura"]
    recuo = painel["recuo"]
    util = largura_ - 2 * recuo
    medidos = []
    for nome, texto, campo in _itens_do_painel(c, ficha, frases, resumir):
        caixa = c.template.caixa(nome)
        if oferta_no_minimo and nome == "oferta":
            caixa = replace(caixa, corpos=caixa.corpos[-1:])
        medida = _linhas_na_caixa(texto, caixa, c.fonte(nome), util)
        if medida is None:
            raise _NaoCabe(
                f"{_rotulo(campo.split(':', 1)[0]).capitalize()} não cabe no {c.formato.chave}: "
                f"{texto!r}."
            )
        medidos.append((nome, campo, *medida))
    espaco = painel["espaco"]
    altura_do_conteudo = sum(
        len(linhas) * corpo * entrelinha(c.fonte(nome)) for nome, _, corpo, linhas in medidos
    )
    altura_do_conteudo += espaco * max(len(medidos) - 1, 0)
    topo = painel["base"] - painel["recuo_em_baixo"] - altura_do_conteudo - recuo
    if topo < painel["topo_minimo"]:
        raise _NaoCabe(
            f"O conteúdo não cabe no {c.formato.chave} sem descer abaixo do corpo mínimo: o painel "
            f"subiria até {round(topo)} px, e o limite é {painel['topo_minimo']} px."
        )
    if painel.get("cor"):
        # Sem cor, o painel não se desenha: os itens ficam direto sobre o fundo, como na FIC e na
        # UAB, e o teste geométrico os confere contra os obstáculos da imagem.
        altura = painel["base"] - topo
        c.retangulo(x, topo, largura_, altura, cor=painel["cor"], raio=painel["raio"])
    y = topo + recuo
    for nome, campo, corpo, linhas in medidos:
        y = _escrever_em(c, nome, (x + recuo, y, util, 0), linhas, corpo, campo) + espaco


def _fundo(c, imagem):
    formato = c.formato
    c.elementos.append(
        Figura(
            0,
            0,
            formato.largura,
            formato.altura,
            imagem.arquivo(formato.chave),
            "image/jpeg",
            "imagem",
        )
    )


def _ativos_posicionados(c):
    """Os ativos fixos que o template posiciona (D-004, D-011).

    Os que `dimensoes["opacos"]` nomeia, com a cor de dentro, recebem texto, como o balão; os
    outros são obstáculo para o teste geométrico.
    """
    opacos = c.template.dimensoes.get("opacos", {})
    for nome, retangulo in c.template.ativos_posicionados.items():
        cor = opacos.get(nome)
        c.elementos.append(
            Figura(
                *retangulo,
                c.familia.ativos[nome].arquivo,
                "image/png",
                nome,
                opaca=cor is not None,
                cor=c.cor(cor) if cor else "",
            )
        )


def _faixa(c, ficha):
    """A prorrogação como faixa de ponta a ponta, quando o template a declara (119, T047).

    Sai nas mesmas condições do selo no painel — período declarado e prorrogação comprovada — e o
    painel deixa de trazê-lo.
    """
    faixa = c.template.dimensoes.get("faixa")
    if not faixa or ficha.modo != fichas.COM_PERIODO or not ficha.prorrogado:
        return
    c.retangulo(*faixa["retangulo"], cor=faixa["cor"])
    _caixa_unica(
        c,
        "selo_prorrogado",
        c.familia.frases["prorrogado"],
        "fixo",
        recusa="A faixa da prorrogação não cabe no {formato}.",
    )


def _balao(c):
    """A chamada à ação, no balão quando o template o declara; sem ele, direto no fundo."""
    balao = c.template.dimensoes.get("balao")
    if balao:
        ativo = c.familia.ativos[balao["ativo"]]
        cor = c.cor(balao["cor"]) if balao.get("cor") else ""
        figura = Figura(
            *balao["retangulo"], ativo.arquivo, "image/png", "balao", opaca=True, cor=cor
        )
        c.elementos.append(figura)
    _caixa_unica(
        c,
        "chamada_a_acao",
        c.formato.chamada_a_acao,
        "chamada_a_acao",
        recusa="A chamada à ação não cabe no {formato}.",
    )


def _imagem_escolhida(familia, escolha):
    if not familia.imagens:
        return None
    for imagem in familia.imagens:
        if imagem.chave == escolha.imagem:
            return imagem
    raise EscolhaInvalida("A imagem escolhida não está no banco da família.")


def _compor_em_caixas(ficha, template, escolha):
    c = _Composicao(template)
    familia, frases = c.familia, c.familia.frases
    imagem = _imagem_escolhida(familia, escolha)
    if imagem is not None:
        _fundo(c, imagem)
    _ativos_posicionados(c)
    _faixa(c, ficha)
    # As frases fixas posicionadas da família — a chamada do alto da UAB —, `{caixa: frase}`. Cada
    # uma é aprovada pela comunicação e passa pela varredura (FR-3814).
    for nome, frase in template.dimensoes.get("frases_posicionadas", {}).items():
        _caixa_unica(c, nome, frases[frase], "chamada", recusa="{texto!r} não cabe no {formato}.")
    avisos, omissao = [], ""
    titulo = _resolver_titulo(ficha, template, escolha)
    if titulo is None:
        omissao = SEM_TITULO
        avisos.append(SEM_TITULO_EM.format(formatos=template.formato.chave))
    else:
        campo, corpo, linhas = titulo
        _escrever_em(c, "titulo", template.caixa("titulo").retangulo, linhas, corpo, campo)
    _caixa_unica(
        c,
        "numero",
        ficha.identificacao,
        "identificacao",
        recusa="O número do Edital não cabe no {formato}: {texto!r}.",
    )
    if _painel(c, ficha, frases):
        avisos.append(RESUMO_EM.format(formatos=template.formato.chave))
    _balao(c)
    for nome, texto, campo in (
        ("busca", busca_na_peca(ficha), "busca"),
        ("selo_da_versao", selo_da_versao(ficha), "selo"),
    ):
        if template.caixa(nome).retangulo is not None:
            _caixa_unica(c, nome, texto, campo, recusa="{texto!r} não cabe no {formato}.")
    if template.tem_contato and ficha.contato:
        caixa = template.caixa("contato")
        texto = kit_textos.duvidas(ficha)
        medida = _linhas_na_caixa(
            texto, caixa, c.fonte("contato"), caixa.retangulo[2], caixa.retangulo[3]
        )
        if medida is None:
            avisos.append(SEM_CONTATO_EM.format(formatos=template.formato.chave))
        else:
            _escrever_em(c, "contato", caixa.retangulo, medida[1], medida[0], "contato")
    peca = Peca(
        elementos=tuple(c.elementos),
        alternativo=_alternativo_em_caixas(ficha, familia, imagem, c.elementos),
        titulo=titulo[0] if titulo else "",
        manchete=" ".join(titulo[2]) if titulo and titulo[0] == "manchete" else None,
        omissao=omissao,
        corpo=tuple(c.elementos),
        deslocamento=0,
        template=template,
        avisos=tuple(avisos),
        imagem=imagem,
    )
    ausentes = fora_dos_textos(peca, kit_textos.compor(ficha))
    if ausentes:
        raise PecaRecusada(f"A peça diria o que o kit textual não diz: {', '.join(ausentes)}.")
    return peca


def _alternativo_em_caixas(ficha, familia, imagem, elementos):
    """Em frases, na ordem em que a peça mostra, com a descrição da imagem (FR-3825)."""
    por_campo = {}
    for elemento in elementos:
        if isinstance(elemento, Texto):
            por_campo.setdefault(elemento.campo, []).append(elemento.conteudo)

    def junto(campo):
        return " ".join(por_campo.get(campo, []))

    abertura = f"Peça de divulgação do {kit_textos.assinatura(ficha)}, na identidade {familia.nome}"
    frases = [f"{abertura}, com {imagem.descricao}." if imagem else f"{abertura}."]
    if "chamada" in por_campo:
        frases.append(f"{junto('chamada').capitalize()}.")
    titulo = junto("titulo_sem_numero") or junto("titulo_do_processo") or junto("manchete")
    frases.append(f"{ficha.identificacao}: {titulo}." if titulo else f"{ficha.identificacao}.")
    if "periodo_curto" in por_campo:
        if ficha.prorrogado:
            frases.append("Prazo prorrogado.")
        partes = [junto("periodo_curto"), junto("hora")]
        frases.append(", ".join(filter(None, partes)) + ".")
        if "inicio" in por_campo:
            frases.append(f"{junto('inicio')}.")
    elif "fixo" in por_campo:
        frases.append(f"{familia.frases['publicado'].capitalize()}. {familia.frases['consulte']}.")
    if "total_de_vagas" in por_campo:
        frases.append(f"{junto('total_de_vagas')}.")
    for oferta in ficha.ofertas:
        linha = junto(f"oferta:{oferta.perfil_id}")
        if linha:
            frases.append(f"{linha}.")
    if "contagem" in por_campo:
        frases.append(f"{junto('contagem')}; {familia.frases['todas'].lower()}.")
    frases.append(f"{junto('chamada_a_acao')}, {junto('busca')}.")
    if "contato" in por_campo:
        frases.append(f"{junto('contato')}.")
    frases.append(f"{junto('selo').replace(' · ', ', ')}.")
    return " ".join(frases)


COMPOSITORES["caixas"] = _compor_em_caixas


def manchetes_dos_templates(ficha, templates):
    """A lista fechada da FR-3427 para vários formatos (FR-3818).

    Oferecida quando nenhum título oficial cabe em algum dos templates; fica com as candidatas que
    cabem como título em ao menos um deles, e cada formato a usa só se nenhum oficial couber nele.
    """
    sem_titulo = [t for t in templates if not titulo_oficial_cabe(ficha, t)]
    if not sem_titulo or not ficha.ofertas:
        return ()
    return tuple(
        candidata
        for candidata in _candidatas(ficha)
        if any(_cabe_como_titulo(candidata, template) for template in sem_titulo)
    )


def _cabe_como_titulo(texto, template):
    if template.composicao != "caixas":
        return bool(medidas_do_titulo(texto, template))
    caixa = template.caixa("titulo")
    fonte = kit_familias.familia(template.familia).fonte(caixa.fonte)
    _, _, largura_, altura = caixa.retangulo
    return _linhas_na_caixa(texto, caixa, fonte, largura_, altura) is not None


# ---- A conferência de coerência (FR-3423) ------------------------------------------------------

_DATA = re.compile(r"\b\d{2}/\d{2}(?:/\d{4})?\b")
_HORA = re.compile(r"\b\d{2}h\d{2}\b")
_QUANTIDADE = re.compile(r"\b\d+ (?:vagas?|opções)\b")


#: Os campos da peça que entram inteiros na conferência, além de datas e quantidades (119, FR-3813):
#: toda carga horária e todo contato que a peça mostra estão também nos textos.
CAMPOS_CONFERIDOS_POR_INTEIRO = ("carga_horaria", "contato", "oferta")


def fora_dos_textos(peca, textos):
    """As datas, horas e quantidades da peça que o kit textual não traz. Vazio é coerente."""
    corpo_dos_textos = "\n".join(textos.values())
    ausentes = []
    por_inteiro = {}
    for texto in peca.textos:
        campo = texto.campo.split(":", 1)[0]
        if campo in CAMPOS_CONFERIDOS_POR_INTEIRO:
            # Pode ter quebrado em linhas: confere-se o valor juntado, e não cada linha.
            por_inteiro.setdefault(texto.campo, []).append(texto.conteudo)
    for partes in por_inteiro.values():
        valor = " ".join(partes).removeprefix("Dúvidas? ")
        if " ".join(valor.split()) not in " ".join(corpo_dos_textos.split()):
            ausentes.append(valor)
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
def _ativo_em_base64(caminho):
    return base64.b64encode(Path(caminho).read_bytes()).decode("ascii")


@cache
def _fontes_embutidas(chaves):
    """O `@font-face` das fontes da família em `data:` (`D-021` da `111`, `D-005`).

    O SVG exportado é aberto fora do GPS — num navegador, no Inkscape, numa ferramenta de design —,
    e sem a fonte cada um desenharia com outra, e as caixas medidas extravasariam. A OFL permite
    embutir. O PNG não precisa: o rasterizador recebe as fontes por arquivo.
    """
    return kit_fontes.font_face(chaves)


def _elemento_em_svg(elemento, familia):
    if isinstance(elemento, Texto):
        fonte = kit_fontes.FONTES[elemento.fonte]
        ancora = f' text-anchor="{elemento.ancora}"' if elemento.ancora != "start" else ""
        return (
            f'<text x="{elemento.x}" y="{elemento.y}" font-family="{fonte.familia}" '
            f'font-size="{elemento.tamanho}" font-weight="{fonte.peso}" fill="{elemento.cor}"'
            f"{ancora} data-campo={quoteattr(elemento.campo)}>{escape(elemento.conteudo)}</text>"
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
    if isinstance(elemento, Figura):
        dados = _ativo_em_base64(str(familia.pasta_dos_ativos / elemento.arquivo))
        return (
            f'<image x="{elemento.x}" y="{elemento.y}" width="{elemento.largura}" '
            f'height="{elemento.altura}" preserveAspectRatio="none" '
            f"data-campo={quoteattr(elemento.campo)} "
            f'href="data:{elemento.tipo};base64,{dados}"/>'
        )
    # A marca entra em `data:`: o rasterizador não resolve nenhum recurso externo, e o arquivo
    # exportado é inteiro em si (D-007, item 4).
    dados = _ativo_em_base64(str(familia.pasta_dos_ativos / elemento.marca.arquivo))
    return (
        f'<image x="{elemento.x}" y="{elemento.y}" width="{elemento.largura}" '
        f'height="{elemento.altura}" data-campo={quoteattr(elemento.campo)} '
        f'href="data:image/png;base64,{dados}"/>'
    )


def svg(peca, ficha, *, fonte_embutida=False):
    """O SVG da peça. `fonte_embutida` na exportação; o rasterizador recebe as fontes à parte."""
    formato = peca.template.formato
    familia = kit_familias.familia(peca.template.familia)
    estilo = (
        f"<style>{_fontes_embutidas(familia.chaves_das_fontes())}</style>" if fonte_embutida else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{formato.largura}" '
        f'height="{formato.altura}" viewBox="0 0 {formato.largura} {formato.altura}" role="img" '
        'aria-labelledby="titulo descricao">'
        f'<title id="titulo">{escape(grafia.normalizar(ficha.identificacao))} — '
        "material de divulgação</title>"
        f'<desc id="descricao">{escape(grafia.normalizar(peca.alternativo))}</desc>'
        + estilo
        + "".join(_elemento_em_svg(elemento, familia) for elemento in peca.elementos)
        + "</svg>"
    )


def fontes_da_peca(peca):
    """As chaves das fontes da família da peça, para o rasterizador e o manifesto (`D-005`)."""
    return kit_familias.familia(peca.template.familia).chaves_das_fontes()


def conferir_marcas():
    """Os arquivos da marca são os que `ORIGEM.md` registra? `{arquivo: resumo}` dos que não são."""
    divergentes = {}
    for marca in MARCAS.values():
        resumo = hashlib.sha256((PASTA_DAS_MARCAS / marca.arquivo).read_bytes()).hexdigest()
        if resumo != marca.sha256:
            divergentes[marca.arquivo] = resumo
    return divergentes
