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
from datetime import datetime

from django.utils import timezone

from processo_seletivo.editais.domain.secoes import GERADA
from processo_seletivo.publicacoes.infrastructure import humano

LARGURA, ALTURA = 595, 842  # A4 em pontos
MARGEM = 56
TOPO = ALTURA - 64
RODAPE = 56

REGULAR, NEGRITO = "F1", "F2"

# Larguras em milésimos de em, para ASCII 32 a 126, na ordem do código (`008`, D-001).
#
# São as métricas das fontes base-14, que são fixas e não dependem de instalação — a mesma razão
# pela qual o documento pode declarar Helvetica sem embutir arquivo de fonte. Antes desta feature a
# quebra contava **caracteres** e multiplicava por um fator médio de 0,52: conservador o bastante
# para refluir parágrafo, e inservível para centralizar um cabeçalho ou alinhar uma coluna.
_ASCII_REGULAR = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
    1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
    333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584,
)
_ASCII_NEGRITO = (
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611,
    975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556,
    333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584,
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
    "—": (1000, 1000), "–": (556, 556), "·": (278, 278), "•": (350, 350),
    "§": (556, 556), "°": (400, 400), "º": (365, 330), "ª": (370, 300),
    "“": (333, 500), "”": (333, 500), "‘": (222, 278), "’": (222, 278),
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
CORPO_INSTITUCIONAL = 9.0
CORPO_ATO = 14.0
CORPO_SECAO = 11.5
CORPO_BLOCO = 10.5
CORPO_TEXTO = 10.0
CORPO_NOTA = 8.5

ESQUERDA, CENTRO, DIREITA = "esquerda", "centro", "direita"

# O modo do renderizador (FR-015). Um parâmetro, e não condicionais espalhadas pela composição:
# a diferença entre o que se revisa e o que se publica precisa ter **um** lugar onde está
# declarada, ou os dois documentos divergem sem que nada acuse.
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


def _quebrar(texto: str, tamanho: float, recuo: float, fonte: str = REGULAR) -> list[str]:
    """Reflui por largura real, e não por contagem de caracteres (FR-002, FR-032)."""
    disponivel = LARGURA - 2 * MARGEM - recuo
    linhas, atual = [], ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if largura(candidato, tamanho, fonte) <= disponivel:
            atual = candidato
        else:
            if atual:
                linhas.append(atual)
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
    if not valor:
        return "—"
    try:
        momento = datetime.fromisoformat(str(valor))
    except ValueError:
        return str(valor)
    if timezone.is_aware(momento):
        momento = timezone.localtime(momento)
    return momento.strftime("%d/%m/%Y %H:%M")


def _x(texto, fonte, tamanho, recuo, alinhamento):
    """Onde a linha começa. Centralizar e alinhar à direita só é possível por causa de FR-002."""
    if alinhamento == ESQUERDA:
        return MARGEM + recuo
    util = LARGURA - 2 * MARGEM
    sobra = util - largura(texto, tamanho, fonte)
    return MARGEM + (sobra / 2 if alinhamento == CENTRO else sobra)


class Composicao:
    """Acumula linhas com estilo e recuo; a paginação acontece depois, em uma passada."""

    def __init__(self):
        self.linhas: list[tuple[str, str, float, float, float, str]] = []

    def escrever(
        self, texto, *, tamanho=CORPO_TEXTO, fonte=REGULAR, recuo=0.0, antes=0.0,
        alinhamento=ESQUERDA,
    ):
        for indice, parte in enumerate(_quebrar(texto, tamanho, recuo, fonte)):
            self.linhas.append(
                (parte, fonte, tamanho, recuo, antes if indice == 0 else 0.0, alinhamento)
            )

    def espaco(self, altura=8.0):
        self.linhas.append(("", REGULAR, 0.0, 0.0, altura, ESQUERDA))

    def paginar(self):
        paginas, atual, y = [], [], TOPO
        for texto, fonte, tamanho, recuo, antes, alinhamento in self.linhas:
            altura = tamanho * 1.45 if tamanho else 0.0
            if y - antes - altura < RODAPE + 24 and atual:
                paginas.append(atual)
                atual, y = [], TOPO
                antes = 0.0
            y -= antes + altura
            if texto:
                x = _x(texto, fonte, tamanho, recuo, alinhamento)
                atual.append((texto, fonte, tamanho, x, y))
        if atual:
            paginas.append(atual)
        return paginas or [[]]


# A identificação do órgão é constante do documento, como já era — o que muda é a forma, não a
# origem (FR-005). O Processo e o objeto vêm do conteúdo publicado, que desde a `007` carrega o
# código e o título do Processo justamente para que o documento possa nomeá-lo.
ORGAO = ("MINISTÉRIO DA EDUCAÇÃO", "INSTITUTO FEDERAL DO ESPÍRITO SANTO")
UNIDADE = "CENTRO DE REFERÊNCIA EM FORMAÇÃO E EM EDUCAÇÃO A DISTÂNCIA"


def _cabecalho(composicao, snapshot):
    """A abertura de um ato administrativo (FR-005 a FR-007).

    Calibrado contra os Editais 62/2026 e 73/2026 do Cefor: a hierarquia vem de **peso, caixa alta
    e centralização**, não de corpo grande. Nos dois alvos o ato está em corpo próximo ao do texto,
    e destacar por tamanho produziria um título fora do padrão institucional.
    """
    for linha in ORGAO:
        composicao.escrever(
            linha, tamanho=CORPO_INSTITUCIONAL, fonte=NEGRITO, alinhamento=CENTRO
        )
    composicao.escrever(UNIDADE, tamanho=CORPO_INSTITUCIONAL, alinhamento=CENTRO)
    composicao.escrever(
        f"EDITAL Nº {snapshot.get('number', '')}/{snapshot.get('year', '')}",
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=22,
        alinhamento=CENTRO,
    )
    if snapshot.get("processoTitle"):
        composicao.escrever(
            snapshot["processoTitle"].upper(),
            tamanho=CORPO_SECAO,
            fonte=NEGRITO,
            antes=4,
            alinhamento=CENTRO,
        )
    composicao.escrever(
        snapshot.get("title", ""), tamanho=CORPO_BLOCO, antes=4, alinhamento=CENTRO
    )
    if snapshot.get("description"):
        composicao.escrever(snapshot["description"], tamanho=CORPO_TEXTO, antes=16)


def _modalidades(composicao, perfil):
    modalidades = perfil.get("competitionModalities") or []
    if not modalidades:
        return
    composicao.escrever(
        "Modalidades de concorrência:", tamanho=10, fonte=NEGRITO, recuo=18, antes=6
    )
    for modalidade in modalidades:
        composicao.escrever(
            f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
            tamanho=10,
            recuo=32,
        )
        regra = modalidade.get("normativeRule")
        if not regra:
            continue
        partes = [f"fundamento: {regra.get('foundation', '')}"]
        if regra.get("version"):
            partes.append(f"versão: {regra['version']}")
        if regra.get("percentage"):
            partes.append(f"percentual: {humano.decimal(regra['percentage'])}%")
        if regra.get("effectiveFrom"):
            partes.append(f"vigência: {_instante(regra['effectiveFrom'])}")
        composicao.escrever("Regra Normativa — " + "; ".join(partes), tamanho=9, recuo=46)


def _perfis(composicao, snapshot, secao=0):
    for perfil in snapshot.get("profiles") or []:
        composicao.escrever(
            f"{perfil.get('code', '')} — {perfil.get('name', '')}",
            tamanho=11,
            fonte=NEGRITO,
            antes=12,
        )
        if perfil.get("description"):
            composicao.escrever(perfil["description"], tamanho=10, recuo=18, antes=3)
        if perfil.get("locality"):
            composicao.escrever(f"Localidade: {perfil['locality']}", tamanho=10, recuo=18)
        composicao.escrever(
            f"Vagas imediatas: {perfil.get('immediateVacancies', 0)}", tamanho=10, recuo=18
        )
        # Atribuições, carga horária e remuneração (FR-015). Cada um é omitido quando vazio: um
        # rótulo sobre nada não informa que não há nada — informa que alguém esqueceu de preencher.
        # As atribuições preservam parágrafos, pelo caminho que a `006.1` abriu para as seções.
        if perfil.get("duties"):
            composicao.escrever("Atribuições:", tamanho=10, fonte=NEGRITO, recuo=18, antes=6)
            for paragrafo in _paragrafos(perfil["duties"]):
                composicao.escrever(paragrafo, tamanho=10, recuo=32, antes=3)
        if perfil.get("workload"):
            composicao.escrever(f"Carga horária: {perfil['workload']}", tamanho=10, recuo=18)
        if perfil.get("compensation"):
            composicao.escrever(f"Remuneração: {perfil['compensation']}", tamanho=10, recuo=18)
        reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
        if perfil.get("reserveLimit") is not None:
            reserva = f"{reserva} em {perfil['reserveLimit']}"
        composicao.escrever(f"Cadastro Reserva: {reserva}", tamanho=10, recuo=18)
        requisitos = perfil.get("requirements") or []
        if requisitos:
            composicao.escrever("Requisitos:", tamanho=10, fonte=NEGRITO, recuo=18, antes=6)
            for requisito in requisitos:
                composicao.escrever(f"• {requisito}", tamanho=10, recuo=32)
        _modalidades(composicao, perfil)


def _cronograma(composicao, snapshot, secao=0):
    for evento in snapshot.get("schedule") or []:
        composicao.escrever(
            f"{evento.get('order', '')}. {evento.get('type', '')} — "
            f"{evento.get('description', '')}",
            tamanho=10,
            fonte=NEGRITO,
            antes=8,
        )
        periodo = f"Início: {_instante(evento.get('startAt'))}"
        if evento.get("endAt"):
            periodo += f"    Término: {_instante(evento['endAt'])}"
        composicao.escrever(periodo, tamanho=10, recuo=18)
        # O estado do Evento **não é composto**, e não recebe mapa de tradução (FR-002).
        # Existe o precedente de `RESERVA` logo acima, e a tentação de imitá-lo aqui: mas os dois
        # casos são distintos. O tipo de cadastro reserva descreve a vaga e interessa a quem se
        # inscreve; `PLANEJADO`, `EM_ANDAMENTO` e `CONCLUIDO` descrevem a execução do certame e são
        # informação de gestão. Um Edital publicado não diz que suas inscrições estão "planejadas" —
        # ele as anuncia. Traduzir o rótulo produziria uma frase correta dizendo ao candidato algo
        # que não é matéria de Edital.


CARATER_DA_ETAPA = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _etapas(composicao, snapshot, secao=0):
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
        composicao.escrever(
            f"{secao}.{ordem} {etapa.get('name', '')}",
            tamanho=CORPO_BLOCO,
            fonte=NEGRITO,
            antes=10,
        )
        caracteres = [
            rotulo for chave, rotulo in CARATER_DA_ETAPA if etapa.get(chave)
        ]
        partes = []
        if caracteres:
            partes.append("caráter: " + " e ".join(caracteres))
        if etapa.get("weight") is not None:
            partes.append(f"peso: {humano.decimal(etapa['weight'])}")
        if etapa.get("minimumScore") is not None:
            partes.append(f"nota mínima: {humano.decimal(etapa['minimumScore'])}")
        if partes:
            composicao.escrever("; ".join(partes), tamanho=10, recuo=18)
        # As datas são do Evento e não são copiadas: o documento as lê de lá, como o domínio.
        evento = eventos.get(etapa.get("scheduleEventId"))
        if evento:
            periodo = f"Início: {_instante(evento.get('startAt'))}"
            if evento.get("endAt"):
                periodo += f"    Término: {_instante(evento['endAt'])}"
            composicao.escrever(
                f"Conforme o Cronograma — {evento.get('type', '')}: {periodo}",
                tamanho=9,
                recuo=18,
            )


# Cada seção gerada nomeia a coleção que a origina; aqui está o que fazer com cada uma. Uma origem
# que não estiver neste mapa não é composta — e a validação de publicação já recusa origem que
# divirja do catálogo, então isso não é silêncio: é a consequência de uma recusa que veio antes.
_CORPO_GERADO = {"profiles": _perfis, "schedule": _cronograma, "stages": _etapas}


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


def _secoes(composicao, snapshot):
    """O documento numerado, em dois passos: selecionar, depois enumerar (FR-010 a FR-012).

    **A ordem dos dois passos é o requisito.** Numerar durante a iteração produziria `5.`, `7.`,
    `8.` no primeiro Edital sem Etapas de Avaliação — um defeito que o cenário de demonstração não
    revela, porque nele está tudo preenchido. O número é da materialização: ele não existe no
    conteúdo homologado e não sobrevive a uma mudança de ordem (FR-012).
    """
    for numero, (secao, corpo) in enumerate(_materializaveis(snapshot), 1):
        titulo = f"{numero}. {secao.get('title', '').upper()}"
        composicao.escrever(titulo, tamanho=CORPO_SECAO, fonte=NEGRITO, antes=18)
        if corpo is not None:
            corpo(composicao, snapshot, numero)
        else:
            for indice, paragrafo in enumerate(_paragrafos(secao.get("content", ""))):
                composicao.escrever(
                    paragrafo, tamanho=CORPO_TEXTO, antes=6 if indice == 0 else 7
                )


def _integridade(composicao, snapshot, content_hash):
    composicao.escrever("INTEGRIDADE", tamanho=12, fonte=NEGRITO, antes=18)
    composicao.escrever(
        "Este documento deriva integralmente da versão homologada identificada abaixo.",
        tamanho=10,
        antes=6,
    )
    # Identificação **institucional**, não técnica (FR-004). O SHA-256 permanece porque é o que a
    # declaração prova; o UUID sai porque não prova nada a quem lê e era a forma interna vazando
    # para a apresentação. Os identificadores continuam no snapshot — o que muda é o que se imprime.
    composicao.escrever(
        f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}", tamanho=9
    )
    processo = " — ".join(
        parte
        for parte in (snapshot.get("processoCode", ""), snapshot.get("processoTitle", ""))
        if parte
    )
    composicao.escrever(f"Processo Seletivo {processo}", tamanho=9)
    composicao.escrever(f"Versão do schema: {snapshot.get('schemaVersion', '')}", tamanho=9)
    composicao.escrever(f"SHA-256 do conteúdo: {content_hash}", tamanho=9)


def _fluxo_da_pagina(linhas, rodape, marca=""):
    partes = []
    if marca:
        partes.append(
            b"BT /" + NEGRITO.encode()
            + f" 9.0 Tf {MARGEM:.1f} {FAIXA_DE_PREVIA:.1f} Td (".encode()
            + _texto_pdf(marca)
            + b") Tj ET"
        )
    for texto, fonte, tamanho, x, y in linhas:
        partes.append(
            b"BT /"
            + fonte.encode()
            + f" {tamanho:.1f} Tf {x:.1f} {y:.1f} Td (".encode()
            + _texto_pdf(texto)
            + b") Tj ET"
        )
    partes.append(
        b"BT /" + REGULAR.encode() + f" 8.0 Tf {MARGEM:.1f} {RODAPE - 16:.1f} Td (".encode()
        + _texto_pdf(rodape)
        + b") Tj ET"
    )
    return b"\n".join(partes)


def render_edital_pdf(snapshot: dict, content_hash: str, modo: str = MODO_PUBLICADO) -> bytes:
    """O mesmo documento, em dois modos.

    Em `MODO_PUBLICADO` o resultado é o de sempre, byte a byte — uma fixture o guarda. Em
    `MODO_PREVIA` a seção de integridade não é composta e `content_hash` **não é lido em lugar
    nenhum**: um documento administrativo que parece publicado sem ter sido é risco normativo, e
    depender de o chamador passar vazio seria deixar a garantia com quem não a tem (FR-014).
    """
    if modo not in MODOS:
        raise ValueError(f"Modo de renderização desconhecido: {modo!r}.")
    previa = modo == MODO_PREVIA

    composicao = Composicao()
    _cabecalho(composicao, snapshot)
    _secoes(composicao, snapshot)
    if not previa:
        _integridade(composicao, snapshot, content_hash)
    paginas = composicao.paginar()

    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = (
        f"{MARCA_DE_PREVIA} · {edital}" if previa else f"{edital} · SHA-256 {content_hash[:16]}…"
    )
    fluxos = [
        _fluxo_da_pagina(
            linhas,
            f"{identificacao} · Página {numero} de {len(paginas)}",
            marca=MARCA_DE_PREVIA if previa else "",
        )
        for numero, linhas in enumerate(paginas, 1)
    ]

    # Objetos: 1 catálogo, 2 páginas, 3 e 4 fontes, depois pares página/conteúdo.
    primeiro_pagina = 5
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
    ]
    for indice, fluxo in enumerate(fluxos):
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] ".encode()
            + b"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
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
