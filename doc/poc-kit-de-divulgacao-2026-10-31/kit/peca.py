"""A peça do feed, 1080 × 1350, em SVG — um template, composto da ficha e de mais nada.

**Mede antes de desenhar.** SVG não quebra linha sozinho, e a largura que decide a quebra é a da
fonte que vai ser desenhada: a métrica é a da Edital Sans, a mesma que o Edital embute
(`publicacoes/infrastructure/fonte.py`), e a quebra é a `_quebrar` do compositor do Edital. Duas
medidas — uma para quebrar, outra para desenhar — dariam linha que transborda só no PNG.

**Recusa em vez de encolher sem fim.** O título desce de corpo até um mínimo legível no celular; se
nem assim cabe, ele **sai da peça** e a recusa é dita, nomeando o que faltou — a peça não trunca o
título com reticências, porque o que sobra de um título cortado pode dizer outra coisa. A oferta,
acima de quatro opções, vira contagem. Nada é reescrito para caber.

**Cada texto leva o campo da ficha de onde veio** (`data-campo`). É o que a conferência de coerência
lê para provar que a peça não diz nada que a ficha não diga.

**A marca é um marcador.** O repositório não tem ativo oficial do Ifes (estudo, Eixo E). A faixa do
topo diz isso, por extenso, em vez de imitar uma marca.
"""

from dataclasses import dataclass, field
from xml.sax.saxutils import escape, quoteattr

from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure.fonte import METRICA, NEGRITO, REGULAR
from processo_seletivo.publicacoes.infrastructure.pdf import _quebrar

from .ficha import COM_PERIODO, INDISPONIVEL
from .textos import assinatura, rotulo_da_oferta, rotulos_distintos

LARGURA, ALTURA = 1080, 1350
MARGEM = 80
UTIL = LARGURA - 2 * MARGEM
FAMILIA = "Edital Sans"

# Os tokens do produto (`shared/static/shared/tokens.css`), e **não** o manual do Ifes: a POC não
# inventa a paleta institucional, usa a que o GPS já tem e já passou no contraste AA.
VERDE_ESCURO = "#0b5a2a"
VERDE_TEXTO = "#146c37"
VERDE_CLARO = "#e7f5ec"
TEXTO = "#1c1c1c"
TEXTO_FRACO = "#555555"
BORDA = "#d4d4d4"
FUNDO = "#ffffff"
AMARELO = "#8a5300"
AMARELO_FUNDO = "#fdf5e5"

# O título, do maior ao menor corpo admitido, e o número de linhas em cada um. 40 px em 1080 px é
# ~13 pt numa tela de 6" vista inteira — o mínimo que se lê sem ampliar (hipótese a medir com a
# comunicação).
CORPOS_DO_TITULO = ((52, 3), (46, 3), (40, 4))
LIMITE_DE_OPCOES = 4

# As frases fixas do template. A conferência aceita só estas, além dos valores da ficha.
FIXOS = {
    "marca": "MARCA INSTITUCIONAL",
    "marca_nota": "marcador da POC — não é ativo oficial",
    "chamada": "PROCESSO SELETIVO",
    "inscricoes": "INSCRIÇÕES",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "prorrogado": "PRAZO PRORROGADO",
    "horario": "horário de Brasília",
    "oferta": "OFERTA",
    "todas": "Confira todas na página oficial",
    "rodape": "Condições, documentos e cronograma:",
}


class PecaNaoCabe(Exception):
    """A composição recusada, com o motivo dito para quem gera."""


@dataclass
class Composicao:
    elementos: list = field(default_factory=list)
    leitura: list = field(default_factory=list)  # o texto alternativo, na ordem de leitura
    omissoes: list = field(default_factory=list)

    def texto(
        self,
        x,
        y,
        conteudo,
        *,
        tamanho,
        campo,
        fonte=REGULAR,
        cor=TEXTO,
        ancora="start",
        espacamento=0,
        ler=True,
    ):
        faltam = grafia.sem_grafia(conteudo)
        if faltam:
            raise PecaNaoCabe(f"Caractere sem grafia na fonte da peça, em {campo}: {faltam}")
        peso = "700" if fonte == NEGRITO else "400"
        extra = f' letter-spacing="{espacamento}"' if espacamento else ""
        self.elementos.append(
            f'<text x="{x}" y="{y}" font-family="{FAMILIA}" font-size="{tamanho}" '
            f'font-weight="{peso}" fill="{cor}" text-anchor="{ancora}"{extra} '
            f"data-campo={quoteattr(campo)}>{escape(conteudo)}</text>"
        )
        if ler:
            # As linhas de um mesmo campo são uma frase só: o título quebrado em duas linhas não
            # vira duas frases no texto alternativo.
            if self.leitura and self.leitura[-1][0] == campo and campo != "fixo":
                self.leitura[-1] = (campo, f"{self.leitura[-1][1]} {conteudo}")
            else:
                self.leitura.append((campo, conteudo))

    def retangulo(self, x, y, largura, altura, *, cor, raio=0, contorno=None, tracejado=False):
        borda = f' stroke="{contorno}" stroke-width="3"' if contorno else ""
        traco = ' stroke-dasharray="14 10"' if tracejado else ""
        self.elementos.append(
            f'<rect x="{x}" y="{y}" width="{largura}" height="{altura}" rx="{raio}" '
            f'fill="{cor}"{borda}{traco}/>'
        )


def largura(texto, tamanho, fonte=REGULAR):
    return METRICA.largura(texto, tamanho, fonte)


def quebrar(texto, tamanho, fonte=REGULAR, limite=UTIL):
    return _quebrar(texto, tamanho, 0, fonte, limite=limite, metrica=METRICA)


def _titulo(c, ficha, y):
    """O título do Edital; se não couber, o do Processo; se nenhum couber, nada — e a omissão dita.

    O do Processo é dado publicado como o do Edital (`processoTitle`), e não resumo feito pela peça:
    trocar um título oficial por outro não muda o que se afirma. No 92/2026 o do Edital tem 208
    caracteres e o do Processo, 63.
    """
    candidatos = (
        ("titulo_sem_numero", ficha["titulo_sem_numero"] or ficha["titulo"]),
        ("titulo_do_processo", ficha["titulo_do_processo"]),
    )
    for campo, titulo in candidatos:
        if not titulo:
            continue
        for tamanho, maximo in CORPOS_DO_TITULO:
            linhas = quebrar(titulo, tamanho, NEGRITO)
            if len(linhas) <= maximo:
                if campo != "titulo_sem_numero":
                    c.omissoes.append(
                        f"Título do Edital não coube ({len(candidatos[0][1])} caracteres): "
                        "a peça usa o título do Processo. Manchete curta é a D-3."
                    )
                for linha in linhas:
                    y += round(tamanho * 1.18)
                    c.texto(MARGEM, y, linha, tamanho=tamanho, campo=campo, fonte=NEGRITO)
                return y
    c.omissoes.append(
        f"Título omitido: nem o do Edital nem o do Processo couberam em {CORPOS_DO_TITULO[-1][1]} "
        f"linhas a {CORPOS_DO_TITULO[-1][0]} px. Pede manchete curta (D-3)."
    )
    return y


def _periodo(c, ficha, y):
    """O bloco do período: a norma em data absoluta, e nenhuma palavra sobre o agora."""
    altura = 250
    c.retangulo(MARGEM - 20, y, UTIL + 40, altura, cor=VERDE_ESCURO, raio=28)
    topo = y + 64
    c.texto(
        MARGEM + 10,
        topo,
        FIXOS["inscricoes"],
        tamanho=34,
        campo="fixo",
        fonte=NEGRITO,
        cor=FUNDO,
        espacamento=6,
    )
    if ficha["prorrogado"]:
        # Na mesma linha de "INSCRIÇÕES", à direita: o selo é qualificação do período, e uma linha
        # só para ele empurrava a oferta para dentro do rodapé num Edital de quatro polos.
        rotulo = FIXOS["prorrogado"]
        largura_do_selo = largura(rotulo, 26, NEGRITO) + 3 * len(rotulo) + 44
        esquerda = LARGURA - MARGEM - 10 - largura_do_selo
        c.retangulo(
            round(esquerda), topo - 40, round(largura_do_selo), 54, cor=AMARELO_FUNDO, raio=27
        )
        c.texto(
            round(esquerda + 22),
            topo - 3,
            rotulo,
            tamanho=26,
            campo="fixo",
            fonte=NEGRITO,
            cor=AMARELO,
            espacamento=3,
        )
    datas = ficha["periodo_curto"]
    tamanho = 92
    while largura(datas, tamanho, NEGRITO) > UTIL - 20 and tamanho > 64:
        tamanho -= 4
    c.texto(
        MARGEM + 10,
        topo + 104,
        datas,
        tamanho=tamanho,
        campo="periodo_curto",
        fonte=NEGRITO,
        cor=FUNDO,
    )
    if ficha["fim_hora"]:
        c.texto(
            MARGEM + 10,
            topo + 158,
            f"até as {ficha['fim_hora']} · {FIXOS['horario']}",
            tamanho=32,
            campo="fim_hora",
            cor=VERDE_CLARO,
        )
    return y + altura


def _publicado(c, y):
    c.retangulo(MARGEM - 20, y, UTIL + 40, 220, cor=VERDE_ESCURO, raio=28)
    c.texto(
        MARGEM + 10, y + 100, FIXOS["publicado"], tamanho=64, campo="fixo", fonte=NEGRITO, cor=FUNDO
    )
    c.texto(MARGEM + 10, y + 165, FIXOS["consulte"], tamanho=34, campo="fixo", cor=VERDE_CLARO)
    return y + 220


def _oferta(c, ficha, y):
    ofertas = ficha["ofertas"]
    if not ofertas:
        return y
    y += 76
    c.texto(
        MARGEM,
        y,
        FIXOS["oferta"],
        tamanho=28,
        campo="fixo",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        espacamento=4,
    )
    # O total na linha do rótulo: é resumo da lista, e não mais uma linha dela.
    if ficha["total_de_vagas"] and len(ofertas) > 1:
        c.texto(
            LARGURA - MARGEM,
            y,
            f"{ficha['total_de_vagas']} vagas no total",
            tamanho=28,
            campo="total_de_vagas",
            fonte=NEGRITO,
            cor=VERDE_TEXTO,
            ancora="end",
        )
    if ficha["nomes_iguais"]:
        for linha in quebrar(ofertas[0]["nome"], 34, NEGRITO):
            y += 48
            c.texto(MARGEM, y, linha, tamanho=34, campo="oferta_nome", fonte=NEGRITO)
    if len(ofertas) > LIMITE_DE_OPCOES or not rotulos_distintos(ficha):
        y += 58
        c.texto(MARGEM, y, f"{len(ofertas)} opções", tamanho=44, campo="contagem", fonte=NEGRITO)
        y += 50
        c.texto(MARGEM, y, FIXOS["todas"], tamanho=32, campo="fixo", cor=TEXTO_FRACO)
        return y
    for oferta in ofertas:
        rotulo = rotulo_da_oferta(oferta, ficha)
        quantidade = oferta["quantidade"]
        # A coluna da quantidade é medida, e não reservada: "3 vagas e cadastro reserva" ocupa o
        # dobro de "40 vagas", e a largura fixa fazia um invadir o outro.
        lado = UTIL - largura(quantidade, 32, NEGRITO) - 32
        linhas = quebrar(rotulo, 32, REGULAR, limite=lado)
        empilhar = len(linhas) > 1
        if empilhar:
            linhas = quebrar(rotulo, 32, REGULAR)
        if len(linhas) > 2:
            raise PecaNaoCabe(f"Opção com rótulo longo demais para a lista: {rotulo!r}")
        y += 54
        topo = y
        for posicao, linha in enumerate(linhas):
            c.texto(MARGEM, y, linha, tamanho=32, campo=f"oferta_rotulo:{oferta['perfil_id']}")
            if posicao < len(linhas) - 1:
                y += 42
        if quantidade and empilhar:
            y += 42
            c.texto(
                LARGURA - MARGEM,
                y,
                quantidade,
                tamanho=32,
                campo=f"oferta_quantidade:{oferta['perfil_id']}",
                fonte=NEGRITO,
                ancora="end",
            )
        elif quantidade:
            c.texto(
                LARGURA - MARGEM,
                topo,
                quantidade,
                tamanho=32,
                campo=f"oferta_quantidade:{oferta['perfil_id']}",
                fonte=NEGRITO,
                ancora="end",
            )
        c.elementos.append(
            f'<line x1="{MARGEM}" y1="{y + 20}" x2="{LARGURA - MARGEM}" y2="{y + 20}" '
            f'stroke="{BORDA}" stroke-width="2"/>'
        )
    return y


def _alternativo(leitura):
    """O texto alternativo em frases, com o que a peça **mostra**, na ordem em que mostra.

    Lê o que foi desenhado, e não a ficha: uma opção que a peça resumiu em contagem não aparece
    por extenso aqui, porque quem ouve o texto alternativo precisa receber a mesma peça que quem a vê.
    Os rótulos de seção ("OFERTA", "INSCRIÇÕES") viram a frase que eles introduzem.
    """
    partes = []
    for campo, texto in leitura:
        tipo = campo.partition(":")[0]
        if campo == "assinatura":
            partes.append(f"Peça de divulgação — {texto}")
        elif campo == "identificacao":
            partes.append(f"Processo seletivo, {texto}")
        elif campo in ("titulo_sem_numero", "titulo_do_processo"):
            partes[-1] += f": {texto}"
        elif campo == "fixo" and texto == FIXOS["prorrogado"]:
            partes.append("Prazo prorrogado")
        elif campo == "fixo" and texto in (FIXOS["publicado"], FIXOS["consulte"]):
            partes.append(texto.capitalize() if texto.isupper() else texto)
        elif campo == "periodo_curto":
            partes.append(
                f"Inscrições {texto}" if texto[:1].isalpha() else f"Inscrições de {texto}"
            )
        elif campo == "fim_hora":
            partes[-1] += f", {texto.replace(' · ', ', ')}"
        elif campo == "oferta_nome":
            partes.append(f"Oferta: {texto}")
        elif campo == "total_de_vagas":
            partes.append(texto.capitalize())
        elif tipo == "oferta_rotulo":
            partes.append(texto)
        elif tipo == "oferta_quantidade":
            partes[-1] += f", {texto}"
        elif campo == "contagem":
            partes.append(f"Oferta: {texto}, todas na página oficial")
        elif campo == "destino":
            partes.append(f"Condições, documentos e cronograma: {texto.replace(' · ', ', ')}")
    return ". ".join(parte.rstrip(".") for parte in partes) + "."


def compor(ficha):
    """`(svg, texto_alternativo, omissoes)`, ou `PecaNaoCabe`."""
    if ficha["modo"] == INDISPONIVEL:
        raise PecaNaoCabe(ficha["motivo"])
    c = Composicao()
    c.retangulo(0, 0, LARGURA, ALTURA, cor=FUNDO)
    # A faixa da marca: marcador declarado, nunca imitação.
    c.retangulo(0, 0, LARGURA, 150, cor=VERDE_ESCURO)
    c.retangulo(
        MARGEM - 20, 34, 420, 82, cor=VERDE_ESCURO, raio=12, contorno=VERDE_CLARO, tracejado=True
    )
    c.texto(
        MARGEM,
        72,
        FIXOS["marca"],
        tamanho=24,
        campo="fixo",
        fonte=NEGRITO,
        cor=FUNDO,
        espacamento=2,
        ler=False,
    )
    c.texto(MARGEM, 102, FIXOS["marca_nota"], tamanho=20, campo="fixo", cor=VERDE_CLARO, ler=False)
    c.texto(
        LARGURA - MARGEM,
        96,
        assinatura(ficha),
        tamanho=40,
        campo="assinatura",
        fonte=NEGRITO,
        cor=FUNDO,
        ancora="end",
    )

    corpo = len(c.elementos)
    y = 224
    c.texto(
        MARGEM,
        y,
        FIXOS["chamada"],
        tamanho=30,
        campo="fixo",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
        espacamento=5,
    )
    y += 46
    c.texto(MARGEM, y, ficha["identificacao"], tamanho=34, campo="identificacao", cor=TEXTO_FRACO)
    y = _titulo(c, ficha, y + 6)
    y += 38
    y = _periodo(c, ficha, y) if ficha["modo"] == COM_PERIODO else _publicado(c, y)
    y = _oferta(c, ficha, y)

    rodape = ALTURA - 176
    if y > rodape - 30:
        raise PecaNaoCabe(f"A composição passou do rodapé ({y} px > {rodape - 30} px).")
    # O que sobra entre o corpo e o rodapé vai em parte para cima do corpo: com duas opções, o vazio
    # inteiro embaixo fazia a peça parecer cortada. Só desloca — nada muda de tamanho nem de ordem.
    folga = round((rodape - 30 - y) * 0.35)
    if folga > 0:
        c.elementos[corpo:] = [
            f'<g transform="translate(0 {folga})">',
            *c.elementos[corpo:],
            "</g>",
        ]
    c.elementos.append(
        f'<line x1="{MARGEM}" y1="{rodape}" x2="{LARGURA - MARGEM}" y2="{rodape}" '
        f'stroke="{BORDA}" stroke-width="2"/>'
    )
    c.texto(MARGEM, rodape + 50, FIXOS["rodape"], tamanho=30, campo="fixo", cor=TEXTO_FRACO)
    # O endereço é da implantação, e o seu comprimento não se conhece de antemão: mede-se, desce de
    # corpo até 28 px e, se nem assim couber, a busca vai para a linha de cima do selo.
    destino = f"{ficha['caminho_curto']} · busque por {ficha['numero']}/{ficha['ano']}"
    tamanho = 36
    while largura(destino, tamanho, NEGRITO) > UTIL and tamanho > 28:
        tamanho -= 2
    if largura(destino, tamanho, NEGRITO) > UTIL:
        raise PecaNaoCabe(f"Endereço longo demais para o rodapé: {ficha['caminho_curto']!r}")
    c.texto(
        MARGEM,
        rodape + 96,
        destino,
        tamanho=tamanho,
        campo="destino",
        fonte=NEGRITO,
        cor=VERDE_TEXTO,
    )
    selo = (
        f"Versão vigente desde {ficha['versao_desde_texto']} · {ficha['versao_ato']} · "
        f"ref. {ficha['impressao'][:8]}"
    )
    c.texto(MARGEM, rodape + 140, selo, tamanho=20, campo="selo", cor=TEXTO_FRACO, ler=False)

    alternativo = _alternativo(c.leitura)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" '
        f'viewBox="0 0 {LARGURA} {ALTURA}" role="img" aria-labelledby="titulo descricao">'
        f'<title id="titulo">{escape(ficha["identificacao"])} — material de divulgação</title>'
        f'<desc id="descricao">{escape(alternativo)}</desc>' + "".join(c.elementos) + "</svg>"
    )
    return svg, alternativo, c.omissoes
